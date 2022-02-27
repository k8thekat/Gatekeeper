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
#Gatekeeper Bot - whitelist.py
from datetime import datetime
import base64
import json
import logging
import parse
import timehandler
import UUIDhandler


#whitelist wait list
WhitelistWaitList = []

def init(origAMP,origAMPservers,origdb,origdbconfig):
    global AMP,AMPservers,db,dbconfig
    AMP = origAMP
    AMPservers = origAMPservers
    db = origdb
    dbconfig = origdbconfig
    return


#Used to add users to the DB when they request whitelist in the WL channel if Autowhitelist is False.
def wlmessagehandler(message):
    logging.info('User to Database...')
    logging.info(message.author.id,message.author.name)
    global WhitelistWaitList 
    curtime = datetime.now()
    user = db.GetUser(str(message.author.id)) 
    wl_request = parse.ParseIGNServer(message.content)
    IGN,sel_server = wl_request
    if user == None:
        logging.info('New User Setup...')
        curuser = db.AddUser(DiscordID = str(message.author.id), DiscordName = message.author.name)
        if wl_request == None:
            return True, f'**Unable to process**: {message.content} Please manually whitelist this user and update their IGN via //user {message.author.id} ign MC_name'
        ign_check = UUIDhandler.uuidcheck(IGN)
        #IGN check...
        if ign_check[0] != True:
            return False, f'Your IGN: {IGN} is not correct, please double check your IGN...'
        #Updates the DB users IGN
        curuser.IngameName = IGN
        curuser.UUID = ign_check[1][0]['id']
        #Converts and checks for the server in the DB
        curserver = db.GetServer(Name = sel_server.replace(' ', '_'))
        if curserver == None:
            return True,f'**Unable to process**: {message.content} Please manually whitelist this user, the Server: {sel_server} is invalid...'
        #Donator Status check
        if curserver.Donator:
            if not user.Donator:
                return False, f'This {curserver.FriendlyName} requires being a Donator!' 
        #Server whitelist flag check 
        if not curserver.Whitelist:
            return False, f'**Server**: {sel_server} whitelist is currently closed.'
        #Checks the whitelist file if the user already exists..
        status = whitelistUserCheck(curserver,curuser)
        if status == False:
            return False, f'You are already whitelisted on {curserver.FriendlyName}.'
        WhitelistWaitList.append({'User': curuser, 'IGN': IGN, 'timestamp' : curtime, 'server' : curserver, 'Context': message})
        return True, f'**Added User**: {user.DiscordName} to the Whitelist list...'
    else: 
        logging.info('Found Exisitng user...')
        #Checking if the user has an IGN (to prevent whitelisting others)
        if user.IngameName != None:
            curserver = db.GetServer(Name = sel_server.replace(' ', '_'))
            if curserver == None: 
                return True, f'**Unable to process**: {message.content} Please manually whitelist this user, the Server: {sel_server} is invalid...'
            #Donator Status check..
            if curserver.Donator:
                if not user.Donator:
                    return False, f'This {curserver.FriendlyName} requires being a Donator!' 
            if not curserver.Whitelist: #Check the servers whitelist flag
                return False, f'**Server**: {sel_server} whitelist is currently closed.'
            #Checks the whitelist file if the user already exists..
            status = whitelistUserCheck(curserver,user)
            if status == False:
                return False, f'You are already whitelisted on {curserver.FriendlyName}.'
            WhitelistWaitList.append({'User': user, 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message})
            return True,f'**Added User**: {user.DiscordName} to the Whitelist list...'
        else: 
            logging.warning('Found Existing User without an IGN...')
            #If no IGN; check the message for IGN and check its validity.
            ign_check = UUIDhandler.uuidcheck(IGN)
            if ign_check[0] != True:
                return False, f'Your IGN: {IGN} is not correct, please double check your IGN...'
            #Updates the DB users IGN
            user.IngameName = IGN
            user.UUID = ign_check[1][0]['id']
            #Converts and checks for the server in the DB
            curserver = db.GetServer(Name = sel_server.replace(' ', '_'))
            if curserver == None: 
                return True, f'**Unable to process**: {message.content} Please manually whitelist this user, the **Server**: {sel_server} is invalid...'
            #Server Whitelist flag check
            if not curserver.Whitelist: #Check the servers whitelist flag
                return False, f'**Server**: {sel_server} whitelist is currently closed.'
            #Checks the whitelist file if the user already exists..
            status = whitelistUserCheck(curserver,user)
            if status == False:
                return False, f'You are already whitelisted on {curserver.FriendlyName}.'
            WhitelistWaitList.append({'User': user , 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message})
            return True, f'**Added User**: {user.DiscordName} to the Whitelist list...'

#f'{message.author.name} you have been whitelisted on {curserver.FriendlyName}.'
#f'{message.author.name} you have been whitelisted on {curserver.FriendlyName}.'
#f'Whitelisting is currently *disabled* for {curserver.FriendlyName}.'

#Handles checking the whitelist list and adding users
def whitelistListCheck(client):
    #user = {'User': user , 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message}
    logging.info('Whitelist Wait List Check...')
    wl_channel = dbconfig.Whitelistchannel #ERROR DBConfig object has no attribute 
    if wl_channel == None:
        return False
    global WhitelistWaitList
    curtime = datetime.now()
    if not dbconfig.Whitelistwaittime == None or not dbconfig.Whitelistwaittime == '0':
        if len(WhitelistWaitList) == 0:
            return False
        for index in range(0,len(WhitelistWaitList)):
            user = WhitelistWaitList[index]
            waittime = timehandler.parse(dbconfig.Whitelistwaittime,True)
            if user['timestamp'] + waittime >= curtime :
                AMPservers[user['server'].InstanceID].ConsoleMessage(f'whitelist add {user["IGN"]}')
                user['server'].AddUser(user)
                discord_user = client.get_user(user['user'].DiscordID)
                #print(discord_user)
                WhitelistWaitList.remove(user)
                return user
    else:
        if len(WhitelistWaitList) == 0:
            return False
        for index in range(0,len(WhitelistWaitList)):
            user = WhitelistWaitList[index]
            AMPservers[user['server'].InstanceID].ConsoleMessage(f'whitelist add {user["IGN"]}')
            user['server'].AddUser(user)
            discord_user = client.get_user(user['user'].DiscordID)
            #print(discord_user)
            WhitelistWaitList.remove(user)
            return user

#This checks if the user is already whitelisted on the server...
def whitelistUserCheck(server,user):
    logging.info('Whitelist User Check...')
    whitelistcheck = AMPservers[server.InstanceID].getDirectoryListing('')
    for entry in whitelistcheck['result']:
        if entry['Filename'] == 'whitelist.json':
            whitelist = AMPservers[server.InstanceID].getFileChunk("whitelist.json",0,33554432)
            whitelist_data = base64.b64decode(whitelist["result"]["Base64Data"])
            whitelist_json = json.loads(whitelist_data.decode("utf-8"))
            for whitelist_user in whitelist_json:
                if whitelist_user['name'] == user.IngameName:
                    return False
                else:
                    continue

#Removes a user from the list if they have left for any reason. 
#Usually if they leave the Discord Server prior to getting Whitelisted...     
def whitelistUpdate(user,var = None):
    logging.info('Whitelist Update...')
    global WhitelistWaitList
    if var.lower() == 'leave':
        for entry in WhitelistWaitList:
            if entry['User'].DiscordName == user.name:
                WhitelistWaitList.remove(entry)