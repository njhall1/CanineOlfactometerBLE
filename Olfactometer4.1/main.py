#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:32:41 2021

@author: nathhall
"""

import asyncio
from bleak import BleakClient
from bleak import discover
import UI_4_1 as UI
from PyQt5 import QtCore, QtGui, QtWidgets
from asyncqt import QEventLoop
import fileIO
import time
import sys
from datetime import datetime
import os
import random
import math
myos=os.name

if myos=='posix':
    import pyglet
else: 
    import winsound


##############################################################################

# These values have been randomly generated - they must match between the Central and Peripheral devices
# Any changes you make here must be suitably made in the Arduino program as well
OdorSwitch_CHR = "19B10001-E8F2-537E-4F6C-D104768A1214"
OdorValve_CHR = "19B10002-E8F2-537E-4F6C-D104768A1214"
IRSwitch_CHR = "e82f4442-15dc-44c9-93de-36014d4cee8c"
IRReady_CHR = "e82f4445-15dc-44c9-93de-36014d4cee8c"
SniffTime_CHR = "e82f4443-15dc-44c9-93de-36014d4cee8c"
SniffCrit_CHR= "e82f4444-15dc-44c9-93de-36014d4cee8c"
##############################################################################

###############################################################################
myolfactometers=["Olfactometer1",  "Olfactometer2",  "Olfactometer3"]
###############################################################################

def create_datasheet(subj_ID, folder):
    #C:\Users\DogOdorLab\Documents/AutoPanelData
    now=datetime.now()
    sessiontime=now.strftime("%m_%d_%y_%H_%M_%S")#Create date to save data sheet
    wd=os.getcwd()
    #########################################################################
    #wd="C:/Users/DogOdorLab/Documents/AutoPanelData"
    filename="{}_{}.csv".format(subj_ID, sessiontime)
    datasheet=fileIO.fileIO(("{}/data/{}/{}_{}.csv").format(wd, folder, subj_ID, sessiontime))
    
    header=['subjID', 'expID', 'numbTrials', "alertTime", 
             "trialTime", "session", "daySession", "trainingLevel",
             "handlerBlind", "waitforCorrect", "runCorrections",
             "odorPrevelance", "reinforceBlanks", "reinforceTargets",
             "useTones", "generalizationTest", "autoscoreAlerts",
             "notes", "correctPort", "response",
             "latency", "poke1Number", "poke2Number", "poke3Number",
             "poke4Number", "poke5Number", "poke6Number",
             "cumulative1", "cumulative2", "cumulative3",
             "cumulative4", "cumulative5", "cumulative6",
             "firstResponse",
             "timestamp","port1Odor", "port2Odor", "port3Odor",
             "port4Odor", "port5Odor", "port6Odor",
             "pokeOrder", "pokeTimes", 
             "pokeITI","reinforced", "probe", "TrialNumber", "OdorLine", "DilutionLine", 
             "Concentration", "ReversalNumber"]       
   
        
    datasheet.create(header)
    return(datasheet, filename)
###############################################################################
    
class myapp(UI.Ui_MainWindow):

    def __init__(self,loop):
       UI.Ui_MainWindow.__init__(self)
       self.loop=loop
       self.ready=False
       
       
    def setupApp(self):  
        #Connect buttons to functions 
        self.tabWidget.setCurrentIndex(0)
        self.searchBLE=False
        self.setDefaults()
        self.Info={}
        
        
        #Define Button Actions 
        
        self.ResetOdors.clicked.connect(self.updateOdors)
        self.TrainingLevel.setCurrentIndex(0)
        self.EditOdorList.clicked.connect(lambda: self.changeScreen(5))
        self.pushButton.clicked.connect(self.responseSubmitted)
        self.response_1.clicked.connect(lambda x:self.updateResponse(myolfactometers[0]))
        self.response_2.clicked.connect(lambda x:self.updateResponse(myolfactometers[1]))
        self.response_3.clicked.connect(lambda x:self.updateResponse(myolfactometers[2]))
        self.response_4.clicked.connect(lambda x:self.updateResponse(myolfactometers[3]))
        self.response_5.clicked.connect(lambda x:self.updateResponse(myolfactometers[4]))
        self.response_6.clicked.connect(lambda x:self.updateResponse(myolfactometers[5]))
        self.response_7.clicked.connect(lambda x:self.updateResponse('All Clear'))
        
        self.V1On.stateChanged.connect(self.TestOlfactometers)#Pick up here
        self.BLEScan.clicked.connect(self.scanForOlfactometers)
        self.Submit1.clicked.connect(self.screen1)
        self.ConnectOlfactometers.clicked.connect(self.runTrials) #Start connections and running 
        self.Submit.clicked.connect(self.runTrials)
        
        #Add odor list to boxes
        self.addOdors()
        
    def screen1(self):
        self.Info['DogName']=str(self.DogName.text()).capitalize().strip()
        self.Info['ExpName']=str(self.ExperimenterName.text()).capitalize().strip()
        self.Info['TrainingLevel']= str(self.TrainingLevel.currentText())
        self.tabWidget.setCurrentIndex(1)
        
    def addOdors(self):
        odorFile=fileIO.fileIO("Odors.csv")
        O1=odorFile.lookup(returnval=1,key1="Valve 1")
        O2=odorFile.lookup(returnval=1,key1="Valve 2")
        O3=odorFile.lookup(returnval=1,key1="Valve 3")
        O4=odorFile.lookup(returnval=1,key1="Valve 4")
        O5=odorFile.lookup(returnval=1,key1="Valve 5")
        O6=odorFile.lookup(returnval=1,key1="Valve 6")
        O7=odorFile.lookup(returnval=1,key1="Valve 7")
        O8=odorFile.lookup(returnval=1,key1="Valve 8")
        O9=odorFile.lookup(returnval=1,key1="Valve 9")
        O10=odorFile.lookup(returnval=1,key1="Valve 10")
        O11=odorFile.lookup(returnval=1,key1="Valve 11")
        O12=odorFile.lookup(returnval=1,key1="Valve 12")
        
        odorlist=[O1, O2, O3,O4,O5, O6, O7, O8, O9, O10, O11, O12]
        myboxes=[self.Odor1, self.Odor2, self.Odor3, self.Odor4, self.Odor5, self.Odor6,
                 self.Odor7, self.Odor8, self.Odor9, self.Odor10, self.Odor11, self.Odor12]
        odorIndex=0
        for box in myboxes:
            for i in odorlist:
                box.addItem(i)
            box.setCurrentIndex(odorIndex)
            odorIndex=odorIndex+1
        
    
    def setDefaults(self):
        self.AlertTime.setValue(3.00)
        self.NumberofTrials.setCurrentIndex(1)
        self.TrialTime.setValue(45)
        self.ReinforceBlanks.setCurrentIndex(10)
        self.TargDist_3.setCurrentIndex(1)
        self.TargDist_4.setCurrentIndex(0)
        self.TargDist_5.setCurrentIndex(0)
        self.TargDist_6.setCurrentIndex(0)
        self.comboBox.setCurrentText("Yes")
        self.OdorPrev.setCurrentIndex(0)
        self.NumberofTrials.setCurrentIndex(3)
        self.Response_Box.addItem("")
        self.Submit.setEnabled(False)
        
    def offOdor(self):
        self.Trials.valvestatus="off"
        
    def onOdor(self):
        self.Trials.valvestatus="on"
    
    def nextValve(self):
        self.Trials.valvestatus="next"
    
    def nextOlfactometer(self):
        self.Trials.olfactometerstatus="next"
        
    def scanForOlfactometers(self):
        self.searchBLE=True
        
        
    def changeScreen(self, page):
        self.tabWidget.setCurrentIndex(page)
        
    def responseSubmitted(self):
        self.Trials.R1=self.Response_Box.currentText()
        
    def updateResponse (self, x):
        self.Response_Box.addItem(x)
        self.Response_Box.setCurrentText(x)
        
    # def updateSettings(self):
    #     if self.TrainingLevel.currentText()=="GoNoGo":
    #         print("updating stuff")
    #         self.OdorPrev.setCurrentIndex(5)
            
    #     if self.TrainingLevel.currentText=="AFC":
    #         print("Updating Save Sedttings")
    #         mysettings=fileIO.fileIO("Settings.csv")
    #         print(mysettings.lookup(1, "Number of Trials"))
    #         self.NumberTrials.setCurrentIndex(mysettings.lookup(1, "Number of Trials"))
    #         self.AlertTime.setValue(float(mysettings.lookup(1, "Alert Time")))
    #         self.TrialTime.setValue(float(mysettings.lookup(1, "Trial Time")))
    #         self.Session.setValue(float(mysettings.lookup(1, "Session")))
    #         self.DaySession.setValue(int(mysettings.lookup(1, "Day Session")))
    #         self.HandlerBlind.setCurrentIndex(int(mysettings.lookup(1, "Handler Blind")))
    #         self.WaitforCorrect.setCurrentIndex(int(mysettings.lookup(1, "Wait for Correct")))
    #         self.RunCorrections.setCurrentIndex(int(mysettings.lookup(1, "Run Corrections")))
    #         self.OdorPrev.setCurrentIndex(int(mysettings.lookup(1, "Target Odor Frequency")))
    #         self.ReinforceBlanks.setCurrentIndex(int(mysettings.lookup(1, "Reinforce Blanks")))
    #         self.ReinforceTargets.setCurrentIndex(int(mysettings.lookup(1, "Reinforce Targets")))
    #         self.Context.setCurrentIndex(int(mysettings.lookup(1, "Use Tones")))
    #         self.GenProbes.setCurrentIndex(int(mysettings.lookup(1, "N Generalization Trials")))
    #         self.comboBox.setCurrentIndex(int(mysettings.lookup(1, "AutoScore")))
    #         self.Notes.setText(mysettings.lookup(1, "Notes"))
            
    #         self.TargDist_1.setCurrentIndex(int(mysettings.lookup(1, "Valve1")))
    #         self.TargDist_2.setCurrentIndex(int(mysettings.lookup(1, "Valve2")))
    #         self.TargDist_3.setCurrentIndex(int(mysettings.lookup(1, "Valve3")))
    #         self.TargDist_4.setCurrentIndex(int(mysettings.lookup(1, "Valve4")))
    #         self.TargDist_5.setCurrentIndex(int(mysettings.lookup(1, "Valve5")))
    #         self.TargDist_6.setCurrentIndex(int(mysettings.lookup(1, "Valve6")))
            
            
            
    def updateOdors(self):
        newodors=[str(self.NewOdor_1.text()).capitalize().strip(),
                  str(self.NewOdor_2.text()).capitalize().strip(),
                  str(self.NewOdor_3.text()).capitalize().strip(),
                  str(self.NewOdor_4.text()).capitalize().strip(),
                  str(self.NewOdor_5.text()).capitalize().strip(),
                  str(self.NewOdor_6.text()).capitalize().strip(),
                  str(self.NewOdor_7.text()).capitalize().strip(),
                  str(self.NewOdor_8.text()).capitalize().strip(),
                  str(self.NewOdor_9.text()).capitalize().strip(),
                  str(self.NewOdor_10.text()).capitalize().strip(),
                  str(self.NewOdor_11.text()).capitalize().strip(),
                  str(self.NewOdor_12.text()).capitalize().strip()
                  ]
        
        odorFile=fileIO.fileIO("Odors.csv")
        
        
        row1=["Valve 1", newodors[0]]
        row2=["Valve 2", newodors[1]]
        row3=["Valve 3", newodors[2]]
        row4=["Valve 4", newodors[3]]
        row5=["Valve 5", newodors[4]]
        row6=["Valve 6", newodors[5]]
        row6=["Valve 7", newodors[6]]
        row6=["Valve 8", newodors[7]]
        row6=["Valve 9", newodors[8]]
        row6=["Valve 10", newodors[9]]
        row6=["Valve 11", newodors[10]]
        row6=["Valve 12", newodors[11]]
        odorFile.save_all([row1, row2, row3, row4, row5, row6, 
                           row7, row8, row9, row10, row11, row12])
        
        odorBoxes=[self.Odor1, self.Odor2, self.Odor3, self.Odor4, self.Odor5, self.Odor6,
                   self.Odor7, self.Odor8, self.Odor9, self.Odor10, self.Odor11, self.Odor12]
        
        for box in odorBoxes:
            box.clear()
       
        odorIndex=0
        for box in odorBoxes:
            for i in newodors:
                box.addItem(i)
            box.setCurrentIndex(odorIndex)
            odorIndex=odorIndex+1
                  
        self.tabWidget.setCurrentIndex(3)
        
        
        
    def connectArduinos(self):
            #Generate Names for Each Olfactometer Box Asked for
        OlfactometerNames=[]
        for i in self.OlfactometersFound:
            OlfactometerNames.append("{}".format(i))
           
        Olfactometer_tx=[]
        for i in OlfactometerNames:
            Olfactometer_tx.append("{}_tx".format(i))
            
        Olfactometer_rx=[]
        for i in OlfactometerNames:
            Olfactometer_rx.append("{}_rx".format(i))
            
            #Create a dictionary with the Send Recive Queues for each Olfactometer
        OlfactometerQs={}
        for i in Olfactometer_tx:
            OlfactometerQs[i]=asyncio.Queue()
        for i in Olfactometer_rx:
            OlfactometerQs[i]=asyncio.Queue()
            
            #Initialize each Olfactometer with a Stream of input/ouput Data 
        devices={}
        for i in range(0,len(OlfactometerNames)):
            devices[OlfactometerNames[i]]=Olfactometer(OlfactometerNames[i],
                                                           OlfactometerQs[Olfactometer_tx[i]],
                                                           OlfactometerQs[Olfactometer_rx[i]])
            
        return(devices, OlfactometerQs)   


     
    def collectUserInput(self):
         #Collect User input
        
        self.Info['NumberTrials']=int(self.NumberofTrials.currentText())
        self.Info['SniffTime']=int(float(self.AlertTime.value())*1000) #Convert to millisecond 
        self.Info['AddSniffTime']=int(float(self.AlertTime_2.value())*1000) #Convert to millisecond 
        self.Info['TrialTime']=int(self.TrialTime.value())
        self.Info['SessionNumber']=self.Session.value()
        self.Info['DaySession']=self.DaySession.value()
        self.Info['HandlerBlind']=str(self.HandlerBlind.currentText())
        

        self.Info['WaitforCorrect']=str(self.WaitforCorrect.currentText())
        self.Info['OdorPrev']=float(self.OdorPrev.currentText())
        self.Info['ReinforceBlanks']=float(self.ReinforceBlanks.currentText())
        self.Info["ReinforceTargets"]=float(self.ReinforceTargets.currentText())
        self.Info['Tones']=str(self.Context.currentText())
        self.Info['GeneralizationProbes']=int(self.GenProbes.currentText())
        self.Info['AutoScore']=str(self.comboBox.currentText())
        self.Info['Connection']=str(self.connection.currentText())
        self.Info['Notes']=str(self.Notes.text()).capitalize().strip()
        
        self.Info["Odor1"]=self.Odor1.currentText()
        self.Info["Odor2"]=self.Odor2.currentText()
        self.Info["Odor3"]=self.Odor3.currentText()
        self.Info["Odor4"]=self.Odor4.currentText()
        self.Info["Odor5"]=self.Odor5.currentText()
        self.Info["Odor6"]=self.Odor6.currentText()
        
        self.Info["Odor1Type"]=self.TargDist_1.currentText()
        self.Info["Odor2Type"]=self.TargDist_2.currentText()
        self.Info["Odor3Type"]=self.TargDist_3.currentText()
        self.Info["Odor4Type"]=self.TargDist_4.currentText()
        self.Info["Odor5Type"]=self.TargDist_5.currentText()
        self.Info["Odor6Type"]=self.TargDist_6.currentText()
        
        self.Info["odorLine"]=float(self.odorLine.currentText())
        self.Info["airLine"]=float(self.airLine.currentText())
        self.Info["concentration"]=self.Info['odorLine']/(self.Info["odorLine"]+self.Info["airLine"])
        
        mytargets=[]
        mydistractors=[]
        myprobes=[]
        mypurge=[]
        mykeys=["Odor1Type", "Odor2Type", "Odor3Type", "Odor4Type", "Odor5Type", "Odor6Type",
               "Odor7Type", "Odor8Type", "Odor9Type", "Odor10Type", "Odor11Type", "Odor12Type" ]
        mykeys2=["Odor1", "Odor2", "Odor3", "Odor4", "Odor5", "Odor6",
                 "Odor7", "Odor8", "Odor9", "Odor10", "Odor11", "Odor12",]
        
        for i in range(0, len(mykeys)):
            if self.Info[mykeys[i]]=="Target":
                mytargets.append(self.Info[mykeys2[i]]) 
            elif self.Info[mykeys[i]]=="Probe":
                myprobes.append(self.Info[mykeys2[i]])  
            elif self.Info[mykeys[i]]=="Distractor":
                mydistractors.append(self.Info[mykeys2[i]])
            elif self.Info[mykeys[i]]=="Purge":
                mypurge.append(self.Info[mykeys2[i]])
            else:
                pass
              
        self.Info["Targets"]=mytargets
        self.Info["Distractors"]=mydistractors
        self.Info['Probes']=myprobes
        self.Info['Purge']=mypurge
        
        
        
        myweights=[]
        if self.Info["Odor1Type"]=="Target":
            myweights.append(int(self.OdorWeights_1.currentText()))
        if self.Info["Odor2Type"]=="Target":
            myweights.append(int(self.OdorWeights_2.currentText()))
        if self.Info["Odor3Type"]=="Target":
            myweights.append(int(self.OdorWeights_3.currentText())) 
        if self.Info["Odor4Type"]=="Target":
            myweights.append(int(self.OdorWeights_4.currentText())) 
        self.Info["OdorWeights"]=myweights
        
        
        
    def runTrials(self):
        #Get values and deactivate user input
        self.Submit.setEnabled(False)
        self.tabWidget.setCurrentIndex(1)
        self.collectUserInput() 
        self.initializeSession()
        
        
       
        
    def initializeSession(self):
        self.devices, self.OlfactometerQs=self.connectArduinos()
        self.Info["WindowController"]=self
   
        #Start Testing Thread
        print("Initializing Threads")
        if self.Info['TrainingLevel']=="AFC":
                self.Info['datasheet'], self.Info['filename'] =create_datasheet(self.Info['DogName'], self.Info['TrainingLevel']) 
                self.Trials= AFC_SessionLoop(self.devices, self.OlfactometerQs, self.Info)
        
        elif self.Info['TrainingLevel']=="Threshold":
                self.Info['datasheet'], self.Info['filename'] =create_datasheet(self.Info['DogName'], self.Info['TrainingLevel']) 
                self.Trials= AFC_SessionLoop(self.devices, self.OlfactometerQs, self.Info)
                

            
            #Set Connections to update User info
        self.Trials.statusUpdate.connect(self.infoLabel.setText)
        self.Trials.portStatus.connect(self.Response_Box.setCurrentText)
        self.Trials.trialNum.connect(self.trialNumber.display)
        self.Trials.msg.connect(self.exception_screen)
        self.Trials.concentration1.connect(self.Position1_2.setText)
        self.Trials.concentration2.connect(self.Position1_3.setText)
        self.ready=True
            #asyncio.run_coroutine_threadsafe(self.runOlfactometers(), self.loop)
            #Add Slots for Manual Port Data Collection 
         
            
            
    async def runOlfactometers(self):
        print("Looking for Olfactometers")
        self.OlfactometersFound=[]
        while not self.ready:
            if self.searchBLE==True:
                print("looking for BLE")
                #Clear anything from previous pushes 
                self.OlfactometersFound=[]
                self.OlfactometerList.clear()
                print("Collecting Devices")
                devices = await discover()
                for d in devices:
                    print(d)
                    print (d.name)
                    try: 
                        if "Olfactometer" in d.name:
                            if d.name in myolfactometers:
                                self.OlfactometerList.addItem(d.name)
                                self.OlfactometersFound.append(d.name)
                    except:
                        pass
                self.searchBLE=False #Make sure it only Runs Once
                self.Submit.setEnabled(True)
                
            await asyncio.sleep(1)
            
        
        print("Starting Olfactometer Threads")
        await asyncio.gather(*(self.devices[key].connect() for key in self.devices),
                             self.Trials.run()) 
                        

    def exception_screen(self, msg):
        choice=QtWidgets.QMessageBox.question(self.centralwidget, 'Alert', msg,
                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        return choice
        pass
  



      

class AFC_SessionLoop (QtCore.QThread):
    statusUpdate=QtCore.pyqtSignal(str)
    portStatus=QtCore.pyqtSignal(str)
    trialNum=QtCore.pyqtSignal(int)
    msg=QtCore.pyqtSignal(str)
    R1=QtCore.pyqtSignal(str)
    concentration1=QtCore.pyqtSignal(str)
    concentration2=QtCore.pyqtSignal(str)
   
    
    def __init__(self, Devices, Qs, Info):     
        super().__init__()
        self.stopped = QtCore.QEvent(QtCore.QEvent.User)
        self.stopped.setAccepted(False)
        self.devices=Devices
        self.Info=Info
        self.Qs=Qs
        self.RunSession=False
        print("Session Loop Initialized")
      
        
    def loadAudio(self):
        wd=os.getcwd()  
        if myos=='posix':
            self.sound=pyglet.media.load('{}/Tones/food.wav'.format(wd), streaming=False)
            self.tone=pyglet.media.load('{}/Tones/432_short.wav'.format(wd), streaming=False)
            self.fail=pyglet.media.load('{}/Tones/fail_buzzer.wav'.format(wd), streaming=False)
            self.end=pyglet.media.load('{}/Tones/beepEnd.wav'.format(wd), streaming=False)
        else:     
            self.sound ='{}/Tones/food.wav'.format(wd)
            self.tone ='{}/Tones/432_short.wav'.format(wd)
            self.fail ='{}/Tones/fail_buzzer.wav'.format(wd)
            self.end ='{}/Tones/beepEnd.wav'.format(wd)
        
        
    def playAudio(self, audio):
        if self.Info["Tones"]=="Yes":
            if myos=="posix":
                audio.play()
            else:
                winsound.PlaySound(audio, winsound.SND_FILENAME)
       
        
    async def initializeRun(self):
        #Load Audios
        self.loadAudio()
        
        self.Info["ReversalNumber"]=0
        self.Info["ConcentrationDirection"]="None" 
        self.Info["ConcentrationIndex"]=0
        self.Info["Flag"]="none"
        
        
        #Wait until all devices indicated they are connected
        for key in self.devices:      
            while self.Qs["{}_rx".format(key)].empty(): 
                 await asyncio.sleep(0)
            if not self.Qs["{}_rx".format(key)].empty():
                print("Recieved message from olfactometer: ")
                print(self.Qs["{}_rx".format(key)].get_nowait())


      #Create Randomized Trials for session
        self.odors, self.valves, self.odorNames = self.createOdorDictionary()
        self.trialOrder, self.outcome, self.probes=self.createTrialOrder()
      
        #Deactivate any valves that maybe on previously
        self.odorsOff()
        
        #Update the Alert Time
        for key in self.devices:
                 await self.Qs["{}_tx".format(key)].put(("updateSniff", self.Info['SniffTime']))
  
    
      
    async def run(self):   
        print("Session Loop Started")
        await self.initializeRun()
        self.correctList=[]
        self.wrongList=[]
        trial=0
        await asyncio.sleep(1)
        for i in self.trialOrder:
            await self.changeSniffTime()
            port=i
            self.updateMessage(port, trial+1)
            print("Sending Message to Turn On Odor")
            await self.odorOn(port, self.probes[trial])
            print ("Waiting for confirmation of olfactometer msg sent")
            await self.waitForMessageReceipt()
            #Start the Trial
            self.startTime= time.time()
            self.playAudio(self.tone)
            
            print("Looking for Response")
            self.Trial= await self.lookForResponse(port=port, 
                                            waitforcorrect=self.Info["WaitforCorrect"],
                                            timeout= self.Info["TrialTime"], 
                                            blankSearch="yes")
             
            print("Scoring Response for feedback {}".format(self.Trial['response']))
            self.giveFeedback(port, trial)
            self.odorsOff() #Clear the ports
           
            self.Trial["reinforce"]=self.outcome[trial]
            self.Trial["probe"]=self.probes[trial]
            self.Trial['TrialNumber']=trial+1
            print ("Saving Data")
            self.recordData()
            
            #If this is a threshold test- see if we need to change Concentration 
            await self.CheckforModifications()
            
            if self.Info["Flag"]=="passed":
                
                break
            
            #ITI
            print("Going to ITI")
            await asyncio.sleep(20)
            self.portStatus.emit("")
            trial=trial+1
           
            
        self.statusUpdate.emit("Finished")

        
    async def CheckforModifications(self):
        if self.Info['TrainingLevel']=="Threshold": #Check if concentration needs to be changed
            if self.correctList[-1]==0: #Wrong Go Up 
                self.correctList=[]
                #Check if reversal or direction change
                if self.Info["ConcentrationDirection"]=="Down":
                    self.Info["ReversalNumber"]=self.Info["ReversalNumber"]+1
                    self.Info["ConcentrationDirection"]="Up"
                
                if self.Info["ReversalNumber"]==7:
                        self.Info["Flag"]="passed"
               
                if self.Info["ConcentrationIndex"]>0:
                    self.Info["ConcentrationIndex"]=self.Info["ConcentrationIndex"]-1
                    if self.Info["Flag"]!="passed":
                           await self.AlertConcentrationChange()
                   
                
            elif len(self.correctList)>2: 
                if sum(self.correctList)>=3:
                    self.correctList=[]
                    
                    #If first down, set direction to down
                    if self.Info["ConcentrationDirection"]=="None":
                        self.Info["ConcentrationDirection"]="Down"
                        
                    #Check if reversal or direction change
                    if self.Info["ConcentrationDirection"]=="Up":
                        self.Info["ReversalNumber"]=self.Info["ReversalNumber"]+1
                        self.Info["ConcentrationDirection"]="Down"
                        
                    if self.Info["ReversalNumber"]==7:
                        self.Info["Flag"]="passed"
                        
                    if self.Info["ConcentrationIndex"]<5:
                        self.Info["ConcentrationIndex"]=self.Info["ConcentrationIndex"]+1
                       
                        if self.Info["ConcentrationIndex"]>4:
                            self.Info["Flag"]="passed"
                            
                        if self.Info["Flag"]!="passed":
                           await self.AlertConcentrationChange()
                   
                    
               
                
                
    async def AlertConcentrationChange(self):
        concentrations=[0.8, 0.50, 0.25, 0.12, 0.03]
        self.Info["concentration"]=concentrations[self.Info["ConcentrationIndex"]]
        self.Info["WindowController"].tabWidget.setCurrentIndex(2)
        if self.Info["ConcentrationIndex"]==0:
            o1=1000
            o2=0.25
        elif self.Info["ConcentrationIndex"]==1:
            o1=1000
            o2=1.0
        elif self.Info["ConcentrationIndex"]==2:
            o1=750
            o2=2.25
        elif self.Info["ConcentrationIndex"]==3:
            o1=360
            o2=2.65
        elif self.Info["ConcentrationIndex"]==4:
            o1=90
            o2=2.91
            
        self.concentration1.emit(str(o1))
        self.concentration2.emit(str(o2))
        self.Info["odorLine"]=o1
        self.Info["airLine"]=o2
        self.blankOn()
        await asyncio.sleep(2)
        await self.waitForMessageReceipt()
        await self.lookForResponse(port="port1", 
                                            waitforcorrect=self.Info["WaitforCorrect"],
                                            timeout= self.Info["TrialTime"], 
                                            blankSearch="yes")
        self.odorsOff()
        self.Info["WindowController"].tabWidget.setCurrentIndex(1)
       
        
        
        
        
    async def changeSniffTime(self):
        addRandom=random.uniform(0, self.Info['AddSniffTime'])
        self.Info['TrialSniff']=self.Info['SniffTime']+addRandom
        #If the time needs updating, do it.
        if addRandom!=0: 
             for key in self.devices:
                 await self.Qs["{}_tx".format(key)].put(("updateSniff", self.Info['TrialSniff']))
       
        

    async def waitForMessageReceipt(self):
        for key in self.devices: 
            print("looking for sent receipt")
            confirmed=False
            while not confirmed:
                await asyncio.sleep(0)
                print("Waiting for send confirmation")
                if not self.Qs["{}_rx".format(key)].empty():
                   val= await self.Qs["{}_rx".format(key)].get()
                   self.Qs["{}_rx".format(key)].task_done()
                   if val=="Sent":
                       confirmed=True
                       

    def updateMessage(self, port, trial):
        self.trialNum.emit(trial)
        message="Blind"
        if self.Info["HandlerBlind"]=="No":
            message=port
        self.statusUpdate.emit(message)
            
        
        
    def giveFeedback(self, port, trial):  
        if self.outcome[trial]==1:
            if port==self.Trial['response']:
                self.playAudio(self.sound)
                time.sleep(1)
                self.playAudio(self.end)
                self.statusUpdate.emit("Correct")
                self.correctList.append(1)
                
            
            elif port=="blank" :
                if self.Trial['response']=="All Clear":
                    self.playAudio(self.sound)  
                    time.sleep(1)
                    self.playAudio(self.end)
                    self.statusUpdate.emit("Correct")
                    self.correctList.append(1)
                    
                if self.Trial['response']!= "All Clear":
                    self.playAudio(self.fail)
                    time.sleep(0.5)
                    self.playAudio(self.end)
                    self.statusUpdate.emit("Wrong")
                    self.correctList.append(0)
        
            else: 
                self.playAudio(self.fail)
                self.playAudio(self.end)
                self.statusUpdate.emit("Wrong")
                self.correctList.append(0)
       
        elif self.outcome[trial]==0:
            if port =="blank":
                if self.Trial['response']!="All Clear":
                    self.playAudio(self.fail)
                    self.statusUpdate.emit("Wrong")
                    self.correctList.append(0)
                    
            self.playAudio(self.end)
            self.statusUpdate.emit("Unknown")
         
            
    def createTrialOrder(self):
        blocknumber=10
        if self.Info["OdorPrev"]<0.1:
            blocknumber=self.Info['NumberTrials']
        
        trialTypes=[]
        
        Odorreinforce=[]
        Blankreinforce=[]
        
        probes=self.Info["GeneralizationProbes"]
            
        reinforcerList=[]
        probenumbers=[]
        probeList=[]
        blocks=round(self.Info['NumberTrials']/blocknumber)

        #Calculate number of odor and non odor trials for a block of 10 trials
        odornumber=int(round(blocknumber*self.Info["OdorPrev"]))
        blanknumber=int (round(blocknumber-odornumber))
    
        eachportnumber=math.floor(odornumber/len(self.devices))
        unbalance=odornumber%len(self.devices) # get the remainder of dividing odor number by 3
       
        Odorreinforcenumber=int(math.floor(odornumber*self.Info["ReinforceTargets"]*blocks))
        nonreinforceodornumber=(blocks*odornumber)-Odorreinforcenumber
        
        Blankreinforcenumber=int(math.floor(blanknumber*self.Info["ReinforceBlanks"]*blocks))
        nonreinforceblanknumber=(blocks*blanknumber)-Blankreinforcenumber
        
        for i in range(0,Odorreinforcenumber):
            Odorreinforce.append(1)
        for i in range(0, nonreinforceodornumber):
            Odorreinforce.append(0)
        random.shuffle(Odorreinforce)
        
        for i in range(0, Blankreinforcenumber):
            Blankreinforce.append(1)
        for i in range(0, nonreinforceblanknumber):
            Blankreinforce.append(0)
        random.shuffle(Blankreinforce)
           
        for i in range(0, probes): 
            probenumbers.append(1)    
        for i in range(0, len(Odorreinforce)-probes):
            probenumbers.append(0)
        random.shuffle(probenumbers)
        

        for i in range(0,blocks): #4 block of 10 trials for 40 trials
            odorlist=[]
            portlist=[]
            for key in self.devices:
                portlist.append(key)
                
            #Make an odor list with each of the olfactometer numbers for the number of times the port should appear    
            for i in range(0, eachportnumber):
                for i in portlist:
                    odorlist.append(i)
             
            additionals=random.sample(portlist,unbalance)
            odorlist=odorlist+additionals
            for i in range (0, blanknumber):
                odorlist.append('blank')
            #shuffle to randomize the mix
            random.shuffle(odorlist)
            trialTypes=trialTypes+odorlist 
        
        reinforcerIndex=0
        blankReinforceIndex=0
        
        for i in trialTypes:
            if i != "blank":
                toReinforce=Odorreinforce[reinforcerIndex]
                if probenumbers[reinforcerIndex]==1:
                    toReinforce=0
    
                reinforcerList.append(toReinforce)
                probeList.append(probenumbers[reinforcerIndex])
                reinforcerIndex=reinforcerIndex+1
            else:
                reinforcerList.append(Blankreinforce[blankReinforceIndex])
                blankReinforceIndex=blankReinforceIndex+1
                probeList.append(0)
        print (trialTypes)
        return(trialTypes, reinforcerList, probeList)
    
     
    
    def createOdorDictionary(self):
        #Create Dictionary of odors
        myodors={}
        myvalves={}
        pins=[1,2,3,4,5,6]
        Odornames=[self.Info["Odor1"], self.Info["Odor2"],self.Info["Odor3"],
               self.Info["Odor4"], self.Info["Odor5"],self.Info["Odor6"]]
        index=0        
        for i in pins:
            myodors[i]=Odornames[index]
            myvalves[Odornames[index]]=i
            index=index+1    
        return(myodors, myvalves, Odornames)
           
    
        
    def recordData(self):
        now=datetime.now()
        timestamp=now.strftime("%m_%d_%y_%H_%M_%S")
        pokes=[]
        for i in myolfactometers:
            pokes.append("pokenumber_{}".format(i))
        cumulative=[]
        for i in myolfactometers:
            cumulative.append("cumulative_{}".format(i))
        #Note, may need to fill out this list if <6 olfactometers are used
        Os=[]
        for i in myolfactometers:
            Os.append(i)
        
        trialData=[self.Info["DogName"], self.Info["ExpName"],
                   self.Info["NumberTrials"],
                   self.Info["TrialSniff"], self.Info["TrialTime"],
                   self.Info["SessionNumber"], self.Info['DaySession'],
                    self.Info['TrainingLevel'],self.Info["HandlerBlind"],
                    self.Info["WaitforCorrect"], 'NA',
                    self.Info["OdorPrev"], self.Info["ReinforceBlanks"],
                    self.Info["ReinforceTargets"], self.Info["Tones"],
                    self.Info["GeneralizationProbes"], self.Info["AutoScore"],
                   self.Info["Notes"],
                   self.Trial["correctPort"],
                   self.Trial['response'], self.Trial['latency'],
                   self.Trial[pokes[0]], self.Trial[pokes[1]],
                   self.Trial[pokes[2]],
                   self.Trial[pokes[3]], 
                   self.Trial[pokes[4]],
                   self.Trial[pokes[5]],
                   self.Trial[cumulative[0]], 
                   self.Trial[cumulative[1]], 
                   self.Trial[cumulative[2]],
                   self.Trial[cumulative[3]], 
                   self.Trial[cumulative[4]], 
                   self.Trial[cumulative[5]],
                   self.Trial['firstResponse'],timestamp,
                   self.olfactometerOdors[Os[0]], self.olfactometerOdors[Os[1]],
                   self.olfactometerOdors[Os[2]],self.olfactometerOdors[Os[3]],
                   self.olfactometerOdors[Os[4]],self.olfactometerOdors[Os[5]], 
                   self.Trial["pokeOrder"], self.Trial["pokeTimes"], 
                   self.Trial["ITIs"],
                   self.Trial["reinforce"], self.Trial["probe"], self.Trial["TrialNumber"],
                   self.Info["odorLine"], self.Info["airLine"], self.Info['concentration'],
                   self.Info["ReversalNumber"]]
        
        self.Info['datasheet'].appendrow(trialData)
  
    
    
    async def odorOn(self, port, probe=0):
        #Activate the Target port and distractor for the remainder
        Targets=self.Info['Targets']
        Distractors=self.Info['Distractors']
        Probes=self.Info['Probes']
        
        self.olfactometerOdors={}
        for i in myolfactometers:
            self.olfactometerOdors[i]="NA"
        #Pre-fill the dictionary with NA for data sheet whether used or not. 
            
        for key in self.devices:
            if key==port:
                target=random.choices(Targets, weights=self.Info["OdorWeights"])[0]
                if probe==1:
                    target=Probes[0]
                valve=str(self.valves[target])
                await self.Qs["{}_tx".format(key)].put(("activateValve", valve))
                self.olfactometerOdors[key]=target
                
            else:
                distractor=random.choice(Distractors)
                valve=str(self.valves[distractor])
                await self.Qs["{}_tx".format(key)].put(("activateValve", valve))
                self.olfactometerOdors[key]=distractor
        
                                   
    def odorsOff(self):
        for key in self.devices:
            self.Qs["{}_tx".format(key)].put_nowait(("deactivateValve", 0))
             
    def blankOn(self):
        for key in self.devices:
            self.Qs["{}_tx".format(key)].put_nowait(("activateValve", '6'))
            
        
            
    async def lookForResponse(self, port, waitforcorrect, timeout, blankSearch):
        self.Trial={}
        self.Trial["correctPort"]=port
        self.isSniffed=0
        self.startTime=time.time()
        self.Trial['response']=0
        self.Trial['latency']=0
        self.Trial['ITIs']=[]
        self.R1="0"
        self.pokeRecorded=0
        
     
            
        for i in myolfactometers:
            self.Trial['pokenumber_{}'.format(i)]=0      
        for i in myolfactometers:
            self.Trial['cumulative_{}'.format(i)]=0
       
        self.Trial['firstResponse']=0
        self.Trial['pokeOrder']=[]
        self.Trial['pokeTimes']=[]
        self.cumulativeResponses={}
        for i in myolfactometers:
            self.cumulativeResponses[i]=0
        self.lastResponse=time.time()
        self.waitforcorrect=waitforcorrect
        allpoked=0
        
        await self.clearQs()
          
        #Activate Arduinos to look for IR beams
        for key in self.devices:
            if self.Qs["{}_tx".format(key)].empty():
                self.Qs["{}_tx".format(key)].put_nowait(("readIR", 0))
                
        while(self.Trial['response']==0):
            #print("Looking for Pokes")
            await self.lookForPokes() 
            if self.Info["AutoScore"]=="No": #Check for a manual response
                if self.R1!="0":
                    if self.Trial['firstResponse']==0:
                        self.Trial['firstResponse']=self.R1
                    if self.waitforcorrect=="Yes":
                        if self.R1==port:
                            self.Trial['response']=self.R1
                    else:
                        self.Trial['response']=self.R1
                        
                if self.Trial['response']==0:#Check for a timeout
                          if time.time()-self.startTime>timeout:
                              self.Trial['response']="timeout"
                 
                    
            elif self.Info["AutoScore"]=="Yes":
                for key in self.devices:
                    if float(self.cumulativeResponses[key])>self.Info["TrialSniff"]:
                        if self.Trial['firstResponse']==0:
                            self.Trial['firstResponse']=key
                        if self.waitforcorrect=="Yes":
                            if key==port:
                                self.Trial['response']=key
                        elif self.waitforcorrect=="No":
                            self.Trial['response']=key
                    npokes=0        
                    for key in self.devices:
                        if self.Trial["pokenumber_{}".format(key)]>0:
                            npokes=npokes+1
                    if npokes==len(self.devices):
                        allpoked=1
                    
                    if allpoked!=0 and time.time()-self.lastResponse>((self.Info["TrialSniff"]+10000)/1000):
                        if self.waitforcorrect=="Yes":
                            if port=="blank":
                                self.Trial['response']="All Clear"
                        else: 
                            self.Trial['response']="All Clear"
                            
                    if self.Trial['response']==0:#Check for a timeout
                          if time.time()-self.startTime>timeout:
                              self.Trial['response']="timeout"
                    
                           
            await asyncio.sleep(0)
      
        await self.endPokes()
       
        return(self.Trial)  
   
    async def endPokes(self):
        for key in self.devices:
            if self.Qs["{}_tx".format(key)].empty():
                self.Qs["{}_tx".format(key)].put_nowait(("endIR", 0))
                
    async def clearQs(self):
        #Empty any leftover inbound data that might have come in from a previosu trial 
          for key in self.devices:
            while not self.Qs["{}_rx".format(key)].empty(): 
                 print ("clearing Qs ")
                 olfactometer, msg = await  self.Qs["{}_rx".format(key)].get()
                 self.Qs["{}_rx".format(key)].task_done()
                 
                 
    async def lookForPokes(self):
        #Check to see if there is poke data available. If so, process it
        #Process data until each Q is empty
        #Ask each olfactometer to look out for a new poke
        
        for key in self.devices:
            if not self.Qs["{}_rx".format(key)].empty(): #If poke data is available process all of it
                print("Processing IR Q for {}".format(key))
                olfactometer, msg = await  self.Qs["{}_rx".format(key)].get()
         
                if msg!=0.0: #If a poketotal is ready to record, record it.
                    self.Trial["pokenumber_{}".format(key)]=self.Trial["pokenumber_{}".format(key)]+1
                    self.Trial["cumulative_{}".format(key)]=self.Trial["cumulative_{}".format(key)]+msg
                    self.Trial["pokeOrder"].append(key)
                    self.Trial["pokeTimes"].append(msg)
                    self.Trial["ITIs"].append(time.time()-self.lastResponse)
                    self.cumulativeResponses[key]=msg
                    self.lastResponse=time.time()
                    if self.pokeRecorded==0:
                        self.Trial['Latency']=time.time()-self.startTime
                        self.pokeRecorded=1
                        
                self.Qs["{}_rx".format(key)].task_done()
                
                await asyncio.sleep(0)
               

    

 
##############################################################################    
class Threshold_SessionLoop (AFC_SessionLoop):
    statusUpdate=QtCore.pyqtSignal(str)
    portStatus=QtCore.pyqtSignal(str)
    trialNum=QtCore.pyqtSignal(int)
    msg=QtCore.pyqtSignal(str)
    R1=QtCore.pyqtSignal(str)
    
   
    
    def __init__(self, Devices, Qs, Info):     
        super().__init__()
        self.stopped = QtCore.QEvent(QtCore.QEvent.User)
        self.stopped.setAccepted(False)
        self.devices=Devices
        self.Info=Info
        self.Qs=Qs
        print("Session Loop Initialized")               
        
        
##############################################################################     
class Test_SessionLoop (AFC_SessionLoop):
    statusUpdate=QtCore.pyqtSignal(str)
    portStatus=QtCore.pyqtSignal(str)
    trialNum=QtCore.pyqtSignal(int)
    msg=QtCore.pyqtSignal(str)
    R1=QtCore.pyqtSignal(str)
    olfactNumber=QtCore.pyqtSignal(str)
    valveNumber=QtCore.pyqtSignal(str)
    valvestatus=QtCore.pyqtSignal(str)
    olfactometerstatus=QtCore.pyqtSignal(str)
   
    def __init__(self, Devices, Qs, Info):     
        super().__init__(Devices, Qs, Info)
        self.stopped = QtCore.QEvent(QtCore.QEvent.User)
        self.stopped.setAccepted(False)
        self.devices=Devices
        self.Info=Info
        self.Qs=Qs
        print("Session Loop Initialized")       

    async def run(self):   
        self.valvestatus="null"
        self.olfactometerstatus="null"
        await self.initializeRun()
        await self.changeSniffTime()
        
    
       
        
        print("Session Loop Started")
        
        for key in self.devices:
            self.olfactNumber.emit(key)
            for v in range(1,7):    
                 v=str(v)
                 print("Activating Valve")
                 await self.Qs["{}_tx".format(key)].put(("activateValve", v))
                 await self.waitForMessageReceipt()
                 await asyncio.sleep(1)
                 self.valveNumber.emit(v)
                 while self.valvestatus!="next":
                     pass
                     await asyncio.sleep(1)
                 
                 self.odorsOff() 
                 self.valvestatus='null'
    
    
    
    
#############################################################################   
class Olfactometer(object):
    
    def __init__(self, olfactometerName, tx_Q, rx_Q):   
        self.name=olfactometerName
        self.tx_Q=tx_Q
        self.rx_Q=rx_Q
        

    async def connect (self):
        print('Looking for {}.'.format(self.name))
        found = False
        devices = await discover()
       
        for d in devices:   
            if self.name == d.name:
                while not found:
                    print("Trying to Connect to {}".format(d.name))
                    try:
                        async with BleakClient(d.address) as self.olfactometer:
                            print(f'Connected to {d.name}')
                            #await asyncio.sleep(4)
                            found = True
                            await self.run()
                    except:
                        print("Issue finding {}".format(self.name))
                    


        
    async def run(self):
        self.rx_Q.put_nowait("Connected")
        print("Signaling {} is connected".format(self.name))
        await self.olfactometer.start_notify(SniffTime_CHR, self.checkIR)
        #Run forever a send/rx stream forever
        while True:
           # print("Send Q status {}".format(self.send_Q.empty()))
            if not self.tx_Q.empty():
                command, val1 = await self.tx_Q.get()
                print("{} Processing Command of {} with value of {}".format(self.name, command,val1))
                await self.process_command(command, val1)
                self.tx_Q.task_done()
                print("Command Processed")
            else:
                #print("Nothing to work on")
                pass
            await asyncio.sleep(0)
        
    
    async def process_command(self, command, val1):
        if command=="activateValve":
            await self.activateValve(val1)
        elif command=="deactivateValve":
            await self.deactivateValve(val1)
        elif command=="deactivateAll":
            await self.deactivateAll()
        elif command=="readIR":
            await self.readIR()
        elif command=="endIR":
            await self.endIR()
        elif command=="updateSniff":
            await self.updateSniff(val1)
        
    
    async def activateValve(self, pin):
        print("Activating Valve {}".format(pin))
        pin=bytes(pin, "utf-8")
        print("converted to bites {}".format(pin))
        await self.olfactometer.write_gatt_char(OdorValve_CHR, pin)
        await self.olfactometer.write_gatt_char(OdorSwitch_CHR, b'1')
        print("Sent pin Number")
        self.rx_Q.put_nowait("Sent")

    # async def deactivateValve(self, pin):
    #     pin=bytes(pin, "utf-8")
    #     await self.olfactometer.write_gatt_char(OdorValve_CHR, pin)
    #     await self.olfactometer.write_gatt_char(OdorSwitch_CHR, b'2')
        
    async def deactivateValve(self, pin):
        await self.olfactometer.write_gatt_char(OdorSwitch_CHR, b'0')

    async def readIR(self):
        pass
        #await self.olfactometer.write_gatt_char(IRSwitch_CHR, b'1')
        
        
    async def endIR(self):
        pass
        #await self.olfactometer.write_gatt_char(IRSwitch_CHR, b'0')
       # await self.olfactometer.stop_notify(SniffTime_CHR)
        
        
    async def updateSniff(self,val):
        val=str(val)
        val=bytes(val, "utf-8")
        await self.olfactometer.write_gatt_char(SniffCrit_CHR, val)
    
    
    async def checkIR(self, sender, data):
        sniff=data.decode()
        sniff=float(sniff[0:8])
        self.rx_Q.put_nowait((self.name, sniff))
        




    



app = QtWidgets.QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
MainWindow = QtWidgets.QMainWindow()
ui = myapp(loop)
ui.setupUi(MainWindow)
ui.setupApp()
MainWindow.show()  
 
loop.run_until_complete(ui.runOlfactometers())
        

