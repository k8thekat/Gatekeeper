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
#Gatekeeper Bot - logger
import config
import os
import json
from datetime import datetime
import traceback
import platform
import logging
from logging.handlers import TimedRotatingFileHandler
import sys



COMMANDLOGS = []
FILES = {'log' : 'log',
        'commands' : 'commandlog.json'}
DIR = '\\logs\\'
CURTIME = datetime.now()
DATE = CURTIME.strftime('%Y-%m-%d-')
OSPLAT = platform.system()
BOTDIR = os.getcwd()
LOG = None

def init():
    global DIR
    if OSPLAT.lower() == 'linux': #Flip the slash to accomadate Linux users <3
        DIR.replace('\\','//')
    
    dircheck = os.path.isdir(BOTDIR + DIR)
    if dircheck != True:
        print('Making Log Directory...')
        os.makedirs(BOTDIR + DIR)
        
    log_file_name = BOTDIR + DIR + FILES['log']
    logging.basicConfig(level=config.logginglevel, format='%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        handlers = [logging.StreamHandler(sys.stdout),
                        TimedRotatingFileHandler(log_file_name,'midnight',atTime=datetime.min.time(),backupCount= 4,encoding='utf-8',utc=True)])
    return

def logfilelist():
    list = os.listdir(BOTDIR + DIR)
    for file in list:
        if not file.endswith('.json'):
            list.remove(file)
    return list

def varupdate(time):
    global DATE,CURTIME
    if CURTIME.day != time.day:
        CURTIME = datetime.now()
        DATE = CURTIME.strftime('%d-%m-%Y-') 
    return

def commandLog(ctx,curserver,parameter,loc):
    global COMMANDLOGS
    server = curserver
    save = False
    time = datetime.now().strftime('%c')
    if curserver != None:
        server = curserver.FriendlyName
    if loc == 'bot':
        command_user = str(ctx.author)
        command_user_id = str(ctx.author.id)
        command = str(ctx.command)
        if type(parameter) == tuple:
            save = True
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
            save = True
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
            save = True
            logentry = {
                'User': command_user,
                'User_ID': command_user_id,
                'Timestamp' : time,
                'Type' : 'Discord Bot',
                'Server' : server,
                'Command' : command
                }     

        if save == True:
            logfilesaver([logentry])
            return logging.info('Logged a Discord Command...')
             

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
            logfilesaver([logentry])
            logging.info('Logged a Console Command...')
    return


def logfilehandler(type):
    logging.info(f'File Handler Type {type}')
    global COMMANDLOGS,DATE
    if type == 'command':
        dircheck = os.path.isfile(BOTDIR + DIR + DATE + FILES['commands'])
        filename = DATE + FILES['commands']
        
    try:    
        if dircheck:
            newfile = open(BOTDIR + DIR + filename, 'a+')
            COMMANDLOGS = json.load(newfile)
            newfile.close()
            return COMMANDLOGS,filename
        else:
            return COMMANDLOGS,filename
    except json.decoder.JSONDecodeError as e:
        logging.error(e)
        logging.error(traceback.print_exc())
    return COMMANDLOGS,filename

def logfilesaver(log):
    filename = DATE + FILES['commands']
    logging.info(f'Log File Saver {filename}')
    try:
        newfile = open(BOTDIR + DIR + filename, 'r+', newline= '\n')
    except:
        newfile = open(BOTDIR + DIR + filename, 'w', newline= '\n')

    endoffile = newfile.seek(0, os.SEEK_END)
    if endoffile == 0:
        #new file, just dump 
        json.dump(log,newfile, indent=0)
    else:
        #go back 1 spot to rewrite the close ]
        newfile.seek(endoffile-2, os.SEEK_SET)

        #get the json data string and write data after the first [
        jsondata = json.dumps(log,indent=0)[1:]
        if jsondata[0] == '\n':
            jsondata = jsondata[1:]
        newfile.write("," + jsondata)
    newfile.close()
    return


def logfileparse(filename,count= 5,start_index= 0):
    global DIR
    try:
        newfile = open(BOTDIR + DIR + filename)
        parse_log = json.load(newfile)
    except:
        return 'The File: {filename} was not correct...'
    if count > 15:
        return 'Please keep your values lower than 15...'
    if count > len(parse_log): 
        count = len(parse_log)
    if start_index + count > len(parse_log):
        start_index = len(parse_log) - count
    
        #return f'Youve exceeded the length of the log file, Entries: {len(parse_log)}'
    if start_index != 0:
        log_return = []
        for logentry in parse_log[-start_index:-start_index+count]:
            log_return.append(str(logentry)[1:-1])
        return log_return
    else:
        log_return = []
        for logentry in parse_log[:count]:
            log_return.append(str(logentry)[1:-1])
        return log_return

