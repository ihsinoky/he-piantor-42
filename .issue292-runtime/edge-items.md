# Issue #292 edge-fix S1: copper-vs-outline enumeration (adopted board 509e52a7)

Method: KiCad `GetBoardPolygonOutlines` outline (14 vertices) vs exact
effective-shape geometry (tracks/vias/pads per layer, zone fills) via shapely.
Cross-check vs completion round DRC (`completion-final2-drc.json`): all 114 DRC
copper_edge_clearance items are contained in this list (0 missed); this list adds
17 items DRC did not flag separately (all CROSSING, west fanout). Values agree
to <=0.0001mm on shared items.

Totals: 131 unique items flagged (Counter({'CROSSING': 72, 'CLOSE': 59})); 167 item-layer instances; 4030 copper instances scanned.

Inherited vs introduced: Rev.10 board (same outline) has exactly 2 flagged items
(MUX_OUT_C track, 2 segments, CLOSE 0.4414) and neither is flagged in the wireless
board. No flagged wireless item matches a flagged Rev.10 item => **all items below
are wireless-introduced** (new parts/routing or moved Rev.10 geometry).

## Cluster E - east slant - 7 items (Counter({'CLOSE': 6, 'CROSSING': 1}))

| cls | dist mm | outside mm2 | kind | net | layers | DRC actual | item |
|---|---|---|---|---|---|---|---|
| CROSSING | 0.0 | 0.09 | pad | GND | F.Cu | 0.0 | pad RPD1.2 [GND] @(131.825,128.000) 0.80x0.95 |
| CLOSE | 0.1548 | 0.0 | track | GND | F.Cu | 0.1548 | track [GND] (131.825,128.000)->(132.071,128.918) w=0.300 |
| CLOSE | 0.2318 | 0.0 | via | GND | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.3646 | via [GND] @(128.675,122.998) d=0.600 |
| CLOSE | 0.2508 | 0.0 | via | GND | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.2507 | via [GND] @(132.071,128.918) d=0.600 |
| CLOSE | 0.2538 | 0.0 | track | VBAT_GATE | F.Cu | 0.2538 | track [VBAT_GATE] (127.400,111.600)->(119.300,103.500) w=0.100 |
| CLOSE | 0.2612 | 0.0 | pad | GND | F.Cu | 0.2612 | pad CFC.2 [GND] @(128.200,122.175) 0.80x0.95 |
| CLOSE | 0.3817 | 0.0 | track | GND | F.Cu | 0.3817 | track [GND] (128.200,122.175)->(128.675,122.998) w=0.300 |

## Cluster N - north-west shoulder / north edge - 13 items (Counter({'CLOSE': 11, 'CROSSING': 2}))

| cls | dist mm | outside mm2 | kind | net | layers | DRC actual | item |
|---|---|---|---|---|---|---|---|
| CROSSING | 0.0 | 0.0116 | pad | GND | F.Cu | 0.0 | pad CIN2.2 [GND] @(85.800,98.388) 1.02x1.40 |
| CROSSING | 0.0 | 0.173 | pad | GND | F.Cu | 0.0 | pad CVS.2 [GND] @(93.500,83.975) 0.80x0.95 |
| CLOSE | 0.0744 | 0.0 | track | GND | F.Cu | 0.0743 | track [GND] (93.500,83.975)->(93.280,84.796) w=0.300 |
| CLOSE | 0.0987 | 0.0 | pad | VIN_IN | F.Cu | 0.0986 | pad TP1.1 [VIN_IN] @(90.800,89.600) 1.20x1.20 |
| CLOSE | 0.137 | 0.0 | pad | GND | F.Cu | 0.137 | pad CIN1.2 [GND] @(90.000,91.588) 1.02x1.40 |
| CLOSE | 0.1944 | 0.0 | via | GND | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.1943 | via [GND] @(93.280,84.796) d=0.500 |
| CLOSE | 0.216 | 0.0 | via | GND | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.216 | via [GND] @(85.128,99.059) d=0.600 |
| CLOSE | 0.2555 | 0.0 | pad | SYS_3V3 | F.Cu | 0.2555 | pad RRST.1 [SYS_3V3] @(92.175,87.500) 0.80x0.95 |
| CLOSE | 0.3029 | 0.0 | track | VBAT_SENSE | F.Cu | 0.3029 | track [VBAT_SENSE] (94.500,82.500)->(94.900,82.100) w=0.100 |
| CLOSE | 0.3029 | 0.0 | track | VBAT_SENSE | F.Cu | 0.3029 | track [VBAT_SENSE] (94.500,84.200)->(94.500,82.500) w=0.100 |
| CLOSE | 0.366 | 0.0 | track | GND | F.Cu | 0.366 | track [GND] (85.800,98.388)->(85.128,99.059) w=0.300 |
| CLOSE | 0.438 | 0.0 | pad | VBAT_SENSE | F.Cu | 0.438 | pad CVS.1 [VBAT_SENSE] @(93.500,85.625) 0.80x0.95 |
| CLOSE | 0.4493 | 0.0 | track | VBAT_SENSE | F.Cu | 0.4493 | track [VBAT_SENSE] (94.900,82.100)->(99.300,82.100) w=0.100 |

## Cluster S - south edge - 1 items (Counter({'CLOSE': 1}))

| cls | dist mm | outside mm2 | kind | net | layers | DRC actual | item |
|---|---|---|---|---|---|---|---|
| CLOSE | 0.475 | 0.0 | pad | MUX_EN1 | F.Cu | 0.475 | pad RPD3.1 [MUX_EN1] @(118.500,137.025) 0.80x0.95 |

## Cluster T - north tab east shoulder / JPAD - 8 items (Counter({'CLOSE': 6, 'CROSSING': 2}))

| cls | dist mm | outside mm2 | kind | net | layers | DRC actual | item |
|---|---|---|---|---|---|---|---|
| CROSSING | 0.0 | 0.0568 | pad | GND | F.Cu | 0.0 | pad JPAD.6 [GND] @(113.750,96.800) 0.30x1.80 |
| CROSSING | 0.0 | 0.1825 | pad |  | F.Cu | 0.0 | pad JPAD.MP [] @(114.700,98.400) 1.00x1.20 |
| CLOSE | 0.1637 | 0.0 | via | GND | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.1636 | via [GND] @(115.750,100.475) d=0.600 |
| CLOSE | 0.2082 | 0.0 | track | GND | F.Cu | 0.2082 | track [GND] (113.750,96.800)->(113.750,97.950) w=0.300 |
| CLOSE | 0.2113 | 0.0 | pad | PAD_DR | F.Cu | 0.2113 | pad JPAD.5 [PAD_DR] @(113.250,96.800) 0.30x1.80 |
| CLOSE | 0.2538 | 0.0 | track | VBAT_GATE | F.Cu | 0.2542 | track [VBAT_GATE] (117.400,103.500)->(119.300,103.500) w=0.100 |
| CLOSE | 0.3136 | 0.0 | track | GND | F.Cu | 0.3136 | track [GND] (114.800,100.475)->(115.750,100.475) w=0.300 |
| CLOSE | 0.4983 | 0.0 | track | VBAT_GATE | F.Cu | 0.4983 | track [VBAT_GATE] (115.000,101.100)->(117.400,103.500) w=0.100 |

## Cluster W - west dent / module fanout - 102 items (Counter({'CROSSING': 67, 'CLOSE': 35}))

| cls | dist mm | outside mm2 | kind | net | layers | DRC actual | item |
|---|---|---|---|---|---|---|---|
| CROSSING | 0.0 | 0.015 | track | ADC_B | B.Cu | 0.0 | track [ADC_B] (70.850,123.500)->(70.500,123.150) w=0.100 |
| CROSSING | 0.0 | 0.0002 | track | HALL_PWR_EN | In2.Cu | 0.0 | track [HALL_PWR_EN] (70.400,121.150)->(70.850,120.700) w=0.100 |
| CROSSING | 0.0 | 0.2299 | track | HALL_PWR_EN | In2.Cu | 0.0 | track [HALL_PWR_EN] (70.400,126.550)->(70.400,121.150) w=0.100 |
| CROSSING | 0.0 | 0.0404 | track | LED_DRV | In2.Cu | 0.0 | track [LED_DRV] (70.000,121.250)->(70.450,120.800) w=0.100 |
| CROSSING | 0.0 | 0.0591 | track | LED_DRV | F.Cu | 0.0 | track [LED_DRV] (71.650,121.950)->(69.650,121.950) w=0.050 |
| CROSSING | 0.0 | 0.1399 | track | MUX_A0 | B.Cu | 0.0 | track [MUX_A0] (70.450,120.400)->(69.150,121.700) w=0.100 |
| CROSSING | 0.0 | 0.0193 | track | MUX_A0 | F.Cu | 0.0 | track [MUX_A0] (70.550,124.200)->(69.650,124.200) w=0.050 |
| CROSSING | 0.0 | 0.1399 | track | MUX_A1 | F.Cu | 0.0 | track [MUX_A1] (70.450,120.400)->(69.150,121.700) w=0.100 |
| CROSSING | 0.0 | 0.0102 | track | MUX_A1 | F.Cu | 0.0 | track [MUX_A1] (70.500,123.250)->(70.550,123.250) w=0.100 |
| CROSSING | 0.0 | 0.0053 | track | MUX_A1 | F.Cu | 0.0 | track [MUX_A1] (70.550,123.250)->(70.600,123.300) w=0.100 |
| CROSSING | 0.0 | 0.0832 | track | MUX_A1 | F.Cu | 0.0 | track [MUX_A1] (71.400,123.550)->(69.600,123.550) w=0.100 |
| CROSSING | 0.0 | 0.1399 | track | MUX_A2 | In2.Cu | 0.0 | track [MUX_A2] (70.200,120.650)->(69.150,121.700) w=0.100 |
| CROSSING | 0.0 | 0.0003 | track | MUX_A2 | F.Cu | 0.0 | track [MUX_A2] (72.050,124.950)->(69.600,124.950) w=0.050 |
| CROSSING | 0.0 | 0.0991 | track | PAD_SCL | In2.Cu | 0.0 | track [PAD_SCL] (69.150,126.000)->(69.150,124.750) w=0.100 |
| CROSSING | 0.0 | 0.0181 | track | PAD_SCL | In2.Cu | 0.0 | track [PAD_SCL] (69.950,120.600)->(69.950,119.150) w=0.100 |
| CROSSING | 0.0 | 0.0832 | track | PAD_SCL | In2.Cu | 0.0 | track [PAD_SCL] (70.050,123.350)->(70.050,126.000) w=0.100 |
| CROSSING | 0.0 | 0.068 | track | PAD_SCL | F.Cu | 0.1881 | track [PAD_SCL] (72.000,122.600)->(69.600,122.600) w=0.050 |
| CROSSING | 0.0 | 0.0372 | track | USB_DM | B.Cu | 0.0 | track [USB_DM] (68.650,118.850)->(70.900,116.600) w=0.100 |
| CROSSING | 0.0 | 0.0366 | track | USB_DM | B.Cu | 0.0 | track [USB_DM] (69.480,126.630)->(68.700,125.850) w=0.100 |
| CROSSING | 0.0 | 0.05 | track | USB_DP | B.Cu | 0.0 | track [USB_DP] (68.450,118.750)->(70.700,116.500) w=0.100 |
| CROSSING | 0.0 | 0.0493 | track | USB_DP | B.Cu | 0.0 | track [USB_DP] (69.150,126.600)->(68.500,125.950) w=0.100 |
| CROSSING | 0.0 | 0.133 | via | MUX_A2 | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.0 | via [MUX_A2] @(69.600,124.950) d=0.600 |
| CROSSING | 0.0067 | 0.0149 | track | MUX_A1 | F.Cu | 0.0067 | track [MUX_A1] (70.450,123.200)->(70.500,123.250) w=0.100 |
| CROSSING | 0.021 | 0.1493 | track | PAD_SCL | In2.Cu | 0.021 | track [PAD_SCL] (68.950,121.600)->(69.950,120.600) w=0.100 |
| CROSSING | 0.0362 | 0.2826 | via | MUX_A0 | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.0361 | via [MUX_A0] @(69.600,124.250) d=0.600 |
| CROSSING | 0.0567 | 0.0729 | track | ADC_B | B.Cu | 0.0567 | track [ADC_B] (70.500,123.150)->(69.850,123.150) w=0.100 |
| CROSSING | 0.075 | 0.0129 | track | MUX_A1 | F.Cu | 0.075 | track [MUX_A1] (70.400,123.200)->(70.450,123.200) w=0.100 |
| CROSSING | 0.1183 | 0.0149 | track | MUX_A1 | F.Cu | 0.1183 | track [MUX_A1] (70.350,123.150)->(70.400,123.200) w=0.100 |
| CROSSING | 0.1251 | 0.0545 | track | MUX_A2 | In2.Cu | 0.1251 | track [MUX_A2] (69.150,124.450)->(69.480,124.780) w=0.100 |
| CROSSING | 0.1866 | 0.0129 | track | MUX_A1 | F.Cu | 0.1866 | track [MUX_A1] (70.300,123.150)->(70.350,123.150) w=0.100 |
| CROSSING | 0.2299 | 0.0149 | track | MUX_A1 | F.Cu | 0.2299 | track [MUX_A1] (70.250,123.100)->(70.300,123.150) w=0.100 |
| CROSSING | 0.2656 | 0.2179 | track | USB_DM | B.Cu | 0.2656 | track [USB_DM] (68.700,125.850)->(68.700,123.750) w=0.100 |
| CROSSING | 0.2716 | 0.4929 | track | USB_DM | B.Cu | 0.2716 | track [USB_DM] (68.650,123.700)->(68.650,118.850) w=0.100 |
| CROSSING | 0.2928 | 0.0055 | track | MUX_A0 | F.Cu | 0.2928 | track [MUX_A0] (69.650,124.200)->(69.600,124.250) w=0.050 |
| CROSSING | 0.2982 | 0.0179 | track | MUX_A1 | F.Cu | 0.2982 | track [MUX_A1] (70.150,123.100)->(70.250,123.100) w=0.100 |
| CROSSING | 0.3027 | 0.0179 | track | LED_DRV | In2.Cu | 0.3027 | track [LED_DRV] (70.000,121.350)->(70.000,121.250) w=0.100 |
| CROSSING | 0.3464 | 0.022 | track | PAD_SCL | In2.Cu | 0.3464 | track [PAD_SCL] (69.950,123.250)->(70.050,123.350) w=0.100 |
| CROSSING | 0.3527 | 0.0545 | track | LED_DRV | In2.Cu | 0.3527 | track [LED_DRV] (69.670,121.680)->(70.000,121.350) w=0.100 |
| CROSSING | 0.3848 | 0.0149 | track | MUX_A1 | F.Cu | 0.3848 | track [MUX_A1] (70.100,123.050)->(70.150,123.100) w=0.100 |
| CROSSING | 0.3862 | 0.2826 | via | MUX_A1 | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.3861 | via [MUX_A1] @(69.600,123.550) d=0.600 |
| CROSSING | 0.3888 | 0.0129 | track | USB_DP | B.Cu | 0.3888 | track [USB_DP] (68.500,125.950)->(68.500,125.900) w=0.100 |
| CROSSING | 0.3948 | 0.0129 | track | USB_DP | B.Cu | 0.3948 | track [USB_DP] (68.450,118.800)->(68.450,118.750) w=0.100 |
| CROSSING | 0.4138 | 0.0149 | track | USB_DP | B.Cu | 0.4138 | track [USB_DP] (68.500,125.900)->(68.450,125.850) w=0.100 |
| CROSSING | 0.4198 | 0.0149 | track | USB_DP | B.Cu | 0.4198 | track [USB_DP] (68.400,118.850)->(68.450,118.800) w=0.100 |
| CROSSING | 0.4259 | 0.0361 | track | PAD_SCL | In2.Cu | 0.4258 | track [PAD_SCL] (69.150,124.750)->(68.950,124.550) w=0.100 |
| CROSSING | 0.4531 | 0.0779 | track | MUX_A1 | F.Cu | 0.4531 | track [MUX_A1] (69.400,123.050)->(70.100,123.050) w=0.100 |
| CROSSING | 0.4751 | 0.0545 | track | MUX_A0 | B.Cu | 0.4751 | track [MUX_A0] (69.150,123.750)->(69.480,124.080) w=0.100 |
| CROSSING | 0.4821 | 0.2179 | track | USB_DP | B.Cu | 0.4821 | track [USB_DP] (68.450,125.850)->(68.450,123.750) w=0.100 |
| CROSSING | 0.483 | 0.0229 | track | PAD_SCL | In2.Cu | 0.483 | track [PAD_SCL] (69.950,123.100)->(69.950,123.250) w=0.100 |
| CROSSING | 0.4881 | 0.4929 | track | USB_DP | B.Cu | 0.4881 | track [USB_DP] (68.400,123.700)->(68.400,118.850) w=0.100 |
| CROSSING | 0.558 | 0.0474 | track | PAD_SCL | In2.Cu | - | track [PAD_SCL] (69.670,122.820)->(69.950,123.100) w=0.100 |
| CROSSING | 0.5759 | 0.2829 | track | MUX_A2 | In2.Cu | - | track [MUX_A2] (69.150,121.700)->(69.150,124.450) w=0.100 |
| CROSSING | 0.6196 | 0.0149 | track | ADC_B | B.Cu | - | track [ADC_B] (69.850,123.150)->(69.800,123.100) w=0.100 |
| CROSSING | 0.6879 | 0.0279 | track | ADC_B | B.Cu | - | track [ADC_B] (69.800,123.100)->(69.600,123.100) w=0.100 |
| CROSSING | 0.6991 | 0.0129 | track | PAD_SCL | In2.Cu | - | track [PAD_SCL] (68.950,124.550)->(68.950,124.500) w=0.100 |
| CROSSING | 0.7241 | 0.0149 | track | PAD_SCL | In2.Cu | - | track [PAD_SCL] (68.950,124.500)->(68.900,124.450) w=0.100 |
| CROSSING | 0.7242 | 0.2826 | via | LED_DRV | B.Cu,F.Cu,In1.Cu,In2.Cu | - | via [LED_DRV] @(69.600,121.900) d=0.600 |
| CROSSING | 0.7924 | 0.2829 | track | PAD_SCL | In2.Cu | - | track [PAD_SCL] (68.900,124.450)->(68.900,121.700) w=0.100 |
| CROSSING | 0.8612 | 0.2826 | via | PAD_SCL | B.Cu,F.Cu,In1.Cu,In2.Cu | - | via [PAD_SCL] @(69.600,122.600) d=0.600 |
| CROSSING | 0.9259 | 0.2129 | track | MUX_A0 | B.Cu | - | track [MUX_A0] (69.150,121.700)->(69.150,123.750) w=0.100 |
| CROSSING | 0.9809 | 0.0055 | track | LED_DRV | F.Cu | - | track [LED_DRV] (69.650,121.950)->(69.600,121.900) w=0.050 |
| CROSSING | 1.0593 | 0.0432 | track | MUX_A1 | F.Cu | - | track [MUX_A1] (69.150,122.800)->(69.400,123.050) w=0.100 |
| CROSSING | 1.2638 | 0.1179 | track | MUX_A1 | F.Cu | - | track [MUX_A1] (69.150,121.700)->(69.150,122.800) w=0.100 |
| CROSSING | 1.3156 | 0.0149 | track | USB_DM | B.Cu | - | track [USB_DM] (68.700,123.750)->(68.650,123.700) w=0.100 |
| CROSSING | 1.387 | 0.0129 | track | PAD_SCL | In2.Cu | - | track [PAD_SCL] (68.950,121.650)->(68.950,121.600) w=0.100 |
| CROSSING | 1.412 | 0.0149 | track | PAD_SCL | In2.Cu | - | track [PAD_SCL] (68.900,121.700)->(68.950,121.650) w=0.100 |
| CROSSING | 1.5321 | 0.0149 | track | USB_DP | B.Cu | - | track [USB_DP] (68.450,123.750)->(68.400,123.700) w=0.100 |
| CLOSE | 0.0049 | 0.0 | track | MUX_A1 | F.Cu | 0.0049 | track [MUX_A1] (70.600,123.300)->(70.650,123.300) w=0.100 |
| CLOSE | 0.021 | 0.0 | track | SYS_3V3 | B.Cu | 0.021 | track [SYS_3V3] (70.420,120.930)->(72.100,119.250) w=0.300 |
| CLOSE | 0.0334 | 0.0 | via | GND | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.0334 | via [GND] @(70.850,121.350) d=0.600 |
| CLOSE | 0.0482 | 0.0 | track | MUX_A1 | F.Cu | 0.0482 | track [MUX_A1] (70.650,123.300)->(70.700,123.350) w=0.100 |
| CLOSE | 0.0705 | 0.0 | track | MUX_A2 | In2.Cu | 0.0705 | track [MUX_A2] (70.200,119.150)->(70.200,120.650) w=0.100 |
| CLOSE | 0.0992 | 0.0 | track | PAD_SCL | In2.Cu | 0.0992 | track [PAD_SCL] (69.400,126.250)->(69.150,126.000) w=0.100 |
| CLOSE | 0.1165 | 0.0 | track | MUX_A1 | F.Cu | 0.1165 | track [MUX_A1] (70.700,123.350)->(70.800,123.350) w=0.100 |
| CLOSE | 0.1362 | 0.0 | pad |  | F.Cu | 0.1362 | pad U1.2 [] @(71.400,122.250) 0.40x0.40 |
| CLOSE | 0.1389 | 0.0 | via | USB_DP | B.Cu,F.Cu,In1.Cu,In2.Cu | 0.1389 | via [USB_DP] @(69.600,125.800) d=0.600 |
| CLOSE | 0.1789 | 0.0 | pad | GND | F.Cu | 0.1789 | pad COUT2.2 [GND] @(81.800,103.888) 1.02x1.40 |
| CLOSE | 0.2031 | 0.0 | track | MUX_A1 | F.Cu | 0.2031 | track [MUX_A1] (70.800,123.350)->(70.850,123.400) w=0.100 |
| CLOSE | 0.212 | 0.0 | track | LED_DRV | In2.Cu | 0.212 | track [LED_DRV] (70.450,120.800)->(70.450,119.150) w=0.100 |
| CLOSE | 0.2334 | 0.0 | track | GND | F.Cu | 0.2334 | track [GND] (71.600,121.350)->(70.850,121.350) w=0.200 |
| CLOSE | 0.2552 | 0.0 | track | SYS_3V3 | B.Cu | 0.2552 | track [SYS_3V3] (70.650,120.650)->(70.650,120.860) w=0.300 |
| CLOSE | 0.2714 | 0.0 | track | MUX_A1 | F.Cu | 0.2714 | track [MUX_A1] (70.850,123.400)->(70.900,123.400) w=0.100 |
| CLOSE | 0.2745 | 0.0 | pad |  | F.Cu | 0.3414 | pad U1.4 [] @(71.400,122.900) 0.40x0.40 |
| CLOSE | 0.3039 | 0.0 | track | PAD_SCL | In2.Cu | 0.3039 | track [PAD_SCL] (75.900,108.850)->(81.200,103.550) w=0.100 |
| CLOSE | 0.3039 | 0.0 | track | PAD_SCL | In2.Cu | 0.3039 | track [PAD_SCL] (81.200,103.550)->(84.250,103.550) w=0.100 |
| CLOSE | 0.3147 | 0.0 | track | MUX_A1 | F.Cu | 0.3147 | track [MUX_A1] (70.900,123.400)->(70.950,123.450) w=0.100 |
| CLOSE | 0.3214 | 0.0 | track | ADC_B | B.Cu | 0.3214 | track [ADC_B] (71.400,123.500)->(70.850,123.500) w=0.100 |
| CLOSE | 0.3364 | 0.0 | track | VIN_IN | F.Cu | 0.3364 | track [VIN_IN] (83.800,101.300)->(83.800,102.300) w=0.300 |
| CLOSE | 0.3364 | 0.0 | track | VIN_IN | F.Cu | 0.3364 | track [VIN_IN] (84.200,100.900)->(83.800,101.300) w=0.300 |
| CLOSE | 0.3602 | 0.0 | track | SYS_3V3 | B.Cu | 0.3602 | track [SYS_3V3] (70.750,120.550)->(70.650,120.650) w=0.300 |
| CLOSE | 0.383 | 0.0 | track | MUX_A1 | F.Cu | 0.383 | track [MUX_A1] (70.950,123.450)->(71.000,123.450) w=0.100 |
| CLOSE | 0.3889 | 0.0 | track | USB_DP | F.Cu | 0.3889 | track [USB_DP] (71.600,125.800)->(69.600,125.800) w=0.100 |
| CLOSE | 0.3992 | 0.0 | track | USB_DP | B.Cu | 0.3992 | track [USB_DP] (69.150,127.700)->(69.150,126.600) w=0.100 |
| CLOSE | 0.412 | 0.0 | track | MUX_A0 | B.Cu | 0.412 | track [MUX_A0] (70.450,119.150)->(70.450,120.400) w=0.100 |
| CLOSE | 0.412 | 0.0 | track | MUX_A1 | F.Cu | 0.412 | track [MUX_A1] (70.450,119.150)->(70.450,120.400) w=0.100 |
| CLOSE | 0.4263 | 0.0 | track | MUX_A1 | F.Cu | 0.4263 | track [MUX_A1] (71.000,123.450)->(71.050,123.500) w=0.100 |
| CLOSE | 0.4364 | 0.0 | pad | GND | F.Cu | 0.4364 | pad U1.1 [GND] @(71.600,121.350) 0.80x0.80 |
| CLOSE | 0.4366 | 0.0 | track | MUX_A0 | F.Cu | 0.4366 | track [MUX_A0] (70.850,123.900)->(70.550,124.200) w=0.050 |
| CLOSE | 0.4407 | 0.0 | track | PAD_SCL | In2.Cu | 0.4407 | track [PAD_SCL] (69.800,126.250)->(69.400,126.250) w=0.100 |
| CLOSE | 0.4828 | 0.0 | track | VIN_IN | F.Cu | 0.4828 | track [VIN_IN] (84.400,100.900)->(84.200,100.900) w=0.300 |
| CLOSE | 0.4946 | 0.0 | track | MUX_A1 | F.Cu | 0.4946 | track [MUX_A1] (71.050,123.500)->(71.100,123.500) w=0.100 |
| CLOSE | 0.4968 | 0.0 | track | SYS_3V3 | B.Cu | 0.4968 | track [SYS_3V3] (70.750,120.450)->(70.750,120.550) w=0.300 |
