# This script will install the camera, dng support, and any required prerequisites.
cd ~
echo -e ''
echo -e '\033[32mCamera Zero [Installation Script] \033[0m'
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e ''
echo -e '\033[93mUpdating package repositories... \033[0m'
sudo apt update

echo ''
echo -e '\033[93mInstalling prerequisites... \033[0m'
sudo apt install -y git python3 python3-pip python3-picamera2 libopenblas-dev libatlas-base-dev daemontools daemontools-run ffmpeg
sudo pip3 install piexif RPi.GPIO trackball adafruit-circuitpython-neopixel PiDNG numpy --force --break-system-packages


echo ''
echo -e '\033[93mProvisioning logs... \033[0m'
sudo mkdir -p /home/pi/logs
sudo chmod +rw /home/pi/logs
sudo sed -i '\|^tmpfs /home/pi/logs|d' /etc/fstab
sudo sed -i '$ a tmpfs /home/pi/logs tmpfs defaults,noatime,nosuid,size=16m 0 0' /etc/fstab
sudo mount -a


echo ''
echo -e '\033[93mInstalling Camera Zero... \033[0m'
cd ~
sudo rm -Rf ~/camera.zero
sudo git clone https://github.com/eat-sleep-code/camera.zero
sudo chown -R $USER:$USER camera.zero
cd camera.zero
sudo chmod +x camera.py


echo ''
echo -e '\033[93mDownloading color profiles... \033[0m'
cd ~
sudo rm -Rf ~/camera.zero/profiles
mkdir ~/camera.zero/profiles
sudo chown -R $USER:$USER ~/camera.zero/profiles
wget -q https://github.com/davidplowman/Colour_Profiles/raw/master/imx477/PyDNG_profile.dcp -O ~/camera.zero/profiles/basic.dcp
wget -q https://github.com/davidplowman/Colour_Profiles/raw/master/imx477/Raspberry%20Pi%20High%20Quality%20Camera%20Lumariver%202860k-5960k%20Neutral%20Look.dcp -O ~/camera.zero/profiles/neutral.dcp
wget -q https://github.com/davidplowman/Colour_Profiles/raw/master/imx477/Raspberry%20Pi%20High%20Quality%20Camera%20Lumariver%202860k-5960k%20Skin%2BSky%20Look.dcp -O ~/camera.zero/profiles/skin-and-sky.dcp


echo ''
echo -e '\033[093mSetting up autostart daemon... \033[0m'
cd ~
sudo svc -d /etc/service/camera.zero
sudo rm -Rf /etc/service/camera.zero
sudo mkdir /etc/service/camera.zero
sudo mv ~/camera.zero/run.disabled /etc/service/camera.zero/run.disabled
sudo chmod +x /etc/service/camera.zero/run.disabled
sudo chown -R root:root /etc/service/camera.zero


echo ''
echo -e '\033[93mSetting up alias... \033[0m'
cd ~
sudo touch ~/.bash_aliases
sudo sed -i '/\b\(function camera.zero\)\b/d' ~/.bash_aliases
sudo sed -i '/\b\(function camera.focus\)\b/d' ~/.bash_aliases
sudo sed -i '$ a function camera.zero { sudo python3 ~/camera.zero/camera.py "$@"; }' ~/.bash_aliases
sudo sed -i '$ a function camera.stream { sudo python3 ~/camera.zero/stream.py "$@"; }' ~/.bash_aliases
echo -e 'Please ensure that your camera and I2C interfaces are enabled in raspi-config before proceeding.'


echo ''
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e '\033[32mInstallation completed. \033[0m'
echo ''
sudo rm ~/install-camera.sh
bash
