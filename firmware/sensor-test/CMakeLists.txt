cmake_minimum_required(VERSION 3.13)

if(NOT DEFINED PICO_SDK_PATH)
    if(DEFINED ENV{PICO_SDK_PATH})
        set(PICO_SDK_PATH "$ENV{PICO_SDK_PATH}")
    else()
        message(FATAL_ERROR "Set PICO_SDK_PATH to a Raspberry Pi Pico SDK checkout.")
    endif()
endif()

include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(he_piantor_sensor_test C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(sensor_test
    main.c
)

target_link_libraries(sensor_test
    pico_stdlib
    hardware_adc
)

pico_enable_stdio_usb(sensor_test 1)
pico_enable_stdio_uart(sensor_test 0)

pico_add_extra_outputs(sensor_test)
