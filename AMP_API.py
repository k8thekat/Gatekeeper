#AMP API 
# by k8thekat // Lightning
# 11/10/2021

import requests
from requests.sessions import Session
import tokens
import config
import pyotp # 2Factor Authentication Python Module
import json
import time
from pprint import pprint

def Login(func):
    def wrapper(*args, **kargs):
        self = args[0]

        if self.Running == False:
            print(f'Instance offline: {self.FriendlyName}')
            return False

        if self.SessionID == 0:
            print(f'Logging in {self.InstanceID}')
            parameters = {
                    'username': config.AMPUser,
                    'password': config.AMPPassword,
                    'token': self.AMP2Factor.now(), #get current 2Factor Code
                    'rememberMe': True}

            result = self.CallAPI('Core/Login',parameters)
            self.SessionID = result['sessionID']
            if ("checkup" not in kargs) or (kargs["checkup"] == False):
                self.sessionIDlist.append(self.SessionID)

        return func(*args, **kargs)
    return wrapper

class AMPAPI:
    def __init__(self, instanceID = 0, serverdata = {},sessionIDlist = [],Index = 0):
        self.url = config.AMPurl + '/API/' #base url for AMP console /API/
        if instanceID != 0:
            self.url += f"ADSModule/Servers/{instanceID}/API/"
        self.InstanceID = instanceID
        self.AMPheader = {'Accept': 'text/javascript'} #custom header for AMP API POST requests. AMP is pure POST requests. ***EVERY REQUEST MUST HAVE THIS***
        try:
            self.AMP2Factor = pyotp.TOTP(tokens.AMPAuth) #Handles time based 2Factory Auth Key/Code
            #print('Found 2 Factor')
        except AttributeError:
            #print('No 2 Factor found')
            return
        self.SessionID = 0
        self.Index = Index
        self.sessionIDlist = sessionIDlist
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
            print(f"AMP_API CallAPI ret is 0: status_code {post_req.status_code}")
            print(post_req.raw)
        return post_req.json()

    @Login
    def getInstances(self,checkup = False):
        parameters = {}
        result = self.CallAPI('ADSModule/GetInstances',parameters) 
        serverlist = {}
        for i in range(0,len(result["result"][0]['AvailableInstances'])): #entry = name['result']['AvailableInstances'][0]['InstanceIDs']
            entry = result["result"][0]['AvailableInstances'][i]
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
        print(parameters)
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

    def sessionCleanup(self):
        sessions = self.getActiveAMPSessions()
        for entry in sessions['result']:
            if entry['Username'] == config.AMPUser:
                if entry['SessionID'] not in self.sessionIDlist:
                    self.endUserSession(entry['SessionID'])
        return