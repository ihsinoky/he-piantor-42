import React from "react"
import { HallKey } from "./components/HallKey"

/** A deliberately small geometry fixture, not a manufacturing design. */
export const CheckpointABoard = () => (
  <board width={16} height={12} routingDisabled>
    <HallKey />
    {/* Fixture-only net: this does not connect the Hall sensor for Checkpoint B. */}
    <copperpour name="CHECKPOINT_A_TOP_POUR" connectsTo="net.GND" layer="top" />
    <copperpour
      name="CHECKPOINT_A_BOTTOM_POUR"
      connectsTo="net.GND"
      layer="bottom"
    />
  </board>
)
