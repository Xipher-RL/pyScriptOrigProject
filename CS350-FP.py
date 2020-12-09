import time
import grovepi
from grovepi import *
import math
import json #json libarary access


#Light Sensor connection to GrovePi board at A0(zero).
light_sensor = 0

#Green LED connection to GrovePi board at D2.
green_led = 2

#Blue LED connection to GrovePi board at D3.
blue_led = 3

#Red LED connection to GrovePi board at D4.
red_led = 4

#Sets the Light Sensor port as input.
pinMode(light_sensor, "INPUT")

#Sets the LED ports to output settings.
pinMode(green_led, "OUTPUT")
pinMode(blue_led, "OUTPUT")
pinMode(red_led, "OUTPUT")


#Temp/Humidity Sensor connection to GrovePi board at D8.
temp_hum_sensor = 8

#Temp/Humidity Sensor type.
blue = 0

path = "/home/pi/Desktop/" #path to desktop director to store json file.
filename = "data" #file name to store json data
ext = ".json" #extion of the file type for the file.
totFileLoc = path + filename + ext #complete file location with file name and extention.
#Sets the sensitivity of the light sensor to control readings. General resistance reading of dark overcast day is
#roughly 1.5K ohms resistance set higher to ensure capture from sunrise to sunset on those days as well.  Setting
#resistances much higher than 1.5K ohms could begin to skew results from clear days by recording too early.
#For comparison full moonlight night on clear nights is roughly 70K ohms.
threshold = 2000

#setup of an Array of objects for JSON storage.
data = []

#method to write to JSON File
def writeToJSONFile(path, filename, data):
    with open(totFileLoc, 'w') as output:
        json.dump(data, output)

def Lights():
    #Sets the condition for Humidity being greater than 80%
    if humidity > 80:
        digitalWrite(green_led, 1) #Sends HIGH command to turn led on.
        digitalWrite(blue_led, 1) #Sends HIGH command to turn led on.
            
    #Sets the conditions for humitity less than 80.
    else:
        #Sets the conditions for temp within 60-85 range within the < 80 humidity.
        if temp > 60 and temp < 85:
            digitalWrite(green_led, 1) #Sends HIGH command to turn led on.
                
        #Sets the conditions for temp within 85-95 range within the < 80 humidity.
        elif temp > 85 and temp < 95: 
            digitalWrite(blue_led, 1) #Sends HIGH command to turn led on.
              
        #Sets the conditions for temp greater than 95 within the < 80 humidity.
        elif temp > 95:
            digitalWrite(red_led, 1)

def NoLights():
    digitalWrite(green_led, 0) #Sends LOW command to turn led off.
    digitalWrite(blue_led, 0) #Sends LOW command to turn led off.
    digitalWrite(red_led, 0) #Sends LOW command to turn led off.
    

while True:
    try:
        #Get light sensor value
        sensor_value = analogRead(light_sensor)
        #Calculate resistance based off of sensor readings
        #This 'IF' statement prevents divison by zero if senzor_value is 0 during the night, thus crashing program.
        if sensor_value != 0:  
            resistance = (float)(1023 - sensor_value) * 10 / sensor_value
        else:
            resistance = 999999999  #in case of sensor_value = 0, this will allow the program to continue to
                                    #function avoiding a division by zero error.
        
        if resistance < threshold:  #conditional to control readings taken during daylight hours.
            try:
                # The first parameter is the port, the second parameter is the type of sensor.
                [temp, humidity] = grovepi.dht(temp_hum_sensor, blue)
    
                temp = ((temp * 1.8) + 32) #conversion from Celcius to Fahrenheit.
    
                if math.isnan(temp) == False and math.isnan(humidity) == False:
                    print("temp = %.02f F humidity =%.02f%%"%(temp, humidity))
                
                Lights()
            
                #Transfer to JSON File
                data.append([temp, humidity])   
                writeToJSONFile(path, filename, data) #sends data to JSON file for storage
                   
                time.sleep(1790.0) #sample rate of 30 minutes (1,800s - 10s prior to measurements = 1,790s).
        
                NoLights() #disables lights prior to next measurement
                time.sleep(10.0) #brief period before next sample.
        
            except IOError:
                print ("Error -- Temp/Humdity Sensor")
        
        else:
            NoLights()
            print("sensor_value = %d resistance = %.2f" %(sensor_value, resistance))
            time.sleep(10.0) #sample rate of 30 minutes (1,800 seconds).

    except IOError:
        print ("Error -- Light_Sensor")