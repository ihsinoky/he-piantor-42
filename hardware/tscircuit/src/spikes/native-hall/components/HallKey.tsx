import React from "react"

/**
 * Native Checkpoint A representation of the DRV5055 DBZ Hall sensor and the
 * two switch locating holes. Values are deliberately literal: this component
 * has no runtime dependency on the KiCad footprint used as its provenance.
 */
export const HallKey = () => (
  <chip
    name="U1"
    pinLabels={{ pin1: "VCC", pin2: "OUT", pin3: "GND" }}
    footprint={
      <footprint>
        <smtpad
          shape="rect"
          pcbX={-0.9375}
          pcbY={-0.95}
          width={1.475}
          height={0.6}
          layer="top"
          portHints={["1"]}
        />
        <smtpad
          shape="rect"
          pcbX={-0.9375}
          pcbY={0.95}
          width={1.475}
          height={0.6}
          layer="top"
          portHints={["2"]}
        />
        <smtpad
          shape="rect"
          pcbX={0.9375}
          pcbY={0}
          width={1.475}
          height={0.6}
          layer="top"
          portHints={["3"]}
        />
        <platedhole
          shape="circle"
          pcbX={2.3}
          pcbY={0}
          holeDiameter={0.3}
          outerDiameter={0.6}
          portHints={["3"]}
        />
        <hole pcbX={-5.08} pcbY={0} diameter={1.7} />
        <hole pcbX={5.08} pcbY={0} diameter={1.7} />
        <keepout
          shape="rect"
          pcbX={0}
          pcbY={0}
          width={4}
          height={3.6}
          layers={["top"]}
          allowTraces
          allowPlacements
        />
        <keepout
          shape="rect"
          pcbX={0}
          pcbY={0}
          width={4}
          height={3.6}
          layers={["bottom"]}
          allowTraces
          allowPlacements
        />
      </footprint>
    }
  />
)
