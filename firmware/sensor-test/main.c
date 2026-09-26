#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "hardware/adc.h"
#include "pico/stdio_usb.h"
#include "pico/stdlib.h"

enum {
    PIN_MUX_A0 = 2,
    PIN_MUX_A1 = 3,
    PIN_MUX_A2 = 4,
    PIN_MUX_EN0 = 5,
    PIN_HALL_PWR_EN = 7,
    PIN_STATUS_LED = 11,
    PIN_ADC0 = 26,
};

enum {
    ADC_INPUT_0 = 0,
    MUX_ADDRESS_COUNT = 4,
    MUX_SETTLE_US = 20,
    ADC_SAMPLES_PER_KEY = 8,
    USB_WAIT_MS = 3000,
    HALL_POWER_SETTLE_MS = 10,
    FRAME_PERIOD_MS = 10,
};

static void init_output(uint pin, bool value) {
    gpio_init(pin);
    gpio_set_dir(pin, GPIO_OUT);
    gpio_put(pin, value);
}

static void mux_set_address(uint8_t address) {
    gpio_put(PIN_MUX_A0, (address >> 0) & 1u);
    gpio_put(PIN_MUX_A1, (address >> 1) & 1u);
    gpio_put(PIN_MUX_A2, (address >> 2) & 1u);
}

static uint16_t read_adc_average(void) {
    // First conversion after an analog-mux transition is intentionally discarded.
    (void)adc_read();

    uint32_t sum = 0;
    for (uint i = 0; i < ADC_SAMPLES_PER_KEY; ++i) {
        sum += adc_read();
    }
    return (uint16_t)((sum + ADC_SAMPLES_PER_KEY / 2u) / ADC_SAMPLES_PER_KEY);
}

int main(void) {
    // Keep the Hall rail and mux disabled from the first software-controlled state.
    init_output(PIN_HALL_PWR_EN, false);
    init_output(PIN_MUX_EN0, false);
    init_output(PIN_MUX_A0, false);
    init_output(PIN_MUX_A1, false);
    init_output(PIN_MUX_A2, false);
    init_output(PIN_STATUS_LED, false);

    adc_init();
    adc_gpio_init(PIN_ADC0);
    adc_select_input(ADC_INPUT_0);

    stdio_init_all();

    // Give USB CDC time to enumerate, but do not require a host for board operation.
    absolute_time_t usb_deadline = make_timeout_time_ms(USB_WAIT_MS);
    while (!stdio_usb_connected() && !time_reached(usb_deadline)) {
        sleep_ms(10);
    }

    gpio_put(PIN_HALL_PWR_EN, true);
    sleep_ms(HALL_POWER_SETTLE_MS);
    gpio_put(PIN_MUX_EN0, true);
    gpio_put(PIN_STATUS_LED, true);

    printf("# he-piantor-42 sensor-test\n");
    printf("# settle_us=%u,samples_per_key=%u\n", MUX_SETTLE_US, ADC_SAMPLES_PER_KEY);
    printf("timestamp_us,key,mux_address,adc_raw,hall_power,test_marker\n");

    while (true) {
        absolute_time_t frame_start = get_absolute_time();

        for (uint8_t address = 0; address < MUX_ADDRESS_COUNT; ++address) {
            mux_set_address(address);
            busy_wait_us_32(MUX_SETTLE_US);

            const uint16_t raw = read_adc_average();
            const uint64_t timestamp_us = time_us_64();

            printf("%llu,%u,%u,%u,1,stream\n",
                   (unsigned long long)timestamp_us,
                   (unsigned)address,
                   (unsigned)address,
                   (unsigned)raw);
        }

        // Keep the initial logger bandwidth modest and deterministic.
        const int64_t elapsed_us = absolute_time_diff_us(frame_start, get_absolute_time());
        const int64_t target_us = (int64_t)FRAME_PERIOD_MS * 1000;
        if (elapsed_us < target_us) {
            sleep_us((uint32_t)(target_us - elapsed_us));
        }
    }
}
