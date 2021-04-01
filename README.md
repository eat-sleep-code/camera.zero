# Camera Zero

Combining this program with a Raspberry Pi HQ camera, a Raspberry Pi Zero WH, a PiMoRoNi trackball breakout, and an Adafruit 16-LED NeoPixel ring will result in a neat little screenless camera that can be controlled with your thumb.

---
## Getting Started

- Use [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to:
  - Set the Memory Split value to a value of at least 192MB
  - Enable the CSI camera interface
  - Enable the I2C interface
  - Set up your WiFi connection
- Connect the Raspberry Pi HQ Camera to your Raspberry Pi


## Installation

Installation of the program, any software prerequisites, as well as DNG support can be completed with the following two-line install script.

```
wget -q https://raw.githubusercontent.com/eat-sleep-code/camera.zero/master/install-camera.sh -O ~/install-camera.sh
sudo chmod +x ~/install-camera.sh && ~/install-camera.sh
```

---

## Usage
```
camera.zero
```

### Trackball Controls
- Scroll left and right to change setting selection:
     - Capture Photo
     - Capture Video
     - Shutter Speed
     - ISO Setting
     - Exposure Compensation
     - Bracketing
     - Scene Light: Red Light Level
     - Scene Light: Green Light Level
     - Scene Light: Blue Light Level
     - Scene Light Natural White Level
- Scroll up and down to change the values of the current setting
- Press the trackball to trigger the shutter

### Web Controls
If you need to control your camera via a web-based interface, please see [camera.remote](https://github.com/eat-sleep-code/camera.remote).

---

## Autostart at Desktop Login

To autostart the program as soon as the Raspberry Pi OS desktop starts, execute the following command:

```
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Add the following line to the end of the file and then save the file:

```
@lxterminal --geometry=1x1 -e sudo python3 /home/pi/camera.zero/camera.py
```
---

## Infrared Cameras
If you are using an infrared (IR) camera, you will need to modify the Auto White Balance (AWB) mode at boot time.

This can be achieved by executing `sudo nano /boot/config.txt` and adding the following lines.

```
# Camera Settings 
awb_auto_is_greyworld=1
```

Also note, that while IR cameras utilize "invisible" (outside the spectrum of the human eye) light, they can not magically see in the dark.   You will need to illuminate night scenes with one or more [IR emitting LEDs](https://www.adafruit.com/product/387) to take advantage of an Infrared Camera.

---

:information_source: *This application was developed using a Raspberry Pi HQ (2020) camera and Raspberry Pi Zero WH and Raspberry Pi 4B boards.   Issues may arise if you are using either third party or older hardware.*
