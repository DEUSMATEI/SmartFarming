# -*- coding: utf-8 -*-
from __future__ import division
from Tkinter import *
import spidev
import time
import os
import urllib2,json
import RPi.GPIO as GPIO
import httplib, urllib
import I2C_LCD_driver
from PyQt4 import QtCore
import sys
import tkMessageBox
from sys import argv
####################################### Variables ##########################################

#Keys for thingspeak.com
#We must store this data about channel into a local file
#WriteAPI="FY78DVB56QKM46X3"
#ReadAPI="IONWH1HIGS4U041C"
#ID="108248"

#WriteAPI1="YL9I1KQG5501X5VB"
#ReadAPI1="6FRWXPKW6MOEXKI8"
#ID1="123144"

#gpio setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#we start serial communication with sensor sheild
spi=spidev.SpiDev()
spi.open(0,0)

#parameters for process
#important... first thing to do is tpo oinitializate this variables
temperatura_set=0
umiditate_aer_set=0
umiditate_sol_set=0


#sensors
senzor_temp = 0
senzor_lumina = 2
senzor_umiditate_aer = 1
senzor_umiditate_sol = 3
senzor_magnetic=4
senzor_nivel=5

#relay
releu_irigatie=26
releu_alimentare_apa=19
releu_buzzer=13
releu_aux_incalzire=6

#LEDs
LED_verde=16
LED_galben=20
LED_rosu=21

#Outputs for LEDs
GPIO.setup(LED_verde, GPIO.OUT)
GPIO.setup(LED_galben, GPIO.OUT)
GPIO.setup(LED_rosu, GPIO.OUT)

#Outputs for reley
GPIO.setup(releu_irigatie, GPIO.OUT)
GPIO.setup(releu_alimentare_apa, GPIO.OUT)
GPIO.setup(releu_buzzer, GPIO.OUT)
GPIO.setup(releu_aux_incalzire, GPIO.OUT)

#turn off all outputs
GPIO.output(releu_alimentare_apa, False)
GPIO.output(releu_irigatie, False)	
GPIO.output(releu_buzzer, False)

#Input for digital sensor
GPIO.setup(senzor_nivel, GPIO.IN)

# Import the PCA9685 module.
import Adafruit_PCA9685

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

#display
mylcd = I2C_LCD_driver.lcd()

#clear LCD
mylcd.lcd_display_string("                ", 1)
mylcd.lcd_display_string("                ", 2)

####################################### Functions ##########################################

#readding datas from sensors
def readadc(adcnum):
    if((adcnum>7) or (adcnum<0)):
        return -1
    r = spi.xfer2([1,(8+adcnum)<<4,0])
    adcount = ((r[1]&3)<<8)+r[2]
    return adcount

#reminder
        # field1 = temperatura
        # field2 = umiditate aer
        # field3 = umiditate sol
        # field4 = luminozitate
        # field5 = empty
        # field6 = empty
        # field7 = empty

#read configuration data from file 
def citeste_date_canale():
    try:
        with open("Config.txt") as f: content=f.readlines()
    except:
        print "reading problem"
    return content

#sending data to thingspeak.com
def send(ch1, ch2, ch3, ch4, WRITE):
    f = {'field1': ch1, 'field2': ch2, 'field3': ch3, 'field4':ch4, 'key':WRITE}
    params = urllib.urlencode(f) 
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")                
    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()       
        data = response.read()
        conn.close()
    except:
        print "Message from send: connection failed"


#read data from thingspeak.com
def read(ID, READ):
    conn = urllib2.urlopen("http://api.thingspeak.com/channels/" + ID + "/feeds/last.json?api_key="+READ)
    response = conn.read()
    data=json.loads(response)
    return data

#show welcome text to display
mylcd.lcd_display_string("                ", 1)
mylcd.lcd_display_string("                ", 2)
mylcd.lcd_display_string("Bine ai venit", 1)


#Main GUI
mainWindow = Tk()
mainWindow.title("SmartFarming")
mainWindow.geometry('600x300')

#define frames
frame_left_top=Frame(mainWindow, width=50, height=100)
frame_left_top.place(x=0, y=0)
frame_center_top=Frame(mainWindow, width=50, height=50)
frame_center_top.place(x=130, y=0)
frame_right_top=Frame(mainWindow, width=50, height=50)
frame_right_top.place(x=200, y=0)

frame_left_bottom=Frame(mainWindow, width=50, height=100)
frame_left_bottom.place(x=0, y=100)
frame_center_bottom=Frame(mainWindow, width=50, height=50)
frame_center_bottom.place(x=130, y=100)
frame_right_bottom=Frame(mainWindow, width=50, height=50)
frame_right_bottom.place(x=200, y=100)

Rframe_left_top=Frame(mainWindow, width=50, height=100)
Rframe_left_top.place(x=300, y=0)
Rframe_center_top=Frame(mainWindow, width=50, height=50)
Rframe_center_top.place(x=430, y=0)

Rframe_left_bottom=Frame(mainWindow, width=50, height=100)
Rframe_left_bottom.place(x=300, y=100)
Rframe_center_bottom=Frame(mainWindow, width=50, height=50)
Rframe_center_bottom.place(x=430, y=100)

frame_lef=Frame(mainWindow, width=50, height=50)
frame_lef.place(x=0, y=240)

frame_right=Frame(mainWindow, width=50, height=50)
frame_right.place(x=450, y=240)

#define labels for name (show)
l=Label(frame_left_top, text="Temperatura aer: ")
l.pack(side=TOP)
l_1=Label(frame_left_top, text="Umiditate aer: ")
l_1.pack()
l_2=Label(frame_left_top, text="Umiditate sol: ")
l_2.pack()
l_3=Label(frame_left_top, text="Luminozitate: ")
l_3.pack()

#labels for name (set)
l_12=Label(frame_left_bottom, text="Temperatura aer: ")
l_12.pack(side=TOP)
l_13=Label(frame_left_bottom, text="Umiditate aer: ")
l_13.pack()
l_14=Label(frame_left_bottom, text="Umiditate sol: ")
l_14.pack()

#defin labels wich contain data from sensor
l_tem_aer=Label(frame_center_top, text="100")
l_tem_aer.pack(side=TOP)
l_umid_aer=Label(frame_center_top, text="100")
l_umid_aer.pack()
l_umid_sol=Label(frame_center_top, text="100")
l_umid_sol.pack()
l_lum=Label(frame_center_top, text="100")
l_lum.pack()

#define labels for measure units
l_4=Label(frame_right_top, text="°C")
l_4.pack(side=TOP)
l_5=Label(frame_right_top, text="%")
l_5.pack()
l_6=Label(frame_right_top, text="%")
l_6.pack()
l_7=Label(frame_right_top, text="%")
l_7.pack()

#define labels for measure units (set)
l_8=Label(frame_right_bottom, text="°C")
l_8.pack(side=TOP)
l_9=Label(frame_right_bottom, text="%")
l_9.pack()
l_10=Label(frame_right_bottom, text="%")
l_10.pack()

#labels for show channel 1 property
l=Label(Rframe_left_top, text="Canalul 1 ID: ")
l.pack(side=TOP)
l_1=Label(Rframe_left_top, text="Wirte API: ")
l_1.pack()
l_2=Label(Rframe_left_top, text="Read API: ")
l_2.pack()

#labels for show channel 2 property
l=Label(Rframe_left_bottom, text="Canalul 2 ID: ")
l.pack(side=TOP)
l_1=Label(Rframe_left_bottom, text="Wirte API: ")
l_1.pack()
l_2=Label(Rframe_left_bottom, text="Read API: ")
l_2.pack()

def sera():
    temperatura_set= 0
    umiditate_aer_set=0
    umiditate_sol_set=0
    
    #read data from backUp file
    #if there is no internet connection this data will be used for process
    try:
        with open("BackUp.txt") as f: content=f.readlines()
        temperatura_set= int(content[0].rstrip())
        umiditate_aer_set=int(content[0].rstrip())
        umiditate_sol_set=int(content[0].rstrip())
    except:
        print "reading problem"
        
    #read data from temperature sensor
    value = readadc(senzor_temp)
    voltage = value *3.3
    voltage /=1024.0
    temperatureCelsius = (voltage-0.5)*100
   
    #read data from luminosity sensor
    val_l=readadc(senzor_lumina)
    voltage_l=val_l *100.0
    voltage_l/=1024.0
    luminozitate = voltage_l

    #read data from air humidity
    val_u = readadc(senzor_umiditate_aer)
    voltage_u= val_u *100.0
    voltage_u/=1024.0
    umiditate_aer= voltage_u

    #read data from soil moisture sensor
    val_us = readadc(senzor_umiditate_sol)
    voltage_us= val_us *100.0
    voltage_us/=1024.0
    umiditate_sol= voltage_us
    
    
    #converting data to string
    temp=str( int(temperatureCelsius))
    umid_aer=str(int(umiditate_aer))
    umid_sol=str(int(umiditate_sol))
    lum=str(int(luminozitate))
    
    
    #display data on GUI
    if(temperatureCelsius>100.0):
        l_tem_aer["text"]="ERR"
    else:
        l_tem_aer["text"]=temp
    l_umid_aer["text"]=umid_aer
    l_umid_sol["text"]=umid_sol
    l_lum["text"]=lum
    
    #obtain channels info
    conf=citeste_date_canale()
    WriteAPI=conf[1].rstrip()
    ReadAPI=conf[2].rstrip()
    ID=conf[0].rstrip()

    WriteAPI1=conf[4].rstrip()
    ReadAPI1=conf[5].rstrip()
    ID1=conf[3].rstrip()
    
    #send data to thingspeak.com
    send(temperatureCelsius, umiditate_aer, umiditate_sol, luminozitate, WriteAPI)
     
    #read data from thingspeak.com
    data=read(ID1, ReadAPI1)
    try:
        temperatura_set= float(data['field1'])
        umiditate_aer_set=float(data['field2'])
        umiditate_sol_set=float(data['field3'])
        print temperatura_set
    except:
        print "Message from sera there is a problem"

    #compare data from thingspeak with data colectd from sensors
    if (temperatureCelsius >temperatura_set - 3 and temperatureCelsius<temperatura_set + 3 and umiditate_aer<umiditate_aer_set + 10.0 and umiditate_aer>umiditate_aer_set-10.0 ):
    #favorable case. green LED
        GPIO.output(LED_verde, True)
        GPIO.output(LED_galben, False)
        GPIO.output(LED_rosu, False)
        GPIO.output(releu_aux_incalzire, False)
        pwm.set_pwm(0, 0, servo_max)
        pwm.set_pwm(1, 0, servo_max)
        pwm.set_pwm(2, 0, servo_max)
        pwm.set_pwm(3, 0, servo_max)
    else:
    #nefavorable case...... Yellow LED....take an action
        pwm.set_pwm(0, 0, 550)
        pwm.set_pwm(1, 0, 550)
        pwm.set_pwm(2, 0, 450)
        pwm.set_pwm(3, 0, 450)
        GPIO.output(LED_verde, False)
        GPIO.output(LED_galben, True)
        GPIO.output(LED_rosu, False)
        
    #if temerature drop too low an auxiliar relay is turned on for heating system    
    if(temperatureCelsius <temperatura_set - 10):
        GPIO.output(releu_aux_incalzire, True)
    else:
        GPIO.output(releu_aux_incalzire, False)
        
    #allert...... red LED and message   
    if (temperatura_set==0 or umiditate_aer_set==0 or umiditate_sol_set==0 or temperatureCelsius<5.0 or umiditate_sol<10.0 ):
        GPIO.output(LED_verde, False)
        GPIO.output(LED_galben, False)
        GPIO.output(LED_rosu, True)
        #display a message
        mylcd.lcd_display_string("ATENTIE!        ", 1)
        mylcd.lcd_display_string("A aparut o eroare!", 2)
    else:
        #display data to dysplay
        mylcd.lcd_display_string("t="+ temp+" u_aer="+umid_aer, 1)
        mylcd.lcd_display_string("lum=" + lum + "u_sol="+umid_sol, 2)
    #time.sleep(32)
    
def irigatie():
    conf=citeste_date_canale()
    WriteAPI=conf[1].rstrip()
    ReadAPI=conf[2].rstrip()
    ID=conf[0].rstrip()

    WriteAPI1=conf[4].rstrip()
    ReadAPI1=conf[5].rstrip()
    ID1=conf[3].rstrip()
    umiditate_sol_set=0
    
    #read data from soil moisture sensor
    val_us = readadc(senzor_umiditate_sol)
    voltage_us= val_us *100.0
    voltage_us/=1024.0
    umiditate_sol= voltage_us
     
    #read data from thingspeak.com
    data=read(ID1, ReadAPI1)
    try:
        umiditate_sol_set=float(data['field3'])
    except:
        print ""
    irigatie=False
    if(umiditate_sol>umiditate_sol_set -10.0):
            #favorable case
            irigatie=False
            GPIO.output(releu_irigatie, False)
    else:
            GPIO.output(releu_irigatie, True)
            irigatie=True
    #wather system control
    if(GPIO.input(senzor_nivel)==False or irigatie==True):
            GPIO.output(releu_alimentare_apa, False)
    else:
            GPIO.output(releu_alimentare_apa, True)
            
#if the door stay open too much an allarm is turned on
def Monitorizare_usa():
    val = readadc(senzor_magnetic)
    voltage= val *100.0
    voltage/=1024.0
    semnal= voltage
    sec=0
    while(True):
        if(semnal>50):
            sec=sec+1
        else:
            sec=0
        if(sec>60):
            GPIO.output(releu_buzzer, True)
        else:
            GPIO.output(releu_buzzer, False)
        time.sleep(1)
    
class AThread(QtCore.QThread):
   def run (self):
      while True:
            sera()
class BThread(QtCore.QThread):
   def run (self):
      while True:
            irigatie()           
class CThread(QtCore.QThread):
   def run (self):
        Monitorizare_usa()
        
def usingQThread():
   app=QtCore.QCoreApplication([])
   threadA=AThread()
   threadA.finished.connect(app.exit)
   threadA.start()
   threadB=BThread()
   threadB.finished.connect(app.exit)
   threadB.start()
   threadC=CThread()
   threadC.finished.connect(app.exit)
   threadC.start()
   sys.exit(app.exex_())
   
def seteaza_parametri():
    conf=citeste_date_canale()
    WriteAPI=conf[1]
    ReadAPI=conf[2]
    ID=conf[0]

    WriteAPI1=conf[4]
    ReadAPI1=conf[5]
    ID1=conf[3]
    
    temp_set= 0
    umid_aer_set=0
    umid_sol_set=0
    
    #get user input
    in_temp=int( input_temp.get())
    in_umid_aer=int(input_umid_aer.get())
    in_umid_sol=int(input_umid_sol.get())
    

    f = {'field1': in_temp, 'field2': in_umid_aer, 'field3': in_umid_sol, 'key':WriteAPI1}
    params = urllib.urlencode(f) 
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")                
    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()       
        data = response.read()
        conn.close()
    except:
        tkMessageBox.showinfo("Eroare", "Conectarea la server nu a reusit!")
    #save data to a text file (for backUp)     
    target=open('BackUp.txt', 'w')
    target.truncate()
    target.write(str(in_temp))
    target.write("\n")
    target.write(str(in_umid_aer))
    target.write("\n")
    target.write(str(umid_sol_set))
    target.close()
    tkMessageBox.showinfo("SmartFarming", "Datele au fost actualizate cu succes!")
    
def Setare_canale():
    #get data from user input
    #channel 1
    id1=input_ID1.get()
    write1=input_Write1.get()
    read1=input_Read1.get()
    #channel 2
    id2=input_ID2.get()
    write2=input_Write2.get()
    read2=input_Read2.get()
    if(id1=="" or write1=="" or read1=="" or id2=="" or write2=="" or read2==""):
        tkMessageBox.showinfo("Atentie", "Toate campurile sunt obligatorii!")
    else:
        target=open('Config.txt', 'w')
        target.truncate()
        target.write(id1)
        target.write("\n")
        target.write(write1)
        target.write("\n")
        target.write(read1)
        target.write("\n")
        target.write(id2)
        target.write("\n")
        target.write(write2)
        target.write("\n")
        target.write(read2)
        target.close()
        tkMessageBox.showinfo("SmartFarming", "Datele au fost salvate cu succes!")
def programExit():
    GPIO.cleanup()
    exit()
#buttons
button_start=Button(mainWindow, text="Porneste", bg='green', command=usingQThread)
button_start.pack(side=BOTTOM)
button_setare_parametri=Button(frame_lef, text="Seteaza parametri", command=seteaza_parametri)
button_setare_parametri.pack(side=BOTTOM)
button_setare_parametri=Button(frame_right, text="Seteaza canalele", command=Setare_canale)
button_setare_parametri.pack(side=BOTTOM)
exitbutton=Button(mainWindow, text="Iesire", command=programExit, compound=CENTER, bg='red', anchor=CENTER)
exitbutton.pack(side=BOTTOM)

#inputs 
input_temp=Entry(frame_center_bottom, width=5)
input_temp.pack()
input_umid_aer=Entry(frame_center_bottom, width=5)
input_umid_aer.pack()
input_umid_sol=Entry(frame_center_bottom, width=5)
input_umid_sol.pack()

#inputs for channel 1
input_ID1=Entry(Rframe_center_top, width=12)
input_ID1.pack()
input_Write1=Entry(Rframe_center_top, width=12)
input_Write1.pack()
input_Read1=Entry(Rframe_center_top, width=12)
input_Read1.pack()

#inputs for channel 2
input_ID2=Entry(Rframe_center_bottom, width=12)
input_ID2.pack()
input_Write2=Entry(Rframe_center_bottom, width=12)
input_Write2.pack()
input_Read2=Entry(Rframe_center_bottom, width=12)
input_Read2.pack()

mainWindow.mainloop()
#Author Deus Gheorghe Matei
#deus.matei@gmail.com
