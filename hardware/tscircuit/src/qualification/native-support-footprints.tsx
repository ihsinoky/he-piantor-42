import React from "react"

// Raspberry Pi RP2040 datasheet, 2025-02-20 build, Figure 167 p608.
// 0.20 x 0.875 lands, 0.40 pitch, 7.75 outside / 6.00 inside span;
// centers at +/-3.4375. Native EP is explicitly port 57, 3.20 square.
export const rp2040Footprint = <footprint>
  {Array.from({length:56},(_,i)=>{
    const side=Math.floor(i/14), k=i%14, v=2.6-k*.4
    const x=side===0?-3.4375:side===1?-v:side===2?3.4375:v
    const y=side===0?v:side===1?-3.4375:side===2?-v:3.4375
    return <smtpad key={i} shape="rect" layer="top" pcbX={x} pcbY={y}
      width={side%2===0?.875:.2} height={side%2===0?.2:.875} portHints={[`pin${i+1}`]}/>
  })}
  <smtpad shape="rect" layer="top" pcbX={0} pcbY={0} width={3.2} height={3.2} portHints={["pin57"]}/>
</footprint>

// Qualification-owned transcription of the accepted native fixture geometry.
// The frozen fixture is read-only; no importer or generated data is consumed.
/* TYPE-C-31-M-12 manufacturer recommended land pattern (C165948 drawing).
 * Contacts use their USB Type-C names as pad hints. The two wide power/ground
 * lands each serve the paired receptacle contacts shown in the drawing.
 * Four plated shell stakes and two locating NPTHs are retained separately. */
const usbContact = (id: string, x: number, width = 0.3) =>
  <smtpad key={id} shape="rect" pcbX={x} pcbY={-4.045} width={width} height={1.45} layer="top" portHints={[id]} />
export const usbFootprint = <footprint>
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
export const flashFootprint = <footprint>
  {[[1,-1.4478,-.750001],[2,-1.4478,-.25],[3,-1.4478,.25],[4,-1.4478,.750001],[5,1.4478,.750001],[6,1.4478,.25],[7,1.4478,-.25],[8,1.4478,-.750001]].map(([pin,x,y])=><smtpad key={pin} shape="rect" pcbX={x} pcbY={y} width={.8128} height={.254} layer="top" portHints={[`pin${pin}`]}/>)}
  <smtpad shape="rect" pcbX={0} pcbY={0} width={.254} height={1.651} layer="top" portHints={["EP"]}/>
</footprint>

/* Abracon ABM8 recommended land pattern, bottom view: 1 2 / 4 3. */
export const crystalFootprint = <footprint>
  <smtpad shape="rect" pcbX={-1.15} pcbY={0.875} width={1.3} height={1.05} layer="top" portHints={["pin1"]}/>
  <smtpad shape="rect" pcbX={1.15} pcbY={0.875} width={1.3} height={1.05} layer="top" portHints={["pin2"]}/>
  <smtpad shape="rect" pcbX={1.15} pcbY={-0.875} width={1.3} height={1.05} layer="top" portHints={["pin3"]}/>
  <smtpad shape="rect" pcbX={-1.15} pcbY={-0.875} width={1.3} height={1.05} layer="top" portHints={["pin4"]}/>
</footprint>
