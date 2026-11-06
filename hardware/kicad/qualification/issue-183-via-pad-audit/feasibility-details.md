# 配置固定・単独via移設の探索詳細

各候補は独立。全候補の同時成立・DRC・接続・zone再fillは未確認。
直線stubが見つからないことは、配置変更や広域再配線が必須だという証明ではない。
障害列は最寄りの固定銅箔回避候補への直線接続で当たる対象。全探索点の障害集合ではない。

## main-rev2

35件の0.10mm未達。直線接続候補 33、迂回等の追加検討 2、固定銅箔回避候補なし 0。

| via UUID | 元座標 mm | 対象パッド（重なりがなければ最近傍） | net | 最寄り移設候補 mm | 直線上の障害（層・Reference／ネット） |
| --- | --- | --- | --- | --- | --- |
| 6bf1ec76-373b-473d-8a4f-1220e3ffc25f | [94.5, 102.0] | C5.2 | GND | [94.622018, 103.394673] | F.Cu:PCB_TRACK:XOUT |
| 83b6e9ed-f13d-4984-8aac-1d3fee6bd3fb | [93.5, 99.2] | C4.1 | V3V3 | [92.254757, 99.091055] | In2.Cu:PCB_TRACK:MUX_OUT_C |

## wing-rev1-16mm

32件の0.10mm未達。直線接続候補 22、迂回等の追加検討 10、固定銅箔回避候補なし 0。

| via UUID | 元座標 mm | 対象パッド（重なりがなければ最近傍） | net | 最寄り移設候補 mm | 直線上の障害（層・Reference／ネット） |
| --- | --- | --- | --- | --- | --- |
| 006b0949-7439-4a19-967d-8a0c0858c226 | [97.5, 138.4] | U_MUX_A.2 | WING_EN | [98.465926, 138.658819] | F.Cu:PCB_TRACK:H_A2_RAW |
| 74c94ac3-20f1-4533-8f87-1f0bd3c69b0b | [111.5, 138.4] | U_MUX_B.2 | WING_EN | [112.7, 138.4] | F.Cu:PCB_TRACK:H_B3_RAW; F.Cu:PCB_TRACK:H_C2_RAW |
| 94bebf4f-e047-4e60-bb62-eba654ffe4a5 | [102.932075, 138.375] | U_MUX_A.15 | MUX_A2 | [101.537402, 138.497018] | F.Cu:PCB_TRACK:H_A5_RAW |
| a38f885d-4bc4-4552-b2e8-1e6be4c76e05 | [97.0, 137.7] | U_MUX_A.1 | MUX_A0 | [95.97606, 136.983029] | F.Cu:PCB_TRACK:H_A1_RAW |
| bed16231-bb25-4e9d-bbf7-c9edb2912dde | [97.067925, 139.675] | U_MUX_A.4 | H_A0_RAW | [98.462598, 139.797018] | F.Cu:PCB_TRACK:H_A2_RAW |
| d1927d33-d580-44ec-8926-d9c1d81694a5 | [100.0, 144.5] | TP_W_MUXA.1 | MUX_OUT_A | [99.328249, 143.828249] | F.Cu:PCB_TRACK:MUX_OUT_C |
| 101ba23a-07ec-48f5-82ee-664d42f538dc | [102.932075, 139.675] | U_MUX_A.13 | HALL_5V | [101.475551, 139.144869] | B.Cu:PCB_TRACK:MUX_A2; F.Cu:PCB_TRACK:H_A5_RAW; F.Cu:U_MUX_A.14 |
| d2d25fe9-5482-4f04-93df-0b862a36685e | [133.1, 139.3] | C_MUX_C.2 | GND | [132.604071, 140.662554] | B.Cu:PCB_TRACK:HALL_5V |
| f7206234-7a3c-4aae-bf1f-782d9d757de7 | [116.932075, 139.025] | U_MUX_B.14 | GND | [117.097671, 137.13223] | B.Cu:PCB_TRACK:MUX_A0; B.Cu:PCB_TRACK:MUX_A1; B.Cu:PCB_TRACK:WING_EN; B.Cu:PCB_VIA:MUX_A1; F.Cu:U_MUX_B.15; F.Cu:U_MUX_B.16 |
| fba2bf0e-9e4f-4acd-8ae7-9e10974d6098 | [131.3, 139.7] | U_MUX_C.13 | HALL_5V | [132.410764, 140.632042] | F.Cu:PCB_TRACK:H_C5_RAW; F.Cu:U_MUX_C.12 |

## wing-rev1-17mm

52件の0.10mm未達。直線接続候補 35、迂回等の追加検討 17、固定銅箔回避候補なし 0。

| via UUID | 元座標 mm | 対象パッド（重なりがなければ最近傍） | net | 最寄り移設候補 mm | 直線上の障害（層・Reference／ネット） |
| --- | --- | --- | --- | --- | --- |
| 02f23f73-ee75-40b5-96de-4a981d27b88e | [130.932075, 142.05] | U_MUX_C.13 | HALL_5V | [132.283676, 142.996401] | F.Cu:PCB_TRACK:H_C5_RAW; F.Cu:U_MUX_C.12 |
| 0716b039-b66d-4aed-ae01-5b3498e6d51e | [116.3, 140.0] | U_MUX_B.16 | MUX_A1 | [117.396016, 138.903984] | B.Cu:PCB_TRACK:MUX_A2; B.Cu:PCB_VIA:MUX_A2; F.Cu:PCB_TRACK:MUX_A2; F.Cu:PCB_VIA:MUX_A2 |
| 0bdc4630-4222-4246-a2d6-897d202de379 | [116.6, 141.4] | U_MUX_B.14 | GND | [115.049507, 141.964333] | B.Cu:PCB_TRACK:H_B4_RAW; F.Cu:PCB_TRACK:H_C2_RAW; F.Cu:U_MUX_B.13 |
| 186eb2e8-4742-4af7-8160-281f12ed0ef5 | [62.1, 141.8] | J_WING.6 | MUX_A2 | [61.383029, 140.77606] | F.Cu:PCB_TRACK:WING_EN |
| 1c9f7163-7d7c-4d06-a693-bef95201eea4 | [65.8, 141.8] | J_WING.3 | MUX_A0 | [64.975894, 140.0327] | F.Cu:PCB_TRACK:MUX_A2; F.Cu:PCB_TRACK:WING_EN |
| 2ba0b765-486b-4b0b-9df0-1090989ee687 | [102.9, 141.4] | U_MUX_A.14 | GND | [101.521269, 141.156893] | F.Cu:PCB_TRACK:H_A5_RAW |
| 41052c6a-a785-4722-88ae-b768e552f475 | [63.0, 141.8] | J_WING.5 | MUX_A1 | [62.350162, 140.014584] | F.Cu:PCB_TRACK:MUX_A2; F.Cu:PCB_TRACK:WING_EN; F.Cu:PCB_VIA:MUX_A2 |
| 4474ebc8-b7a1-46f0-92ea-8c8ee8f49e98 | [97.5, 140.8] | U_MUX_A.2 | WING_EN | [98.712436, 141.5] | F.Cu:PCB_TRACK:H_A2_RAW; F.Cu:PCB_TRACK:H_A3_RAW; F.Cu:U_MUX_A.3 |
| 6e3f2a18-5c00-4da8-b185-cfbf9e10c714 | [130.6, 141.4] | U_MUX_C.14 | GND | [129.489236, 142.332042] | B.Cu:PCB_TRACK:H_C4_RAW; F.Cu:PCB_TRACK:H_C6_RAW; F.Cu:PCB_VIA:HALL_5V; F.Cu:U_MUX_C.13 |
| 7e655ac2-9f0b-474b-a62d-a85002997152 | [124.6, 140.8] | U_MUX_C.2 | WING_EN | [123.645406, 141.754594] | B.Cu:PCB_TRACK:H_C0_RAW; F.Cu:PCB_TRACK:H_C1_RAW; F.Cu:U_MUX_C.3 |
| 8abeeb1d-e4c3-4665-b4b2-de965cb779ff | [96.6, 142.0] | U_MUX_A.4 | H_A0_RAW | [95.418231, 142.208378] | F.Cu:PCB_TRACK:H_A1_RAW; F.Cu:PCB_TRACK:H_A4_RAW |
| 8e615c00-06c3-4cc7-916e-a7da07a72810 | [116.5, 142.7] | U_MUX_B.12 | H_B4_RAW | [115.005708, 142.830734] | F.Cu:PCB_TRACK:H_C2_RAW |
| b91f4e4b-4f93-47b9-9188-76af48693563 | [116.932075, 142.05] | U_MUX_B.13 | HALL_5V | [118.283676, 142.996401] | F.Cu:PCB_TRACK:H_B5_RAW; F.Cu:U_MUX_B.12 |
| c7d73aeb-de94-4c38-89bc-b6b8fa11a033 | [130.5, 140.1] | U_MUX_C.16 | MUX_A1 | [131.725671, 139.07154] | B.Cu:PCB_TRACK:MUX_A2; B.Cu:PCB_VIA:MUX_A2; F.Cu:PCB_TRACK:MUX_A2; F.Cu:PCB_VIA:MUX_A2 |
| ec302052-fdcf-4cc4-b3bc-2dab02850420 | [124.6, 142.0] | U_MUX_C.4 | H_C0_RAW | [123.634074, 142.258819] | F.Cu:PCB_TRACK:H_C1_RAW |
| ec8dd72a-7d28-477e-9323-7b5cfac3275a | [119.0, 140.531067] | C_MUX_B.1 | HALL_5V | [120.064898, 141.276716] | F.Cu:PCB_TRACK:H_B5_RAW |
| ef4e2487-2875-4167-b82c-f45da987ef55 | [130.5, 142.7] | U_MUX_C.12 | H_C4_RAW | [129.005708, 142.830734] | F.Cu:PCB_TRACK:GND; F.Cu:PCB_TRACK:H_C6_RAW |
