# Sensor-test verification plan

## Gate objective

The production 42-key PCB must not be released until this board proves the magnetic and analog assumptions.

## Measurements

### A. Static endpoints

For each key:
- record unpressed ADC distribution for at least 5 seconds,
- press fully and record bottom-out distribution,
- repeat at least 30 full strokes,
- report min/mean/max and standard deviation.

Pass criterion:
- no ADC clipping near 0 or full scale,
- median top-to-bottom span >= 500 raw 12-bit counts,
- endpoint repeatability small enough to place actuation thresholds with useful margin.

The 500-count value is a provisional engineering threshold, not a product requirement. It may be adjusted after first measurements.

### B. Travel curve

Slowly press and release each switch while sampling continuously.

Produce:
- raw ADC vs time,
- normalized 0..1 position estimate,
- press and release curves,
- visible hysteresis / nonlinearity assessment.

Purpose:
- determine whether simple endpoint normalization is sufficient,
- decide whether a lookup curve is needed.

### C. Mux settling

For address changes:
- sample immediately after changing address,
- then at 2, 5, 10, 20 and 50 us delays,
- compare the error against a long-settled reference.

Pass criterion:
- identify a stable delay that permits a full 42-key scan comfortably above 1 kHz.

### D. Noise

At fixed key positions:
- collect at least 10,000 readings,
- compare single samples vs 2/4/8-sample averaging,
- measure peak-to-peak and standard deviation.

### E. Power

Measure:
- 3V3 current with HALL_5V off,
- total USB current with HALL_5V on,
- Hall rail current,
- turn-on transient if equipment permits.

Extrapolate to 42 sensors.

### F. Cross-key magnetic coupling

Hold one key at fixed positions while pressing adjacent keys.

Pass criterion:
- adjacent key movement must not shift the stationary key reading enough to materially alter a calibrated actuation point.

### G. Temperature sanity check

Not a formal environmental qualification.

Repeat endpoint measurements after:
- room-temperature cold start,
- at least 30 minutes powered,
- moderate warm environment that can be safely produced without exceeding component ratings.

Purpose:
- detect obvious thermal drift before the main PCB.

## Output files

Measurement firmware shall generate machine-readable CSV.

Required columns:
- timestamp_us
- key
- mux_address
- adc_raw
- hall_power
- event / test marker

Analysis scripts will live under `firmware/tools/` or `hardware/sensor-test/analysis/`.
