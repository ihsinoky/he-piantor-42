# RP2040 minimal reference

Source: https://github.com/tommy-gilligan/RP2040-minimal-design

License: BSD-3-Clause. See `LICENSE.txt`.

This directory is retained as an engineering reference / copy source for the RP2040 core, especially its JLCPCB-oriented implementation.

It is **not** the HE Piantor sensor-test board itself.

Before copying the core into the project schematic, this project will reconcile it against the current Raspberry Pi hardware-design guide. In particular:

- current recommended crystal is Abracon ABM8-272-T3,
- crystal load capacitors are 15 pF each with a 1 kOhm XOUT series resistor,
- USB D+/D- require 27 Ohm series termination near RP2040,
- the HE Piantor board uses USB-C with two 5.1 kOhm CC pull-downs rather than the reference connector,
- the application power tree is different because Hall sensors use a switched 5 V rail.

Project-specific edits must be made under `hardware/sensor-test/` or `hardware/main/`, not by modifying the vendored reference.
