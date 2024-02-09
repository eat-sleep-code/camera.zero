import board
import globals
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

	def updateLight():
		red = globals.buttonDictionary['lightR']
		blue = globals.buttonDictionary['lightG']
		green = globals.buttonDictionary['lightB']
		white = globals.buttonDictionary['lightW']
		pixels.fill((red, blue, green, white))
		pixels.show()



class TrackballController():

	# === Trackball/Button LED Color Handlers =================================

	def off():
		trackball.set_rgbw(0, 0, 0, 0)

	def setColorToDefault():
		trackball.set_rgbw(160, 160, 160, 160)

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

	def setSwitchModeToDefault():
		if globals.buttonDictionary['isRecording'] == False:
			TrackballController.setColorToDefault()
		else:
			TrackballController.setColor(255, 0, 0, 0, 'pulse')
		globals.buttonDictionary.update({'switchMode': 0})


	def setSwitchModeColor():
		currentMode = globals.buttonDictionary['switchMode']
		if currentMode == 1:
			TrackballController.setColor( 160, 0, 0, 0, 'static')
		if currentMode == 2:
			TrackballController.setColor( 160, 96, 0, 0, 'static')
		elif currentMode == 3:
			TrackballController.setColor( 96, 96, 0, 0, 'static')
		elif currentMode == 4:
			TrackballController.setColor( 0, 96, 96, 0, 'static')
		elif currentMode == 5:
			TrackballController.setColor( 96, 0, 96, 0, 'static')
		elif currentMode == 6:
			TrackballController.setColor( 96, 0, 0, 0, 'static')
		elif currentMode == 7:
			TrackballController.setColor( 0, 96, 0, 0, 'static')
		elif currentMode == 8:
			TrackballController.setColor( 0, 0, 96, 0, 'static')
		elif currentMode == 9:
			TrackballController.setColor( 0, 0, 0, 96, 'static')
		elif currentMode == 10:
			TrackballController.setColor( 101, 67, 33, 0, 'static')
		else:
			TrackballController.setColorToDefault()


	# === Trackball/Button Event Handler ======================================

	def handleButtonChanges():
		movementThreshold = 5
		lightingIncrement = 8
		minMode = 0
		maxMode = 10
			
		left, right, down, up, click, state = trackball.read()  # Change the order of these if your inputs are incorrect
		
		# Capture Mode
		if globals.buttonDictionary['switchMode'] == 0:
			#print(' Mode: Capture Photo ')
			if int(click) == 1:
				globals.buttonDictionary.update({'capture': True})
				TrackballController.setColor(0, 255, 255, 128, 'flash')
			else: 
				globals.buttonDictionary.update({'capture': False})
				TrackballController.setColorToDefault()

		# Capture Video Mode
		elif globals.buttonDictionary['switchMode'] == 1:
			#print(' Mode: Capture Video ')
			if int(click) == 1:
				if globals.buttonDictionary['isRecording'] == False:
					globals.buttonDictionary.update({'captureVideo': True})
					globals.buttonDictionary.update({'isRecording': True})
					TrackballController.setColor(255, 0, 0, 0, 'pulse')
				else: 
					globals.buttonDictionary.update({'captureVideo': False})
					globals.buttonDictionary.update({'isRecording': False}) 
					TrackballController.setColorToDefault()

		# Set Shutter Mode
		elif globals.buttonDictionary['switchMode'] == 2:
			#print(' Mode: Shutter Speed Control ')
			if int(up) > movementThreshold:
				globals.buttonDictionary.update({'shutterUp': True})
			elif int(down) > movementThreshold:
				globals.buttonDictionary.update({'shutterDown': True})
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault()

		# Set ISO Mode
		elif globals.buttonDictionary['switchMode'] == 3:
			#print(' Mode: ISO Control ')
			if int(up) > movementThreshold:
				globals.buttonDictionary.update({'isoUp': True})
			elif int(down) > movementThreshold:
				globals.buttonDictionary.update({'isoDown': True})
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault()

		# Set Exposure Compensation Mode
		elif globals.buttonDictionary['switchMode'] == 4:
			#print(' Mode: Exposure Compensation Control ')
			if int(up) > movementThreshold:
				globals.buttonDictionary.update({'evUp': True})
			elif int(down) > movementThreshold:
				globals.buttonDictionary.update({'evDown': True})
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault()

		# Set Bracketing Mode
		elif globals.buttonDictionary['switchMode'] == 5:
			#print(' Mode: Bracketing Control ')
			if int(up) > movementThreshold:
				globals.buttonDictionary.update({'bracketUp': True})
			elif int(down) > movementThreshold:
				globals.buttonDictionary.update({'bracketDown': True})
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault()

		# Set Light's (R)ed Mode
		elif globals.buttonDictionary['switchMode'] == 6:
			#print(' Mode: Red Scene Lighting Control ')
			currentLevel = globals.buttonDictionary['lightR']
			if int(up) > movementThreshold:
				if currentLevel <= (255 - lightingIncrement):
					globals.buttonDictionary.update({'lightR': currentLevel + lightingIncrement})
				else: 
					globals.buttonDictionary.update({'lightR': 0})
				Light.updateLight()
			elif int(down) > movementThreshold:
				if currentLevel >= lightingIncrement:
					globals.buttonDictionary.update({'lightR': currentLevel - lightingIncrement})
				else: 
					globals.buttonDictionary.update({'lightR': 255})
				Light.updateLight()
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault()

		# Set Light's (G)reen Mode
		elif globals.buttonDictionary['switchMode'] == 7:
			#print(' Mode: Green Scene Lighting Control ')
			currentLevel = globals.buttonDictionary['lightG']
			if int(up) > movementThreshold:
				if currentLevel <= (255 - lightingIncrement):
					globals.buttonDictionary.update({'lightG': currentLevel + lightingIncrement})
				else: 
					globals.buttonDictionary.update({'lightG': 0})
				Light.updateLight()
			elif int(down) > movementThreshold:
				if currentLevel >= lightingIncrement:
					globals.buttonDictionary.update({'lightG': currentLevel - lightingIncrement})
				else: 
					globals.buttonDictionary.update({'lightG': 255})
				Light.updateLight()
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault()

		# Set Light's (B)lue Mode
		elif globals.buttonDictionary['switchMode'] == 8:
			#print(' Mode: Blue Scene Lighting Control ')
			currentLevel = globals.buttonDictionary['lightB']
			if int(up) > movementThreshold:
				if currentLevel <= (255 - lightingIncrement):
					globals.buttonDictionary.update({'lightB': currentLevel + lightingIncrement})
				else: 
					globals.buttonDictionary.update({'lightB': 0})
				Light.updateLight()
			elif int(down) > movementThreshold:
				if currentLevel >= lightingIncrement:
					globals.buttonDictionary.update({'lightB': currentLevel - lightingIncrement})
				else: 
					globals.buttonDictionary.update({'lightB': 255})
				Light.updateLight()
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault()

		# Set Light's (W)hite Mode
		elif globals.buttonDictionary['switchMode'] == 9:
			#print(' Mode: Natural White Scene Lighting Control ')
			currentLevel = globals.buttonDictionary['lightW']
			if int(up) > movementThreshold:
				if currentLevel <= (255 - lightingIncrement):
					globals.buttonDictionary.update({'lightW': currentLevel + lightingIncrement})
				else: 
					globals.buttonDictionary.update({'lightW': 0})
				Light.updateLight()
			elif int(down) > movementThreshold:
				if currentLevel >= lightingIncrement:
					globals.buttonDictionary.update({'lightW': currentLevel - lightingIncrement})
				else: 
					globals.buttonDictionary.update({'lightW': 255})
				Light.updateLight()
			elif int(click) == 1:
				TrackballController.setSwitchModeToDefault()

		# Exit / Launch Remote
		elif globals.buttonDictionary['switchMode'] == 10:
			#print(' Mode: Exit / Launch Remote ')
			if int(click) == 1:
				startTime = time.time()

				while trackball.read()[4] == 0:
					pass

				buttonHoldTime = time.time() - startTime
				#print(' Button Held For: ' + str(buttonHoldTime))
				if buttonHoldTime >= 5 and buttonHoldTime < 10:
					globals.buttonDictionary.update({'remote': True})
				elif buttonHoldTime >= 10:
					globals.buttonDictionary.update({'exit': True})	
				else: 
					TrackballController.setSwitchModeToDefault()


		# Left Mode Scrolling
		if int(left) > movementThreshold:
			currentMode = globals.buttonDictionary['switchMode']
			if currentMode > minMode:
				globals.buttonDictionary.update({'switchMode': currentMode - 1})
			else:
				globals.buttonDictionary.update({'switchMode': maxMode})
			TrackballController.setSwitchModeColor()
			time.sleep(0.75)
		
		# Right Mode Scrolling
		elif int(right) > movementThreshold:
			currentMode = globals.buttonDictionary['switchMode']
			if currentMode < maxMode:
				globals.buttonDictionary.update({'switchMode': currentMode + 1})
			else:
				globals.buttonDictionary.update({'switchMode': minMode})
			TrackballController.setSwitchModeColor()
			time.sleep(0.75)


		time.sleep(0.25)
		return globals.buttonDictionary


	# === Trackball/Button Event Handler Init =================================

	def watch(running):
		while running == True:
			TrackballController.handleButtonChanges()
