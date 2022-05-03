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
import discord
from discord.ext import commands
from datetime import datetime,timedelta
import base64
import json
import logging
import parse
import timehandler
import UUIDhandler
import config


#whitelist wait list
WhitelistWaitList = []
UserAssisted = {}
FailedRequests = {}

def init(origAMP,origAMPservers,origdb,origdbconfig):
    global AMP,AMPservers,db,dbconfig
    AMP = origAMP
    AMPservers = origAMPservers
    db = origdb
    dbconfig = origdbconfig
    return


#Used to add users to the DB when they request whitelist in the WL channel if Autowhitelist is False.
async def whitelistMSGHandler(message):
    logging.info('Whitelist Channel Message Handler...')
    global WhitelistWaitList,db,dbconfig
    curtime = datetime.now()
    user = db.GetUser(str(message.author.id))

    if user == None:
        logging.info(f'Adding {message.author.name} to the Database...')
        user = db.AddUser(DiscordID = str(message.author.id), DiscordName = message.author.name)
    
    wl_request = parse.ParseIGNServer(message.content.lower())
    if wl_request == None:
        if message.id not in FailedRequests:
            logging.info('Adding User to FailedRequests...')
            data = {message.id : message}
            FailedRequests.update(data)
            #print(FailedRequests)

        #This is to help assist players if they do not use the proper format to request a whitelist
        if dbconfig.Whitelistassist:
            if message.author.id in UserAssisted:
                return True, f'User has been recently assisted; waiting to send a message again...'

            logging.info('Adding User to User Assisted...')
            data = {message.author.id : curtime}
            UserAssisted.update(data)
            #print(UserAssisted)

            response = f'**Failed Request**: I was unable to understand your message; please send another message or edit your previous message with this following format: \n{config.WhitelistFormat} '
            return False, response
        response = f'**Unable to process**: {message.content} Please manually whitelist this user and update their IGN via //user {message.author.id} ign Minecraft_Name'
        return True, response

    IGN,sel_server = wl_request
    logging.info(f'**Whitelist Request**: {message.author.name} with IGN: {IGN}, on Server: {sel_server}')

    #IGN check...
    ign_check = UUIDhandler.uuidcheck(IGN)
    if ign_check[0] != True:
        return False, f'Hey, your IGN of {IGN} does not exist, could you please double check your IGN...'
        
    #Updates the DB users IGN
    if user.IngameName == None:
        user.IngameName = IGN
        user.UUID = ign_check[1][0]['id']

    #Converts and checks for the server in the DB
    curserver = db.GetServer(Name = (sel_server.replace(' ', '_')))
    if curserver == None:
        if message.id not in FailedRequests:
            logging.info('Adding User to FailedRequests...')
            data = {message.id : message}
            FailedRequests.update(data)
            #print(FailedRequests)

        #This is to assist with users if they provided a server name that does not exist or incorrect.
        if dbconfig.Whitelistassist:
            if message.author.id in UserAssisted:
                return True, f'User has been recently assisted; waiting to send a message again...'
            
            logging.info('Adding User to User Assisted...')
            data = {message.author.id : curtime}
            UserAssisted.update(data)
            #print(UserAssisted)

            response = f'**Failed Request**: I am unable to find the Server: **{sel_server}**, please type `//serverlist` and find the correct server name/server nickname then edit/resubmit your request.'
            return False, response
        return True, f'**Unable to process**: {message.content} Please manually whitelist this user, the Server: {sel_server} is invalid...'

    #Donator Status check
    if curserver.Donator:
        if not user.Donator:
            return False, f'**Server**: {curserver.FriendlyName} requires being a Donator!' 
    
    #Server whitelist flag check 
    if not curserver.Whitelist:
        return False, f'**Server**: {curserver.FriendlyName} whitelist is currently offline.'
    
    #Checks the whitelist file if the user already exists..
    status = await whitelistUserCheck(curserver,user.IngameName)
    if status == False:
        return False, f'You are already whitelisted on {curserver.FriendlyName}.'
    if db.GetConfig().Autowhitelist:
        WhitelistWaitList.append({'User': user, 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message})
        return True, f'**Added User**: {user.DiscordName} to the Whitelist list...'
    return True, f'**Auto-Whitelist** is currently `False`, User information added to Database.'

#Handles checking the whitelist list and adding users
#user = {'User': user , 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message}
async def whitelistListCheck(client):
    logging.info('Whitelist Wait List Check...')
    global WhitelistWaitList

    wl_channel = dbconfig.Whitelistchannel 
    if wl_channel == None:
        return False
    #If my list is empty; return
    if len(WhitelistWaitList) == 0:
        logging.info('Whitelist Wait List is currently empty...')
        return False
        
    curtime = datetime.now()
    for index in range(0,len(WhitelistWaitList)):
        user = WhitelistWaitList[index]
        waittime = timedelta(minutes= 0)
        
        if dbconfig.Whitelistwaittime != None:
            waittime = timehandler.parse(dbconfig.Whitelistwaittime,True)

        if user['timestamp'] + waittime <= curtime :
            discord_user = client.get_user(int(user['User'].DiscordID))
            logging.info(f'**Attempting to Whitelist** {discord_user} on {user["server"].FriendlyName}')
            status = whitelistUserCheck(user['server'],user['IGN'])

            if status == False:
                logging.info(f'**{discord_user} was already whitelisted, removed from list...**')
                WhitelistWaitList.remove(user)
                return None

            WhitelistWaitList.remove(user)
            AMPservers[user['server'].InstanceID].ConsoleMessage(f'whitelist add {user["IGN"]}')
            await discord_user.add_roles(int(user['server'].DiscordRole),reason='Auto Whitelist')
            user['server'].AddUser(user['User'])
            return user
    

#This checks if the user is already whitelisted on the server...
def whitelistUserCheck(server,user_ign):
    logging.info('Whitelist User Check...')
    whitelistcheck = AMPservers[server.InstanceID].getDirectoryListing('')
    for entry in whitelistcheck['result']:
        if entry['Filename'] == 'whitelist.json':
            whitelist = AMPservers[server.InstanceID].getFileChunk("whitelist.json",0,33554432)
            whitelist_data = base64.b64decode(whitelist["result"]["Base64Data"])
            whitelist_json = json.loads(whitelist_data.decode("utf-8"))
            for whitelist_user in whitelist_json:
                #print(whitelist_user,user_ign)
                if whitelist_user['name'].lower() == user_ign.lower():
                    return False
                else:
                    continue
    return True
    

#Removes a user from the list if they have left for any reason. 
#Usually if they leave the Discord Server prior to getting Whitelisted...     
def whitelistUpdate(user = None,var = None):
    logging.info('Whitelist Update...')
    global WhitelistWaitList,FailedRequests,UserAssisted

    if var.lower() == 'leave':
        for entry in WhitelistWaitList:
            if entry['User'].DiscordName == user.name:
                logging.info(f'Removed {entry} from the list, they left the Server...')
                WhitelistWaitList.remove(entry)
    
    if var.lower() == 'cleanup':
        logging.info('Attempting to Cleanup Failed Requests and User Assists')
        curtime = datetime.now()

        if len(FailedRequests) != 0:
            #for request in FailedRequests:
            FRkeys = list(FailedRequests.keys())
            for request in FRkeys:
                print(db.GetConfig().Whitelistwaittime)
                print(FailedRequests[request],FailedRequests[request].created_at)
                if FailedRequests[request].created_at + timedelta(minutes = int(db.GetConfig().Whitelistwaittime)) <= curtime:
                    FailedRequests.pop(request)
                    logging.info(f'Removed {request}')
            
        if len(UserAssisted) != 0:
            UAkeys = list(UserAssisted.keys())
            for assist in UAkeys:
                print(UserAssisted[assist])
                if UserAssisted[assist] + timedelta(minutes = 5) <= curtime:
                    UserAssisted.pop(assist)
                    logging.info(f'Removed {assist}')
    