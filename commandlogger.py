#command logger
import config
import os
import json
from datetime import datetime

curtime = datetime.now()
botdir = os.getcwd()
filename = f'\\logs\\log-{curtime.strftime("%d-%m-%Y")}.json'

def logHandler(ctx,curserver,parameter,loc):
    #print(curserver,parameter,loc)
    log = []
    server = curserver
    time = datetime.now().strftime('%c')
    if curserver != None:
        server = curserver.FriendlyName
    if loc == 'bot':
        command_user = str(ctx.author)
        command_user_id = str(ctx.author.id)
        command = str(ctx.command)
        if type(parameter) == tuple:
            logentry = {
                    'Users': command_user,
                    'User_ID': command_user_id,
                    'Timestamp' : time,
                    'Type' : 'Discord Bot',
                    'Server' : server,
                    'Command' : command,
                    'Usage' : " ".join(parameter)
                    }     
        elif parameter != None:
            contents_split = parameter.split(' ')
            logentry = {
                'Users': command_user,
                'User_ID': command_user_id,
                'Timestamp' : time,
                'Type' : 'Discord Bot',
                'Server' : server,
                'Command' : command,
                'Usage' : " ".join(contents_split[1:])
                }     
        else:
            logentry = {
                'Users': command_user,
                'User_ID': command_user_id,
                'Timestamp' : time,
                'Type' : 'Discord Bot',
                'Server' : server,
                'Command' : command
                }     
             
        #log.append(logentry)
        logfilesaver(logentry)
        print('Logged a Bot Command')

    if loc == 'console':
        contents_split = parameter['Contents'].split(' ')
        command_user = contents_split[0]
        command = contents_split[4]
        commandlist = config.CommandList

        if command in commandlist:
            time = datetime.fromtimestamp(float(parameter['Timestamp'][6:-2])/1000).strftime('%c')
            logentry = {
                    'Users': command_user,
                    'Timestamp' : time,
                    'Type' : 'Console',
                    'Server' : server,
                    'Command' : command,
                    'Usage' : " ".join(contents_split[5:])
                    }                   
            #log.append(logentry)
            logfilesaver(logentry)
            print('Logged a Console Command')
    return

def init():
    try:
        print('Making Log Directory')
        os.makedirs(botdir + '\\logs')
        logfileloader()
    except Exception as e:
        print(e)

def logfileloader():
    try:    
        if os.path.isfile(botdir +  filename) != True:
            print('Created a new log file')
            newfile = open(botdir + filename, 'x')
            newfile.close()

    except json.decoder.JSONDecodeError as e:
        print(e)
    return

def logfilesaver(log):
    newfile = open(botdir + filename, 'a') 
    json.dump(log,newfile, indent=0)
    newfile.close()
    #print(f"log file saved")
    return

def logfilearchiver():
    logdate = filename.replace('log.json',f'log-{curtime.strftime("%d-%m-%Y")}.json')
    print(logdate)
    try:
        if os.path.isfile(botdir + filename) != True:
            return
        else:
            print('Attempting to rename file')
            os.rename(botdir + filename, botdir + logdate)
    except Exception as e:
        print(e)
    return

