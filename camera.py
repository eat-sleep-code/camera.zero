from functions import Echo, Console
from libcamera import ColorSpace, controls, Transform
from picamera2 import MappedArray, Picamera2, Preview
from picamera2.controls import Controls
from picamera2.outputs import FileOutput
from picamera2.encoders import H264Encoder, Quality
from controls import Light, TrackballController
from PIL import Image
import argparse
import datetime
import fractions
import os
import piexif
import subprocess
import sys
import threading
import time

version = '2024.02.07'


console = Console()
echo = Echo()
camera = Picamera2()
camera.set_logging(Picamera2.ERROR)
stillConfiguration = camera.create_still_configuration(main={"size": (1920, 1080)})
videoConfiguration = camera.create_video_configuration(main={"size": (1920, 1080)})
try:
	camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})
except Exception as ex:
	console.info('Camera does not support autofocus.')
	time.sleep(3)
	pass

# === Argument Handling ========================================================

parser = argparse.ArgumentParser()
parser.add_argument('--rotate', dest='rotate', help='Rotate the camera in 90* increments', type=int)
parser.add_argument('--exifFStop', dest='exifFStop', help='Set the numeric F-Stop value in the image EXIF data', type=float)
parser.add_argument('--exifFocalLength', dest='exifFocalLength', help='Set the numeric Focal Length value (mm) in the image EXIF data', type=float)
parser.add_argument('--exifFocalLengthEquivalent', dest='exifFocalLengthEquivalent', help='Set the numeric 35mm Focal Length value (mm) in the image EXIF data', type=float)
args = parser.parse_args()


running = False
buttons = TrackballController()
statusDictionary = {'message': '', 'action': '', 'colorR': 0, 'colorG': 0, 'colorB': 0, 'colorW': 0}
buttonDictionary = {'switchMode': 0, 'shutterUp': False, 'shutterDown': False, 'isoUp': False, 'isoDown': False, 'evUp': False, 'evDown': False, 'bracketUp': False, 'bracketDown': False, 'capture': False, 'captureVideo': False, 'isRecording': False, 'lightR': 0, 'lightB': 0, 'lightG': 0, 'lightW': 0, 'exit': False, 'remote': False}

previewVisible = False
previewWidth = 800
previewHeight = 460

rotate = args.rotate or 0
try:
	rotate = int(rotate)
except:
	rotate = 0

shutter = 'auto'
shutterLong = 30000
shutterLongThreshold = 1000
shutterShort = 0
defaultFramerate = 30

iso = 'auto'
isoMin = 100
isoMax = 1600

exposure = 'auto'

ev = 0
evMin = -25
evMax = 25

bracket = 0
bracketLow = 0
bracketHigh = 0 

awb = 'auto'

outputFolder = 'dcim/'

timer = 0

raw = False
try:
	from pidng.core import RPICAM2DNG
	dng = RPICAM2DNG()
	raw = False # Going to disable this by default as the Pi Zero W struggles with it 
except:
	console.info( ' WARNING: DNG file format not currently supported on this device. ')


# === Data Objects ============================================================

class EXIFData:
	def __init__(self, Orientation = 1, FStop = None, FocalLength = None, FocalLengthEquivalent = None):

		self.Orientation = Orientation
		self.FStop = FStop
		self.FocalLength = FocalLength
		self.FocalLengthEquivalent = FocalLengthEquivalent
		

EXIFDataOverride = EXIFData()
EXIFDataOverride.FStop = args.exifFStop
EXIFDataOverride.FocalLength = args.exifFocalLength
EXIFDataOverride.FocalLengthEquivalent = args.exifFocalLengthEquivalent



# === Functions ================================================================

def setShutter(input, wait = 0):
	global shutter
	global shutterLong
	global shutterLongThreshold
	global shutterShort
	global defaultFramerate
	global statusDictionary
	
	if str(input).lower() == 'auto' or str(input) == '0':
		shutter = 0
	else:
		shutter = int(float(input))
		if shutter < shutterShort:
			shutter = shutterShort
		elif shutter > shutterLong:
			shutter = shutterLong 
	
	try:
		if camera.framerate == defaultFramerate and shutter > shutterLongThreshold:
			camera.framerate=fractions.Fraction(5, 1000)
		elif camera.framerate != defaultFramerate and shutter <= shutterLongThreshold:
			camera.framerate = defaultFramerate
	except Exception as ex:
		# console.info( ' WARNING: Could not set framerate!')
		pass
	
	try:
		if shutter == 0:
			camera.shutter_speed = 0
			# console.info(str(camera.shutter_speed) + '|' + str(camera.framerate) + '|' + str(shutter))	
			console.info('Shutter Speed: auto')
			statusDictionary.update({'message': 'Shutter Speed: auto'})
		else:
			camera.shutter_speed = shutter * 1000
			# console.info(str(camera.shutter_speed) + '|' + str(camera.framerate) + '|' + str(shutter))		
			floatingShutter = float(shutter/1000)
			roundedShutter = '{:.3f}'.format(floatingShutter)
			if shutter > shutterLongThreshold:
				console.info('Shutter Speed: ' + str(roundedShutter)  + 's [Long Exposure Mode]')
				statusDictionary.update({'message': ' Shutter Speed: ' + str(roundedShutter)  + 's [Long Exposure Mode]'})
			else:
				console.info('Shutter Speed: ' + str(roundedShutter) + 's')
				statusDictionary.update({'message': ' Shutter Speed: ' + str(roundedShutter) + 's'})
		time.sleep(wait)
		return
	except Exception as ex:
		console.info('WARNING: Invalid Shutter Speed!' + str(shutter))

# ------------------------------------------------------------------------------				

def setISO(input, wait = 0):
	global iso
	global isoMin
	global isoMax
	global statusDictionary

	if str(input).lower() == 'auto' or str(input) == '0':
		iso = 0
	else: 
		iso = int(input)
		if iso < isoMin:	
			iso = isoMin
		elif iso > isoMax:
			iso = isoMax	
	try:	
		camera.iso = iso
		#console.info(str(camera.iso) + '|' + str(iso))
		if iso == 0:
			console.info('ISO: auto')
			statusDictionary.update({'message': ' ISO: auto'})
		else:	
			console.info('ISO: ' + str(iso))
			statusDictionary.update({'message': ' ISO: ' + str(iso)})
		time.sleep(wait)
		return
	except Exception as ex:
		console.info('WARNING: Invalid ISO Setting! ' + str(iso))

# ------------------------------------------------------------------------------

def setExposure(input, wait = 0):
	global exposure
	global statusDictionary

	exposure = input
	try:	
		camera.exposure_mode = exposure
		console.info('Exposure Mode: ' + exposure)
		statusDictionary.update({'message': ' Exposure Mode: ' + exposure})
		time.sleep(wait)
		return
	except Exception as ex:
		console.info('WARNING: Invalid Exposure Mode!')
				
# ------------------------------------------------------------------------------

def setEV(input, wait = 0, displayMessage = True):
	global ev 
	global bracket
	global statusDictionary

	ev = input
	ev = int(ev)
	evPrefix = '+/-'
	if ev > 0:
		evPrefix = '+'
	elif ev < 0:
		evPrefix = ''
	try:
		camera.exposure_compensation = ev
		# console.info(str(camera.exposure_compensation) + '|' + str(ev))
		if displayMessage == True:
			console.info('Exposure Compensation: ' + evPrefix + str(ev))
			statusDictionary.update({'message': ' Exposure Compensation: ' + evPrefix + str(ev)})
		time.sleep(wait)
		return
	except Exception as ex: 
		console.info('WARNING: Invalid Exposure Compensation Setting!')	
		
# ------------------------------------------------------------------------------				

def setBracket(input, wait = 0, displayMessage = True):
	global bracket
	global bracketLow
	global bracketHigh
	global evMax
	global evMin
	global statusDictionary

	bracket = int(input)
	try:
		bracketLow = camera.exposure_compensation - bracket
		if bracketLow < evMin:
			bracketLow = evMin
		bracketHigh = camera.exposure_compensation + bracket
		if bracketHigh > evMax:
			bracketHigh = evMax
		if displayMessage == True:
			console.info('Exposure Bracketing: ' + str(bracket))
			statusDictionary.update({'message': ' Exposure Bracketing: ' + str(bracket)})
		time.sleep(wait)
		return
	except Exception as ex:
		console.info('WARNING: Invalid Exposure Bracketing Value!')

# ------------------------------------------------------------------------------

def setAWB(input, wait = 0):
	global awb
	global statusDictionary

	awb = input
	try:	
		camera.awb_mode = awb
		console.info('White Balance Mode: ' + awb)
		statusDictionary.update({'message': ' White Balance Mode: ' + awb})
		time.sleep(wait)
		return
	except Exception as ex:
		console.info('WARNING: Invalid Auto White Balance Mode!')

# ------------------------------------------------------------------------------

def getFileName(timestamped = True, isVideo = False):
	now = datetime.datetime.now()
	datestamp = now.strftime('%Y%m%d')
	timestamp = now.strftime('%H%M%S')		
			
	if isVideo==True:
		extension = '.h264'
		return datestamp + '-' + timestamp + extension
	else:
		extension = '.jpg'
		if timestamped == True:
			return datestamp + '-' + timestamp + '-' + str(imageCount).zfill(2) + extension
		else:
			return datestamp + '-' + str(imageCount).zfill(8) + extension

# ------------------------------------------------------------------------------

def getfilePath(timestamped = True, isVideo = False):
	try:
		os.makedirs(outputFolder, exist_ok = True)
	except OSError:
		console.error(' ERROR: Creation of the output folder ' + outputFolder + ' failed!')
		echo.on()
		quit()
	else:
		return outputFolder + getFileName(timestamped, isVideo)

# ------------------------------------------------------------------------------

def postProcessImage(filePath, angle):

	global EXIFDataOverride

	try:
		image = Image.open(filePath)
		FileEXIFData = piexif.load(filePath)

		if angle > 0:
			newOrientation = 1
			if angle == 90:
				newOrientation = 6
				image = image.rotate(-90, expand=True)
			elif angle == 180:
				newOrientation = 3
				image = image.rotate(180, expand=True)
			elif angle == 270:
				newOrientation = 8
				image = image.rotate(90, expand=True)
			EXIFDataOverride.Orientation = newOrientation
				
			FileEXIFData['Orientation'] = EXIFDataOverride.Orientation

		try:
			if EXIFDataOverride.FStop is not None:
				FileEXIFData['Exif'][piexif.ExifIFD.FNumber] = (int(EXIFDataOverride.FStop * 100), 100)
				
			if EXIFDataOverride.FocalLength is not None:
				FileEXIFData['Exif'][piexif.ExifIFD.FocalLength] = (int(EXIFDataOverride.FocalLength * 100), 100)
				
			if EXIFDataOverride.FocalLengthEquivalent is not None:
				FileEXIFData['Exif'][piexif.ExifIFD.FocalLengthIn35mmFilm] = int(EXIFDataOverride.FocalLengthEquivalent)
		except Exception as ex:
			console.warn('Could not rotate apply additional EXIF data to image.   Please check supplied data. ' + str(ex))
			pass

		EXIFBytes = piexif.dump(FileEXIFData)
		image.save(filePath, exif=EXIFBytes)
	except Exception as ex:
		console.warn('Could not rotate ' + filePath + ' ' + str(angle) + ' degrees. ' + str(ex))
		pass

# ------------------------------------------------------------------------------

def showPreview(xPosition = 0, yPosition = 0, w = 800, h = 600):
	global previewVisible
	try:
		camera.start_preview(Preview.QTGL, x=xPosition, y=yPosition, width=w, height=h) # transform=Transform(hflip=1)
	except Exception as ex:
		console.warn('Could not display preview window.')
		pass
	previewVisible = True
	time.sleep(0.1)
	return
	
# ------------------------------------------------------------------------------

def hidePreview():
	global previewVisible
	try:
		camera.stop_preview()
	except Exception as ex:
		console.warn('Could not hide preview window.')
		pass
	previewVisible = False
	time.sleep(0.1)
	return

# ------------------------------------------------------------------------------

def captureImage(filePath, raw = True):
	global rotate

	console.info('Capturing ' + str(filePath) + ' ...')		
	request = camera.switch_mode_and_capture_request(stillConfiguration)
	request.save('main', filePath)
	request.release()

	postProcessImage(filePath, rotate)
				
	if raw == True:
		conversionThread = threading.Thread(target=convertBayerDataToDNG, args=(filePath,))
		conversionThread.daemon = True
		conversionThread.start()

# ------------------------------------------------------------------------------		

def convertBayerDataToDNG(filePath):
	try:
		dng.convert(filePath)
	except:
		pass

# ------------------------------------------------------------------------------
def createControls():
	global running
	global statusDictionary	
	global buttonDictionary
	
	running = True
	TrackballController.watch(running, statusDictionary, buttonDictionary)
	
# -------------------------------------------------------------------------------
def darkMode():
	Light.off()
	TrackballController.off()


# === Image Capture ============================================================

controlsThread = threading.Thread(target=createControls)
controlsThread.daemon = True
controlsThread.start()


try:
	echo.clear()
	os.chdir('/home/pi') 
	
	console.info('Camera Zero ' + version )
	console.print('----------------------------------------------------------------------', '\n ', '\n ')
	


	imageCount = 1
	isRecording = False
	mode = 'persistant'

	setShutter(shutter, 0)		
	setISO(iso, 0)
	setExposure(exposure, 0)
	setEV(ev, 0)
	setBracket(bracket, 0)
	setAWB(awb, 0)
	
	
	showPreview(0, 0, previewWidth, previewHeight)
	
	while True:
		try:
			# Exit / Spawn
			if buttonDictionary['exit'] == True or buttonDictionary['remote'] == True:
				running = False
				darkMode()
				echo.on()
				camera.close()
				try:
					# Tell service to not auto restart after it is killed
					subprocess.run('sudo svc -d /etc/service/camera.zero', shell=True)
					
					# Kill the current running service
					subprocess.run('sudo svc -k /etc/service/camera.zero', shell=True)
					
				except Exception as ex:
					console.warn(ex)
					pass
				time.sleep(1.0)
				
				if buttonDictionary['remote'] == True:
					try:
						console.info('Launching remote control...')
						subprocess.Popen(['sudo', '/usr/bin/python3', '/home/pi/camera.remote/camera.py'])	
					except Exception as ex:
						console.info('Could not launch remote control.')
		
				sys.exit(0)
				
			# Capture
			elif buttonDictionary['capture'] == True:
				
				if mode == 'persistent':
					# Normal photo
					filePath = getfilePath(True)
					console.info('Capturing image: ' + filePath + '\n')
					captureImage(filePath, raw)
					
					imageCount += 1
			
					if (bracket != 0):
						baseEV = ev
						# Take underexposed photo
						setEV(baseEV + bracketLow, 0, False)
						filePath = getfilePath(True)
						console.info('Capturing image: ' + filePath + '  [' + str(bracketLow) + ']\n')
						captureImage(filePath, raw)
						imageCount += 1

						# Take overexposed photo
						setEV(baseEV + bracketHigh, 0, False)
						filePath = getfilePath(True)
						console.info('Capturing image: ' + filePath + '  [' + str(bracketHigh) + ']\n')
						captureImage(filePath, raw)
						imageCount += 1						
						
						# Reset EV to base photo's value
						setEV(baseEV, 0, False)
						
				elif mode == 'timelapse':
					# Timelapse photo series
					if timer < 0:
						timer = 1
					while True:
						filePath = getfilePath(False)
						console.info('Capturing timelapse image: ' + filePath + '\n')
						captureImage(filePath, raw)
						imageCount += 1
						time.sleep(timer) 	
						
				else:
					# Single photo and then exit
					filePath = getfilePath(True)
					console.info('Capturing single image: ' + filePath + '\n')
					captureImage(filePath, raw)
					echo.on()
					break

				buttonDictionary.update({'capture': False})

			elif buttonDictionary['captureVideo'] == True:

				# Video
				if isRecording == False:
					isRecording = True
					statusDictionary.update({'action': 'recording'})
					filePath = getfilePath(True, True)
					camera.resolution = (1920, 1080)
					console.info('Capturing video: ' + filePath + '\n')
					statusDictionary.update({'message': ' Recording: Started '})
					buttonDictionary.update({'captureVideo': False})
					camera.configure(videoConfiguration)
					encoder = H264Encoder()
					camera.start_recording(encoder, filePath, quality=Quality.VERY_HIGH)

				else:
					isRecording = False
					statusDictionary.update({'action': ''})
					camera.stop_recording()
					console.info('Capture complete \n')
					statusDictionary.update({'message': ' Recording: Stopped '})
					buttonDictionary.update({'captureVideo': False})
				
				time.sleep(1)

			# Shutter Speed	
			elif buttonDictionary['shutterUp'] == True:
				if shutter == 0:
					shutter = shutterShort
				elif shutter > shutterShort and shutter <= shutterLong:					
					shutter = int(shutter / 1.5)
				setShutter(shutter, 0.25)
				buttonDictionary.update({'shutterUp': False})
			elif buttonDictionary['shutterDown'] == True:
				if shutter == 0:						
					shutter = shutterLong
				elif shutter < shutterLong and shutter >= shutterShort:					
					shutter = int(shutter * 1.5)
				elif shutter == shutterShort:
					shutter = 0
				setShutter(shutter, 0.25)
				buttonDictionary.update({'shutterDown': False})

			# ISO
			elif buttonDictionary['isoUp'] == True:
				if iso == 0:
					iso = isoMin
				elif iso >= isoMin and iso < isoMax:					
					iso = int(iso * 2)
				setISO(iso, 0.25)
				buttonDictionary.update({'isoUp': False})
			elif buttonDictionary['isoDown'] == True:
				if iso == 0:
					iso = isoMax
				elif iso <= isoMax and iso > isoMin:					
					iso = int(iso / 2)
				elif iso == isoMin:
					iso = 0
				setISO(iso, 0.25)
				buttonDictionary.update({'isoDown': False})

			# Exposure Compensation
			elif buttonDictionary['evUp'] == True:
				if ev >= evMin and ev < evMax:					
					ev = int(ev + 1)
					setEV(ev, 0.25)
					buttonDictionary.update({'evUp': False})
			elif buttonDictionary['evDown'] == True:
				if ev <= evMax and ev > evMin:					
					ev = int(ev - 1)
					setEV(ev, 0.25)
					buttonDictionary.update({'evDown': False})
					
			# Exposure Bracketing
			elif buttonDictionary['bracketUp'] == True:
				if bracket < evMax:
					bracket = int(bracket + 1)
					setBracket(bracket, 0.25)
					buttonDictionary.update({'bracketUp': False})
			elif buttonDictionary['bracketDown'] == True:
				if bracket > 0:					
					bracket = int(bracket - 1)
					setBracket(bracket, 0.25)
					buttonDictionary.update({'bracketDown': False})

			
		except Exception as ex:
			console.error(str(ex))
			pass

	

except KeyboardInterrupt:
	darkMode()
	echo.on() 
	sys.exit(0)
