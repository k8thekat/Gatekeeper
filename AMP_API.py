'''
   Copyright (C) 2021-2022 Katelynn Cadwallader.

   This file is part of Gatekeeper, the AMP Minecraft Discord Bot.

   Gatekeeper is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.

   Gatekeeper is distributed in the hope that it will be useful, but WITHOUT
   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
   or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
   License for more details.

   You should have received a copy of the GNU General Public License
   along with Gatekeeper; see the file COPYING.  If not, write to the Free
   Software Foundation, 51 Franklin Street - Fifth Floor, Boston, MA
   02110-1301, USA. 
'''
#AMP API 
# by k8thekat // Lightning
# 11/10/2021
import requests
import requests.sessions
import tokens
import config
import pyotp # 2Factor Authentication Python Module
import json
import time
from pprint import pprint
import sys
import os
import logging

SessionIDlist = {}

#Checks for Errors in Config
def init():
    reset = False
    if config.AMPurl[-1] == '/' or "\\":
        config.AMPurl = config.AMPurl[0:-1]
    if os.path.isfile('tokenstemplate.py') or not os.path.isfile('tokens.py'):
        logging.error('**ERROR** Please rename your tokenstemplate.py file to tokens.py before trying again.')
        reset = True
    if len(tokens.AMP2Factor) < 7 or tokens.AMP2Factor != '':
        logging.error("**ERRORR** Please check your 2 Factor Set-up Code in tokens.py, should not contain spaces and enclosed in ' '")
        reset = True
    if reset:
        input("Press any Key to Exit")
        sys.exit(0)

def Login(func):
    def wrapper(*args, **kargs):
        global SessionIDlist
        self = args[0]

        if self.Running == False:
            #print(f'Instance offline: {self.FriendlyName}')
            return False

        if self.SessionID == 0:
            if self.InstanceID in SessionIDlist:
                self.SessionID = SessionIDlist[self.InstanceID]
                return func(*args, **kargs)

            logging.info(f'Logging in {self.InstanceID}')
            if self.AMP2Factor != None:
                token = self.AMP2Factor.now()
            else:
                token = ''  
            parameters = {
                    'username': config.AMPUser,
                    'password': config.AMPPassword,
                    'token': token, #get current 2Factor Code
                    'rememberMe': True}

            result = self.CallAPI('Core/Login',parameters)
            self.SessionID = result['sessionID']
            if ("checkup" not in kargs) or (kargs["checkup"] == False):
                SessionIDlist[self.InstanceID] = self.SessionID

        return func(*args, **kargs)
    return wrapper

class AMPAPI:
    def __init__(self, instanceID = 0, serverdata = {},Index = 0):
        self.url = config.AMPurl + '/API/' #base url for AMP console /API/
        if instanceID != 0:
            self.url += f"ADSModule/Servers/{instanceID}/API/"
        self.InstanceID = instanceID
        self.AMPheader = {'Accept': 'text/javascript'} #custom header for AMP API POST requests. AMP is pure POST requests. ***EVERY REQUEST MUST HAVE THIS***
        try:
            self.AMP2Factor = pyotp.TOTP(tokens.AMPAuth) #Handles time based 2Factory Auth Key/Code
            self.AMP2Factor.now()
            #print('Found 2 Factor')
        except AttributeError:
            self.AMP2Factor = None
            #print('No 2 Factor found').
            return
        self.SessionID = 0
        self.Index = Index
    
        self.serverdata = serverdata
        if instanceID != 0:
            for entry in serverdata:
                setattr(self, entry, serverdata[entry])
            self.FriendlyName = self.FriendlyName.replace(' ', '_')
        else:
           self.Running = True

    def CallAPI(self,APICall,parameters):
        if self.SessionID != 0:
            parameters['SESSIONID'] = self.SessionID
        jsonhandler = json.dumps(parameters)
        post_req = requests.post(self.url+APICall, headers=self.AMPheader, data=jsonhandler)
        #pprint(post_req.json())
        if type(post_req.json()) == None:
            logging.error(f"AMP_API CallAPI ret is 0: status_code {post_req.status_code}")
            logging.error(post_req.raw)
        return post_req.json()

    @Login
    def getInstances(self):
        parameters = {}
        result = self.CallAPI('ADSModule/GetInstances',parameters) 
        #pprint(result)
        serverlist = {}
        for i in range(0,len(result["result"][0]['AvailableInstances'])): #entry = name['result']['AvailableInstances'][0]['InstanceIDs']
            entry = result["result"][0]['AvailableInstances'][i]
            if entry['Module'] == 'Minecraft':
                server = AMPAPI(entry['InstanceID'],entry,Index = i)
                serverlist[server.InstanceID] = server 
        return serverlist

    @Login  
    def ConsoleUpdate(self):
        #print('Console update')
        parameters = {}
        # Will post all updates from previous API call of console update.
        result = self.CallAPI('Core/GetUpdates', parameters)
        return result

    @Login
    def ConsoleMessage(self,msg):
        parameters = {'message': msg}
        #print(parameters)
        result = self.CallAPI('Core/SendConsoleMessage', parameters)
        time.sleep(0.5)
        update = self.ConsoleUpdate()
        return update

    @Login
    def StartInstance(self):
        parameters = {}
        result = self.CallAPI('Core/Start', parameters)
        return

    @Login
    def StopInstance(self):
        parameters = {}
        result = self.CallAPI('Core/Stop', parameters)
        return

    @Login
    def RestartInstance(self):
        parameters = {}
        result = self.CallAPI('Core/Restart', parameters)
        return

    @Login
    def KillInstance(self):
        parameters = {}
        result = self.CallAPI('Core/Kill', parameters)
        return

    @Login
    def getStatus(self):
        parameters = {}
        result = self.CallAPI('Core/GetStatus', parameters)
        #Uptime = '**Uptime**: ' + str(result['Uptime'])
        tps = '**TPS**: ' + str(result['State'])
        activeusers = '**Players**: ' + str(result['Metrics']['Active Users']['RawValue'])
        self.Metrics = result['Metrics']
        status = f'{tps}\n{activeusers}'
        return status

    @Login
    def getSchedule(self):
        parameters = {}
        result = self.CallAPI('Core/GetScheduleData', parameters)
        return result['result']['PopulatedTriggers']
  
    def setFriendlyName(self,instance,name,description):
        parameters = {
                'InstanceId' : instance.InstanceID,
                'FriendlyName': name,
                'Description' : description,
                'StartOnBoot': instance.DaemonAutostart,
                'Suspended' : instance.Suspended,
                'ExcludeFromFirewall': instance.ExcludeFromFirewall,
                'RunInContainer': instance.IsContainerInstance,
                'ContainerMemory' : instance.ContainerMemoryMB,
                'MemoryPolicy' : instance.ContainerMemoryPolicy,
                'ContainerMaxCPU': instance.ContainerCPUs}
        response = f'{instance.FriendlyName} is about to be changed to {name}; this will restart the instance.'
        result = self.CallAPI('ADSModule/UpdateInstanceInfo', parameters)
        #print(result)
        return response

    @Login
    # Test AMP API calls with this function
    def getAPItest(self):
        parameters = {}
        result = self.CallAPI('Core/GetActiveAMPSessions', parameters)
        return result

    @Login
    def addTask(self,triggerID,methodID,parammap):
        parameters = {
                'TriggerID' : triggerID,
                'MethodID' : methodID,
                'ParameterMapping' : parammap
                }
        result = self.CallAPI('Core/AddTask', parameters)
        return result

    @Login
    def copyFile(self,source,destination):
        parameters = {
            'Origin' : source,
            'TargetDirectory' : destination
        }
        result = self.CallAPI('FileManagerPlugin/CopyFile', parameters)
        return result

    @Login
    def renameFile(self,original,new):
        parameters = {
            'Filename' : original,
            'NewFilename' : new
        }
        result = self.CallAPI('FileManagerPlugin/RenameFile', parameters)
        return result

    @Login
    def getDirectoryListing(self,directory):
        parameters = {
            'Dir' : directory
            }
        result = self.CallAPI('FileManagerPlugin/GetDirectoryListing',parameters)
        return result

    @Login    
    def getFileChunk(self,name,position,length):
        parameters = {
            'Filename' : name,
            'Position' : position,
            'Length' : length
        }
        result = self.CallAPI('FileManagerPlugin/GetFileChunk',parameters)
        return result

    @Login
    def writeFileChunk(self,filename,position,data):
        parameters = {
            'Filename' : filename,
            'Position' : position,
            'Data' : data
        }
        result = self.CallAPI('FileManagerPlugin/WriteFileChunk', parameters)
        return result

    @Login
    def endUserSession(self,sessionIDold):
        parameters = {
            'Id' : sessionIDold
        }
        result = self.CallAPI('Core/EndUserSession', parameters)
        #print(f'Ended user Session {sessionIDold}')
        return

    @Login
    def getActiveAMPSessions(self):
        parameters = {}
        result = self.CallAPI('Core/GetActiveAMPSessions', parameters)
        return result

    @Login
    def getInstanceStatus(self):
        parameters = {}
        result = self.CallAPI('ADSModule/GetInstanceStatuses', parameters)

        return result

    @Login
    def trashDirectory(self,dirname):
        parameters = {
            'DirectoryName' : dirname
        }
        result = self.CallAPI('FileManagerPlugin/TrashDirectory',parameters)
        return result

    @Login
    def trashFile(self,filename):
        parameters = {
            'Filename' : filename
        }
        result = self.CallAPI('FileManagerPlugin/TrashFile',parameters)
        return result
    
    @Login
    def emptyTrash(self,trashdir):
        parameters = {
            'TrashDirectoryName' : trashdir
        }
        result = self.CallAPI('FileManagerPlugin/EmptyTrash',parameters)
        return result

    #TODO Need to fix list
    def sessionCleanup(self):
        global SessionIDlist
        sessions = self.getActiveAMPSessions()
        for entry in sessions['result']:
            if entry['Username'] == config.AMPUser:
                if entry['SessionID'] not in SessionIDlist:
                    self.endUserSession(entry['SessionID'])
        return
