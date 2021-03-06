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
## Gatekeeper Bot
## k8thekat - 11/5/2021
## 
import discord
from discord.ext import commands 
import json
from distutils.util import strtobool
import time
from pprint import pprint
import threading
import asyncio
from datetime import datetime, timedelta
import base64
import random
import traceback
import logging

# Bot Scripts
import database
import tokens
import logger
logger.init()
from AMP_API import AMPAPI
import config
import endReset
import whitelist 
import chatfilter
import timehandler
import UUIDhandler
import console
import chat


data = 'alpha-3.0.18' #Major.Minor.Revisions
logging.info(f'Version: {data}')

async_loop = asyncio.new_event_loop()
asyncio.set_event_loop(async_loop)

intents = discord.Intents.default() # Default
intents.members = True
client = commands.Bot(command_prefix = '//', intents=intents, loop=async_loop)
client.remove_command('help')

#AMP API setup
AMP = AMPAPI()
AMPservers = AMP.getInstances() # creates objects for each server in AMP (returns serverlist)
#AMP.sessionCleanup() #cleans up any existing connections to prevent excessive AMP connections

#database setup
db = database.Database()
dbconfig = db.GetConfig()

  
#sets the whitelist flag to true/false for a specific server
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'whitelist' 'true/false'
def serverwhitelistflag(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    logging.info('Server Whitelist Flag...')       
    if len(parameter) == 3:
        try:
            curserver.Whitelist = strtobool(parameter[2])
            response = f'**Set Whitelist on Server**: {curserver.FriendlyName} to {bool(curserver.Whitelist)}.'
        except:
            response = f'**Format**: //server {curserver.FriendlyName} whitelist (true or false)'
    else:
        flag = bool(curserver.Whitelist)
        response = f'**Server**: {curserver.FriendlyName} Whitelist is currently set to {flag}.'
    return response

#sets the donator flag to true/false for a specific server
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'donator' 'true/false'
def serverdonatorflag(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    logging.info('Server Donator Flag...')
    if len(parameter) == 3:
        try:
            curserver.Donator = strtobool(parameter[2])
            if config.donations:
                response = f'Set Donator Only on Server: {curserver.FriendlyName} to {bool(curserver.Donator)}.'
            else:
                response = f'You have set Donator Only on Server: {curserver.FriendlyName} to {bool(curserver.Donator)}, but your config setting Donations is False'

        except:
            response = f'**Format**: //server {curserver.FriendlyName} donator (true or false)'
    else:
        flag = bool(curserver.Donator)
        response = f'**Server**: {curserver.FriendlyName} Donator Only is currently set to {flag}.'
    return response

#set a specific servers discord role
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'role' '1234567890'
#Test Role: 914303203917574185
def serverrole(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    logging.info('Server Role...')
    if len(parameter) >= 3:
        role = roleparse(ctx,parameter[2]) #returns a role object or None
        if role != None:
            curserver.DiscordRole = role.id
            response = f'**Server**: {curserver.FriendlyName} now has its role set to {role.name}'
        else:
            response = f'The Discord Role ID: {parameter[2]}, does not exist in **{ctx.guild.name}**.'
    else:
        response = f'**Format**: //server {curserver.FriendlyName} role (Discord Role ID or Discord Role Name).'
    return response

#set a specific servers discord channel
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'discordchannel' 'chat/console' '1234567890'
def serverdiscordchannel(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    logging.info('Server Discord Channel...')
    if len(parameter) == 4:
        channel = channelparse(ctx,parameter[3]) #returns a channel object or None
        if channel == None:
            return f'The Channel ID: {parameter[3]} is not valid.'    
        if parameter[2].lower() == 'chat':
            if parameter[3] == 'None':
                curserver.DiscordChatChannel(None)
            else:
                curserver.DiscordChatChannel = str(channel.id)
                return f'Set Discord Chat Channel for {curserver.FriendlyName} to {channel.name}.'  
        elif parameter[2].lower() == 'console':
            if parameter[3] == 'None':
                curserver.DiscordConsoleChannel(None)
                console.threadstop(curserver) #curserver = db object
            else:
                curserver.DiscordConsoleChannel = str(channel.id)
                #This starts up the thread now that a discord console channel was set.
                console.threadinit(curserver,channel,client,async_loop) #curserver= db object, channel = discord object, client = bot object
                return f'Set Discord Console Channel for {curserver.FriendlyName} to {channel.name}.'
    else:
        return f'**Format**: //server {curserver.FriendlyName} discordchannel (chat or console) discord_channel_name or discord_channel_id'

#add/remove a specific servers nickname
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'nickname' 'add/remove' 'nickname'
def servernickname(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    logging.info('Server Nickname...')
    if parameter[2].lower() == 'list':
        nicknames = ', '.join(curserver.Nicknames)
        return f'{curserver.FriendlyName} has the Nicknames: {nicknames}'
    elif parameter[2].lower() == 'add':
        if parameter[3] not in curserver.Nicknames:
            curserver.AddNickname(parameter[3])
            return f'Added {parameter[3]} to {curserver.FriendlyName}.'
        else:
            return f'The nickname {parameter[3]} already exist for {curserver.FriendlyName}.'
    elif parameter[2].lower() == 'remove':
        if parameter[3] in curserver.Nicknames:
            curserver.RemoveNickname(parameter[3])
            return f'Removed {parameter[3]} from {curserver.FriendlyName}.'
        else:
            return f'The nickname {parameter[3]} does not exist for {curserver.FriendlyName}.'
    else:
        return f'**Format**: //server {curserver} nickname (add or remove or list) name'

#get a specific servers status
def serverstatus(ctx,curserver,parameter):
    if curserver.Running == False:
        return f'The Server: {curserver.FriendlyName} is currently offline... '
    logging.info('Server Status...')
    status = AMPservers[curserver.InstanceID].getStatus()
    stats = f'**Server**: {curserver.FriendlyName}\n{status}'
    return stats

#get a list of users for a specific server
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'userlist'
def serveruserlist(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    logging.info(f'Server User list...')
    userlist = curserver.GetAllUsers()
    userlist_names = []
    #print(len(userlist))
    if len(userlist) == 0:
        return None
    for user in userlist:
        #print(dir(user))
        curuser = user.GetUser()
        userlist_names.append(curuser.DiscordName)
        users = ', '.join(userlist_names)
    return users

#check a specific user infractions for a specific server
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'userinfraction' 'user' 'notes/details'
#user:DBUser, mod:DBUser, note:str
def serveruserinfraction(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    logging.info('Server User Infraction...')
    modauthor = db.GetUser(ctx.author.id)
    details = ' '.join(parameter[3:])
    curuser = db.GetUser(parameter[2])
    if curuser != None:
        curserver.AddUserInfraction(user= curuser ,mod= modauthor ,note= details)
        return f'User Infraction for {curuser.DiscordName} added to {curserver.FriendlyName} by {modauthor.DiscordName}\n**Note**: {details}'
    else:
        return f'**Error Adding Infraction**: User: {parameter[2]} needs to be added to the database...'

def serverinfo(ctx,curserver,parameter):
    if not rolecheck(ctx, 'General'):
        return 'User does not have permission.'
    logging.info('Server Info...')
    try:
        role = ctx.guild.get_role(int(curserver.DiscordRole))
    except:
        role = curserver.DiscordRole
    servernicknames = ', '.join(curserver.Nicknames)
    if len(curserver.Nicknames) == 0:
        return f'**Name**: {curserver.FriendlyName}\n**Whitelist**: `{bool(curserver.Whitelist)}`\n**Donator**: `{bool(curserver.Donator)}`\n**Discord Console Channel**: <#{curserver.DiscordConsoleChannel}>\n**Discord Chat Channel**: <#{curserver.DiscordChatChannel}>\n**Discord Role**: {role}'
    
    response = f'**Name**: {curserver.FriendlyName}\n\t*Nicknames*: {servernicknames}\n**Whitelist**: `{bool(curserver.Whitelist)}`\n**Donator**: `{bool(curserver.Donator)}`\n**Discord Console Channel**: <#{curserver.DiscordConsoleChannel}>\n**Discord Chat Channel**: <#{curserver.DiscordChatChannel}>\n**Discord Role**: {role}'
    return response

#bans a specific user from a specific server
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'userban' 'user' 'time' 'reason'
def serveruserban(ctx,curserver,parameter):
    if curserver.Running == False:
        return f'The Server: {curserver.FriendlyName} is currently offline... '
    logging.info('Server Ban Initiated...')
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    curuser = None
    if len(parameter) <= 2:
        return f'**Format**: //server {curserver.FriendlyName} userban {curuser} time(Optional) reason:(optional)'
    if len(parameter) >= 3:
        curuser = db.GetUser(parameter[2])
    if curuser == None:
           return f'Unable to find the User: {parameter[2]}'
    serveruser = curserver.GetUser(curuser)
    if serveruser == None:
        curserver.AddUser(curuser)
        serveruser = curserver.GetUser(curuser)
    bantime = timehandler.parse(parameter)
    response = f'**User**: {curuser.DiscordName} has been banned until {bantime.strftime("%Y/%m/%d **Time**: %X (UTC)")}'
    if bantime == True:
        return f'**Format**: //server {curserver.FriendlyName} userban {curuser} time(Optional) **reason**:(optional)'
    if bantime == False:
        bantime = dbconfig.Bantimeout
    for entry in parameter:
        entry = entry.replace('Reason:','reason:')
        reason_id = entry.find('reason:')
        if reason_id != -1:
            reason_id = parameter.index('reason:')
            reason = []
            reason = ' '.join(parameter[reason_id+1:])
            response += f' **Reason**: {reason}'
    if reason_id != -1:      
        AMPservers[curserver.InstanceID].ConsoleMessage(f'ban {curuser.IngameName} {bantime} {reason}')
        serveruser.SuspensionExpiration = bantime
    else:
        AMPservers[curserver.InstanceID].ConsoleMessage(f'ban {curuser.IngameName} {bantime}')
        serveruser.SuspensionExpiration = bantime
    return response
    
#AMP API functions for servers
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'restart'
def serverrestart(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    botoutput(f'**Server**: {curserver.FriendlyName} Restarted by {ctx.author.name}...',level= 'warning')
    AMPservers[curserver.InstanceID].RestartInstance()
    return f'**Server**: {curserver.FriendlyName} is restarting...'

def serverstart(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    botoutput(f'**Server**: {curserver.FriendlyName} Started by {ctx.author.name}...',level= 'warning')
    AMPservers[curserver.InstanceID].StartInstance()
    return f'**Server**: {curserver.FriendlyName} has been started...'

def serverstop(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    if curserver.Running == False:
        return f'The Server: {curserver.FriendlyName} is currently offline... '
    botoutput(f'**Server**: {curserver.FriendlyName} Stopped by {ctx.author.name}...',level= 'warning')
    AMPservers[curserver.InstanceID].StopInstance()
    curserver.Running = False
    return f'**Server**: {curserver.FriendlyName} has been stopped...'

def serverkill(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    if curserver.Running == False:
        return f'The Server: {curserver.FriendlyName} is currently offline... '
    botoutput(f'**Server**: {curserver.FriendlyName} Killed by {ctx.author.name}...',level= 'warning')
    AMPservers[curserver.InstanceID].KillInstance()
    return f'**Server**: {curserver.FriendlyName} has been killed...'

def servermaintenance(ctx,curserver,parameter):
    if curserver.Running == False:
        return f'The Server: {curserver.FriendlyName} is currently offline... '
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    botoutput(f'**Server**: {curserver.FriendlyName} Maintenance Mode toggled by {ctx.author.name}...',level= 'warning')
    dbuser_list = db.GetAllUsers(ServerModerator=True)
    if len(parameter) <= 2:
        return f'**Format**: //server {curserver.FriendlyName} maintenance (on or off)'
    serverfile_list = AMPservers[curserver.InstanceID].getDirectoryListing('')
    if parameter[2].lower() == 'true':
        #prevents players from requesting whitelist
        curserver.Whitelist = False
        #op's every member of staff for said server to allow them to bypass the whitelist setting.(just in case)
        for user in dbuser_list:
            if user.IngameName != None:
                AMPservers[curserver.InstanceID].ConsoleMessage(f'op {user.IngameName}')
        for filename in serverfile_list['result']:
            if filename['Filename'] == 'whitelist.json':
                blankwhitelistgenerator(curserver.InstanceID)
                AMPservers[curserver.InstanceID].renameFile('whitelist.json', 'whitelist_public.json')
                time.sleep(.5)
                AMPservers[curserver.InstanceID].renameFile('whitelist_blank.json', 'whitelist.json')
        return f'**Server**: {curserver.FriendlyName} has been put into Maintenance Mode'
    if parameter[2].lower() == 'false':
        #allows players to request whitelist
        curserver.Whitelist = True
        for filename in serverfile_list['result']:
            if filename['Filename'] == 'whitelist.json':
                AMPservers[curserver.InstanceID].renameFile('whitelist.json', 'whitelist_blank.json')
                time.sleep(.5)
                AMPservers[curserver.InstanceID].renameFile('whitelist_public.json', 'whitelist.json')
        return f'**Server**: {curserver.FriendlyName} has been taken out of Maintenance Mode'
    return

def serverEndReset(ctx,curserver,parameter):
    global AMPservers
    if config.DragonReset:
        results = endReset.init(AMPservers,curserver)
    if results == True:
        return f'**Server**: {curserver.FriendlyName} has had The End fight reset and the World removed...'
    else:
        botoutput(f'**ERROR**: Resetting the End for {curserver.FriendlyName}, check your config file...',level= 'error')
 
serverfuncs = {
            'info' : serverinfo, 
            'whitelist': serverwhitelistflag, 
            'donator': serverdonatorflag, 
            'role': serverrole, 
            'channel' : serverdiscordchannel,
            'nickname' : servernickname,
            'status' : serverstatus,
            'list' : serveruserlist,
            'infraction' : serveruserinfraction,
            'ban' : serveruserban,
            'restart' : serverrestart,
            'start' : serverstart,
            'stop' : serverstop,
            'kill' : serverkill,
            'maintenance' : servermaintenance,
            'endreset' : serverEndReset
}

@client.command()
#This is the main handler for all Server related Functions
#'//server 'parameter[0]' 'parameter[1]' 'parameter[2]' 'parameter[3]'
#'//server (server) (funcs: whitelist,donator,role,channel,nickname,status) (options: add,remove,set) (parameter)
async def server(ctx,*parameter):
    #checks if curserver is a server in the database.
    if 'example' in parameter:
        await ctx.send('**Examples**:' +
            '\n //server Vanilla userban Notch w:3d:6 reason: Stealing someones items.'+ 
            '\n //server Valhelsia3 role 617967701381611520' +
            '\n //server ProjectOzone3 nickname add po3' +
            '\n //server SkyFactory channel chat SkyFactory-Chat')

    if 'help' in parameter:
        option_help = '**Options**: None'
        parameter_help = '**Parameters**: server_name '

        if 'channel' in parameter:
            option_help = '**Options**: chat or console'
            parameter_help += '/ channel'

        if 'nickname' in parameter:
            option_help = '**Options**: list or add or remove'

        if ('whitelist' in parameter) or ('donator' in parameter) or ('maintenance' in parameter):
            parameter_help += '/ true or false'

        if 'infraction' in parameter:
            parameter_help += '/ user_name / note(Optional) '

        if 'role' in parameter:
            parameter_help += '/ role'

        if 'ban' in parameter:
            parameter_help += '/ user_name / time(Optional) / reason:(Optional)'

        await ctx.send(f'**Format**: //server server_name `function` `option` `parameter`',reference = ctx.message.to_reference())
        return await ctx.send(f"**Functions**: " + ', '.join(serverfuncs.keys()) + '\n' + option_help + '\n' + parameter_help)

    if len(parameter) < 2:
        return await ctx.send(f'**Format**: //server server_name `function` `option` `parameter`',reference = ctx.message.to_reference())

    curserver = db.GetServer(Name= parameter[0])
    if curserver == None:
        response = f'**Server**: {parameter[0]} does not exist.'

    if curserver != None:
            if parameter[1].lower() in serverfuncs:
                response = serverfuncs[parameter[1]](ctx,curserver,parameter) 
            else:
                response = f'The Command: {parameter[1]} is not apart of my list. Commands: ' + ", ".join(serverfuncs.keys())
    return await ctx.send(response,reference= ctx.message.to_reference())

#Converts IGN to discord_name
def userIGNdiscord(user):
    user_find = db.GetUser(user)
    if user_find != None:
        return user_find.DiscordName
    return user

#Gets a users data from the database and discord
#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'username' 'info'
def userinfo(ctx,curuser,parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    logging.info('User Info...')
    userinfractionslist = curuser.Infractions
    userservers = curuser.GetAllServers() 
    if curuser.GlobalBanExpiration != None:
        globalbanformat = curuser.GlobalBanExpiration['Date'].strftime('%Y/%m/%d Time: %X (UTC)')
    else:
        globalbanformat = curuser.GlobalBanExpiration
    response = f'**DiscordID**: {curuser.DiscordID}\n**DiscordName**: {curuser.DiscordName}\n**InGameName**: {curuser.IngameName}\n**Donator**: `{bool(curuser.Donator)}`\n**Banned**: {globalbanformat}'
    if len(userservers) != 0:
        for entry in userservers:
            if entry.LastLogin != None:
                lastloginformat = entry.LastLogin.strftime('Date: %Y/%m/%d | Time: %X (UTC)')
            else:
                lastloginformat = entry.LastLogin
            if entry.SuspensionExpiration != None:
                Suspensionformat = entry.SuspensionExpiration.strftime('Date: %Y/%m/%d | Time: %X (UTC)')
            else:
                Suspensionformat = entry.SuspensionExpiration
            data = f'\n**Server**: {entry.GetServer().FriendlyName}\n\t__Whitelisted__: `{bool(entry.Whitelisted)}`\n\t__Suspended__: {Suspensionformat}\n\t__Last Login__: {lastloginformat}'
            response += data
    if len(userinfractionslist) != 0:
        for entry in userinfractionslist:
            dateformat = entry['Date'].strftime('%Y/%m/%d Time: %X (UTC)')
            if entry['Server'] == None:
                data = (f"\n**Infraction ID**: {entry['ID']}\n\t__Date__: {dateformat}\n\t__Who Reported__: {entry['DiscordName']}\n\t__Notes__: {entry['Note']}")
                response += data
            else:
                data = (f"\n**Infraction ID**: {entry['ID']}\n\__Date__: {dateformat}\n\t__Who Reported__: {entry['DiscordName']}\n\t__Server__: {entry['Server']}\n\t__Notes__: {entry['Note']}")
                response += data
    return response

#add user to database (!!REQUIRES DISCORD ID!!)
#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'discordid' 'add'
def useradd(ctx,curuser,parameter = None):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    logging.info('User add...')
    db.AddUser(DiscordID = str(curuser.id), DiscordName = curuser.name)
    response = f'Successfuly added {curuser.name} to database. (DiscordID: {curuser.id}).'
    return response

#gets the users infractions
#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'name'  4 'add/del' 'server' 'notes'
#/user 'name'  4 'del' 'ID'
def userinfractions(ctx,curuser,parameter):
    logging.info('User Infractions Triggered...')
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    if len(parameter) >= 4:
        if parameter[2].lower() == 'add':
            mod = db.GetUser(ctx.author.id)
            server_id,reason_id = -1, -1
            found_reason,found_server = False,False
            db_server, reason = None,None
            response = f'Added Infraction for {curuser.DiscordName}'

            for index in range(2,len(parameter)):
                entry = parameter[index]
                entry = entry.replace('Reason:','reason:')
                entry = entry.replace('Server:','server:')
                if entry.find('server:') != -1:
                    server_id = index
                if entry.find('reason:') != -1:
                    reason_id = index
            
            if reason_id != -1:
                found_reason = True
                reason = []
                reason = ' '.join(parameter[reason_id:])
                if len(reason) == 0:
                    reason = parameter[reason_id+1]

            if server_id != -1:
                found_server = True
                server = parameter[server_id].replace('server:','')    
                if len(server) == 0:
                    server = parameter[server_id+1]

            if found_server == True:
                db_server = db.GetServer(Name = server)
                response += f'on {server.FriendlyName}' 
            
            if found_reason == True:
                response += f'Reason: {reason}'

            curuser.AddInfraction(server = db_server, mod = mod, note = reason)
            
        elif parameter[2].lower() == 'del':
                curuser.DelInfraction(ID=parameter[3])
                response = f'Removed Infraction {parameter[3]} on {curuser.DiscordName}' 
    else:
        response = f"**Format**: //user user_name infraction option(Add or Del) infractionID('Del' only) reason:(Optional)"
    return response

# updates user parameters in database (donator)
#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'username' 'donator' 'true/false'
def userdonator(ctx,curuser,parameter):
    if not rolecheck(ctx, 'Moderator'):
        return 'User does not have permission.'
    logging.info('User Donator...')
    if len(parameter) == 3:
        if parameter[2].lower() == 'true':
            curuser.Donator = True
            response = f'Set {curuser.DiscordName} donator to `True`'
        else:
            curuser.Donator = False
            response = f'Set {curuser.DiscordName} donator to `False`'
    else:
        response = 'You must specify True or False.'
    return response

#Sets a user Moderator flag to True or False for auto OP on Maintenance Mode
def usermoderator(ctx,curuser,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    logging.info('User Moderator...')
    if len(parameter) == 3:
        if parameter[2].lower() == 'true':
            curuser.ServerModerator = True
            response = f'Set {curuser.DiscordName} Server Moderator to `True`'
        else:
            curuser.ServerModerator = False
            response = f'Set {curuser.DiscordName} Server Moderator to `False`'
    else:
        response = 'You must specify True or False.'
    return response

#updates user ign in database
#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'username' 'ingamename' 'k8_thekat'
def userign(ctx,curuser,parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    logging.info('User IGN...')
    if len(parameter) == 3:
        ign_check = UUIDhandler.uuidcheck(parameter[2])
        if ign_check[0] != False:
            curuser.InGameName = parameter[2]
            curuser.UUID = ign_check[1][0]['id']
            response = f'Set User: {curuser.DiscordName} Minecraft_IGN to {parameter[2]}'
        else:
            response = f'{parameter[2]} is not a registered **Minecraft IGN**.'
    else:
        response = 'The In-game Name cannot be blank.'
    return response

#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'username' 'ban' 'time' 'reason'
async def userban(ctx,curuser,parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    logging.info('User Ban...')
    discorduser = ctx.guild.get_member(int(curuser.DiscordID))
    if discorduser == None:
        return f'The User: {parameter[0]} is not apart of this guild.'
    bantime = timehandler.parse(dbconfig.GetSetting('bantimeout'))
    response = f'{curuser.DiscordName} has been banned until {bantime.strftime("%Y/%m/%d Time: %X (UTC)")}'
    if parameter[2].isnumeric():
        bantime = timehandler.parse(parameter[2:])
    if bantime == False:
        return f'**Format**: //user {curuser} ban time(Days:# or Hours:#)(Optional) reason:(optional)'
    curuser.GlobalBanExpiration = bantime
    #Attempts to find a reason and adds it to the reply.
    for entry in parameter:
        entry = entry.replace('Reason:','reason:')
        reason_id = entry.find('reason:')
        if reason_id != -1:
            reason_id = parameter.index('reason:')
            reason = []
            reason = ' '.join(parameter[reason_id+1:])
            await ctx.guild.ban(discorduser, reason = reason, delete_message_days = 7)
            return response + f' Reason: {reason}'
    #Ban on each server..
    if curuser.IngameName != None:
        for server in AMPservers:
            if AMPservers[server].Running == False:
                continue 
            AMPservers[server].ConsoleMessage('/ban {curuser.IngameName}')
    else:
        await ctx.guild.ban(discorduser, delete_message_days = 7)
        return response + f'\nUnable to find User: {curuser.DiscordName} In-game Name, please manually ban this player on all servers.'
    return response
    
#user functions dictionary
userfuncs = {
            'info': userinfo,
            'add' : useradd,
            'infraction' : userinfractions,
            'donator' : userdonator,
            'ign' : userign,
            'ban' : userban, 
            'mod' : usermoderator, 
            #'roles' : userroles
            }

#Handles all ways of discord user identification
def userparse(ctx,parameter = None):
    #Discord ID catch
    if parameter[0].isnumeric():
        return parameter[0]
    #Profile Name Catch
    elif parameter[0].find('#') != -1:
        cur_member = ctx.guild.get_member_named(parameter[0])
        return cur_member
    #Using @ at user and stripping
    elif parameter[0].startswith('<@!') and parameter[0].endswith('>'):
        user_discordid = parameter[0][2:-1]
        cur_member = ctx.guild.get_member(int(user_discordid))
        return cur_member
    else:
        #DiscordName/IGN Catch(DB Get user can look this up)
        cur_member = ctx.guild.get_member_named(parameter[0])
        if cur_member != None:
            return cur_member
        else:
            return None

#Checks all users in a guild for a certain role and sets Donator to True
def donatorcheck():
    member_list = client.get_all_members()
    for member in member_list:
        for role in member.roles:
            if config.donatorID == None:
                return
            if str(role.id) == config.donatorID:
                user = db.GetUser(str(member.id))
                if user == None:
                    db.AddUser(DiscordID = str(member.id), DiscordName = member.name,Donator= True)
                if not user.Donator:
                    user.Donator == True
    return

@client.command()
#/user 'parameter[0]' 'parameter[1]' 'parameter[2]' 'parameter[3]'
#user specific settings
async def user(ctx,*parameter):
    if 'example' in parameter:
        await ctx.send('**Examples**:' +
        '\n //user Notch infraction add Vanilla_server note: Griefing Spawn with creepers.' + 
        '\n //user k8_thekat ban d:3h:12 reason: Attempting to catch staff members in Pok-e balls.' + 
        '\n //user Notch254 IGN The_Notch')
    if 'help' in parameter:
        option_help = '**Options**: None'
        parameter_help = '**Parameters**: user_name '

        if 'infraction' in parameter:
            option_help = '**Options**: Add or Del'
            parameter_help = '**Parameters**: user_name / infractionID("Del" only) / time("Add" only: Optional) / reason:("Add" only: Optional)'

        if ('moderator' in parameter) or ('donator' in parameter):
            parameter_help = '**Parameters**: user_name / True or False'

        if 'ban' in parameter:
            parameter_help = '**Parameters**: user_name / time(Optional) / reason:(Optional)'

        await ctx.send('**Format**: //user discord_id `function` `option` `parameter`',reference = ctx.message.to_reference())
        return await ctx.send('**Functions**: ' + ", ".join(userfuncs.keys()) + '\n' + option_help + '\n' + parameter_help)
        
    if len(parameter) < 2:
        return await ctx.send('**Format**: //user discord_id (function) (option) (parameter)',reference = ctx.message.to_reference())
    curuser = userparse(ctx,parameter)
    if curuser == None:
        return await ctx.send(f'**The User**: {parameter[0]} does not exist in **{ctx.guild.name}**.', reference = ctx.message.to_reference())
    elif parameter[1].lower() in userfuncs:
        cur_db_user = db.GetUser(curuser.id)
        if cur_db_user != None:
            if parameter[1].lower() == 'add':
                return await ctx.send(userfuncs[parameter[1]](ctx,curuser,parameter),reference = ctx.message.to_reference())
            try:
                response = await asyncio.gather(userfuncs[parameter[1]](ctx,cur_db_user,parameter))
            except:
                response = userfuncs[parameter[1]](ctx,cur_db_user,parameter)
        else:
            return await ctx.send(f'**The User**: {parameter[0]} does not exist in the Database.', reference = ctx.message.to_reference())

    else:
        return await ctx.send(f'**Format**: //user {curuser.DiscordName} {parameter[1]} (option) (parameter)',reference = ctx.message.to_reference())
    return await ctx.send(response,reference= ctx.message.to_reference()) 

#Adds the User to the Server Lists and updates their whitelist flags        
def serverUserWhitelistFlag(curserver,whitelist,localdb):
    logging.info('Server User whitelist update...')
    non_dbusers = []
    for entry in whitelist:
        curuser = localdb.GetUser(entry['name'])
        if curuser != None:
            curserveruser = curserver.GetUser(curuser)
            #If the user isnt apart of the server_user_list add them and set whitelist
            if curserveruser == None:
                curserver.AddUser(curuser)
                curserveruser = curserver.GetUser(curuser)  
                curserveruser.Whitelisted = True
            else:
                curserveruser.Whitelisted = True
        else:
            #Helps prevent bot error spam if users are whitelisted without a discord account
            if entry['name'] not in non_dbusers:
                non_dbusers.append(entry['name'])
                botoutput(f'Failed to handle: **Server**: {AMPservers[curserver.InstanceID].FriendlyName} **IGN**: {entry["name"]} in whitelist file, adding user to non DB user list...',level= 'warning')
    return

#Updates users whitelisted flags for each server
def serverUserInfoUpdate(curserver,whitelist):
    logging.info('Server User whitelist name update...')
    serveruserlist = curserver.GetAllUsers()
    for serveruser in serveruserlist:
        curuser = serveruser.GetUser()
        if curuser.UUID == None and curuser.IngameName != None:
            ign_check = UUIDhandler.uuidcheck(curuser.IngameName)
            curuser.UUID = ign_check[1][0]['id']
        found = False
        ign_check = UUIDhandler.uuidcheck(curuser.IngameName)
        for whitelist_user in whitelist:
            if curuser.UUID == whitelist_user['uuid'].replace('-',''): #If I find a matching UUID lets continue...
                found = True
                if curuser.IngameName != whitelist_user['name']: #Names do not match; so lets update the name
                    mc_user_curname = UUIDhandler.uuidCurName(curuser.UUID)
                    curuser.IngameName = mc_user_curname['name']
                    botoutput(f'**Updated User**: {curuser.DiscordName} **IGN**: {mc_user_curname} in the database.')
                break
        if not found:
            serveruser.Whitelisted = False
            botoutput(f'**Set User**: {curuser.DiscordName} **Server**: {curserver.FriendlyName} whitelist flag to `False`.')
    return
    
#Checks if a users ban is expired and pardons the user.
async def databasebancheck(localdb):
    logging.info('Database User Banned Check...')
    user_dblist = localdb.GetAllUsers(GlobalBanExpiration=datetime.now())
    for user in user_dblist:
        banneduser = await client.fetch_user(user)
        curuser = localdb.GetUser(banneduser.id)
        curuser.GlobalBanExpiration = None
        await client.guild.unban(banneduser)
        botoutput(f'{banneduser.name} has been unbanned from Discord...',level= 'warning')
    for server in AMPservers:
        if AMPservers[server].Running == False:
            continue 
        curserver = localdb.GetServer(AMPservers[server].InstanceID)
        server_userlist = curserver.GetAllUsers(SuspensionExpiration=datetime.now())
        for serveruser in server_userlist:
            serveruser.SuspensionExpiration = None
            AMPservers[server].ConsoleMessage(f'pardon {serveruser.IngameName}')
            botoutput(f'Unbanned: {serveruser.FriendlyName} on {server.FriendlyName}',level= 'warning')
    return

#handles all ways of identifying a discrd_channel
def channelparse(ctx,parameter):
    logging.info('Channel Parse...')
    channel_list = ctx.guild.channels
    if parameter.isnumeric():
        channel = ctx.guild.get_channel(int(parameter))
        return channel
    else:
        for channel in channel_list:
            if channel.name == parameter:
                return channel
        else:
            return None

#Bot communcation channel, outputs any errors with any functions for staff to handle.
def botoutput(message,ctx = None, level = 'info'):
    asyncio.run_coroutine_threadsafe(botawaitsend(message,ctx,level), async_loop)

#Handles the bot messages and tags the user if provided.
async def botawaitsend(message,ctx = None, level = 'info'):
    if level == 'info':
        logging.info(message)
    if level == 'warning':
        logging.warning(message)
    if level == 'error':
        logging.error(message)
    try:
        #If the bot doesn't have an output chanel; it will use general
        if dbconfig.Botcomms == None:
            channel_list = client.get_all_channels()
            for channel in channel_list:
                if channel.name == 'general':
                    boterror = channel
        else:
            boterror = client.get_channel(dbconfig.Botcomms)
    except Exception as e:
        logging.exception(e)
        logging.error(traceback.print_exc())
    if ctx == None:
        await boterror.send(content = message)
    else:
        await boterror.send(content = f'{ctx.author.name} ' + message)
    return

async def wlbotreply(channel, context = None):
    logging.info('Whitelist Bot Reply...')
    #context = {'User': user , 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message}
    channel = client.get_channel(int(channel))
    if config.Randombotreplies: #Default is True
        replynum = random.randint(0,len(config.Botwhitelistreplies)-1)
        return await channel.send(config.Botwhitelistreplies[replynum], reference = context['Context'].to_reference())
    if not config.Randombotreplies:
        try:
            return await channel.send(config.Botwhitelistreplies[AMPservers[context['server'].InstanceID].Index], reference = context['Context'].to_reference())
        except Exception as e:
            botoutput(e,level= 'error')
            return await channel.send(f'{context.author.name} you have been whitelisted on {context["server"].FriendlyName}.', reference = context['Context'].to_reference())
    return


@client.event
async def on_ready():
    botoutput('I am the Key Master...')

@client.event
#this is a nickname change; shouldn't need to update the database. Maybe other functionality?
async def on_user_update(user_before,user_after):
    logging.info(f'Discord User update...{user_before}')
    try:
        botoutput(f'{user_before.name} changed their discord info, updating database name to {user_after.name}')
        curuser = db.GetUser(user_before.id)
        curuser.DiscordName = user_after.name
    except:
        pass

@client.event
#remove user form database and remove whitelist on all servers
async def on_member_remove(member):
    botoutput(f'{member.name} with ID: {member.id} has left the guild.',level= 'warning')
    #Checks if the user is in the Whitelist list, removes them if they are.
    whitelist.whitelistUpdate(member,'leave')
    curuser = db.GetUser(member.id)
    if curuser != None and curuser.IngameName != None:
        for server in AMPservers:
            if AMPservers[server].Running == False:
                continue 
            AMPservers[server].ConsoleMessage(f'whitelist remove {curuser.IngameName}')
            curserver = db.GetServer(server.InstanceID)
            cur_server_user = curserver.GetUser(curuser)
            cur_server_user.Whitelisted = False

@client.command()
async def ping(ctx):
    logger.commandLog(ctx,None,None,'bot')
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

botflags = ['autowhitelist','autorole','autoreply','autoconsole','convertign']
botchans = ['whitelistchannel','faqchannel','supportchannel','ruleschannel','infochannel','botcomms']
bottime = ['infractiontimeout','bantimeout','whitelistwaittime']


@client.command()
#/botsettings parameter[0] parameter[1] parameter[2]
#/botsettings autowhitelist true
#/botsettings faqchannel 123456789012
#/botsettings infractiontimeout D:2 H:6
async def botsetting(ctx,*parameter):
    if not rolecheck(ctx, 'Moderator'):
        return 'User does not have permission.'
    logger.commandLog(ctx,None,parameter,'bot')
    curtime = datetime.now()
    functions = []
    for entry in botflags: 
        functions.append(entry.capitalize())
    for entry in botchans:
        functions.append(entry.capitalize())
    for entry in bottime:
        functions.append(entry.capitalize())
    functions = ', '.join(functions)
    if len(parameter) < 1:
        return await ctx.send(f'**Format**: //botsetting (function) (parameter)',reference=ctx.message.to_reference())
    if 'help' in parameter:
        return await ctx.send(f'**Format**: //botsetting `function` `parameter`' + 
                        f'\n**Functions**: {functions}' +
                        '\n**Parameters**: True or False / channel_name or channel_id / time(See Commands.md)',reference=ctx.message.to_reference())
    if 'example' in parameter:
        return await ctx.send(f'**Example**: //botsetting bantimeout y:1 d:3',reference = ctx.message.to_reference())
    if 'info' in parameter:
        curbotflags = []
        curbotchans = []
        curbottimes = []
        for entry in botflags:
            curbotflags.append(f'{entry.capitalize()}: `{bool(dbconfig.GetSetting(entry))}`')
        for entry in botchans:
            botchans_cfg = dbconfig.GetSetting(entry)
            if botchans_cfg != None:
                curbotchans.append(f'{entry.capitalize()}: <#{dbconfig.GetSetting(entry)}>')
            else:
                curbotchans.append(f'{entry.capitalize()}: `{dbconfig.GetSetting(entry)}`')
        for entry in bottime:
            bottime_conversion = None
            if dbconfig.GetSetting(entry) != None:
                bottime_conversion = timehandler.parse(dbconfig.GetSetting(entry))
                time_display = bottime_conversion - curtime
            if type(bottime_conversion) == datetime:
                time_display_conv = timehandler.conversion(time_display)
                curbottimes.append(f'{entry.capitalize()}: `{time_display_conv}`')
            else:
                curbottimes.append(f'{entry.capitalize()}: `{dbconfig.GetSetting(entry)}`')
        response = '\n'.join(curbotflags) + "\n" + '\n'.join(curbotchans) + "\n" + '\n'.join(curbottimes)
        return await ctx.send(response,reference = ctx.message.to_reference())

    #/botsettings faq 1234567890
    elif parameter[0].lower() in botchans:
        channel = channelparse(ctx,parameter[1])
        if len(parameter) == 2:
            if channel != None:
                dbconfig.SetSetting(parameter[0], channel.id)
                response = f'**{parameter[0].capitalize()}** is now set to channel: #{channel.name} ID: {channel.id}'
            else:
                response = f'Channel {parameter[0]} is apart of {ctx.guild.name}, please try again.'
        else:
            response = f'**Format**: //botsetting {parameter[0]} (parameter)'

    #/botsettings autowhitelist True
    elif parameter[0].lower() in botflags:
        if len(parameter) == 2:
            try:
                value = strtobool(parameter[1])
                dbconfig.SetSetting(parameter[0], value)
                response = f'**{parameter[0].capitalize()}** is now set to {bool(value)}.'
            except:
                response = f'**Format:** //botsetting {parameter[0]} (True or False)'
        else:
            response = f'{parameter[0]} is set to {bool(dbconfig.GetSetting(parameter[0]))}'
    #/botsettings infractiontimeout 'days:hours:'
    #/botsettings parameter[0] parameter[1]
    elif parameter[0].lower() in bottime:
        if len(parameter) >= 2:
            dbconfig.SetSetting(parameter[0], str(parameter[1:]))
            time_setting = timehandler.parse(dbconfig.GetSetting(parameter[0]))
            if time_setting == False:
                return await ctx.send(f'**Format**: //botsetting {parameter[0]} (time:value)',reference= ctx.message.to_reference())
            response = f'**{parameter[0].capitalize()}** is now set to {timehandler.conversion((time_setting - curtime),True)}.'
        else:
            response = f'**Format**: //botsetting ({parameter[0]}) (time)'
    else:
        
        response = f'The function: {parameter[0]} is not part of my function list.' 
    return await ctx.send(response,reference= ctx.message.to_reference())

#/role 'parameter[0] 'parameter[1]' 'parameter[2]'
#/role 'discordid' 'set' 'Admin' 'true/false'
def roleset(ctx,currole,parameter):
    if not rolecheck(ctx, 'Admin'):
        return f'User does not have permission.'
    logging.info('Role Set...')
    #currole is the discord_role object
    for role in roles:
        #print(parameter[2],role['Name'])
        if parameter[2].lower() == role['Name'].lower():
            dbconfig.SetSetting(parameter[2], currole.id)
            return f'**Discord Role**: {currole.name} now has the Role: **{role["Name"]}**.'
    return f'The Role: {parameter[2]} is not apart of my roles.'

roles = [{'Name': 'Operator', 'Description': 'Full control over the bot, this is set during startup.'},
        {'Name': 'Admin', 'Description': 'Similar to Operator, Full Control over the bot.'},
        {'Name': 'Maintenance', 'Description': 'Full access to Bot commands/settings, AMP commands/settings and Console.'},
        {'Name': 'Moderator', 'Description': 'Full access to Bot commands/settings.'},
        {'Name': 'Staff', 'Description' : 'Full access to User commands and Ban/Pardon.'},
        {'Name': 'General', 'Description' : 'General User in the server.'}
        ]

#role check
#will check user role and perms
def rolecheck(ctx,parameter):
    logging.info(f'Role Check...{ctx.author.name} for {parameter}')
    global roles
    if ctx == 'bot':
        return True
    user_roles = ctx.author.roles
    user_rolelist = []
    for role in user_roles:
        user_rolelist.append(role.id) #List of users roles as discord_role_ids

    #parameter = Maintenance / index = 2
    for role in roles:
        dbrole = dbconfig.GetSetting(role['Name'])
        if dbrole == None:
            continue
        if dbrole in user_rolelist: #Contains Admins / index = 1
            logging.info(f'Role Check Passed {ctx.author.name}')
            return True
        if parameter == role['Name']:
            break

    botoutput('ERROR: Rolecheck failed', ctx,level= 'warning')
    return False

rolefuncs = { 
            'set' : roleset,
            }

#Checks if the role exists and returns the discord role object.
def roleparse(ctx,parameter): #returns None on failure
    role_list = ctx.guild.roles
    #Role ID catch
    if parameter.isnumeric():
        role = ctx.guild.get_role(int(parameter))
        return role
    else:
        #If a user provides a role name; this will check if it exists and return the ID
        for role in role_list:
            parameter.replace('_',' ')
            if role.name.lower() == parameter.lower():
                return role

@client.command()
#/role 'parameter[0] 'parameter[1]' 'parameter[2]'
#/role 'discordid' 'set' 'Moderator'
async def role(ctx,*parameter):
    logger.commandLog(ctx,None,parameter,'bot')
    if 'help' in parameter[0:2]:
        role_display = []
        for entry in roles:
            role_display.append(f'**{entry["Name"]}**: {entry["Description"]}')
        await ctx.send('**Format**: //role discrd_role set (role)',reference= ctx.message.to_reference())
        await ctx.send("**Functions**: " + ",".join(rolefuncs.keys()))
        return await ctx.send("**Roles**: \n" + '\n'.join(role_display))
    if len(parameter) < 3:
        response = f'**Format**: //role discrd_role set (role)'
        return await ctx.send(response,reference = ctx.message.to_reference()) 
    #gets a discord_role object
    role = parameter[2]
    #This allows a user to set a discord ID role to None
    if parameter[2] != 'None':
        role = roleparse(ctx,parameter[0])
        if role == None:
            response = f'The Role: {parameter[0]} does not exist in **{ctx.guild.name}**.'
            return await ctx.send(response,reference = ctx.message.to_reference()) 
    if parameter[1].lower() in rolefuncs:
        response = rolefuncs[parameter[1]](ctx,role,parameter)
        return await ctx.send(response,reference = ctx.message.to_reference())
    else:
        response = f'The Function: {parameter[1]} does not exist.'
    return await ctx.send(response,reference= ctx.message.to_reference())


def loglist(ctx,parameter):
    list = logger.logfilelist #list of all the log files in botdirectory + \\logs
    return "**List of Log Files:**\n" + '\n'.join(list)

#/logs read filename count start_index
def logread(ctx,parameter):
    #print(parameter, len(parameter))
    filename = parameter[1]
    if len(parameter) == 2:
        logs = '\n'.join(logger.logfileparse(filename))
        return logs
    elif len(parameter) == 3:
        if parameter[2].isnumeric():
            count = int(parameter[2])
            logs = '\n'.join(logger.logfileparse(filename, count))
            return logs
    elif len(parameter) == 4:
        if parameter[2].isnumeric() and parameter[3].isnumeric():
            count = int(parameter[2])
            start_index = int(parameter[3])
            logs = '\n'.join(logger.logfileparse(filename, count, start_index))
            return logs
    else:
        botoutput('We encountered an Error reading a log file {parameter}',ctx,level= 'warning')
        return 'Error'
   

logfuncs = {
            'list' : loglist,
            'read' : logread
}

@client.command()
#/logs parameter[0] parameter[1]
#/logs (functions) functions = list, read
async def logs(ctx,*parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    logger.commandLog(ctx,None,parameter,'bot')
    if len(parameter) < 1:
        return await ctx.send('**Format**: //logs (function) (parameter)', reference = ctx.message.to_reference())
    if 'help' in parameter:
        return await ctx.send('**Functions**: ' + '`' + ','.join(logfuncs.keys()) + '`', reference = ctx.message.to_reference())
    if parameter[0].lower() in logfuncs:
        response = logfuncs[parameter[0]](ctx,parameter)
    else:
        response = f'The Function: {parameter[1]} does not exist.'
    return await ctx.send(response,reference = ctx.message.to_reference())


#Gets a list of all AMP Instances, their Friendly Names and Database Nicknames
@client.command()
async def serverlist(ctx):
    staff = False
    if not rolecheck(ctx, 'General'):
        return 'User does not have permission.'
    if rolecheck(ctx,'Staff'): 
        staff = True
    logging.info('Server List...')
    AMPinstancecheck()
    logger.commandLog(ctx,None,None,'bot')
    status = AMP.getInstanceStatus()
    serverlist = []
    for entry in status['result']:
        if entry['InstanceID'] in AMPservers:
            curserver = db.GetServer(entry['InstanceID'])
            curservernick = ', '.join(curserver.Nicknames)
            if entry['Running']:
                serv_status = '`Online`'
            else:
                serv_status = '`Offline`'
                
            serverinfo = f'**Server**: {curserver.FriendlyName} - {serv_status}' 
            #Staff see ALL servers
            if staff == True:
                if len(curserver.Nicknames) != 0: #If the server has nicknames
                    serverlist.append(f'{serverinfo}\n\t**__Nicknames__**: {curservernick}')
                else:
                    serverlist.append(serverinfo)
            elif serv_status != '`Offline`': #If the server is OFFLINE; do not display it to a general user..
                if len(curserver.Nicknames) != 0:
                    serverlist.append(f'{serverinfo}\n\t**__Nicknames__**: {curservernick}')
                else:
                    serverlist.append(serverinfo)

    serverlist = '\n'.join(serverlist)
    return await ctx.send(serverlist, reference=ctx.message.to_reference())

@client.command()
#/banhammer parameter[0] parameter[1]
#/banhammer 'user' 'reason/note'
async def banhammer(ctx,*parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    logging.info('Ban Hammer...')
    logger.commandLog(ctx,None,parameter,'bot')
    user = db.GetUser(parameter[0])
    curmember = ctx.guild.get_member(int(parameter[0]))
    curtime = datetime.now()
    if user != None: #If the user exists in the DB
        #if the command contains a 'reason/note'
        if len(parameter) >= 2:
            await ctx.guild.ban(curmember, parameter[1:])
            response = f'{user.DiscordName} has been BAN HAMMERED! Reason: {parameter[1:]}'
        else:
            await ctx.guild.ban(curmember)
            response = f'{user.DiscordName} has been BAN HAMMERED!'
        user.GlobalBanExpiration = curtime + timedelta(days=9999)
    else:
        if len(parameter) >= 2:
            await ctx.guild.ban(curmember, parameter[1:])
            response = f'{parameter[0]} has been BAN HAMMERED! Reason: {parameter[1:]}'
        else:
            await ctx.guild.ban(curmember)
            response = f'{parameter[0]} has been BAN HAMMERED!'
    return await ctx.send(response,reference = ctx.message.to_reference())

@client.command()
async def pardon(ctx,*parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    print('Pardon...')
    logger.commandLog(ctx,None,parameter,'bot')
    user = db.GetUser(parameter[0])
    banneduser = await client.fetch_user(parameter[0])
    if user != None:
        for server in AMPservers:
            if AMPservers[server].Running == False:
                continue 
            AMPservers[server].ConsoleMessage('pardon {user.IngameName}')
        try:
            await ctx.guild.unban(banneduser)
            response = f'User: {user.DiscordName} has been allowed back into the fold!!!.'
            user.GlobalBanExpiration = None
        except discord.errors.NotFound:
            response = f'User: {banneduser.name} is not currently banned on this server.'
    else:
        try:
            await ctx.guild.unban(banneduser)
            response = 'User: {banneduser.name} has been allowed back into the fold!!!.'
            user.GlobalBanExpiration = None
        except discord.errors.NotFound:
            response = f'User: {banneduser.name} is not currently banned on this server.'

    return await ctx.send(response,reference = ctx.message.to_reference())
          
@client.event
async def on_message(message):
    if message.author.bot:
        return
    if (message.content.startswith('//')):
        logging.info('Found /command.')
        if message.channel.id in console.SERVERCONSOLE:
            console.on_message(message)
        else:
            return await client.process_commands(message)
    if message.channel.id in chat.SERVERCHAT:
        chat.on_message(message,client)
    if message.channel.id == dbconfig.Whitelistchannel:
        if dbconfig.Autowhitelist:
            reply = whitelist.wlmessagehandler(message)
            if reply[0] == False:
                return await message.reply(reply[1])
            else:
                botoutput(reply[1])
        else:
            db.AddUser(DiscordID = str(message.author.id), DiscordName = message.author.name)
    else:
        chat_filter = chatfilter.spamFilter(message)
        if chat_filter == True:
            logging.info('Kicking the user from the server...')
            await client.kick(message.author, reason = 'Spamming our Discord Server...')
            return 
        if dbconfig.Autoreply:
            if (message.content.lower() == 'help'):
                response = config.helpmsg
                botoutput(f'Auto-reply triggered. Message: {message.content}')
                return await message.channel.send(response, reference=message.to_reference())
            if message.content.lower() == 'version' or message.content.lower() =='ip':
                response = config.infomsg
                botoutput(f'Auto-reply triggered. Message: {message.content}')
                return await message.channel.send(response, reference=message.to_reference())
       

#Initial Setup to set Operator Role...
@client.command()
async def setup(ctx,*parameter):
    if len(parameter) < 1:
        return await ctx.send('**Format**: //setup discord_role_id or discord_role_name',reference = ctx.message.to_reference())
    if dbconfig.Firststartup == True:
        logging.info('Initializing...')
        role = roleparse(ctx,parameter[0]) #Verify the Discord_role_id exists
        if role == None:
            response = f'The role: {parameter[0]} does not exist.'
            return botoutput('**ERROR**: Setting Startup Role',ctx,level= 'error')
        dbconfig.Operator = role.id
        dbconfig.Firststartup = False
        response = f'First time startup completed. Operator role set to {role.name}'
       
    else:
        return await ctx.send('First time startup has been done already...', reference = ctx.message.to_reference())
    await ctx.send('You are now the Key Master!...')
    return await ctx.send(response,reference= ctx.message.to_reference())


#Allows a person to Call an Instance Check on command if needed...
@client.command()
async def AMPcheck(ctx):
    response = AMPinstancecheck()
    return  await ctx.send(response = response, reference = ctx.message.to_reference())

#Generates a blank whitelist file for other functions/events
def blankwhitelistgenerator(server):
    if server.Running == False:
            return 
    serverfile_list = AMPservers[server.InstanceID].getDirectoryListing('')
    for filename in serverfile_list['result']:
            if filename['Filename'] != 'whitelist_blank.json':
                AMPservers[server.InstanceID].writeFileChunk('whitelist_blank.json',0,'')
                time.sleep(.5)
                return     

#whitelist file check
def whitelistfilecheck(localdb):
    logging.info('Whitelist file check in progress...')
    for server in AMPservers:
        whitelistcheck = AMPservers[server].getDirectoryListing('')
        if whitelistcheck == False:
            continue
        curserver = localdb.GetServer(server) 
        if curserver.Whitelist:        
            for entry in whitelistcheck['result']:
                if entry['Filename'] == 'whitelist.json':
                    ts = float(entry['Modified'][6:-2])/1000
                    newts = datetime.fromtimestamp(ts)
                    if datetime.fromisoformat(dbconfig.GetSetting('Whitelistfilecheck')) < newts:
                        botoutput('The Whitelist file has been changed since last check, updating time and checking contents...') 
                        dbconfig.SetSetting('Whitelistfilecheck', str(datetime.now()))
                        whitelist = AMPservers[server].getFileChunk("whitelist.json",0,33554432)
                        whitelist_data = base64.b64decode(whitelist["result"]["Base64Data"])
                        whitelist_json = json.loads(whitelist_data.decode("utf-8"))
                        #Checks user UUIDs and updated the database if their IGN has changed. Updates Whitelisted Flag.
                        serverUserInfoUpdate(curserver,whitelist_json)
                        #Adds the user to the server_user_list and updates their Whitelisted Flag.
                        serverUserWhitelistFlag(curserver,whitelist_json,localdb)

#Checks AMP for any new Instances...
def AMPinstancecheck(startup = False):
    global AMPservers, AMPserverConsoles
    logging.info('Checking for any new Instances..')
    if startup == True:
        for server in AMPservers:
            cur_server = db.GetServer(server)
            if cur_server == None:
                cur_server = db.AddServer(InstanceID = AMPservers[server].InstanceID, FriendlyName = AMPservers[server].FriendlyName)
                if AMPservers[server].Module == 'Minecraft':
                    blankwhitelistgenerator(InstanceID = AMPservers[server].InstanceID)
                    botoutput(f'Found a new Instance, adding it to the Database...{AMPservers[server].FriendlyName}')
        return
    AMPserverscheck = AMP.getInstances()
    time.sleep(1)
    #AMP.sessionCleanup()
    response = f'Found no new Instances..'
    if AMPserverscheck.keys() != AMPservers.keys():
        AMPserverConsoles = AMP.getInstances()
        AMPservers = AMP.getInstances()
        for server in AMPservers:
            cur_server = db.GetServer(server)
            if cur_server == None:
                cur_server = db.AddServer(InstanceID = AMPservers[server].InstanceID, FriendlyName = AMPservers[server].FriendlyName)
                if AMPservers[server].Module == 'Minecraft':
                    blankwhitelistgenerator(InstanceID = AMPservers[server].InstanceID)
                    botoutput(f'Found a new Instance, adding it to the Database...{AMPservers[server].FriendlyName}')
    #Updating the Instance Names
    logging.info('Checking if names have been changed...')
    for server in AMPservers:
        cur_server = db.GetServer(server)
        if AMPservers[server].FriendlyName != cur_server.FriendlyName:
            botoutput(f'{cur_server.FriendlyName} has been updated too {AMPservers[server].FriendlyName}...')
            cur_server.FriendlyName = AMPservers[server].FriendlyName
    logging.info(response)
    return 

#This sets the users discord role to that of the servers
#user = {'User': user , 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message}
async def discordRoleSet(user):
    logging.info(user['server'].DiscordRole)
    server_role = client.guild.get_role(int(user['server'].DiscordRole))
    logging.info(user['context'])
    #cur_user = user['context'].author
    await user['context'].author.add_roles(server_role)
    return

#General thread loop for all recurring checks/events...
def threadloop():
    time.sleep(1)
    logging.info('Recurring Thread Loop Initiated...')
    localdb = database.Database()
    updateinterval = datetime.now()
    while(1):
        if (updateinterval+timedelta(seconds=60)) < datetime.now(): #1 minute checkup interval
            logging.info(f'Updating and Saving...{datetime.now().strftime("%c")}')
            #Database check on bans
            asyncio.run_coroutine_threadsafe(databasebancheck(localdb), async_loop)
            time.sleep(.5)
            AMPinstancecheck() #Check if any new AMP Instances have been created or started...
            time.sleep(.5)

            #whitelist file check to update db for non whitelisted users
            whitelistfilecheck(localdb)

            #status = asyncio.run_coroutine_threadsafe(whitelist.whitelistListCheck(), async_loop)
            status = whitelist.whitelistListCheck(client)
            #whitelistListCheck returns False if it has no entries.
            if status != False:
                asyncio.run_coroutine_threadsafe(wlbotreply(dbconfig.Whitelistchannel,status), async_loop)
                asyncio.run_coroutine_threadsafe(discordRoleSet(status),async_loop)
            if config.donations:
                #Checks all user roles and updates the DB flags
                donatorcheck()
            logger.varupdate(updateinterval)
            updateinterval = datetime.now()
        time.sleep(.5)
        if (updateinterval+ timedelta(seconds=3500)) < datetime.now(): #5 minute checkup interval
            chatfilter.logCleaner() #Cleans up the MSGLOG for potential chat spam.
        
        
    return

#Runs on startup...
def defaultinit():
    global AMPservers,async_loop
    loop = threading.Thread(target=threadloop)
    loop.start()
    chatloop = threading.Thread(target = chat.init, args = (client,))
    chatloop.start()
    consoleloop = threading.Thread(target = console.init, args=(client,rolecheck,botoutput,async_loop))
    consoleloop.start()
    try:
        isconfigured = dbconfig.Isconfigured
        return 
    except:
        pass
    #Populated the Database with AMP server entries.
    for entry in AMPservers:
        db.AddServer(InstanceID= AMPservers[entry].InstanceID, FriendlyName= AMPservers[entry].FriendlyName)

    logging.info('Setting up database...')
    dbconfig.AddSetting('Isconfigured', True)
    dbconfig.AddSetting('Firststartup', True)
    dbconfig.AddSetting('Whitelistfilecheck', str(datetime.now()))
    for entry in botflags:
        dbconfig.AddSetting(entry, False)
    for entry in botchans:
        dbconfig.AddSetting(entry, None)
    for entry in bottime:
        dbconfig.AddSetting(entry, None)
        if entry == 'infractiontimeout':
            #set default infraction expiration to 2 weeks(14 Days)
            dbconfig.SetSetting(entry,'D:14')
        if entry == 'bantimeout':
            #set default tempban to 3 days
            dbconfig.SetSetting(entry,'D:3')
    for entry in roles:
        dbconfig.AddSetting(entry['Name'], None)

defaultinit()
AMPinstancecheck(startup = True)
whitelist.init(AMP,AMPservers,db,dbconfig)
whitelistfilecheck(db)
client.run(tokens.token)
