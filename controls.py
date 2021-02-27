import os
import threading
import time
from trackball import TrackBall

trackball = TrackBall(interrupt_pin=4)
	
class Buttons():
	
	# === Trackball/Button Event Handler ============================================

	def watch(buttonDictionary):
		movementThreshold = 4

		while true:	
			left, right, down, up, click, state = trackball.read()  # Change the order of these if your inputs are incorrect
			
			# Capture Mode
			if buttonDictionary['switchMode'] == 'default' or buttonDictionary['switchMode'] == 'capture':
				if int(click) == 1:
					buttonDictionary.update({'capture': True})
					setColor(0, 255, 255, 64, 'flash')
				else: 
					buttonDictionary.update({'capture': False})
					setColorToDefault()

			# Capture Video Mode
			elif buttonDictionary['switchMode'] == 'captureVideo':
				if int(click) == 1:
					if buttonDictionary['isRecording'] == False:
						buttonDictionary.update({'captureVideo': True})
						buttonDictionary.update({'isRecording': True})
						setColor(255, 0, 0, 0, 'pulse')
					else 
						buttonDictionary.update({'captureVideo': False})
						buttonDictionary.update({'isRecording': False}) 
						setColorToDefault()

			# Set Shutter Mode
			elif buttonDictionary['switchMode'] == 'setShutter':
				if int(up) > movementThreshold:
					buttonDictionary.update({'shutterUp': True})
				elif int(down) > movementThreshold:
					buttonDictionary.update({'shutterDown': True})
				elif int(click) == 1:
					setSwitchModeToDefault()

			# Set ISO Mode
			elif buttonDictionary['switchMode'] == 'setIso':
				if int(up) > movementThreshold:
					buttonDictionary.update({'isoUp': True})
				elif int(down) > movementThreshold:
					buttonDictionary.update({'isoDown': True})
				elif int(click) == 1:
					setSwitchModeToDefault()

			# Set Exposure Compensation Mode
			elif buttonDictionary['switchMode'] == 'setEv':
				if int(up) > movementThreshold:
					buttonDictionary.update({'evUp': True})
				elif int(down) > movementThreshold:
					buttonDictionary.update({'evDown': True})
				elif int(click) == 1:
					setSwitchModeToDefault()

			# Set Bracketing Mode
			elif buttonDictionary['switchMode'] == 'setBracket':
				if int(up) > movementThreshold:
					buttonDictionary.update({'bracketUp': True})
				elif int(down) > movementThreshold:
					buttonDictionary.update({'bracketDown': True})
				elif int(click) == 1:
					setSwitchModeToDefault()

			# TODO: Handle Left Right Scrolling		
			time.sleep(0.2)
	

		return buttonDictionary


	def setColorToDefault():
		trackball.set_rgbw(0, 0, 0, 64)


	def setColor(r, g, b, w, mode):
		if mode == 'flash':
			trackball.set_rgbw(r, g, b, w)
			time.sleep(0.2)
			setColorToDefault()
		elif mode = 'pulse':
			trackball.set_rgbw(r, g, b, w)
			#TODO: Make pulse -- threaded?
		else:
			trackball.set_rgbw(r, g, b, w)


	def setSwitchModeToDefault():
		if buttonDictionary['isRecording'] == False:
			setColorToDefault()
		else:
			setColor(255, 0, 0, 0, 'pulse')
		buttonDictionary.update({'switchMode': 'default'})
	