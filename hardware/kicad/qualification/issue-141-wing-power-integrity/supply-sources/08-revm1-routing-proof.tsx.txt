import React from "react"
import { HallKey } from "../components/HallKey"
import { JstGh14 } from "./JstGh14"
import { usbFootprint, flashFootprint, crystalFootprint, rp2040Footprint } from "./native-support-footprints"

/** Disposable representative routing qualification. NON-PRODUCT.
 * Not final Rev.M1 geometry. Two separate boards; accepted 100mm 1:1 harness
 * is an external interconnect, never an on-board Hall-to-ADC shortcut.
 * Source coordinates and ordinary source-net traces are the sole authority.
 */
export const interfaceNets = ["HALL_5V", "GND", "MUX_A0", "GND", "MUX_A1",
  "MUX_A2", "WING_EN", "GND", "MUX_OUT_A", "GND", "MUX_OUT_B", "GND", "MUX_OUT_C", "GND"]
export type Strategy = 1 | 2 | 3
type Link = [string, string, string]
const linksTo = (name: string, pairs: [string, string][]): Link[] =>
  pairs.map(([pin, net]) => [name, pin, net])
const powerPins = [1, 10, 22, 33, 42, 43, 44, 48, 49]
const mcuFunctions: Record<number, string> = {4:"MUX_A0",5:"MUX_A1",6:"MUX_A2",7:"WING_EN",
  9:"HALL_PWR_EN",19:"TESTEN",20:"XIN",21:"XOUT",23:"DVDD23",24:"SWCLK",25:"SWDIO",
  26:"RUN",38:"ADC_A",39:"ADC_B",40:"ADC_C",45:"VREG_OUT",46:"USB_DM",47:"USB_DP",
  50:"DVDD50",51:"QSPI_SD3",52:"QSPI_SCLK",53:"QSPI_SD0",54:"QSPI_SD2",
  55:"QSPI_SD1",56:"QSPI_SS",57:"GND_EP"}
const mcuLabels = Object.fromEntries(Array.from({length:57}, (_, i) => {
  const n=i+1; return [`pin${n}`, powerPins.includes(n) ? `PWR${n}` : mcuFunctions[n] ?? `UNUSED${n}`]
}))
const mcuNC = Array.from({length:56}, (_,i)=>i+1).filter(n=>!powerPins.includes(n)&&!mcuFunctions[n]).map(n=>`UNUSED${n}`)
const muxLabels = {pin1:"A0",pin2:"EN",pin3:"NC",pin4:"S1",pin5:"S2",pin6:"S3",
  pin7:"S4",pin8:"D",pin9:"S8",pin10:"S7",pin11:"S6",pin12:"S5",pin13:"VDD",
  pin14:"GND",pin15:"A2",pin16:"A1"}
const boardRules = { layers:2 as const, thickness:"1.2mm", autorouter:"default",
  minTraceWidth:"0.2mm", defaultTraceWidth:"0.2mm", minTraceToPadEdgeClearance:"0.2mm",
  minViaHoleDiameter:"0.3mm", minViaPadDiameter:"0.6mm", schematicDisabled:true }

const Wiring = ({links}:{links:Link[]}) => <>
  {[...new Set(links.map(x=>x[2]))].map(n=><net key={n} name={n}
    isPowerNet={["VBUS","V3V3","V1V1","HALL_5V"].includes(n)} isGroundNet={n==="GND"}/>)}
  {links.map(([ref,pin,net],i)=><trace key={i} name={`${ref}_${pin}`}
    from={`.${ref} > .${pin}`} to={`net.${net}`}/>)}
</>

export const RepresentativeMain = ({strategy=1}:{strategy?:Strategy}) => {
  const links: Link[] = []
  const wire=(ref:string,pin:string,net:string)=>links.push([ref,pin,net])
  const passives: React.ReactNode[]=[]
  const resistor=(name:string,value:string,x:number,y:number,a:string,b:string,rotation=0)=>{
    passives.push(<resistor key={name} name={name} resistance={value} footprint="0603" pcbX={x} pcbY={y} pcbRotation={rotation}/>);
    wire(name,"pin1",a);wire(name,"pin2",b)
  }
  const capacitor=(name:string,value:string,x:number,y:number,rail:string,footprint="0402",rotation=0)=>{
    passives.push(<capacitor key={name} name={name} capacitance={value} footprint={footprint} pcbX={x} pcbY={y} pcbRotation={rotation}/>);
    wire(name,"pin1",rail);wire(name,"pin2","GND")
  }
  for(const n of powerPins) wire("U_MCU",`PWR${n}`,"V3V3")
  for(const [pin,net] of Object.entries(mcuFunctions)) wire("U_MCU",net,
    ["DVDD23","DVDD50","VREG_OUT"].includes(net)?"V1V1":
      ["TESTEN","GND_EP"].includes(net)?"GND":net==="QSPI_SS"?"QSPI_SS_MCU":net)
  interfaceNets.forEach((n,i)=>wire("J_WING",`P${i+1}`,n))
  links.push(...linksTo("J_USB",[["A1_B12","GND"],["A12_B1","GND"],["SHIELD","GND"],
    ["A4_B9","VBUS"],["A9_B4","VBUS"],["A6","USB_DP_CONN"],["B6","USB_DP_CONN"],
    ["A7","USB_DM_CONN"],["B7","USB_DM_CONN"],["A5","CC1"],["B5","CC2"]]))
  links.push(...linksTo("U_ESD",[["IO1_1","USB_DP_CONN"],["IO1_2","USB_DP_ESD"],
    ["IO2_1","USB_DM_CONN"],["IO2_2","USB_DM_ESD"],["GND","GND"],["VBUS","VBUS"]]))
  links.push(...linksTo("U_LDO",[["VIN","VBUS"],["EN","VBUS"],["VOUT","V3V3"],["GND","GND"]]))
  links.push(...linksTo("U_LOAD",[["IN","VBUS"],["ON","HALL_PWR_EN"],["OUT","HALL_5V"],["GND","GND"]]))
  links.push(...linksTo("U_FLASH",[["CS","QSPI_SS_FLASH"],["VCC","V3V3"],["GND","GND"],
    ...["QSPI_SD0","QSPI_SD1","QSPI_SD2","QSPI_SD3","QSPI_SCLK"].map(n=>[n,n] as [string,string])]))
  links.push(...linksTo("Y1",[["XIN","XIN"],["XOUT","XOUT_XTAL"],["GND1","GND"],["GND2","GND"]]))
  // Strategies retain every component and net. Attempt 3 partitions the
  // QSPI placement, raises supported routing effort, and explicitly bonds
  // duplicated physical ground lands that the router otherwise treats as
  // internally connected. These are short local bonds, not routed signals.
  const flashX=strategy===3?5:0, flashY=strategy===3?9:11
  const adcY=strategy===1?-9:-11
  resistor("R_CC1","5.1k",-21,13,"CC1","GND",90)
  resistor("R_CC2","5.1k",-9,16,"CC2","GND",90)
  resistor("R_USB_DP","27",-9,8,"USB_DP_ESD","USB_DP")
  resistor("R_USB_DM","27",-9,5,"USB_DM_ESD","USB_DM")
  resistor("R_QSPI_SS","1k",flashX+4,flashY,"QSPI_SS_MCU","QSPI_SS_FLASH",90)
  resistor("R_WING_PD","100k",-7,-12,"WING_EN","GND")
  resistor("R_HALL_PD","100k",-17,-10,"HALL_PWR_EN","GND")
  resistor("R_RUN","10k",-7,-6,"V3V3","RUN",90)
  resistor("R_XOUT","1k",-12,-3,"XOUT_XTAL","XOUT",90)
  capacitor("C_XIN","15pF",-15,-6,"XIN")
  capacitor("C_XOUT","15pF",-15,0,"XOUT_XTAL")
  for(const [i,xy] of [[0,[-6,4]],[1,[-6,1]],[2,[-6,-2]],[3,[0,-6]],
    [4,[4,-6]],[5,[6,-3]],[6,[6,0]],[7,[6,3]]] as [number,number[]][])
    capacitor(`C_MCU_HF${i+1}`,"100nF",xy[0],xy[1],"V3V3", "0402",i>4?90:0)
  capacitor("C_MCU_HF9","100nF",3,6,"V1V1")
  capacitor("C_VREG_IN","1uF",9,3,"V3V3")
  capacitor("C_VREG_OUT","1uF",9,0,"V1V1")
  capacitor("C_MCU_BULK","10uF",9,6,"V3V3","0805")
  capacitor("C_FLASH","100nF",flashX-4,flashY,"V3V3")
  capacitor("C_LDO_IN","1uF",-20,3,"VBUS","0603")
  capacitor("C_LDO_OUT","1uF",-16,3,"V3V3","0603")
  capacitor("C_LOAD_IN","1uF",-20,-4,"VBUS","0603")
  capacitor("C_LOAD_OUT","1uF",strategy===1?-16:-12,strategy===1?-4:-7,"HALL_5V","0603")
  for(const [i,ch] of ["A","B","C"].entries()) {
    const x=11+i*4
    resistor(`R_ADC_${ch}_TOP`,"6.8k",x,adcY,`MUX_OUT_${ch}`,`ADC_${ch}`,90)
    resistor(`R_ADC_${ch}_BOTTOM`,"10k",x,adcY+4,`ADC_${ch}`,"GND",90)
    capacitor(`C_ADC_${ch}`,"1nF",x,adcY+7,`ADC_${ch}`,"0402",90)
  }
  const tps: React.ReactNode[]=[]
  for(const [i,n] of ["SWDIO","SWCLK","RUN","QSPI_SS_FLASH"].entries()) {
    tps.push(<testpoint key={n} name={`TP_${n}`} footprintVariant="pad" padShape="circle"
      padDiameter="1.2mm" pcbX={(strategy===1?-8:-12)+i*3} pcbY={-18}/>); wire(`TP_${n}`,"pin1",n)
  }
  return <board width={48} height={44} {...boardRules} autorouterEffortLevel={strategy===3?"5x":"1x"}>
    <chip name="U_MCU" pcbX={0} pcbY={0} manufacturerPartNumber="RP2040"
      footprint={strategy===1?"qfn56_w7_h7_p0.4mm_thermalpad":rp2040Footprint} pinLabels={mcuLabels} noConnect={mcuNC}/>
    <chip name="J_USB" pcbX={-15} pcbY={19} manufacturerPartNumber="TYPE-C-31-M-12"
      footprint={usbFootprint} pinLabels={{pin1:"A1_B12",pin2:"A4_B9",pin3:"A5",pin4:"A6",pin5:"A7",pin6:"A8",pin7:"B8",pin8:"B7",pin9:"B6",pin10:"B5",pin11:"A9_B4",pin12:"A12_B1",pin13:"SHIELD"}} noConnect={["A8","B8"]}/>
    <chip name="U_ESD" pcbX={-15} pcbY={8} manufacturerPartNumber="USBLC6-2SC6" footprint="sot23_6"
      pinLabels={{pin1:"IO1_1",pin2:"GND",pin3:"IO2_1",pin4:"IO2_2",pin5:"VBUS",pin6:"IO1_2"}}/>
    <chip name="U_FLASH" pcbX={flashX} pcbY={flashY} manufacturerPartNumber="W25Q16JVUXIQ" footprint={flashFootprint}
      pinLabels={{pin1:"CS",pin2:"QSPI_SD1",pin3:"QSPI_SD2",pin4:"GND",pin5:"QSPI_SD0",pin6:"QSPI_SCLK",pin7:"QSPI_SD3",pin8:"VCC",pin9:"EP"}} noConnect={["EP"]}/>
    <chip name="Y1" pcbX={-15} pcbY={-3} manufacturerPartNumber="ABM8-272-T3" footprint={crystalFootprint}
      pinLabels={{pin1:"XIN",pin2:"GND1",pin3:"XOUT",pin4:"GND2"}}/>
    <chip name="U_LDO" pcbX={-18} pcbY={0} manufacturerPartNumber="AP2112K-3.3TRG1" footprint="sot23_5"
      pinLabels={{pin1:"VIN",pin2:"GND",pin3:"EN",pin4:"NC",pin5:"VOUT"}} noConnect={["NC"]}/>
    <chip name="U_LOAD" pcbX={-18} pcbY={-7} manufacturerPartNumber="TPS22919DCKR" footprint="sot363"
      pinLabels={{pin1:"IN",pin2:"GND",pin3:"ON",pin4:"NC",pin5:"QOD",pin6:"OUT"}} noConnect={["NC","QOD"]}/>
    <JstGh14 pcbX={10} pcbY={-16}/>
    {passives}{tps}<Wiring links={links}/>
    {/* Installed pcbPath transforms numeric points in the anchor component
        frame, then appends the resolved endpoint. Close the bond path along
        its existing sides so that endpoint attachment adds no cross-contact
        segment. Distinct physical bond length is 17.00 mm. */}
    {strategy===3&&<trace name="USB_SHELL_BOND" from=".J_USB > .SHIELD" to="net.GND" thickness="0.2mm"
      pcbPath={[{x:-4.32,y:-3.13},{x:-4.32,y:1.05},{x:4.32,y:1.05},{x:4.32,y:-3.13},
        {x:4.32,y:1.05},{x:-4.32,y:1.05},{x:-4.32,y:-3.13}]}/>}
  </board>
}

export const RepresentativeWing = ({strategy=1}:{strategy?:Strategy}) => {
  const links: Link[]=interfaceNets.map((n,i)=>["J_WING",`P${i+1}`,n])
  const sensors=[[-8.5,8.5],[8.5,8.5],[-8.5,-8.5],[8.5,-8.5]]
  const muxes=[[-14,0],[0,0],[14,0]]
  const keys: React.ReactNode[]=[]
  sensors.forEach(([x,y],i)=>{
    keys.push(<HallKey key={`H${i}`} name={`U_H${i}`} pcbX={x} pcbY={y}/>);
    keys.push(<capacitor key={`C${i}`} name={`C_HALL${i}`} capacitance="100nF" footprint="0603" pcbX={x+3.5} pcbY={y+3}/>);
    links.push(...linksTo(`U_H${i}`,[["VCC","HALL_5V"],["GND","GND"],["OUT",`H${i}_RAW`]]),
      ...linksTo(`C_HALL${i}`,[["pin1","HALL_5V"],["pin2","GND"]]))
  })
  const devices: React.ReactNode[]=[]
  muxes.forEach(([x,y],i)=>{
    const ch=["A","B","C"][i], name=`U_MUX_${ch}`
    const used=i===0?2:1
    // A receives H0/H2, B receives H1, C receives H3 (2/1/1).
    const hallIds=i===0?[0,2]:i===1?[1]:[3]
    const yy=y+(strategy===2?(i===1?-3:2):strategy===3?(i===1?3:0):0)
    devices.push(<chip key={name} name={name} pcbX={x} pcbY={yy} manufacturerPartNumber="TMUX1208PWR"
      footprint="tssop16_p0.65mm" pinLabels={muxLabels}
      noConnect={["NC",...Array.from({length:8-used},(_,j)=>`S${j+used+1}`)]}/>);
    devices.push(<capacitor key={`C_MUX_${ch}`} name={`C_MUX_${ch}`} capacitance="100nF"
      footprint="0603" pcbX={x+4} pcbY={yy-4}/>);
    links.push(...linksTo(name,[["A0","MUX_A0"],["A1","MUX_A1"],["A2","MUX_A2"],
      ["EN","WING_EN"],["VDD","HALL_5V"],["GND","GND"],["D",`MUX_OUT_${ch}`],
      ...hallIds.map((h,j)=>[`S${j+1}`,`H${h}_RAW`] as [string,string])]),
      ...linksTo(`C_MUX_${ch}`,[["pin1","HALL_5V"],["pin2","GND"]]))
  })
  return <board width={44} height={44} {...boardRules} autorouterEffortLevel={strategy===3?"5x":"1x"}>
    <JstGh14 pcbY={18}/>{keys}{devices}<Wiring links={links}/>
    {strategy===3&&sensors.map(([x,y],i)=><trace key={i} name={`HALL_GND_BOND_${i}`}
      from={`.U_H${i} > .GND`} to="net.GND" thickness="0.2mm"
      pcbPath={[{x:.9375,y:0},{x:2.3,y:0}]}/>)}
  </board>
}

export default RepresentativeMain
