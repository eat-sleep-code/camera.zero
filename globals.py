#!/usr/bin/python3
import os
import sys



def initialize():
	global buttonDictionary
	buttonDictionary = {'switchMode': 0, 'shutterUp': False, 'shutterDown': False, 'isoUp': False, 'isoDown': False, 'evUp': False, 'evDown': False, 'bracketUp': False, 'bracketDown': False, 'capture': False, 'captureVideo': False, 'isRecording': False, 'lightR': 0, 'lightB': 0, 'lightG': 0, 'lightW': 0, 'exit': False, 'remote': False}

	global statusDictionary
	statusDictionary = {'message': '', 'action': '', 'colorR': 0, 'colorG': 0, 'colorB': 0, 'colorW': 0}

	global detections
	detections = []



def restart():
	os.execv(sys.executable, ['python'] + sys.argv)