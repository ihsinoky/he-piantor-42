"""Generate carrier.kicad_sym + carrier.kicad_sch for Issue #252.
Symbol: SM14B-GHS-TB, pins 1..14 + pin 15 (MP, both mechanical pads).
Schematic: JC1 (Wing-facing) and JC2 (Main-facing) joined pin-k to
pin-k by global labels named per D-024 (unique per pin, GNDs kept
separate = pure 1:1 pass-through). Pin 15 = no-connect (mechanical NC)."""
import uuid

FN = {1: 'HALL_5V', 2: 'GND', 3: 'MUX_A0', 4: 'GND', 5: 'MUX_A1',
      6: 'MUX_A2', 7: 'WING_EN', 8: 'GND', 9: 'MUX_OUT_A', 10: 'GND',
      11: 'MUX_OUT_B', 12: 'GND', 13: 'MUX_OUT_C', 14: 'GND'}
NET = {k: f'P{k:02d}_{FN[k]}' for k in range(1, 15)}

def u():
    return str(uuid.uuid4())

# ---- symbol: pins on left (1..15 top->bottom) and right (1..15) ----
# Body: x -5.08..5.08, y -10.16..10.16 (schematic mm, y down-positive
# in file coords is negative-up; KiCad sch y axis points down).
pins_y = {k: -8.89 + (k - 1) * 1.27 for k in range(1, 16)}
sym_pins = []
for side, x, ang in (('L', -7.62, 0),):
    for k in range(1, 16):
        nm = f'P{k}' if k < 15 else 'MP'
        sym_pins.append(
            f'      (pin passive line (at {x} {pins_y[k]:.2f} {ang}) '
            f'(length 2.54) (name "{nm}" (effects (font (size 1.27 1.27)))) '
            f'(number "{k}" (effects (font (size 1.27 1.27)))))')
sym = f'''(kicad_symbol_lib
  (version 20231120)
  (generator "eeschema")
  (symbol "SM14B-GHS-TB"
    (exclude_from_sim no) (in_bom yes) (on_board yes)
    (property "Reference" "J" (at 0 11.43 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SM14B-GHS-TB" (at 0 -11.43 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Carrier:JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "SM14B-GHS-TB_0_1"
      (rectangle (start -5.08 -10.16) (end 5.08 10.16)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "SM14B-GHS-TB_1_1"
{chr(10).join(sym_pins)}
    )
  )
)
'''
open('/home/hatch/workspace/projects/he-piantor-midconn/hardware/kicad/qualification/issue-252-carrier/carrier.kicad_sym', 'w').write(sym)

# ---- schematic: JC1 at (60,60) pins left used; JC2 at (120,60) ----
def instance(ref, x, y, mirror):
    uid = u()
    sheet_uuid = SHEET_UUID
    pinuids = {k: u() for k in range(1, 16)}
    pins = '\n'.join(f'    (pin "{k}" (uuid "{pinuids[k]}"))' for k in range(1, 16))
    m = ' (mirror y)' if mirror else ''
    return f'''  (symbol (lib_id "Carrier:SM14B-GHS-TB") (at {x} {y} 0){m} (unit 1)
    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid}")
    (property "Reference" "{ref}" (at {x - 6} {y - 12} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SM14B-GHS-TB(LF)(SN)" (at {x} {y + 12} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Carrier:JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))
{pins}
    (instances (project "carrier" (path "/{sheet_uuid}" (reference "{ref}") (unit 1))))
  )''', pinuids

# pin endpoint coords: JC1 unmirrored: left pins at (x-7.62, y+pins_y)
# JC2 mirrored about Y: left pins appear at (x+7.62, y+pins_y)
labels = []
ncs = []
def label(name, x, y):
    labels.append(f'  (global_label "{name}" (shape passive) (at {x} {y} 0) '
                  f'(effects (font (size 1.27 1.27)) (justify left)) '
                  f'(uuid "{u()}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" '
                  f'(at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes))))')
def nc(x, y):
    ncs.append(f'  (no_connect (at {x} {y}) (uuid "{u()}"))')

SHEET_UUID = '25252525-2525-4525-8525-252525252525'
X1, X2, Y = 59.69, 119.38, 59.69
for k in range(1, 15):
    label(NET[k], X1 - 7.62, Y - pins_y[k])
    label(NET[k], X2 + 7.62, Y - pins_y[k])
nc(X1 - 7.62, Y - pins_y[15])
nc(X2 + 7.62, Y - pins_y[15])

inst1, _ = instance('JC1', X1, Y, False)
inst2, _ = instance('JC2', X2, Y, True)
sch = f'''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "{SHEET_UUID}")
  (paper "A4")
  (title_block (title "Issue 252 carrier PCB - GH mid-harness pass-through") (rev "study"))
  (lib_symbols
    (symbol "Carrier:SM14B-GHS-TB"
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 11.43 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SM14B-GHS-TB" (at 0 -11.43 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Carrier:JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "SM14B-GHS-TB_0_1"
        (rectangle (start -5.08 -10.16) (end 5.08 10.16)
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "SM14B-GHS-TB_1_1"
{chr(10).join(sym_pins)}
      )
    )
  )
{chr(10).join(labels)}
{chr(10).join(ncs)}
{inst1}
{inst2}
  (sheet_instances (path "/" (page "1")))
)
'''
open('/home/hatch/workspace/projects/he-piantor-midconn/hardware/kicad/qualification/issue-252-carrier/carrier.kicad_sch', 'w').write(sch)
print('schematic + symbol written')
