import React from "react"
import { HallKey } from "../components/HallKey"

/**
 * Canonical M1 electrical-capture fixture. Routing is deliberately disabled.
 * Package names are stock footprinter descriptions of the manufacturer package:
 * RP2040 QFN-56, W25Q16JV UXIQ USON-8, AP2112 SOT-25, TPS22919 DCK
 * (SC70-6), and TMUX1208 PW (TSSOP-16). The TYPE-C-31-M-12 footprint uses
 * the manufacturer's 16 contact land pattern; its material dimensions are
 * independently asserted by verify-m1-electrical.tsx.
 */
const usbFootprint = (
  <footprint>
    {Array.from({ length: 8 }, (_, i) => (
      <smtpad key={`a${i}`} shape="rect" pcbX={-1.75 + i * 0.5} pcbY={-3.55} width={0.3} height={1.15} layer="top" portHints={[`${i + 1}`]} />
    ))}
    {Array.from({ length: 8 }, (_, i) => (
      <smtpad key={`b${i}`} shape="rect" pcbX={1.75 - i * 0.5} pcbY={-2.8} width={0.3} height={1.15} layer="top" portHints={[`${i + 9}`]} />
    ))}
    <platedhole shape="circle" pcbX={-4.32} pcbY={0} holeDiameter={0.65} outerDiameter={1.05} portHints={["17"]} />
    <platedhole shape="circle" pcbX={4.32} pcbY={0} holeDiameter={0.65} outerDiameter={1.05} portHints={["17"]} />
  </footprint>
)

const Chip = (p: any) => <chip {...p} />
const Passive = ({ name, kind, value }: { name: string; kind: "r" | "c"; value: string }) =>
  kind === "r" ? <resistor name={name} resistance={value} footprint="0603" /> : <capacitor name={name} capacitance={value} footprint="0603" />
const TP = ({ name }: { name: string }) => <testpoint name={name} footprintVariant="pad" padShape="circle" padDiameter="1.2mm" />
const T = ({ name, from, to }: { name: string; from: string; to: string }) => <trace name={name} from={from} to={to} />

export const M1FourKeyElectrical = () => {
  const nets = ["VBUS", "V3V3", "V1V1", "GND", "HALL_5V", "USB_DP", "USB_DM", "USB_DP_CONN", "USB_DM_CONN", "H0_RAW", "H1_RAW", "H2_RAW", "H3_RAW", "MUX_D", "ADC0_FILTERED", "HALL_PWR_EN", "MUX_A0", "MUX_A1", "MUX_A2", "MUX_EN0", "STATUS_LED", "RUN", "SWDIO", "SWCLK", "QSPI_SD0", "QSPI_SD1", "QSPI_SD2", "QSPI_SD3", "QSPI_SCLK", "QSPI_SS", "XIN", "XOUT"]
  const connections: Array<[string, string, string]> = []
  const connect = (name: string, from: string, net: string) => connections.push([name, from, net])

  connect("USB_VBUS", ".J_USB > .VBUS", "VBUS"); connect("USB_GND", ".J_USB > .GND", "GND")
  connect("USB_DP_CONN", ".J_USB > .DP", "USB_DP_CONN"); connect("USB_DM_CONN", ".J_USB > .DM", "USB_DM_CONN")
  connect("USB_CC1_RD", ".R_CC1 > .pin1", "CC1"); connect("USB_CC2_RD", ".R_CC2 > .pin1", "CC2")
  connect("USB_CC1_GND", ".R_CC1 > .pin2", "GND"); connect("USB_CC2_GND", ".R_CC2 > .pin2", "GND")
  connect("LDO_IN", ".U_LDO > .VIN", "VBUS"); connect("LDO_ENABLE", ".U_LDO > .EN", "VBUS"); connect("LDO_OUT", ".U_LDO > .VOUT", "V3V3"); connect("LDO_GND", ".U_LDO > .GND", "GND")
  connect("LOAD_IN", ".U_LOAD > .IN", "VBUS"); connect("LOAD_OUT", ".U_LOAD > .OUT", "HALL_5V"); connect("LOAD_ON", ".U_LOAD > .ON", "HALL_PWR_EN"); connect("LOAD_GND", ".U_LOAD > .GND", "GND")
  connect("MCU_USB_DP", ".U_MCU > .USB_DP", "USB_DP"); connect("MCU_USB_DM", ".U_MCU > .USB_DM", "USB_DM")
  for (const n of ["HALL_PWR_EN", "MUX_A0", "MUX_A1", "MUX_A2", "MUX_EN0", "STATUS_LED", "ADC0_FILTERED", "RUN", "SWDIO", "SWCLK", "QSPI_SD0", "QSPI_SD1", "QSPI_SD2", "QSPI_SD3", "QSPI_SCLK", "QSPI_SS", "XIN", "XOUT"]) connect(`MCU_${n}`, `.U_MCU > .${n}`, n)
  connect("MCU_3V3", ".U_MCU > .IOVDD", "V3V3"); connect("MCU_GND", ".U_MCU > .GND", "GND")
  ;[0, 1, 2, 3].forEach((i) => { connect(`H${i}_VCC`, `.U_H${i} > .VCC`, "HALL_5V"); connect(`H${i}_GND`, `.U_H${i} > .GND`, "GND"); connect(`H${i}_OUT`, `.U_H${i} > .OUT`, `H${i}_RAW`) })
  ;[["A0", "MUX_A0"], ["A1", "MUX_A1"], ["A2", "MUX_A2"], ["EN", "MUX_EN0"], ["D", "MUX_D"], ["VDD", "HALL_5V"], ["GND", "GND"], ["S1", "H0_RAW"], ["S2", "H1_RAW"], ["S3", "H2_RAW"], ["S4", "H3_RAW"]].forEach(([p,n]) => connect(`MUX_${p}`, `.U_MUX > .${p}`, n))
  connect("ADC_TOP_IN", ".R_ADC_TOP > .pin1", "MUX_D"); connect("ADC_TOP_OUT", ".R_ADC_TOP > .pin2", "ADC0_FILTERED"); connect("ADC_BOTTOM_ADC", ".R_ADC_BOTTOM > .pin1", "ADC0_FILTERED"); connect("ADC_BOTTOM_GND", ".R_ADC_BOTTOM > .pin2", "GND"); connect("ADC_CAP_ADC", ".C_ADC > .pin1", "ADC0_FILTERED"); connect("ADC_CAP_GND", ".C_ADC > .pin2", "GND")
  ;["VBUS", "V3V3", "HALL_5V", "H0_RAW", "H1_RAW", "H2_RAW", "H3_RAW", "MUX_D", "ADC0_FILTERED", "GND", "SWDIO", "SWCLK"].forEach((n) => connect(`TP_${n}`, `.TP_${n} > .pin1`, n))
  return <board width={100} height={70} layers={2} thickness="1.2mm" routingDisabled>
    {nets.map((n) => <net key={n} name={n} isPowerNet={["VBUS","V3V3","V1V1","HALL_5V"].includes(n)} isGroundNet={n === "GND"} />)}<net name="CC1"/><net name="CC2"/>
    <Chip name="J_USB" manufacturerPartNumber="TYPE-C-31-M-12" supplierPartNumbers={{jlcpcb:["C165948"]}} footprint={usbFootprint} pinLabels={{pin1:"VBUS",pin2:"GND",pin3:"CC1",pin4:"CC2",pin5:"DP",pin6:"DM",pin7:"SHIELD",pin8:"NC1",pin9:"NC2",pin10:"NC3",pin11:"NC4",pin12:"NC5",pin13:"NC6",pin14:"NC7",pin15:"NC8",pin16:"NC9",pin17:"SHIELD2"}} />
    <Chip name="U_MCU" manufacturerPartNumber="RP2040" supplierPartNumbers={{jlcpcb:["C2040"]}} footprint="qfn56_w7_h7_p0.4mm_thermalpad" pinLabels={{pin3:"MUX_A0",pin4:"MUX_A1",pin5:"MUX_A2",pin6:"MUX_EN0",pin8:"HALL_PWR_EN",pin12:"STATUS_LED",pin31:"ADC0_FILTERED",pin30:"RUN",pin42:"SWCLK",pin43:"SWDIO",pin46:"USB_DM",pin47:"USB_DP",pin51:"QSPI_SD3",pin52:"QSPI_SCLK",pin53:"QSPI_SD0",pin54:"QSPI_SD2",pin55:"QSPI_SD1",pin56:"QSPI_SS",pin20:"IOVDD",pin57:"GND",pin44:"XIN",pin45:"XOUT"}} />
    <Chip name="U_FLASH" manufacturerPartNumber="W25Q16JVUXIQ" footprint="qfn8_w3_h2_p0.5mm" pinLabels={{pin1:"QSPI_SS",pin2:"QSPI_SD1",pin3:"QSPI_SD2",pin4:"GND",pin5:"QSPI_SD0",pin6:"QSPI_SCLK",pin7:"QSPI_SD3",pin8:"VCC"}} />
    <Chip name="Y1" manufacturerPartNumber="ABM8-272-T3" footprint="crystal4_w3.2_h2.5" pinLabels={{pin1:"XIN",pin2:"GND1",pin3:"XOUT",pin4:"GND2"}} />
    <Chip name="U_LDO" manufacturerPartNumber="AP2112K-3.3TRG1" supplierPartNumbers={{jlcpcb:["C51118"]}} footprint="sot23_5" pinLabels={{pin1:"VIN",pin2:"GND",pin3:"EN",pin4:"NC",pin5:"VOUT"}} />
    <Chip name="U_LOAD" manufacturerPartNumber="TPS22919DCKR" supplierPartNumbers={{jlcpcb:["C2149796"]}} footprint="sc70_6" pinLabels={{pin1:"ON",pin2:"GND",pin3:"CT",pin4:"QOD",pin5:"OUT",pin6:"IN"}} />
    <Chip name="U_MUX" manufacturerPartNumber="TMUX1208PWR" supplierPartNumbers={{jlcpcb:["C494728"]}} footprint="tssop16_p0.65mm" pinLabels={{pin1:"A0",pin2:"EN",pin3:"NC",pin4:"S1",pin5:"S2",pin6:"S3",pin7:"S4",pin8:"D",pin9:"S8",pin10:"S7",pin11:"S6",pin12:"S5",pin13:"VDD",pin14:"GND",pin15:"A2",pin16:"A1"}} />
    {[0,1,2,3].map((i) => <HallKey key={i} name={`U_H${i}`} />)}
    <Passive name="R_CC1" kind="r" value="5.1k"/><Passive name="R_CC2" kind="r" value="5.1k"/><Passive name="R_USB_DP" kind="r" value="27"/><Passive name="R_USB_DM" kind="r" value="27"/><Passive name="R_ADC_TOP" kind="r" value="6.8k"/><Passive name="R_ADC_BOTTOM" kind="r" value="10k"/><Passive name="C_ADC" kind="c" value="1nF"/><Passive name="R_XOUT" kind="r" value="1k"/><Passive name="C_XIN" kind="c" value="15pF"/><Passive name="C_XOUT" kind="c" value="15pF"/>
    {["LDO_IN","LDO_OUT","MCU_IO","MCU_CORE","FLASH","MUX",...Array.from({length:4},(_,i)=>`HALL${i}`)].map(n=><Passive key={n} name={`C_${n}`} kind="c" value={n.startsWith("LDO") ? "1uF" : "100nF"}/>)}
    <led name="D_POWER" color="green" footprint="0603"/><resistor name="R_POWER_LED" resistance="2.2k" footprint="0603"/><led name="D_STATUS" color="amber" footprint="0603"/><resistor name="R_STATUS_LED" resistance="2.2k" footprint="0603"/>
    <Chip name="SW_BOOT" footprint="smd2" pinLabels={{pin1:"A",pin2:"B"}}/><Chip name="SW_RUN" footprint="smd2" pinLabels={{pin1:"A",pin2:"B"}}/>
    {['VBUS','V3V3','HALL_5V','H0_RAW','H1_RAW','H2_RAW','H3_RAW','MUX_D','ADC0_FILTERED','GND','SWDIO','SWCLK'].map(n=><TP key={n} name={`TP_${n}`}/>)}
    {connections.map(([name,from,to])=><T key={name} name={name} from={from} to={`net.${to}`}/>)}
    <T name="USB_DP_R_IN" from=".R_USB_DP > .pin1" to="net.USB_DP_CONN"/><T name="USB_DP_R_OUT" from=".R_USB_DP > .pin2" to="net.USB_DP"/><T name="USB_DM_R_IN" from=".R_USB_DM > .pin1" to="net.USB_DM_CONN"/><T name="USB_DM_R_OUT" from=".R_USB_DM > .pin2" to="net.USB_DM"/>
    {[["C_LDO_IN","VBUS"],["C_LDO_OUT","V3V3"],["C_MCU_IO","V3V3"],["C_MCU_CORE","V1V1"],["C_FLASH","V3V3"],["C_MUX","HALL_5V"],["C_HALL0","HALL_5V"],["C_HALL1","HALL_5V"],["C_HALL2","HALL_5V"],["C_HALL3","HALL_5V"]].flatMap(([c,n])=>[<T key={`${c}P`} name={`${c}_POWER`} from={`.${c} > .pin1`} to={`net.${n}`}/>,<T key={`${c}G`} name={`${c}_GND`} from={`.${c} > .pin2`} to="net.GND"/>])}
    <T name="FLASH_VCC" from=".U_FLASH > .VCC" to="net.V3V3"/><T name="FLASH_GND" from=".U_FLASH > .GND" to="net.GND"/>
    {['QSPI_SD0','QSPI_SD1','QSPI_SD2','QSPI_SD3','QSPI_SCLK','QSPI_SS'].map(n=><T key={n} name={`FLASH_${n}`} from={`.U_FLASH > .${n}`} to={`net.${n}`}/>)}
    <T name="POWER_LED_A" from=".D_POWER > .anode" to="net.V3V3"/><T name="POWER_LED_R" from=".D_POWER > .cathode" to=".R_POWER_LED > .pin1"/><T name="POWER_LED_GND" from=".R_POWER_LED > .pin2" to="net.GND"/>
    <T name="STATUS_LED_GPIO" from=".D_STATUS > .anode" to="net.STATUS_LED"/><T name="STATUS_LED_R" from=".D_STATUS > .cathode" to=".R_STATUS_LED > .pin1"/><T name="STATUS_LED_GND" from=".R_STATUS_LED > .pin2" to="net.GND"/>
    <T name="RUN_BUTTON" from=".SW_RUN > .A" to="net.RUN"/><T name="RUN_BUTTON_GND" from=".SW_RUN > .B" to="net.GND"/><T name="BOOT_BUTTON" from=".SW_BOOT > .A" to="net.QSPI_SS"/><T name="BOOT_BUTTON_GND" from=".SW_BOOT > .B" to="net.GND"/>
    <T name="Y_XIN" from=".Y1 > .XIN" to="net.XIN"/><T name="Y_XOUT_R" from=".Y1 > .XOUT" to=".R_XOUT > .pin1"/><T name="R_XOUT_MCU" from=".R_XOUT > .pin2" to="net.XOUT"/><T name="C_XIN_X" from=".C_XIN > .pin1" to="net.XIN"/><T name="C_XIN_G" from=".C_XIN > .pin2" to="net.GND"/><T name="C_XOUT_X" from=".C_XOUT > .pin1" to="net.XOUT"/><T name="C_XOUT_G" from=".C_XOUT > .pin2" to="net.GND"/>
  </board>
}

export default M1FourKeyElectrical
