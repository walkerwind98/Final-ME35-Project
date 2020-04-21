#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

import time
import urequests
import utime
import ujson
import ubinascii

# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()

#Initialize Motors and Sensors

hitter = Motor(Port.D)
touch = TouchSensor(Port.S3)
color = ColorSensor(Port.S4)

#Define Functions
Key = 'bvd8X9LweQY9o2eP1NYL-p8mLL9wMAk6YYOnYSiIo0'

def SL_setup():
     urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
     headers = {"Accept":"application/json","x-ni-api-key":Key}
     return urlBase, headers
     
def Put_SL(Tag, Type, Value):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     propValue = {"value":{"type":Type,"value":Value}}
     try:
          reply = urequests.put(urlValue,headers=headers,json=propValue).text
          print(reply)
     except Exception as e:
          print(e)         
          reply = 'failed'
     return reply

def Get_SL(Tag):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     try:
          value = urequests.get(urlValue,headers=headers).text
          data = ujson.loads(value)
          
          result = data.get("value").get("value")
     except Exception as e:
          print(e)
          result = 'failed'
     return result
     
def Create_SL(Tag, Type):
     urlBase, headers = SL_setup()
     urlTag = urlBase + Tag
     propName={"type":Type,"path":Tag}
     try:
          urequests.put(urlTag,headers=headers,json=propName).text
     except Exception as e:
          print(e)


#this function will return the base rate of pecking
def Calibrate(): #Function used to find the linear regression between peck number (x) and time at which the peck occured
     fc = open('calibratechickenpecks.csv','a+')
     delta = 0
     prevdelta = 0
     starttime = 0
     currenttime = 0
     times = []
     count = []
     counter = 0
     starttime = time.time()
     while(delta < 10):
          
          currenttime = time.time()
          delta = currenttime-starttime
          #print("Here")
          if touch.pressed() is True and (delta-prevdelta)>.2:
               print("Peck")
               counter = counter + 1
               times.append(delta)
               count.append(counter)
               fc.write(str(counter)+","+str(delta)+'\n')
               prevdelta = delta
     print("Done Calibrating")
     #print("Times: ", times)
     m,b = BestFit(count,times)
     fc.close()
     return m,b

def BestFit(x,y):
     m=0
     b=0
     products = []
     xproducts = []
     predicted_fit = []
     
     for m in range(len(x)):
          products.append(x[m]*y[m])
     for n in range(len(x)):
          xproducts.append(x[n]*x[n])
     
     m = (((Mean(x)*Mean(y))-Mean(products))/((Mean(x)*Mean(x)) - Mean(xproducts)))
     b = (Mean(y) - m*Mean(x))

     return m,b

def Mean(a):
     sum = 0
     #print(a)
     for i in range(len(a)):
          sum = sum + a[i]
     return sum/len(a)

#This function will play the next note in the chicken dance
#The rate of pecking determines how fast the song will play
#The song will play when the program ends

def VictorySong():
     k = 300#duration constant
     letternotes='GggaaeeGggaaccBBAGFffggddFffggbbAAGFEggaaeeGggaaeeGggaaccBBAGFffggddFffggbbAAGFEA'
     notes = []
     durations = []
     ev3.speaker.set_volume(25)
     for i in range(len(letternotes)):
          if letternotes[i].isupper() is True:
               durations.append(k)
          else:
               durations.append(k/2)
          
          if letternotes[i].lower() is "c":
               notes.append(523)
          if letternotes[i].lower() is "b":
               notes.append(493)
          if letternotes[i].lower() is "a":
               notes.append(440)
          if letternotes[i].lower() is "g":
               notes.append(391)
          if letternotes[i].lower() is "f":
               notes.append(349)
          if letternotes[i].lower() is "e":
               notes.append(329)
          if letternotes[i].lower() is "d":
               notes.append(293)
          ev3.speaker.beep(notes[i],durations[i])
          wait(15)
     #print(notes)


#VictorySong()


fp = open('chickenpecks.csv','a+')


#Variables
motorspeed = 100
k1 = 1
k2 = 20
peckrate = 0
start=0
current=0
delt=0
prevdelt=0
interval= 1
counter = 0 
predictedtime = 0
prevpredicted = 0
actualtime = 0
prevactual = 0
error = 1000
prevspeed = 180
isRed = color.color()
#While Loop

print(len(Get_SL('Start11')))
while(touch.pressed()!=True or Get_SL('Start11') is not "true"): #GET SYSTEMLINK WORKING
     #print('here')
     wait(100)
counter = 0
print("Calibrating")
m,b = Calibrate()
ev3.speaker.beep()
wait(1000)
print("Starting Actual Experiment")
start=time.time()
while(isRed==None):
     hitter.run(-motorspeed)
     current = time.time()
     delt = current-start
     #print(delt)
     if touch.pressed() is True and (delt-prevdelt)>.25:
          counter = counter + 1
          actualtime = delt 
          predictedtime = m*counter + b
          print("Predicted time is:", predictedtime)
          error = abs((actualtime-prevdelt)-(predictedtime-prevpredicted))
          print("Error is ",error)
          print("Time is", actualtime)
          prevpredicted = predictedtime

          if actualtime < 15 :
               motorspeed = motorspeed +k1/error
          else:
               motorspeed = motorspeed + k1/(error)+ k2*(actualtime-15)
          fp.write(str(counter)+"," + str(actualtime)+","+ str(predictedtime)+","+str(error)+","+str(motorspeed)+"\n")
          #print("Speed is ",motorspeed)
          prevdelt = delt
          
     isRed=color.color()
     
     
     
     
     isRed = color.color()
     #print(isRed)
     #counter = 0
fp.close()
hitter.run(0)
Put_SL("Start12","BOOLEAN","True")
VictorySong()

    
