import React from "react"
import { HallKey } from "../../components/HallKey"

/** Small stock-routed fixture for Checkpoint C manufacturing evidence. */
export const CheckpointCBoard = () => (
  <board
    width={24}
    height={16}
    layers={2}
    thickness="1.2mm"
    autorouter="default"
    minTraceWidth="0.2mm"
    defaultTraceWidth="0.2mm"
    minTraceToPadEdgeClearance="0.2mm"
    minViaHoleDiameter="0.3mm"
    minViaPadDiameter="0.6mm"
  >
    <HallKey />
    <net name="HALL_5V" isPowerNet />
    <net name="GND" isGroundNet />
    <net name="H0_RAW" />
    <capacitor name="C_HALL1" capacitance="100nF" footprint="0603" pcbX={7} pcbY={-3} />
    <testpoint name="TP_H0_RAW" footprintVariant="pad" padShape="circle" padDiameter="1.2mm" pcbX={9} pcbY={4} />
    <via name="VIA_GND_STITCH" pcbX={7} pcbY={3} holeDiameter="0.3mm" outerDiameter="0.6mm" fromLayer="top" toLayer="bottom" connectsTo="net.GND" />
    <copperpour name="GND_TOP" connectsTo="net.GND" layer="top" />
    <copperpour name="GND_BOTTOM" connectsTo="net.GND" layer="bottom" />
    <trace name="HALL_VCC_TO_HALL_5V" from=".U1 > .VCC" to="net.HALL_5V" />
    <trace name="HALL_GND_TO_GND" from=".U1 > .GND" to="net.GND" />
    <trace name="HALL_OUT_TO_H0_RAW" from=".U1 > .OUT" to="net.H0_RAW" />
    <trace name="C_HALL1_TO_HALL_5V" from=".C_HALL1 > .pin1" to="net.HALL_5V" />
    <trace name="C_HALL1_TO_GND" from=".C_HALL1 > .pin2" to="net.GND" />
    <trace name="TP_H0_RAW_TO_H0_RAW" from=".TP_H0_RAW > .pin1" to="net.H0_RAW" />
  </board>
)

export default CheckpointCBoard
