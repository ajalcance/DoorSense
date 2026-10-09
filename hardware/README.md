# Hardware

Physical integration is future work. The prototype uses the laptop webcam and
labelled simulated door sensors. No firmware or emulator is implemented here yet.

The planned ESP32 camera supplies images over local Wi-Fi without an internet
uplink; the laptop/local hub performs vision and language inference. Future
firmware must share the documented frame/sensor contracts and be validated on the
actual board. See [physical integration plan](../WORKING_PLAN.md).
