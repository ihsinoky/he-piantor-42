# ISP1807-LR pad diff — official CAD vs derived footprint (by pad number)

Official positions are given in the derived frame orientation for comparability:
official local frame centred on the package, then rotated so the antenna edge
(official local +Y, the NC-ring side per DS1807 §3 TOP VIEW / §4.3) points along
the derived frame +X, which the derivation used as its antenna edge.

Summary: same=0, position differs=69, size differs=8, added=9 (pads 70-78).

| pad | official x | official y | official size | derived x | derived y | derived size | status |
|---|---|---|---|---|---|---|---|
| 1 | -3.5003 | 3.5 | 0.8x0.8 | -3.575 | 3.6 | 0.78x0.78 | position differs 0.12mm; size 0.8x0.8 vs 0.78x0.78 |
| 2 | -2.6003 | 3.7 | 0.4x0.4 | -2.925 | 3.6 | 0.4x0.4 | position differs 0.34mm |
| 3 | -2.2753 | 3.05 | 0.4x0.4 | -2.275 | 3.6 | 0.4x0.4 | position differs 0.55mm |
| 4 | -1.9503 | 3.7 | 0.4x0.4 | -1.625 | 3.6 | 0.4x0.4 | position differs 0.34mm |
| 5 | -1.6253 | 3.05 | 0.4x0.4 | -0.975 | 3.6 | 0.4x0.4 | position differs 0.85mm |
| 6 | -1.3003 | 3.7 | 0.4x0.4 | -0.325 | 3.6 | 0.4x0.4 | position differs 0.98mm |
| 7 | -0.4003 | 3.5 | 0.8x0.8 | 0.325 | 3.6 | 0.4x0.4 | position differs 0.73mm; size 0.8x0.8 vs 0.4x0.4 |
| 8 | -0.2003 | 2.6 | 0.4x0.4 | 0.975 | 3.6 | 0.4x0.4 | position differs 1.54mm |
| 9 | -0.8503 | 2.275 | 0.4x0.4 | 1.625 | 3.6 | 0.4x0.4 | position differs 2.81mm |
| 10 | -0.2003 | 1.95 | 0.4x0.4 | 2.275 | 3.6 | 0.4x0.4 | position differs 2.97mm |
| 11 | -0.8503 | 1.625 | 0.4x0.4 | 2.925 | 3.6 | 0.4x0.4 | position differs 4.26mm |
| 12 | -0.2003 | 1.3 | 0.4x0.4 | 3.575 | 3.6 | 0.78x0.78 | position differs 4.42mm; size 0.4x0.4 vs 0.78x0.78 |
| 13 | -0.8503 | 0.975 | 0.4x0.4 | 3.6 | 2.925 | 0.4x0.4 | position differs 4.86mm |
| 14 | -0.2003 | 0.65 | 0.4x0.4 | 3.6 | 2.275 | 0.4x0.4 | position differs 4.13mm |
| 15 | -0.8503 | 0.325 | 0.4x0.4 | 3.6 | 1.625 | 0.4x0.4 | position differs 4.64mm |
| 16 | -0.2003 | -0.0 | 0.4x0.4 | 3.6 | 0.975 | 0.4x0.4 | position differs 3.92mm |
| 17 | -0.8503 | -0.325 | 0.4x0.4 | 3.6 | 0.325 | 0.4x0.4 | position differs 4.50mm |
| 18 | -0.2003 | -0.65 | 0.4x0.4 | 3.6 | -0.325 | 0.4x0.4 | position differs 3.81mm |
| 19 | -0.8503 | -0.975 | 0.4x0.4 | 3.6 | -0.975 | 0.4x0.4 | position differs 4.45mm |
| 20 | -0.2003 | -1.3 | 0.4x0.4 | 3.6 | -1.625 | 0.4x0.4 | position differs 3.81mm |
| 21 | -0.8503 | -1.625 | 0.4x0.4 | 3.6 | -2.275 | 0.4x0.4 | position differs 4.50mm |
| 22 | -0.2003 | -1.95 | 0.4x0.4 | 3.6 | -2.925 | 0.4x0.4 | position differs 3.92mm |
| 23 | -0.8503 | -2.275 | 0.4x0.4 | 3.575 | -3.6 | 0.78x0.78 | position differs 4.62mm; size 0.4x0.4 vs 0.78x0.78 |
| 24 | -0.2003 | -2.6 | 0.4x0.4 | 2.925 | -3.6 | 0.4x0.4 | position differs 3.28mm |
| 25 | -0.4003 | -3.5 | 0.8x0.8 | 2.275 | -3.6 | 0.4x0.4 | position differs 2.68mm; size 0.8x0.8 vs 0.4x0.4 |
| 26 | -1.3003 | -3.7 | 0.4x0.4 | 1.625 | -3.6 | 0.4x0.4 | position differs 2.93mm |
| 27 | -1.6253 | -3.05 | 0.4x0.4 | 0.975 | -3.6 | 0.4x0.4 | position differs 2.66mm |
| 28 | -1.9503 | -3.7 | 0.4x0.4 | 0.325 | -3.6 | 0.4x0.4 | position differs 2.28mm |
| 29 | -2.2753 | -3.05 | 0.4x0.4 | -0.325 | -3.6 | 0.4x0.4 | position differs 2.03mm |
| 30 | -2.6003 | -3.7 | 0.4x0.4 | -0.975 | -3.6 | 0.4x0.4 | position differs 1.63mm |
| 31 | -3.5003 | -3.5 | 0.8x0.8 | -1.625 | -3.6 | 0.4x0.4 | position differs 1.88mm; size 0.8x0.8 vs 0.4x0.4 |
| 32 | -3.7003 | -2.6 | 0.4x0.4 | -2.275 | -3.6 | 0.4x0.4 | position differs 1.74mm |
| 33 | -3.0503 | -2.275 | 0.4x0.4 | -2.925 | -3.6 | 0.4x0.4 | position differs 1.33mm |
| 34 | -3.7003 | -1.95 | 0.4x0.4 | -3.575 | -3.6 | 0.78x0.78 | position differs 1.65mm; size 0.4x0.4 vs 0.78x0.78 |
| 35 | -3.0503 | -1.625 | 0.4x0.4 | -3.6 | -2.925 | 0.4x0.4 | position differs 1.41mm |
| 36 | -3.7003 | -1.3 | 0.4x0.4 | -3.6 | -2.275 | 0.4x0.4 | position differs 0.98mm |
| 37 | -3.0503 | -0.975 | 0.4x0.4 | -3.6 | -1.625 | 0.4x0.4 | position differs 0.85mm |
| 38 | -3.7003 | -0.65 | 0.4x0.4 | -3.6 | -0.975 | 0.4x0.4 | position differs 0.34mm |
| 39 | -3.0503 | -0.325 | 0.4x0.4 | -3.6 | -0.325 | 0.4x0.4 | position differs 0.55mm |
| 40 | -3.7003 | -0.0 | 0.4x0.4 | -3.6 | 0.325 | 0.4x0.4 | position differs 0.34mm |
| 41 | -3.0503 | 0.325 | 0.4x0.4 | -3.6 | 0.975 | 0.4x0.4 | position differs 0.85mm |
| 42 | -3.7003 | 0.65 | 0.4x0.4 | -3.6 | 1.625 | 0.4x0.4 | position differs 0.98mm |
| 43 | -3.0503 | 0.975 | 0.4x0.4 | -3.6 | 2.275 | 0.4x0.4 | position differs 1.41mm |
| 44 | -3.7003 | 1.3 | 0.4x0.4 | -3.6 | 2.925 | 0.4x0.4 | position differs 1.63mm |
| 45 | -3.0503 | 1.625 | 0.4x0.4 | -2.925 | 2.95 | 0.4x0.4 | position differs 1.33mm |
| 46 | -3.7003 | 1.95 | 0.4x0.4 | -2.275 | 2.95 | 0.4x0.4 | position differs 1.74mm |
| 47 | -3.0503 | 2.275 | 0.4x0.4 | -1.625 | 2.95 | 0.4x0.4 | position differs 1.58mm |
| 48 | -3.7003 | 2.6 | 0.4x0.4 | -0.975 | 2.95 | 0.4x0.4 | position differs 2.75mm |
| 49 | -2.2753 | -2.275 | 0.4x0.4 | -0.325 | 2.95 | 0.4x0.4 | position differs 5.58mm |
| 50 | -2.2753 | -1.625 | 0.4x0.4 | 0.325 | 2.95 | 0.4x0.4 | position differs 5.26mm |
| 51 | -2.2753 | -0.975 | 0.4x0.4 | 0.975 | 2.95 | 0.4x0.4 | position differs 5.10mm |
| 52 | -2.2753 | -0.325 | 0.4x0.4 | 1.625 | 2.95 | 0.4x0.4 | position differs 5.09mm |
| 53 | -2.2753 | 0.325 | 0.4x0.4 | 2.275 | 2.95 | 0.4x0.4 | position differs 5.25mm |
| 54 | -2.2753 | 0.975 | 0.4x0.4 | 2.925 | 2.95 | 0.4x0.4 | position differs 5.56mm |
| 55 | -2.2753 | 1.625 | 0.4x0.4 | 2.95 | 1.625 | 0.4x0.4 | position differs 5.23mm |
| 56 | -2.2753 | 2.275 | 0.4x0.4 | 2.95 | 0.975 | 0.4x0.4 | position differs 5.38mm |
| 57 | -1.6253 | -2.275 | 0.4x0.4 | 2.95 | 0.325 | 0.4x0.4 | position differs 5.26mm |
| 58 | -1.6253 | -1.625 | 0.4x0.4 | 2.95 | -0.325 | 0.4x0.4 | position differs 4.76mm |
| 59 | -1.6253 | -0.975 | 0.4x0.4 | 2.95 | -0.975 | 0.4x0.4 | position differs 4.58mm |
| 60 | -1.6253 | -0.325 | 0.4x0.4 | 2.95 | -1.625 | 0.4x0.4 | position differs 4.76mm |
| 61 | -1.6253 | 0.325 | 0.4x0.4 | 2.925 | -2.95 | 0.4x0.4 | position differs 5.61mm |
| 62 | -1.6253 | 0.975 | 0.4x0.4 | 2.275 | -2.95 | 0.4x0.4 | position differs 5.53mm |
| 63 | -1.6253 | 1.625 | 0.4x0.4 | 1.625 | -2.95 | 0.4x0.4 | position differs 5.61mm |
| 64 | -1.6253 | 2.275 | 0.4x0.4 | 0.975 | -2.95 | 0.4x0.4 | position differs 5.84mm |
| 65 | 0.5497 | 3.7 | 0.4x0.4 | 0.325 | -2.95 | 0.4x0.4 | position differs 6.65mm |
| 66 | 1.5497 | 3.7 | 0.4x0.4 | -0.325 | -2.95 | 0.4x0.4 | position differs 6.91mm |
| 67 | 2.5497 | 3.7 | 0.4x0.4 | -0.975 | -2.95 | 0.4x0.4 | position differs 7.53mm |
| 68 | 3.4997 | 3.5 | 0.8x0.8 | -1.625 | -2.95 | 0.4x0.4 | position differs 8.24mm; size 0.8x0.8 vs 0.4x0.4 |
| 69 | 3.7002 | 2.5 | 0.4x0.4 | -2.275 | -2.95 | 0.4x0.4 | position differs 8.09mm |
| 70 | 3.7002 | 1.5 | 0.4x0.4 | - | - | - | ADDED (absent in derived) |
| 71 | 3.7002 | 0.5 | 0.4x0.4 | - | - | - | ADDED (absent in derived) |
| 72 | 3.7002 | -0.5 | 0.4x0.4 | - | - | - | ADDED (absent in derived) |
| 73 | 3.7002 | -1.5 | 0.4x0.4 | - | - | - | ADDED (absent in derived) |
| 74 | 3.7002 | -2.5 | 0.4x0.4 | - | - | - | ADDED (absent in derived) |
| 75 | 3.4997 | -3.5 | 0.8x0.8 | - | - | - | ADDED (absent in derived) |
| 76 | 2.5497 | -3.7 | 0.4x0.4 | - | - | - | ADDED (absent in derived) |
| 77 | 1.5497 | -3.7 | 0.4x0.4 | - | - | - | ADDED (absent in derived) |
| 78 | 0.5497 | -3.7 | 0.4x0.4 | - | - | - | ADDED (absent in derived) |
