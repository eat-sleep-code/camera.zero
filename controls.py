import board
import neopixel
import os
import threading
import time
from trackball import TrackBall

trackball = TrackBall(interrupt_pin=4)
pixels = neopixel.NeoPixel(board.D18, 16, pixel_order=neopixel.GRBW)   # GPIO 18 = PIN 12  /// 16 = Number of NeoPixels
	
class Light():

	# === NeoPixel RGBW LED Color Handlers ====================================

	def off():
		pixels.fill((0,0,0,0))
		pixels.show()

	def updateLight(buttonDictionary):
		red = buttonDictionary['lightR']
		blue = buttonDictionary['lightG']
		green = buttonDictionary['lightB']
		white = buttonDictionary['lightW']
		pixels.fill((red, blue, green, white))
		pixels.show()



class TrackballController():

	# === Trackball/Button LED Color Handlers =================================

	def off():
		trackball.set_rgbw(0, 0, 0, 0)

	def setColorToDefault():
		trackball.set_rgbw(128, 128, 128, 128)

	def setColor(r, g, b, w, mode):
		if mode == 'flash':
			trackball.set_rgbw(r, g, b, w)
			time.sleep(0.2)
			TrackballController.setColorToDefault()
		elif mode == 'pulse':
			trackball.set_rgbw(r, g, b, w)
			#TODO: Make pulse -- threaded?
		else:
			trackball.set_rgbw(r, g, b, w)



	# === Trackball/Button Mode Handlers ======================================

	def setSwitchModeToDefault(buttonDictionary):
		if buttonDictionary['isRecording'] == False:
			TrackballController.setColorToDefault()
		else:
			TrackballController.setColor(255, 0, 0, 0, 'pulse')
		buttonDictionary.update({'switchMode': 0})


	def setSwitchModeColor(buttonDictionary):
		currentMode = buttonDictionary['switchMode']
		if currentMode == 2:
			TrackballController.setColor( 128, 64, 0, 0, 'static')
		elif currentMode == 3:
			TrackballController.setColor( 64, 64, 0, 0, 'static')
		elif currentMode == 4:
			TrackballController.setColor( 0, 64, 64, 0, 'static')
		elif currentMode == 5:
			TrackballController.setColor( 64, 0, 64, 0, 'static')
		elif currentMode == 6:
			TrackballController.setColor( 64, 0, 0, 0, 'static')
		elif currentMode == 7:
			TrackballController.setColor( 0, 64, 0, 0, 'static')
		elif currentMode == 8:
			TrackballController.setColor( 0, 0, 64, 0, 'static')
		elif currentMode == 9:
			TrackballController.setColor( 0, 0, 0, 64, 'static')
		elif currentMode == 10:
			TrackballController.setColor( 8, 8, 8, 8, 'static')


	# === Trackball/Button Event Handler ======================================

	def handleButtonChanges(buttonDictionary):
		movementThreshold = 5
		minMode = 0
		maxMode = 10
			
		left, right, down, up, click, state = trackball.read()  # Change the order of these if your inputs are incorrect
		
		# Capture Mode
		if buttonDictionary['switchMode'] == 0:
			#print(' Mode: Capture Photo ')
			if int(click) == 1:
				buttonDictionary.update({'capture': True})
				TrackballController.setColor(0, 255, 255, 128, 'flash')
			else: 
				buttonDictionary.update({'capture': False})
				TrackballController.setColorToDefault()

		# Capture Video Mode
		elif buttonDictionary['switchMode'] == 1:
			#print(' Mode: Capture Video ')
			if int(click) == 1:
				if buttonDictionary['isRecording'] == False:
					buttonDictionary.update({'captureVideo': True})
					buttonDictionary.update({'isRecording': True})
					TrackballController.setColor(255, 0, 0, 0, 'pulse')
				else: 
					buttonDictionary.update({'captureVideo': False})
					buttonDictionary.update({'isRecording': False}) 
					TrackballController.setColorToDefault()

		# Set Shutter Mode
		elif buttonDictionary['switchMode'] == 2:
			#print(' Mode: Shutter Speed Control ')
			if int(up) > movementThreshold:
				buttonDictionary.update({'shutterUp': True})
			elif int(down) > movementThreshold:
				buttonDictionary.update({'shutterDown': True})
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault(buttonDictionary)

		# Set ISO Mode
		elif buttonDictionary['switchMode'] == 3:
			#print(' Mode: ISO Control ')
			if int(up) > movementThreshold:
				buttonDictionary.update({'isoUp': True})
			elif int(down) > movementThreshold:
				buttonDictionary.update({'isoDown': True})
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault(buttonDictionary)

		# Set Exposure Compensation Mode
		elif buttonDictionary['switchMode'] == 4:
			#print(' Mode: Exposure Compensation Control ')
			if int(up) > movementThreshold:
				buttonDictionary.update({'evUp': True})
			elif int(down) > movementThreshold:
				buttonDictionary.update({'evDown': True})
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault(buttonDictionary)

		# Set Bracketing Mode
		elif buttonDictionary['switchMode'] == 5:
			#print(' Mode: Bracketing Control ')
			if int(up) > movementThreshold:
				buttonDictionary.update({'bracketUp': True})
			elif int(down) > movementThreshold:
				buttonDictionary.update({'bracketDown': True})
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault(buttonDictionary)

		# Set Light's (R)ed Mode
		elif buttonDictionary['switchMode'] == 6:
			#print(' Mode: Red Scene Lighting Control ')
			currentLevel = buttonDictionary['lightR']
			if int(up) > movementThreshold:
				if currentLevel < 255:
					buttonDictionary.update({'lightR': currentLevel + 1})
				else: 
					buttonDictionary.update({'lightR': 0})
				Light.updateLight(buttonDictionary)
			elif int(down) > movementThreshold:
				if currentLevel > 0:
					buttonDictionary.update({'lightR': currentLevel - 1})
				else: 
					buttonDictionary.update({'lightR': 255})
				Light.updateLight(buttonDictionary)
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault(buttonDictionary)

		# Set Light's (G)reen Mode
		elif buttonDictionary['switchMode'] == 7:
			#print(' Mode: Green Scene Lighting Control ')
			currentLevel = buttonDictionary['lightG']
			if int(up) > movementThreshold:
				if currentLevel < 255:
					buttonDictionary.update({'lightG': currentLevel + 1})
				else: 
					buttonDictionary.update({'lightG': 0})
				Light.updateLight(buttonDictionary)
			elif int(down) > movementThreshold:
				if currentLevel > 0:
					buttonDictionary.update({'lightG': currentLevel - 1})
				else: 
					buttonDictionary.update({'lightG': 255})
				Light.updateLight(buttonDictionary)
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault(buttonDictionary)

		# Set Light's (B)lue Mode
		elif buttonDictionary['switchMode'] == 8:
			#print(' Mode: Blue Scene Lighting Control ')
			currentLevel = buttonDictionary['lightB']
			if int(up) > movementThreshold:
				if currentLevel < 255:
					buttonDictionary.update({'lightB': currentLevel + 1})
				else: 
					buttonDictionary.update({'lightB': 0})
				Light.updateLight(buttonDictionary)
			elif int(down) > movementThreshold:
				if currentLevel > 0:
					buttonDictionary.update({'lightB': currentLevel - 1})
				else: 
					buttonDictionary.update({'lightB': 255})
				Light.updateLight(buttonDictionary)
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault(buttonDictionary)

		# Set Light's (W)hite Mode
		elif buttonDictionary['switchMode'] == 9:
			#print(' Mode: Natural White Scene Lighting Control ')
			currentLevel = buttonDictionary['lightW']
			if int(up) > movementThreshold:
				if currentLevel < 255:
					buttonDictionary.update({'lightW': currentLevel + 1})
				else: 
					buttonDictionary.update({'lightW': 0})
				Light.updateLight(buttonDictionary)
			elif int(down) > movementThreshold:
				if currentLevel > 0:
					buttonDictionary.update({'lightW': currentLevel - 1})
				else: 
					buttonDictionary.update({'lightW': 255})
				Light.updateLight(buttonDictionary)
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault(buttonDictionary)

		# Exit / Launch Remote
		elif buttonDictionary['switchMode'] == 10:
			#print(' Mode: Exit / Launch Remote ')
			if int(click) == 1:
				startTime = time.time()

				while trackball.read()[4] == 0:
					pass

				buttonHoldTime = time.time() - startTime
				print(' Button Held For: ' + str(buttonHoldTime))
				if buttonHoldTime >= 5 and buttonHoldTime < 10:
					buttonDictionary.update({'remote': True})
				elif buttonHoldTime >= 10:
					buttonDictionary.update({'exit': True})	
				else: 
					TrackballController.setSwitchModeToDefault(buttonDictionary)


		# Left Mode Scrolling
		if int(left) > movementThreshold:
			currentMode = buttonDictionary['switchMode']
			if currentMode > minMode:
				buttonDictionary.update({'switchMode': currentMode - 1})
			else:
				buttonDictionary.update({'switchMode': maxMode})
			TrackballController.setSwitchModeColor(buttonDictionary)
			time.sleep(0.75)
		
		# Right Mode Scrolling
		elif int(right) > movementThreshold:
			currentMode = buttonDictionary['switchMode']
			if currentMode < maxMode:
				buttonDictionary.update({'switchMode': currentMode + 1})
			else:
				buttonDictionary.update({'switchMode': minMode})
			TrackballController.setSwitchModeColor(buttonDictionary)
			time.sleep(0.75)


		time.sleep(0.25)
		return buttonDictionary


	# === Trackball/Button Event Handler Init =================================

	def watch(running, statusDictionary, buttonDictionary):
		while running == True:
			TrackballController.handleButtonChanges(buttonDictionary)
