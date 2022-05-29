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
import asyncio

import random


#whitelist wait list



class Whitelist_module(commands.Cog):
    def __init__(self,client):
        self.client = client


    def vars(self,AMP,AMPservers,DB,DBConfig):
        self.AMP = AMP
        self.AMPservers = AMPservers
        self.DB = DB
        self.DBConfig = DBConfig
        self.WhitelistWaitList = []
        self.UserAssisted = {}
        self.FailedRequests = {}

    #Used to add users to the DB when they request whitelist in the WL channel if Autowhitelist is False.
    async def whitelistMSGHandler(self,message):
        logging.info('Whitelist Channel Message Handler...')
        curtime = datetime.now()
        user = self.DB.GetUser(str(message.author.id))

        if user == None:
            logging.info(f'Adding {message.author.name} to the Database...')
            user = self.DB.AddUser(DiscordID = str(message.author.id), DiscordName = message.author.name)
        
        wl_request = parse.ParseIGNServer(message.content.lower())
        if wl_request == None:
            if message.id not in self.FailedRequests:
                logging.info('Adding User to FailedRequests...')
                data = {message.id : message}
                self.FailedRequests.update(data)
                #print(FailedRequests)

            #This is to help assist players if they do not use the proper format to request a whitelist
            if self.DBConfig.Whitelistassist:
                if message.author.id in self.UserAssisted:
                    return True, f'User has been recently assisted; waiting to send a message again...'

                logging.info('Adding User to User Assisted...')
                data = {message.author.id : curtime}
                self.UserAssisted.update(data)
                #print(UserAssisted)

                response = f'**Failed Request**: I was unable to understand your message; please send another message or edit your previous message with this following format: \n{config.WhitelistFormat} '
                return await message.reply(content = response)
                #return False, response

            response = f'**Unable to process**: {message.content} Please manually whitelist this user and update their IGN via //user {message.author.id} ign Minecraft_Name'
            return True, response

        IGN,sel_server = wl_request
        logging.info(f'**Whitelist Request**: {message.author.name} with IGN: {IGN}, on Server: {sel_server}')

        #IGN check...
        ign_check = UUIDhandler.uuidcheck(IGN)
        if ign_check[0] != True:
            return await message.reply(f'Hey, your IGN of {IGN} does not exist, could you please double check your IGN...')
            #return False, f'Hey, your IGN of {IGN} does not exist, could you please double check your IGN...'
            
        #Updates the DB users IGN
        if user.IngameName == None:
            user.IngameName = IGN
            user.UUID = ign_check[1][0]['id']

        #Converts and checks for the server in the DB
        curserver = self.DB.GetServer(Name = (sel_server.replace(' ', '_')))
        if curserver == None:
            if message.id not in self.FailedRequests:
                logging.info('Adding User to FailedRequests...')
                data = {message.id : message}
                self.FailedRequests.update(data)
                #print(FailedRequests)

            #This is to assist with users if they provided a server name that does not exist or incorrect.
            if self.DBConfig.Whitelistassist:
                if message.author.id in self.UserAssisted:
                    return True, f'User has been recently assisted; waiting to send a message again...'
                
                logging.info('Adding User to User Assisted...')
                data = {message.author.id : curtime}
                self.UserAssisted.update(data)
                #print(UserAssisted)

                response = f'**Failed Request**: I am unable to find the Server: **{sel_server}**, please type `//serverlist` and find the correct server name/server nickname then edit/resubmit your request.'
                return await message.reply(content = response)
                #return False, response

            return True, f'**Unable to process**: {message.content} Please manually whitelist this user, the Server: {sel_server} is invalid...'

        #Donator Status check
        if curserver.Donator:
            if not user.Donator:
                return await message.reply(f'**Server**: {curserver.FriendlyName} requires being a Donator!')
                #return False, f'**Server**: {curserver.FriendlyName} requires being a Donator!' 
        
        #Server whitelist flag check 
        if not curserver.Whitelist:
            return await message.reply(f'**Server**: {curserver.FriendlyName} whitelist is currently offline.')
            #return False, f'**Server**: {curserver.FriendlyName} whitelist is currently offline.'
        
        #Checks the whitelist file if the user already exists..
        status = self.whitelistUserCheck(curserver,user.IngameName)
        if status == False:
            return await message.reply(f'You are already whitelisted on {curserver.FriendlyName}.')
            #return False, f'You are already whitelisted on {curserver.FriendlyName}.'

        if self.DB.GetConfig().Autowhitelist:
            self.WhitelistWaitList.append({'User': user, 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message})
            return True, f'**Added User**: {user.DiscordName} to the Whitelist list...'
        return True, f'**Auto-Whitelist** is currently `False`, User information added to Database.'

    #Handles checking the whitelist list and adding users
    #user = {'User': user , 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message}
    async def whitelistListCheck(self):
        logging.info('Whitelist Wait List Check...')

        wl_channel = self.DBConfig.Whitelistchannel 
        if wl_channel == None:
            return False
        #If my list is empty; return
        if len(self.WhitelistWaitList) == 0:
            logging.info('Whitelist Wait List is currently empty...')
            return False
            
        curtime = datetime.now()
        for index in range(0,len(self.WhitelistWaitList)):
            user = self.WhitelistWaitList[index]
            waittime = timedelta(minutes= 0)
            
            if self.DBConfig.Whitelistwaittime != None:
                waittime = timehandler.parse(self.DBConfig.Whitelistwaittime,True)

            if user['timestamp'] + waittime <= curtime :
                discord_user = user['Context'].guild.get_member(int(user['User'].DiscordID))
                discord_role = user['Context'].guild.get_role(int(user['server'].DiscordRole))
                print(discord_user,dir(discord_user))
                logging.info(f'**Attempting to Whitelist** {discord_user} on {user["server"].FriendlyName}')
                status = self.whitelistUserCheck(user['server'],user['IGN'])

                if status == False:
                    logging.info(f'**{discord_user} was already whitelisted, removed from list...**')
                    self.WhitelistWaitList.remove(user)
                    return None

                self.WhitelistWaitList.remove(user)
                self.AMPservers[user['server'].InstanceID].ConsoleMessage(f'whitelist add {user["IGN"]}')

                if config.Randombotreplies: #Default is True
                    replynum = random.randint(0,len(config.Botwhitelistreplies)-1)
                    await user['Context'].reply(content = f"{config.Botwhitelistreplies[replynum]}")
                    if discord_role != None:
                        await discord_user.add_roles(discord_role,reason='Auto Whitelist')
                    user['server'].AddUser(user['User'])
                return
            
            if not config.Randombotreplies:
                try:
                    await user['Context'].reply(config.Botwhitelistreplies[self.AMPservers[user['server'].InstanceID].Index])
                    await discord_user.add_roles(discord_role,reason='Auto Whitelist')
                    user['server'].AddUser(user['User'])
                    return
                except Exception as e:
                    print(e)
                    await user['Context'].reply(f'{user["User"].name} you have been whitelisted on {user["server"].FriendlyName}.')
                    return
                    
        

    #This checks if the user is already whitelisted on the server...
    def whitelistUserCheck(self,server,user_ign):
        logging.info('Whitelist User Check...')
        print(server,server.InstanceID)
        whitelistcheck = self.AMPservers[server.InstanceID].getDirectoryListing('')
        for entry in whitelistcheck['result']:
            if entry['Filename'] == 'whitelist.json':
                whitelist = self.AMPservers[server.InstanceID].getFileChunk("whitelist.json",0,33554432)
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
    def whitelistUpdate(self,user = None,var = None):
        logging.info('Whitelist Update...')

        if var.lower() == 'leave':
            for entry in self.WhitelistWaitList:
                if entry['User'].DiscordName == user.name:
                    logging.info(f'Removed {entry} from the list, they left the Server...')
                    self.WhitelistWaitList.remove(entry)
        
        if var.lower() == 'cleanup':
            logging.info('Attempting to Cleanup Failed Requests and User Assists')
            curtime = datetime.now()

            if len(self.FailedRequests) != 0:
                #for request in FailedRequests:
                FRkeys = list(self.FailedRequests.keys())
                for request in FRkeys:
                    print(self.DB.GetConfig().Whitelistwaittime)
                    print(self.FailedRequests[request],self.FailedRequests[request].created_at)
                    if self.FailedRequests[request].created_at + timedelta(minutes = int(self.DB.GetConfig().Whitelistwaittime)) <= curtime:
                        self.FailedRequests.pop(request)
                        logging.info(f'Removed {request}')
                
            if len(self.UserAssisted) != 0:
                UAkeys = list(self.UserAssisted.keys())
                for assist in UAkeys:
                    print(self.UserAssisted[assist])
                    if self.UserAssisted[assist] + timedelta(minutes = 5) <= curtime:
                        self.UserAssisted.pop(assist)
                        logging.info(f'Removed {assist}')
    
    async def setup(client):
        await client.add_cog(Whitelist_module(client))
