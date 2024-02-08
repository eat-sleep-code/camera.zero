# Camera Zero

Combining Camera Zero with an Arducam 12MP camera, a Raspberry Pi Zero WH, a PiMoRoNi trackball breakout, and an Adafruit 16-LED NeoPixel ring will result in a neat little screenless camera that can be controlled with your thumb.

  ![Camera](https://github.com/eat-sleep-code/camera.zero/raw/master/images/Camera%20Zero%20-%20LED%20-%20Bright%20White.jpg)

---
## Getting Started

- Use [Raspberry Pi Imager](https://www.raspberrypi.com/software) to install Raspberry Pi OS Lite *(Bookworm)* on a microSD card
- Use [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to:
  - Set the Memory Split value to a value of at least 192MB
  - Enable the I2C interface
  - Set up your WiFi connection
- Connect the camera to your Raspberry Pi


## Installation

Installation of the program, any software prerequisites, as well as DNG support can be completed with the following two-line install script.

```
wget -q https://raw.githubusercontent.com/eat-sleep-code/camera.zero/master/install-camera.sh -O ~/install-camera.sh
sudo chmod +x ~/install-camera.sh && ~/install-camera.sh
```

---

## Usage
```
camera.zero <options>
```

### Options

+ _--rotate_ : Rotate the camera in 90&deg; increments     *(default: 0)*
+ _--exifFStop_ : Set the numeric F-Stop value in the image EXIF data *(default: Not specified)*
+ _--exifFocalLength_ : Set the numeric Focal Length value (mm) in the image EXIF data *(default: Not specified)*
+ _--exifFocalLengthEquivalent_ : Set the numeric 35mm Focal Length value (mm) in the image EXIF data *(default: Not specified)*


### Example
```bash
camera.zero --rotate 180 --exifFStop 2.2 --exifFocalLength 2.75 --exifFocalLengthEquivalent 16
```

> [!TIP]
> The EXIF data shown above is completely optional but may prove useful when using captured images with third-party applications such as photogrammetry software.


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
        - Press for 5 - 9 seconds to exit the program and launch [Camera Remote](https://github.com/eat-sleep-code/camera.remote) (if installed)
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

```bash
# Camera Settings 
awb_auto_is_greyworld=1
```

> [!NOTE]
> While IR cameras utilize "invisible" (outside the spectrum of the human eye) light, they can not magically see in the dark.   You will need to illuminate night scenes with one or more IR lights to take advantage of an Infrared Camera.

---

> [!TIP]
> If you are using a Raspberry Pi with 1GB &ndash; or less &ndash; of memory, you may wish to increase your SWAP file to match your memory size as outlined in this [third-party guide](https://pimylifeup.com/raspberry-pi-swap-file/).

---

> [!IMPORTANT]
> *This application was developed using a  Arducam 12MP camera and a Raspberry Pi Zero WH board.   This application should also work without issue with Raspberry Pi Zero 2W boards.   This application should also work with Raspberry Pi 12MP (2023) and Raspberry Pi HQ (2020) cameras.   Issues may arise if you are using either third party or older hardware.*

