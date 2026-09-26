# HE Piantor 42 sensor-test firmware

Purpose: first-board measurement firmware for the four-key Hall evaluation PCB.

## Baseline

- MCU: RP2040
- SDK target: Raspberry Pi Pico SDK 2.3.1 baseline
- USB CDC stdio enabled
- UART stdio disabled
- Hall power stays off during early boot
- Hall rail is enabled through GPIO7 after USB initialization has been given time to enumerate
- TMUX1208 bank 0 is enabled through GPIO5
- MUX address uses GPIO2..4
- ADC0 / GPIO26 samples the divided Hall signal

## Initial acquisition parameters

- four mux addresses: 0..3
- 20 us settle delay after each address change
- first ADC conversion discarded
- eight conversions averaged per key
- nominal frame period: 10 ms

These are measurement defaults, not product constants. The verification plan intentionally sweeps mux-settle delay and later reduces averaging if the measured signal permits it.

## CSV stream

The USB serial output is:

```text
timestamp_us,key,mux_address,adc_raw,hall_power,test_marker
1234567,0,0,2048,1,stream
...
```

Comment lines beginning with `#` identify the firmware and active measurement constants.

## Build

With Pico SDK 2.3.1 checked out locally:

```sh
export PICO_SDK_PATH=/path/to/pico-sdk
cmake -S firmware/sensor-test -B build/sensor-test -DPICO_BOARD=pico
cmake --build build/sensor-test
```

The `pico` board definition is used only to supply the RP2040 platform/toolchain defaults. The evaluation PCB is a custom RP2040 board and does not rely on Pico board pin wiring.

Expected useful output:
- `sensor_test.uf2`
- `sensor_test.elf`

## Next firmware increments

1. settle-delay sweep mode,
2. static endpoint capture mode,
3. 10k-sample noise mode,
4. per-key endpoint calibration,
5. current/temperature test markers,
6. production 42-key scanner after sensor evaluation passes.
