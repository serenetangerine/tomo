# tomo -- your digital dinosaur pal

## Requirements
- raspberry pi pico
- ssd1306 OLED screen
- (optional pimoroni pico lipo with battery)
  - currently hard coded -- need to write detections and only use / display if available

## Wiring
Note: SDA and SCL pins are hard coded!!
- ssd1306 GND -> pico GND
- ssd1306 VCC -> pico 5V
- ssd1306 SCL -> pico SCL
  - `GPIO 9`
- ssd1306 SDA -> pico SDA
  - `GPIO 8`

## Dependencies
TODO: provide links
- standard pico micropython installation
- ssd1306 driver
- (optional battery daemon driver)

## Installation
- flash all files (and dependencies) to the pico
- copy `tomo.py` to `main.py` to auto-launch