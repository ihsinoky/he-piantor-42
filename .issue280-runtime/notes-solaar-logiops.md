# Source notes: Solaar (pwr-Solaar/Solaar) + logiops (PixlOne/logiops)

Host-side view: the receiver is a USB HID++ 1.0 device; pairing state
lives in the RECEIVER, host software only opens/closes the pairing lock
and reads back what the receiver stored.

## Pairing from the host side (Solaar lib/logitech_receiver/)
- Host opens pairing by writing HID++ 1.0 register RECEIVER_PAIRING
  (0xB2) on the receiver: action 0x01 = open lock (with a timeout
  parameter), 0x02 = close lock, 0x03 = unpair the addressed slot
  (receiver.py Receiver.set_lock / unpair, hidpp10_constants.Registers).
- The receiver notifies the host about lock state and pairing errors
  (notifications.py handle_pairing_lock). PairingError codes
  (hidpp10_constants.py:144-148): 0x01 DEVICE_TIMEOUT, 0x02
  DEVICE_NOT_SUPPORTED, 0x03 TOO_MANY_DEVICES, 0x06 SEQUENCE_TIMEOUT -
  i.e. the receiver itself enforces timeouts on the pairing sequence.
- Per-slot pairing information (device address, WPID, serial, kind,
  name) is stored in the receiver and read back via RECEIVER_INFO
  (0xB5-class) subregisters 0x2N pairing info / 0x3N extended / 0x4N
  device name (hidpp10_constants InfoSubRegisters). Unpairing/erasing
  is a receiver-side operation; nothing is stored host-side.
- Solaar decides a device is "online" by HID++ ping (device.py
  Device.ping); a device that never answers HID++ is shown offline by
  host software. This is a host-software view only: keyboard reports
  reach the OS as plain USB HID reports emitted by the receiver and do
  not transit HID++.

## HID++ essentials for a device (Solaar + logiops)
- HID++ 1.0: register-based, short (10 B) / long (20 B payload) reports;
  over the Unifying RF link these are RF report types 0x10 (short,
  10-byte RF frame) and 0x11 (long, 22-byte RF frame) - frame lengths
  cross-checked in LOGITacker logitacker_devices.c classification.
- HID++ 2.0 feature ids (logiops src/logid/backend/hidpp20/
  feature_defs.h): ROOT 0x0000, FEATURE_SET 0x0001, DEVICE_NAME 0x0005,
  BATTERY_STATUS 0x1000, BATTERY_VOLTAGE 0x1001. A device is probed for
  its protocol version (HID++ 1.0 vs 2.0) by the host through the
  receiver; real Unifying keyboards of the C-U0008 era are HID++ 1.0
  devices or early 2.0 - which one a clone must speak depends on what
  the receiver/host asks, see open items.
- LED state (Caps/Num/Scroll) is delivered receiver->device as RF
  report type 0x0e (10-byte frame) - a keyboard implementation must at
  least tolerate receiving it.

## What Solaar does NOT show
- Solaar never sees the RF pairing exchange (it happens between device
  and receiver below USB). All RF pairing facts come from LOGITacker.
- Bolt pairing (registers 0xC0/0xC1, passkey entry) is a different,
  newer protocol generation and is out of scope for Unifying; Solaar
  code paths for Bolt must not be conflated with Unifying pairing.
