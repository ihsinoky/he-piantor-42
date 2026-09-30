import React from "react"
import { HallKey } from "./components/HallKey"

/** A deliberately small geometry fixture, not a manufacturing design. */
export const CheckpointABoard = () => (
  <board width={16} height={12} routingDisabled>
    <HallKey />
    <copperpour layer="top" />
    <copperpour layer="bottom" />
  </board>
)
