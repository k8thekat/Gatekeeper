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
#Gatekeeper - Minecraft Console
from AMP_API import AMPAPI
import asyncio
import database
import threading
import consolescan
import consolefilters
import time
import traceback
import chat
import logging
import pprint

#database setup
db = database.Database()

#AMP API setup
AMP = AMPAPI()
AMPservers = AMP.getInstances() # creates objects for server console/chat updates

#client = None
SERVERCONSOLE = {}
SERVERTHREADS = {}
ROLECHECK = None
BOTOUTPUT = None

def init(client,rolecheck,botoutput,async_loop):
    while(client.is_ready() == False): #Lets wait to start this until the bot has fully setup.
        time.sleep(1)
    global SERVERCONSOLE,BOTOUTPUT,ROLECHECK,AMPservers,SERVERTHREADS
    ROLECHECK = rolecheck
    BOTOUTPUT = botoutput
    for server in AMPservers:
        channel = db.GetServer(server).DiscordConsoleChannel
        #channel = db_server.DiscordConsoleChannel #Needs to be an int() because of discord message.channel.id type is int()
        #print(db_server.FriendlyName,channel)
        logging.info(f'Starting Console Thread for {AMPservers[server].FriendlyName}')
        server_thread = threading.Thread(target = serverconsole, args = (AMPservers[server],channel,client,async_loop))
        SERVERTHREADS.update({AMPservers[server] : server_thread})
    
        server_thread.start()
        time.sleep(0.1)
        
        if channel != None:
            #disc_channel = client.get_channel(int(channel))
            #print('Adding', AMPservers[server].FriendlyName, channel,'to SERVERCONSOLE')
            SERVERCONSOLE[int(channel)] = {'AMPserver' :AMPservers[server], 'thread' : server_thread, 'status' : AMPservers[server].Running}
    #pprint.pprint(SERVERCONSOLE)
    #pprint.pprint(SERVERTHREADS)
            
#This is called when someone changed a servers console channel; so lets spin up its thread to start scanning.
def threadinit(db_server,channel,client,async_loop): 
    global SERVERCONSOLE,SERVERTHREADS
    if channel not in SERVERCONSOLE:
        logging.info(f'Adding {db_server.FriendlyName} Server Thread to Server Console list.')
        print(SERVERTHREADS[AMPservers[db_server.InstanceID]])
        SERVERCONSOLE[channel.id] = {'AMPserver' :AMPservers[db_server.InstanceID], 'thread' : SERVERTHREADS[AMPservers[db_server.InstanceID]], 'status' : AMPservers[db_server.InstanceID].Running}
        #disc_channel = client.get_channel(int(channel)) #lets update our global so the thread can have an updated value
        server_thread = threading.Thread(target = serverconsole, args = (AMPservers[db_server.InstanceID],channel.id,client,async_loop))
        SERVERTHREADS.update({AMPservers[db_server.InstanceID]: server_thread})
        server_thread.start()
    return

def threadstop(db_server):
    server = AMPservers[db_server.InstanceID]
    global SERVERTHREADS
    if server in SERVERTHREADS:
        SERVERTHREADS[server].stop() 

def threadstopall():
    for server in SERVERTHREADS:
        SERVERTHREADS[server].stop()

#Sends the console to the predefined channel
async def serverConsoletoDiscord(channel, entry):
    global BOTOUTPUT
    try:
        await channel.send(entry) 
    except Exception as e:
        logging.exception(e)
        logging.error(traceback.print_exc())
        BOTOUTPUT(e)

#@client.event()
#This handles passing DISCORD Chat messages to the MC server if they are commands.
def on_message(message):
    command = message.content.replace('//','/')
    if SERVERCONSOLE[message.channel.id]['status']:
        if ROLECHECK(message, 'Maintenance'):
            SERVERCONSOLE[message.channel.id]['AMPserver'].ConsoleMessage(command)
            return True
    return False
        

#Parses each AMP Server Console
def serverconsole(amp_server,channel,client,async_loop):
    global BOTOUTPUT
    while amp_server.Running:
        time.sleep(0.5)
        console = amp_server.ConsoleUpdate()
        if 'ConsoleEntries' not in console:
            logging.error(f'Failed ConsoleUpdate {console}, forcing AMP API relog.')
            print(amp_server.SessionID)
            amp_server.SessionID = 0
            print(amp_server.SessionID)
            console = amp_server.ConsoleUpdate()
            continue
        
        consolemsg = []
        #Walks through every entry of a Console Update
        for entry in console['ConsoleEntries']:
            #logging.info(f'{amp_server.FriendlyName} {entry}')
            #Checks every entry to update DB values if needed
            status = consolescan.scan(amp_server,colorstrip(entry))
            chat.MCchattoDiscord(amp_server,async_loop,client,entry)

            if not db.GetConfig().Autoconsole: #If we don't have auto console; just end our console handling and start over.
                continue
            if status[0] == True:
                BOTOUTPUT(status[1])
                continue

            if status[0] == False:
                entry = status[1]
                #Supports different types of console suppression, see config.py and consolefilter.py
                entry = consolefilters.filters(entry)
            if entry == True:
                continue

            if len(entry['Contents']) > 1500:
                index_hunt = entry['Contents'].find(';')
                if index_hunt == -1:
                    continue

                msg_len_index = entry['Contents'].rindex(';')
                while msg_len_index > 1500:
                    msg_len_indexend = msg_len_index
                    msg_len_index = entry['Contents'].rindex(';',0,msg_len_indexend)
                    if msg_len_index < 1500:
                        newmsg = entry['Contents'][0:msg_len_index]
                        consolemsg.append(f"{entry['Source']}: {newmsg.lstrip()}")
                        entry['Contents'] = entry['Contents'][msg_len_index+1:len(entry['Contents'])]
                        msg_len_index = len(entry['Contents'])
                        continue
            else:
                consolemsg.append(f"{entry['Source']}: {entry['Contents']}") 

        if len(consolemsg) > 0 and channel != None:
            disc_channel = client.get_channel(int(channel))
            bulkentry = ''
            for entry in consolemsg:
                if len(bulkentry + entry) < 1500:
                    bulkentry = bulkentry + entry + '\n' 
                else:
                    ret = asyncio.run_coroutine_threadsafe(serverConsoletoDiscord(disc_channel,bulkentry[:-1]),async_loop)
                    ret.result()
                    bulkentry = entry + '\n'

            if len(bulkentry):
                ret = asyncio.run_coroutine_threadsafe(serverConsoletoDiscord(disc_channel,bulkentry[:-1]),async_loop)
                ret.result()

 

#Removed the odd character for color idicators on text
def colorstrip(entry):
    char =  '�'
    if entry['Contents'].find(char) != -1:
        logging.info('Color strip triggered...')
        index = 0
        while 1:
            index = entry['Contents'].find(char,index)
            if index == -1:
                break
            newchar = entry['Contents'][index:index+2]
            entry['Contents'] = entry['Contents'].replace(newchar,'')
        return entry
    return entry
