import React from "react"
import { HallKey } from "../components/HallKey"

/* TYPE-C-31-M-12 manufacturer recommended land pattern (C165948 drawing).
 * Contacts use their USB Type-C names as pad hints. The two wide power/ground
 * lands each serve the paired receptacle contacts shown in the drawing.
 * Four plated shell stakes and two locating NPTHs are retained separately. */
const usbContact = (id: string, x: number, width = 0.3) =>
  <smtpad key={id} shape="rect" pcbX={x} pcbY={-4.045} width={width} height={1.45} layer="top" portHints={[id]} />
const usbFootprint = <footprint>
  {usbContact("A1_B12", -3.25, 0.6)}{usbContact("A4_B9", -2.45, 0.6)}{usbContact("B8", -1.75)}
  {usbContact("A5", -1.25)}{usbContact("B7", -0.75)}{usbContact("A6", -0.25)}
  {usbContact("A7", 0.25)}{usbContact("B6", 0.75)}{usbContact("A8", 1.25)}{usbContact("B5", 1.75)}
  {usbContact("A9_B4", 2.45, 0.6)}{usbContact("A12_B1", 3.25, 0.6)}
  <platedhole shape="oval" pcbX={-4.32} pcbY={-3.13} holeWidth={0.6} holeHeight={1.7} outerWidth={1} outerHeight={2.1} portHints={["SHIELD"]}/>
  <platedhole shape="oval" pcbX={4.32} pcbY={-3.13} holeWidth={0.6} holeHeight={1.7} outerWidth={1} outerHeight={2.1} portHints={["SHIELD"]}/>
  <platedhole shape="oval" pcbX={-4.32} pcbY={1.05} holeWidth={0.6} holeHeight={1.2} outerWidth={1} outerHeight={1.6} portHints={["SHIELD"]}/>
  <platedhole shape="oval" pcbX={4.32} pcbY={1.05} holeWidth={0.6} holeHeight={1.2} outerWidth={1} outerHeight={1.6} portHints={["SHIELD"]}/>
  <hole pcbX={-2.89} pcbY={-2.60} diameter={0.65}/><hole pcbX={2.89} pcbY={-2.60} diameter={0.65}/>
</footprint>

/* Stock-native transcription of the reviewed USON-8_UX_2x3x0p6_WIN land pattern. */
const flashFootprint = <footprint>
  {[[1,-1.4478,-.750001],[2,-1.4478,-.25],[3,-1.4478,.25],[4,-1.4478,.750001],[5,1.4478,.750001],[6,1.4478,.25],[7,1.4478,-.25],[8,1.4478,-.750001]].map(([pin,x,y])=><smtpad key={pin} shape="rect" pcbX={x} pcbY={y} width={.8128} height={.254} layer="top" portHints={[`pin${pin}`]}/>)}
  <smtpad shape="rect" pcbX={0} pcbY={0} width={.254} height={1.651} layer="top" portHints={["EP"]}/>
</footprint>

/* Abracon ABM8 recommended land pattern, bottom view: 1 2 / 4 3. */
const crystalFootprint = <footprint>
  <smtpad shape="rect" pcbX={-1.15} pcbY={0.875} width={1.3} height={1.05} layer="top" portHints={["pin1"]}/>
  <smtpad shape="rect" pcbX={1.15} pcbY={0.875} width={1.3} height={1.05} layer="top" portHints={["pin2"]}/>
  <smtpad shape="rect" pcbX={1.15} pcbY={-0.875} width={1.3} height={1.05} layer="top" portHints={["pin3"]}/>
  <smtpad shape="rect" pcbX={-1.15} pcbY={-0.875} width={1.3} height={1.05} layer="top" portHints={["pin4"]}/>
</footprint>

const C = ({name, value, footprint="0603"}: {name:string,value:string,footprint?:string}) => <capacitor name={name} capacitance={value} footprint={footprint}/>
const R = ({name, value, footprint="0603"}: {name:string,value:string,footprint?:string}) => <resistor name={name} resistance={value} footprint={footprint}/>
const TP = ({name}: {name:string}) => <testpoint name={`TP_${name}`} footprintVariant="pad" padShape="circle" padDiameter="1.2mm"/>
const T = ({name,from,to}: {name:string,from:string,to:string}) => <trace name={name} from={from} to={to}/>

export const M1FourKeyElectrical = () => {
  const nets=["VBUS","V3V3","V1V1","GND","USB_SHIELD","HALL_5V","USB_DP_CONN","USB_DM_CONN","USB_DP_ESD","USB_DM_ESD","USB_DP","USB_DM","H0_RAW","H1_RAW","H2_RAW","H3_RAW","MUX_D","ADC_SENSE","HALL_PWR_EN","MUX_A0","MUX_A1","MUX_A2","MUX_EN0","STATUS_LED","RUN","SWDIO","SWCLK","QSPI_SD0","QSPI_SD1","QSPI_SD2","QSPI_SD3","QSPI_SCLK","QSPI_SS_MCU","QSPI_SS_FLASH","XIN","XOUT_XTAL","XOUT","CC1","CC2","MUX_S5","MUX_S6","MUX_S7","MUX_S8"]
  const traces:Array<[string,string,string]>=[]
  const n=(name:string,from:string,to:string)=>traces.push([name,from,`net.${to}`])
  // Every material RP2040 supply pin is a distinct physical source port.
  for(const p of ["IOVDD_1","IOVDD_10","IOVDD_22","IOVDD_33","IOVDD_42","IOVDD_49","USB_VDD_48","ADC_AVDD_43","VREG_IN_44"]) n(`MCU_${p}`,`.U_MCU > .${p}`,"V3V3")
  for(const p of ["DVDD_23","DVDD_50"]) n(`MCU_${p}`,`.U_MCU > .${p}`,"V1V1")
  n("MCU_VREG_VOUT_45",".U_MCU > .VREG_VOUT_45","V1V1");n("MCU_TESTEN_19",".U_MCU > .TESTEN_19","GND");n("MCU_GND_57",".U_MCU > .GND_57","GND")
  for(const s of ["MUX_A0","MUX_A1","MUX_A2","MUX_EN0","HALL_PWR_EN","STATUS_LED","ADC_SENSE","XIN","XOUT","SWCLK","SWDIO","RUN","USB_DM","USB_DP","QSPI_SD3","QSPI_SCLK","QSPI_SD0","QSPI_SD2","QSPI_SD1"]) n(`MCU_${s}`,`.U_MCU > .${s}`,s)
  n("MCU_QSPI_SS",".U_MCU > .QSPI_SS","QSPI_SS_MCU")
  for(let i=0;i<4;i++){n(`H${i}_VCC`,`.U_H${i} > .VCC`,"HALL_5V");n(`H${i}_GND`,`.U_H${i} > .GND`,"GND");n(`H${i}_OUT`,`.U_H${i} > .OUT`,`H${i}_RAW`)}
  for(const [p,net] of [["A0","MUX_A0"],["A1","MUX_A1"],["A2","MUX_A2"],["EN","MUX_EN0"],["D","MUX_D"],["VDD","HALL_5V"],["GND","GND"],["S1","H0_RAW"],["S2","H1_RAW"],["S3","H2_RAW"],["S4","H3_RAW"],["S5","MUX_S5"],["S6","MUX_S6"],["S7","MUX_S7"],["S8","MUX_S8"]])n(`MUX_${p}`,`.U_MUX > .${p}`,net)
  return <board width={100} height={70} layers={2} thickness="1.2mm" routingDisabled schematicDisabled>
    {nets.map(x=><net key={x} name={x} isPowerNet={["VBUS","V3V3","V1V1","HALL_5V"].includes(x)} isGroundNet={x==="GND"}/>)}
    <chip name="J_USB" manufacturerPartNumber="TYPE-C-31-M-12" supplierPartNumbers={{jlcpcb:["C165948"]}} footprint={usbFootprint} pinLabels={{pin1:"A1_B12",pin2:"A4_B9",pin3:"A5",pin4:"A6",pin5:"A7",pin6:"A8",pin7:"B8",pin8:"B7",pin9:"B6",pin10:"B5",pin11:"A9_B4",pin12:"A12_B1",pin13:"SHIELD"}} noConnect={["A8","B8"]}/>
    <chip name="U_ESD" manufacturerPartNumber="USBLC6-2SC6" supplierPartNumbers={{jlcpcb:["C7519"]}} footprint="sot23_6" pinLabels={{pin1:"IO1_1",pin2:"GND",pin3:"IO2_1",pin4:"IO2_2",pin5:"VBUS",pin6:"IO1_2"}}/>
    <chip name="U_MCU" manufacturerPartNumber="RP2040" supplierPartNumbers={{jlcpcb:["C2040"]}} footprint="qfn56_w7_h7_p0.4mm_thermalpad" pinLabels={{pin1:"IOVDD_1",pin4:"MUX_A0",pin5:"MUX_A1",pin6:"MUX_A2",pin7:"MUX_EN0",pin9:"HALL_PWR_EN",pin10:"IOVDD_10",pin14:"STATUS_LED",pin19:"TESTEN_19",pin20:"XIN",pin21:"XOUT",pin22:"IOVDD_22",pin23:"DVDD_23",pin24:"SWCLK",pin25:"SWDIO",pin26:"RUN",pin33:"IOVDD_33",pin38:"ADC_SENSE",pin42:"IOVDD_42",pin43:"ADC_AVDD_43",pin44:"VREG_IN_44",pin45:"VREG_VOUT_45",pin46:"USB_DM",pin47:"USB_DP",pin48:"USB_VDD_48",pin49:"IOVDD_49",pin50:"DVDD_50",pin51:"QSPI_SD3",pin52:"QSPI_SCLK",pin53:"QSPI_SD0",pin54:"QSPI_SD2",pin55:"QSPI_SD1",pin56:"QSPI_SS",pin57:"GND_57"}}/>
    <chip name="U_FLASH" manufacturerPartNumber="W25Q16JVUXIQ" supplierPartNumbers={{jlcpcb:["C2843335"]}} footprint={flashFootprint} pinLabels={{pin1:"CS",pin2:"QSPI_SD1",pin3:"QSPI_SD2",pin4:"GND",pin5:"QSPI_SD0",pin6:"QSPI_SCLK",pin7:"QSPI_SD3",pin8:"VCC",pin9:"EP"}} noConnect={["EP"]}/>
    <chip name="Y1" manufacturerPartNumber="ABM8-272-T3" supplierPartNumbers={{jlcpcb:["C20625731"]}} footprint={crystalFootprint} pinLabels={{pin1:"XIN",pin2:"GND1",pin3:"XOUT",pin4:"GND2"}}/>
    <chip name="U_LDO" manufacturerPartNumber="AP2112K-3.3TRG1" supplierPartNumbers={{jlcpcb:["C51118"]}} footprint="sot23_5" pinLabels={{pin1:"VIN",pin2:"GND",pin3:"EN",pin4:"NC",pin5:"VOUT"}} noConnect={["NC"]}/>
    <chip name="U_LOAD" manufacturerPartNumber="TPS22919DCKR" supplierPartNumbers={{jlcpcb:["C2149796"]}} footprint="sot363" pinLabels={{pin1:"IN",pin2:"GND",pin3:"ON",pin4:"NC",pin5:"QOD",pin6:"OUT"}} noConnect={["NC","QOD"]}/>
    <chip name="U_MUX" manufacturerPartNumber="TMUX1208PWR" supplierPartNumbers={{jlcpcb:["C494728"]}} footprint="tssop16_p0.65mm" pinLabels={{pin1:"A0",pin2:"EN",pin3:"NC",pin4:"S1",pin5:"S2",pin6:"S3",pin7:"S4",pin8:"D",pin9:"S8",pin10:"S7",pin11:"S6",pin12:"S5",pin13:"VDD",pin14:"GND",pin15:"A2",pin16:"A1"}} noConnect={["NC"]}/>
    <HallKey name="U_H0" pcbX={-8.5} pcbY={8.5}/><HallKey name="U_H1" pcbX={8.5} pcbY={8.5}/><HallKey name="U_H2" pcbX={-8.5} pcbY={-8.5}/><HallKey name="U_H3" pcbX={8.5} pcbY={-8.5}/>
    <R name="R_CC1" value="5.1k"/><R name="R_CC2" value="5.1k"/><R name="R_USB_DP" value="27"/><R name="R_USB_DM" value="27"/><R name="R_QSPI_SS" value="1k"/><R name="R_ADC_TOP" value="6.8k"/><R name="R_ADC_BOTTOM" value="10k"/><C name="C_ADC" value="1nF"/><R name="R_XOUT" value="1k"/><C name="C_XIN" value="15pF" footprint="0402"/><C name="C_XOUT" value="15pF" footprint="0402"/>
    {Array.from({length:9},(_,i)=><C key={i} name={`C_MCU_HF${i+1}`} value="100nF" footprint="0402"/>)}<C name="C_VREG_IN" value="1uF" footprint="0402"/><C name="C_VREG_OUT" value="1uF" footprint="0402"/><C name="C_MCU_BULK" value="10uF" footprint="0805"/>
    <C name="C_LDO_IN" value="1uF"/><C name="C_LDO_OUT" value="1uF"/><C name="C_LOAD_IN" value="1uF"/><C name="C_LOAD_OUT" value="1uF"/><C name="C_FLASH" value="100nF" footprint="0402"/><C name="C_MUX" value="100nF"/>{[0,1,2,3].map(i=><C key={i} name={`C_HALL${i}`} value="100nF"/>)}
    <led name="D_POWER" color="green" footprint="0603"/><R name="R_POWER_LED" value="1.5k"/><led name="D_STATUS" color="amber" footprint="0603"/><R name="R_STATUS_LED" value="1.5k"/>
    <pushbutton name="SW_BOOT" footprint="smdpushbutton"/><pushbutton name="SW_RUN" footprint="smdpushbutton"/>
    {["VBUS","3V3","HALL_5V","H0_RAW","H1_RAW","H2_RAW","H3_RAW","MUX_D","ADC_SENSE","GND","SWDIO","SWCLK","RUN","MUX_S5","MUX_S6","MUX_S7","MUX_S8"].map(x=><TP key={x} name={x}/>)}
    {traces.map(([name,from,to])=><T key={name} name={name} from={from} to={to}/>)}
    <T name="USB_VBUS_A4_B9" from=".J_USB > .A4_B9" to="net.VBUS"/><T name="USB_VBUS_A9_B4" from=".J_USB > .A9_B4" to="net.VBUS"/><T name="USB_GND_A1_B12" from=".J_USB > .A1_B12" to="net.GND"/><T name="USB_GND_A12_B1" from=".J_USB > .A12_B1" to="net.GND"/><T name="USB_SHIELD" from=".J_USB > .SHIELD" to="net.USB_SHIELD"/>
    <T name="USB_A6_DP" from=".J_USB > .A6" to="net.USB_DP_CONN"/><T name="USB_B6_DP" from=".J_USB > .B6" to="net.USB_DP_CONN"/><T name="USB_A7_DM" from=".J_USB > .A7" to="net.USB_DM_CONN"/><T name="USB_B7_DM" from=".J_USB > .B7" to="net.USB_DM_CONN"/>
    <T name="CC1_R" from=".J_USB > .A5" to=".R_CC1 > .pin1"/><T name="CC1_G" from=".R_CC1 > .pin2" to="net.GND"/><T name="CC2_R" from=".J_USB > .B5" to=".R_CC2 > .pin1"/><T name="CC2_G" from=".R_CC2 > .pin2" to="net.GND"/>
    <T name="ESD_DP_IN" from=".U_ESD > .IO1_1" to="net.USB_DP_CONN"/><T name="ESD_DP_OUT" from=".U_ESD > .IO1_2" to="net.USB_DP_ESD"/><T name="ESD_DM_IN" from=".U_ESD > .IO2_1" to="net.USB_DM_CONN"/><T name="ESD_DM_OUT" from=".U_ESD > .IO2_2" to="net.USB_DM_ESD"/><T name="ESD_VBUS" from=".U_ESD > .VBUS" to="net.VBUS"/><T name="ESD_GND" from=".U_ESD > .GND" to="net.GND"/>
    <T name="DP_R_IN" from=".R_USB_DP > .pin1" to="net.USB_DP_ESD"/><T name="DP_R_OUT" from=".R_USB_DP > .pin2" to="net.USB_DP"/><T name="DM_R_IN" from=".R_USB_DM > .pin1" to="net.USB_DM_ESD"/><T name="DM_R_OUT" from=".R_USB_DM > .pin2" to="net.USB_DM"/>
    <T name="LDO_IN" from=".U_LDO > .VIN" to="net.VBUS"/><T name="LDO_EN" from=".U_LDO > .EN" to="net.VBUS"/><T name="LDO_OUT" from=".U_LDO > .VOUT" to="net.V3V3"/><T name="LDO_GND" from=".U_LDO > .GND" to="net.GND"/>
    <T name="LOAD_IN" from=".U_LOAD > .IN" to="net.VBUS"/><T name="LOAD_OUT" from=".U_LOAD > .OUT" to="net.HALL_5V"/><T name="LOAD_ON" from=".U_LOAD > .ON" to="net.HALL_PWR_EN"/><T name="LOAD_GND" from=".U_LOAD > .GND" to="net.GND"/>
    <T name="ADC_TOP_IN" from=".R_ADC_TOP > .pin1" to="net.MUX_D"/><T name="ADC_TOP_OUT" from=".R_ADC_TOP > .pin2" to="net.ADC_SENSE"/><T name="ADC_BOTTOM" from=".R_ADC_BOTTOM > .pin1" to="net.ADC_SENSE"/><T name="ADC_BOTTOM_G" from=".R_ADC_BOTTOM > .pin2" to="net.GND"/><T name="ADC_CAP" from=".C_ADC > .pin1" to="net.ADC_SENSE"/><T name="ADC_CAP_G" from=".C_ADC > .pin2" to="net.GND"/>
    <T name="QSPI_SS_R_MCU" from=".R_QSPI_SS > .pin1" to="net.QSPI_SS_MCU"/><T name="QSPI_SS_R_FLASH" from=".R_QSPI_SS > .pin2" to="net.QSPI_SS_FLASH"/><T name="FLASH_CS" from=".U_FLASH > .CS" to="net.QSPI_SS_FLASH"/><T name="BOOTSEL" from=".SW_BOOT > .pin1" to="net.QSPI_SS_FLASH"/><T name="BOOTSEL_G" from=".SW_BOOT > .pin2" to="net.GND"/>
    <T name="FLASH_VCC" from=".U_FLASH > .VCC" to="net.V3V3"/><T name="FLASH_GND" from=".U_FLASH > .GND" to="net.GND"/>{["QSPI_SD0","QSPI_SD1","QSPI_SD2","QSPI_SD3","QSPI_SCLK"].map(x=><T key={x} name={`FLASH_${x}`} from={`.U_FLASH > .${x}`} to={`net.${x}`}/>)}
    <T name="Y_XIN" from=".Y1 > .XIN" to="net.XIN"/><T name="Y_XOUT" from=".Y1 > .XOUT" to="net.XOUT_XTAL"/><T name="XOUT_R1" from=".R_XOUT > .pin1" to="net.XOUT_XTAL"/><T name="XOUT_R2" from=".R_XOUT > .pin2" to="net.XOUT"/><T name="CXIN" from=".C_XIN > .pin1" to="net.XIN"/><T name="CXING" from=".C_XIN > .pin2" to="net.GND"/><T name="CXOUT" from=".C_XOUT > .pin1" to="net.XOUT_XTAL"/><T name="CXOUTG" from=".C_XOUT > .pin2" to="net.GND"/>
    {[["C_LDO_IN","VBUS"],["C_LDO_OUT","V3V3"],["C_LOAD_IN","VBUS"],["C_LOAD_OUT","HALL_5V"],["C_FLASH","V3V3"],["C_MUX","HALL_5V"],["C_VREG_IN","V3V3"],["C_VREG_OUT","V1V1"],...[0,1,2,3].map(i=>[`C_HALL${i}`,"HALL_5V"])] .flatMap(([c,rail])=>[<T key={`${c}p`} name={`${c}_P`} from={`.${c} > .pin1`} to={`net.${rail}`}/>,<T key={`${c}g`} name={`${c}_G`} from={`.${c} > .pin2`} to="net.GND"/>])}
    {[["C_MCU_HF1","V3V3"],["C_MCU_HF2","V3V3"],["C_MCU_HF3","V3V3"],["C_MCU_HF4","V3V3"],["C_MCU_HF5","V3V3"],["C_MCU_HF6","V3V3"],["C_MCU_HF7","V3V3"],["C_MCU_HF8","V3V3"],["C_MCU_HF9","V1V1"],["C_MCU_BULK","V3V3"]].flatMap(([c,rail])=>[<T key={`${c}p`} name={`${c}_P`} from={`.${c} > .pin1`} to={`net.${rail}`}/>,<T key={`${c}g`} name={`${c}_G`} from={`.${c} > .pin2`} to="net.GND"/>])}
    {["VBUS","HALL_5V","H0_RAW","H1_RAW","H2_RAW","H3_RAW","MUX_D","ADC_SENSE","GND","SWDIO","SWCLK","RUN","MUX_S5","MUX_S6","MUX_S7","MUX_S8"].map(x=><T key={`tp${x}`} name={`TP_${x}`} from={`.TP_${x} > .pin1`} to={`net.${x}`}/>)}<T name="TP_3V3" from=".TP_3V3 > .pin1" to="net.V3V3"/>
    <T name="RUN_SW" from=".SW_RUN > .pin1" to="net.RUN"/><T name="RUN_SW_G" from=".SW_RUN > .pin2" to="net.GND"/>
    <T name="POWER_LED_A" from=".D_POWER > .anode" to="net.V3V3"/><T name="POWER_LED_R" from=".D_POWER > .cathode" to=".R_POWER_LED > .pin1"/><T name="POWER_LED_G" from=".R_POWER_LED > .pin2" to="net.GND"/>
    <T name="STATUS_LED_A" from=".D_STATUS > .anode" to="net.STATUS_LED"/><T name="STATUS_LED_R" from=".D_STATUS > .cathode" to=".R_STATUS_LED > .pin1"/><T name="STATUS_LED_G" from=".R_STATUS_LED > .pin2" to="net.GND"/>
    <T name="Y_GND1" from=".Y1 > .GND1" to="net.GND"/><T name="Y_GND2" from=".Y1 > .GND2" to="net.GND"/>
  </board>
}
export default M1FourKeyElectrical
