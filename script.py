from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img
import numpy as np
import serial
import time
import random
import mysql.connector

ser = serial.Serial('COM1', 9600)
gps = serial.Serial('COM2', 9600)

def defect_detection(img_path):
	image = load_img(img_path, target_size=(110, 55))
	image = img_to_array(image)
	image = preprocess_input(image)

	data = []
	data.append(image)
	data = np.array(data, dtype="float32")

	model = load_model('defect_detection.model')
	model.load_weights('defect_detection_weights.h5')
	
	pred = model.predict(data, batch_size=32)

	(DEFECT, NODEFECT) = pred[0]

	label = 1 if DEFECT > NODEFECT else 0
	return label

def convertGPS(cord, dir):
    if cord[4] == '.':
        brk = 4-2
    else:
        brk = 5-2
    
    d = cord[:brk]
    m = cord[brk:]

    deg = "{:.4f}".format(float(d) + (float(m)/60))

    if dir == 'S' or dir == 'W' :
        return '-'+deg
    else:
        return deg

def getGPS():
	while 1:
		data = gps.readline()

		if len(data) == 72:
			data = str(data)[2:-5]
			lat, latD, lon, lonD = data.split(',')[3:7]
			lat = convertGPS(lat, latD)
			lon = convertGPS(lon, lonD)
			
			return ','.join([lat,lon])

def send_to_database(img_path, lat, lon):
	mydb = mysql.connector.connect(
		host="localhost",
		user="root",
		password="",
		database="hsr"
	)

	blob_value = open(img_path, 'rb').read()

	mycursor = mydb.cursor()
	sql = "INSERT INTO track_repair(image, latitude, longitude) values (%s, %s, %s)"
	val = (blob_value, lat, lon)
	mycursor.execute(sql, val)
	mydb.commit()
	print(mycursor.rowcount, "record inserted into track_repair.")


print("READY")

while 1:
	if ser.in_waiting > 0:
		print("Data recieved")
		line = ser.read(2)
		print(line)

		img = random.randint(1,8)
		img_path = ''.join(['dataset/RANDOM/',str(img),'.jpg'])
		print(img_path)
		result = defect_detection(img_path)

		if result:
			print('Defect Detected')
			ser.write(b'1')
			loc = getGPS()
			print(loc)
			send_to_database(img_path, loc.split(',')[0], loc.split(',')[1])
		else:
			print('No Defect Detected')
			ser.write(b'0')