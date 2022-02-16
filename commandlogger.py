#command logger
import config
import os
import json
from datetime import datetime
import traceback

curtime = datetime.now()
botdir = os.getcwd()
filename = f'\\logs\\log-{curtime.strftime("%d-%m-%Y")}.json'
logfile_list = os.listdir(botdir + '\\logs')
global LOGS


def init():
    try:
        print('Making Log Directory')
        os.makedirs(botdir + '\\logs')
        logfileloader()
    except Exception as e:
        print(e)
        traceback.print_exc()

def logHandler(ctx,curserver,parameter,loc):
    print('Log file...')
    LOGS = logfileloader()
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
                    'User': command_user,
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
                'User': command_user,
                'User_ID': command_user_id,
                'Timestamp' : time,
                'Type' : 'Discord Bot',
                'Server' : server,
                'Command' : command,
                'Usage' : " ".join(contents_split[1:])
                }     
        else:
            logentry = {
                'User': command_user,
                'User_ID': command_user_id,
                'Timestamp' : time,
                'Type' : 'Discord Bot',
                'Server' : server,
                'Command' : command
                }     
             
        LOGS.append(logentry)
        logfilesaver(LOGS)
        print('Logged a Bot Command')

    if loc == 'console':
        contents_split = parameter['Contents'].split(' ')
        command_user = contents_split[0]
        command = contents_split[4]
        commandlist = config.CommandList

        if command in commandlist:
            time = datetime.fromtimestamp(float(parameter['Timestamp'][6:-2])/1000).strftime('%c')
            logentry = {
                    'User': command_user,
                    'Timestamp' : time,
                    'Type' : 'Console',
                    'Server' : server,
                    'Command' : command,
                    'Usage' : " ".join(contents_split[5:])
                    }                   
            LOGS.append(logentry)
            logfilesaver(LOGS)
            print('Logged a Console Command')
    return

def logfileloader():
    try:    
        if os.path.isfile(botdir +  filename) != True:
            print('Created a new log file')
            newfile = open(botdir + filename, 'x')
            LOGS = []
            newfile.close()
        else:
            newfile = open(botdir + filename)
            LOGS = json.load(newfile)
    except json.decoder.JSONDecodeError as e:
        LOGS = []
        print(e)
    return LOGS

def logfilesaver(log):
    newfile = open(botdir + filename, 'w') 
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
        traceback.print_exc()
    return

def logfileparse(filename,count,start_index = 0):
    print(filename)
    newfile = open(botdir + '\\logs\\' + filename)
    parse_log = json.load(newfile)
    if count > 15:
        return 'Please keep your values lower than 15...'
    if count > len(parse_log) or start_index + count > len(parse_log):
        return f'Youve exceeded the length of the log file {len(parse_log)}'
    if start_index != 0:
        log_return = []
        for logentry in parse_log[-start_index:-start_index+count]:
            log_return.append(str(logentry)[1:-1])
            return log_return
    return