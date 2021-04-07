# Camera Zero

Combining Camera Zero with a Raspberry Pi HQ camera, a Raspberry Pi Zero WH, a PiMoRoNi trackball breakout, and an Adafruit 16-LED NeoPixel ring will result in a neat little screenless camera that can be controlled with your thumb.

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
     - Exit
        - Press for 5 to 9 seconds to exit the program and launch [Camera Remote](https://github.com/eat-sleep-code/camera.zero) (if installed)
        - Press for 10+ seconds to exit the program 
- Scroll up and down to change the values of the current setting
- Press the trackball to trigger the shutter

### Web Controls
If you need to control your camera via a web-based interface, please see [Camera Remote](https://github.com/eat-sleep-code/camera.remote).

---

## Disabling Autostart

To disable autostart of the program, execute the following command:

```
sudo mv /etc/service/camera.zero/run /etc/service/camera.zero/run.disabled
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
