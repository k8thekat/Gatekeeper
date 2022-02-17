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
#Gatekeeper Bot - command logger
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
    dircheck = os.path.isfile(botdir +  filename)
    LOGS = []
    try:    
        if dircheck != True:
            newfile = open(botdir + filename, 'x')
            newfile.close()
            return LOGS
        if dircheck:
            filesize = os.path.getsize(botdir + filename)
            if filesize != 0:
                newfile = open(botdir + filename)
                LOGS = json.load(newfile)
                newfile.close()
                return LOGS
        else:
            return LOGS
    except json.decoder.JSONDecodeError as e:
        print(e)
        traceback.print_exc()
    return LOGS

def logfilesaver(log):
    newfile = open(botdir + filename, 'w') 
    json.dump(log,newfile, indent=0)
    newfile.close()
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

def logfileparse(filename,count= 5,start_index= 0):
    try:
        newfile = open(botdir + '\\logs\\' + filename)
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