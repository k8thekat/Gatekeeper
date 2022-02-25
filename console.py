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


#database setup
db = database.Database()
dbconfig = db.GetConfig()

#Async function setup
async_loop = asyncio.new_event_loop()
asyncio.set_event_loop(async_loop)

#AMP API setup
AMP = AMPAPI()
AMPservers = AMP.getInstances() # creates objects for server console/chat updates


CLIENT = None
SERVERCONSOLE = {}
ROLECHECK = None
BOTOUTPUT = None

def init(client,rolecheck,botoutput):
    global CLIENT,SERVERCONSOLE,ROLECHECK,AMPservers
    CLIENT = client
    ROLECHECK = rolecheck
    BOTOUTPUT = botoutput
    if dbconfig.Autoconsole:
        for server in AMPservers:
            db_server = db.GetServer(server)
            channel = db_server.DiscordChatChannel #Needs to be an int() because of discord message.channel.id type is int()
            if channel != None:
                #channel = int(channel) 
                print('Starting Console Threads...')
                server_thread = threading.Thread(target = serverconsole, args = (AMPservers[server],db_server))
                time.sleep(0.1)
                SERVERCONSOLE = {int(channel): {'AMPserver' :AMPservers[server], 'DBserver': db_server, 'thread' : server_thread, 'status' : AMPservers[server].Running}}
                server_thread.start()
        print(SERVERCONSOLE)

#Sends the console to the predefined channel
async def serverConsoletoDiscord(channel, entry):
    try:
        await channel.send(entry) 
    except Exception as e:
        BOTOUTPUT(e)

#This handles passing DISCORD Chat commands to the MC server
def on_message(message):
    global CLIENT
    if message.channel.id in SERVERCONSOLE:
        #TODO Possible Error Here TypeError: 'AMPAPI' object is not subscriptable
        if SERVERCONSOLE[message.channel.id]['status']:
            if ROLECHECK(message, 'Maintenance'):
                SERVERCONSOLE[message.channel.id].ConsoleMessage(message.content)
                return True
    return False
        

#Parses each AMP Server Console
def serverconsole(amp_server,db_server):
    if amp_server.Running:
        time.sleep(0.5)
        console = amp_server.ConsoleUpdate()
        consolemsg = []
        #Walks through every entry of a Console Update
        for entry in console['ConsoleEntries']:
            #Checks every entry to update DB values if needed
            status = consolescan.scan(amp_server,colorstrip(entry))
            if status[0] == True:
                BOTOUTPUT(status[1])
                continue
            if status[0] == False:
                entry = status[1]
                #Supports different types of console suppression, see config.py and consolefilter.py
                entry = consolefilters.filters(entry)
            if entry == True:
                continue
            elif len(entry['Contents']) > 1500:
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
        if db_server.DiscordConsoleChannel != None:
            channel = CLIENT.get_channel(int(db_server.DiscordConsoleChannel))
            if len(consolemsg) > 0:
                bulkentry = ''
                for entry in consolemsg:
                    if len(bulkentry + entry) < 1500:
                        bulkentry = bulkentry + entry + '\n' 
                    else:
                        serverConsoletoDiscord(channel,entry)
                        #ret = asyncio.run_coroutine_threadsafe(serverconsolemessage(outputchan, bulkentry[:-1]), async_loop)
                        #ret.result()
                        bulkentry = entry + '\n'
                if len(bulkentry):
                    serverConsoletoDiscord(channel,entry)
                    #ret = asyncio.run_coroutine_threadsafe(serverconsolemessage(outputchan, bulkentry[:-1]), async_loop)
                    #ret.result()

#Removed the odd character for color idicators on text
def colorstrip(entry):
    char =  '�'
    if entry['Contents'].find(char) != -1:
        print('Color strip triggered...')
        index = 0
        while 1:
            index = entry['Contents'].find(char,index)
            if index == -1:
                break
            newchar = entry['Contents'][index:index+2]
            entry['Contents'] = entry['Contents'].replace(newchar,'')
        return entry
    return entry