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
#Gatekeeper - Minecraft Chat
from AMP_API import AMPAPI
import asyncio
import database
import threading
import UUIDhandler
import chatfilter
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

#Discord Hook
CLIENT = ''

SERVERCHAT = {}

def init(client):
    #Lets generate our list of servers via Chat channels for easier lookup.
    global SERVERCHAT,CLIENT, AMPservers
    CLIENT = client #Store my discord client for Discord related API functions.
    for server in AMPservers:
        db_server = db.GetServer(server)
        channel = db_server.DiscordChatChannel #Needs to be an int() because of discord message.channel.id type is int()
        if channel != None:
            print('Starting Chat Threads...')
            server_thread = threading.Thread(target = MCchattoDiscord, args= (AMPservers[server],db_server))
            time.sleep(0.1)
            SERVERCHAT = {int(channel): {'AMPserver' : AMPservers[server], 'DBserver': db_server, 'thread' : server_thread, 'status' : AMPservers[server].Running}}
            server_thread.start()
    print(SERVERCHAT)

#This handles scanning discord chat messages to send it to the correct minecraft server

def on_message(message):
    global CLIENT
    if message.channel.id in SERVERCHAT:
        if SERVERCHAT[message.channel.id]['status']:
            message.content = message.content.replace('\n',' ')
            message.content = chatfilter.scan(message.content,CLIENT) #Removes characters that MC cannot display properly (emojis,ascii,etc)
            if message.content == True:
                return True
            else:
                SERVERCHAT[message.channel.id].ConsoleMessage(f'tellraw @a [{{"text":"(Discord)","color":"blue"}},{{"text":"<{message.author.name}>: {message.content}","color":"white"}}]')
                return True
    return False

#This fetches MC avatars heads and uses them for Discord Profile Pics and changes the message name to the IGN from minecraft
async def MCchatsend(channel, user, message):
    if user != None:
        MChead = 'https://mc-heads.net/head/' + str(user[1][0]['id'])
        webhook = await channel.create_webhook(name= user[1][0]['name'])
        await webhook.send(message, username= user[1][0]['name'], avatar_url= MChead)
    
    webhooks = await channel.webhooks()
    for webhook in webhooks:
            await webhook.delete()

#Console messages are checked by 'Source' and by 'Type' to be sent to a designated discord channel.
def MCchattoDiscord(amp_server,db_server):
    if amp_server.Running:
        time.sleep(0.5)
        chat = amp_server.ConsoleUpdate()
        outputchan = CLIENT.get_channel(int(db_server.DiscordChatChannel))
        #Walks through every entry of a Console Update
        for entry in chat['ConsoleEntries']:
            chatmsg = []
            if entry['Source'].startswith('Async Chat Thread'):
                chatmsg.append(entry['Contents'])
            elif entry['Type'] == 'Chat':
                user = UUIDhandler.uuidcheck(entry['Source'])
                chatmsg.append(entry['Contents'])
            else:
                return

            if len(chatmsg) > 0:
                bulkentry = ''
                for entry in chatmsg:
                    if len(bulkentry+entry) < 1500:
                        bulkentry = bulkentry + entry + '\n' 
                    else:
                        MCchatsend(outputchan, user , bulkentry[:-1])
                        #ret = asyncio.run_coroutine_threadsafe(MCchatsend(outputchan, user, bulkentry[:-1]), async_loop)
                        #ret.result()
                        bulkentry = entry + '\n'
                if len(bulkentry):
                    MCchatsend(outputchan, user , bulkentry[:-1])
                    #ret = asyncio.run_coroutine_threadsafe(MCchatsend(outputchan, user, bulkentry[:-1]), async_loop)
                    #ret.result()
