import React from "react"

/** PO-approved BM14B-GHS-TBT.pdf, KRD-32980-5 R0, 2024-03-13.
 * SHA256 1707350a5780a7c8a7b95e67430cc0b8ddda36ebe1a6fb04d6ab4cfc536776d1.
 * Mounting-surface view; +y up. Origin is midpoint of signal-land centers.
 * Pin 1 is rightmost. Reinforcement lands are mechanical NCs, not contacts.
 * This is native project-owned geometry; no KiCad input or generated source.
 */
export const JstGh14 = ({ name = "J_WING", pcbX = 0, pcbY = 0 }:
  { name?: string; pcbX?: number; pcbY?: number }) => (
  <chip name={name} pcbX={pcbX} pcbY={pcbY}
    manufacturerPartNumber="BM14B-GHS-TBT(LF)(SN)"
    supplierPartNumbers={{ jlcpcb: ["C265384"] }}
    pinLabels={{ ...Object.fromEntries(Array.from({ length: 14 }, (_, i) =>
      [`pin${i + 1}`, `P${i + 1}`])), pin15: "MP" }} noConnect={["MP"]}
    footprint={<footprint>
      {Array.from({ length: 14 }, (_, i) => <smtpad key={i}
        shape="rect" layer="top" width={0.6} height={1.7}
        pcbX={8.125 - 1.25 * i} pcbY={0} portHints={[`pin${i + 1}`]} />)}
      {[-9.975, 9.975].map(x => <smtpad key={x} shape="rect" layer="top"
        width={1} height={2.8} pcbX={x} pcbY={-3.35} portHints={["MP"]} />)}
      <silkscreentext text="1" pcbX={8.125} pcbY={1.7} fontSize={0.8} />
      <silkscreenrect pcbX={0} pcbY={-2.325} width={20.75} height={4.25} strokeWidth={0.1} />
    </footprint>} />
)
