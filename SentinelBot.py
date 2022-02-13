## Sentinel Bot
## k8thekat - 11/5/2021
## 
import discord
from discord import channel 
from discord.ext import commands 
import json
import requests
import requests.sessions
from distutils.util import strtobool
import time
from pprint import pprint
import threading
import asyncio
from datetime import datetime, timedelta
import base64
import random

# Bot Scripts
import database
import tokens
from AMP_API import AMPAPI
import parse
import config
#import endReset # Coming soon
import whitelist
import commandlogger
import consolefilters
import plugin_commands
import timehandler
import UUIDhandler
import consolescan

async_loop = asyncio.new_event_loop()
asyncio.set_event_loop(async_loop)

intents = discord.Intents.default() # Default
intents.members = True
client = commands.Bot(command_prefix = '//', intents=intents, loop=async_loop)
#client.remove_command('help')

#AMP API setup
AMP = AMPAPI()
AMPservers = AMP.getInstances() # creates objects for each server in AMP (returns serverlist)
AMPserverConsoles = AMP.getInstances() # creates objects for server console/chat updates
AMP.sessionCleanup() #cleans up any existing connections to prevent excessive AMP connections

#database setup
db = database.Database()
dbconfig = db.GetConfig()

  
#sets the whitelist flag to true/false for a specific server
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'whitelist' 'true/false'
def serverwhitelistflag(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    print('Server Whitelist Flag...')
    if 'help' in parameter:
        return f'**Example**: //server {curserver.FriendlyName} whitelist true'
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
    print('Server Donator Flag...')
    if 'help' in parameter:
        return f'**Example**: //server {curserver.FriendlyName} donator false'
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
    print('Server Role...')
    if 'help' in parameter:
        return f'**Example**: //server {curserver.FriendlyName} role 617967701381611520'
    if len(parameter) >= 3:
        role = roleparse(ctx,parameter[2]) #returns a role object or None
        if role != None:
            curserver.DiscordRole = role.id
            response = f'**Server**: {curserver.FriendlyName} now has its role set to {role.name}'
        else:
            response = f'The Discord Role ID: {parameter[2]}, does not exist in {ctx.guild.name}'
    else:
        response = f'**Format**: //server {curserver.FriendlyName} role (Discord Role ID or Discord Role Name).'
    return response

#set a specific servers discord channel
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'discordchannel' 'chat/console' '1234567890'
def serverdiscordchannel(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    print('Server Discord Channel...')
    if 'help' in parameter:
        return f'**Example**: //server {curserver.FriendlyName} discordchannel chat SkyFactory-Chat'
    if len(parameter) == 4:
        channel = channelparse(ctx,parameter[3]) #returns a channel object or None
        if channel == None:
            return f'The Channel ID: {parameter[3]} is not valid.'    
        if parameter[2].lower() == 'chat':
            if parameter[3] == 'None':
                curserver.DiscordChatChannel(None)
            else:
                curserver.DiscordChatChannel = str(channel.id)
                #
                return f'Set Discord Chat Channel for {curserver.FriendlyName} to {channel.name}.'  
        elif parameter[2].lower() == 'console':
            if parameter[3] == 'None':
                curserver.DiscordConsoleChannel(None)
            else:
                curserver.DiscordConsoleChannel = str(channel.id)
                #
                return f'Set Discord Console Channel for {curserver.FriendlyName} to {channel.name}.'
    else:
        return f'**Format**: //server {curserver.FriendlyName} discordchannel (chat or console) discord_channel_name or discord_channel_id'

#add/remove a specific servers nickname
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'nickname' 'add/remove' 'nickname'
def servernickname(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    print('Server Nickname...')
    if 'help' in parameter:
        return f'**Format**: //server {curserver.FriendlyName} nickname option(add or remove or list) newnickname'
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
    print('Server Status...')
    status = AMPservers[curserver.InstanceID].getStatus()
    stats = f'**Server**: {curserver.FriendlyName}\n{status}'
    return stats

#get a list of users for a specific server
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'userlist'
def serveruserlist(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    print(f'Server User list...')
    userlist = curserver.GetAllUsers()
    userlist_names = []
    print(len(userlist))
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
    print('Server User Infraction...')
    modauthor = db.GetUser(ctx.author.id)
    details = ' '.join(parameter[3:])
    curuser = db.GetUser(parameter[2])
    if 'help' in parameter:
        return f'**Format**: //server {curserver.FriendlyName} infraction user_name notes(optional)'
    if curuser != None:
        curserver.AddUserInfraction(user= curuser ,mod= modauthor ,note= details)
        return f'User Infraction for {curuser.DiscordName} added to {curserver.FriendlyName} by {modauthor.DiscordName}\n**Note**: {details}'
    else:
        return f'**Error Adding Infraction**: User: {parameter[2]} needs to be added to the database...'

def serverinfo(ctx,curserver,parameter):
    if not rolecheck(ctx, 'General'):
        return 'User does not have permission.'
    print('Server Info...')
    try:
        discordconsolechan,discordchatchan = client.get_channel(int(curserver.DiscordConsoleChannel)), client.get_channel(int(curserver.DiscordChatChannel))
    except:
        discordconsolechan,discordchatchan = curserver.DiscordConsoleChannel, curserver.DiscordChatChannel
    try:
        role = ctx.guild.get_role(int(curserver.DiscordRole))
    except:
        role = curserver.DiscordRole
    servernicknames = ', '.join(curserver.Nicknames)
    response = f'**Name**: {curserver.FriendlyName}\n\t*Nicknames*: {servernicknames}\n**Whitelist**: {bool(curserver.Whitelist)}\n**Donator**: {bool(curserver.Donator)}\n**Discord Console Channel**: {discordconsolechan}\n**Discord Chat Channel**: {discordchatchan}\n**Discord Role**: {role}'
    return response

#bans a specific user from a specific server
#/server parameter[0] parameter[1] parameter[2] parameter[3]...
#/server 'server' 'userban' 'user' 'time' 'reason'
def serveruserban(ctx,curserver,parameter):
    if curserver.Running == False:
        return f'The Server: {curserver.FriendlyName} is currently offline... '
    print('Server Ban Initiated...')
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    if 'help' in parameter:
        if parameter[1] == 'help':
            return f'**Example**: //server {curserver.FriendlyName} userban Notch w:3d:6 reason:Stealing someones items'
    curuser = None
    if len(parameter) <= 2:
        return f'Format: //server {curserver.FriendlyName} userban {curuser} time(Optional) reason:(optional)'
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
    botoutput(f'**Server**: {curserver.FriendlyName} Restarted by {ctx.author.name}...')
    AMPservers[curserver.InstanceID].RestartInstance()
    return f'**Server**: {curserver.FriendlyName} is restarting...'

def serverstart(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    botoutput(f'**Server**: {curserver.FriendlyName} Started by {ctx.author.name}...')
    AMPservers[curserver.InstanceID].StartInstance()
    return f'**Server**: {curserver.FriendlyName} has been started...'

def serverstop(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    if curserver.Running == False:
        return f'The Server: {curserver.FriendlyName} is currently offline... '
    botoutput(f'**Server**: {curserver.FriendlyName} Stopped by {ctx.author.name}...')
    AMPservers[curserver.InstanceID].StopInstance()
    curserver.Running = False
    return f'**Server**: {curserver.FriendlyName} has been stopped...'

def serverkill(ctx,curserver,parameter):
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    if curserver.Running == False:
        return f'The Server: {curserver.FriendlyName} is currently offline... '
    botoutput(f'**Server**: {curserver.FriendlyName} Killed by {ctx.author.name}...')
    AMPservers[curserver.InstanceID].KillInstance()
    return f'**Server**: {curserver.FriendlyName} has been killed...'

def servermaintenance(ctx,curserver,parameter):
    if curserver.Running == False:
        return f'The Server: {curserver.FriendlyName} is currently offline... '
    if not rolecheck(ctx, 'Maintenance'):
        return 'User does not have permission.'
    botoutput(f'**Server**: {curserver.FriendlyName} Maintenance Mode toggled by {ctx.author.name}...')
    dbuser_list = db.GetAllUsers(ServerModerator=True)
    if len(parameter) <= 2:
        return f'**Format**: //server {curserver.FriendlyName} maintenance (on or off)'
    serverfile_list = AMPservers[curserver.InstanceID].getDirectoryListing('')
    if parameter[2].lower() == 'on':
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
    if parameter[2].lower() == 'off':
        #allows players to request whitelist
        curserver.Whitelist = True
        for filename in serverfile_list['result']:
            if filename['Filename'] == 'whitelist.json':
                AMPservers[curserver.InstanceID].renameFile('whitelist.json', 'whitelist_blank.json')
                time.sleep(.5)
                AMPservers[curserver.InstanceID].renameFile('whitelist_public.json', 'whitelist.json')
        return f'**Server**: {curserver.FriendlyName} has been taken out of Maintenance Mode'
    return

def serverchathandler(message):
    for server in AMPservers:
        if AMPservers[server].Running == False:
            continue 
        curserver = db.GetServer(InstanceID = server)
        if curserver.DiscordChatChannel == None:
            continue
        if int(curserver.DiscordChatChannel) == message.channel.id:
            message.content = message.content.replace('\n',' ')
            AMPservers[server].ConsoleMessage(f'tellraw @a [{{"text":"(Discord),"color":"blue"}},{{"text":"<{message.author.name}>: {message.content}"}}]')
            return True
        continue
            
def serverconsolehandler(message):
    for server in AMPservers:
        if AMPservers[server].Running == False:
            continue
        curserver = db.GetServer(InstanceID = server)
        if curserver.DiscordConsoleChannel == None:
            continue
        if int(curserver.DiscordConsoleChannel) == message.channel.id:
            if rolecheck(message, 'Maintenance'):
                AMPservers[server].ConsoleMessage(message.content)
                return True
            '''
            if message.content[0] == '/':
                    AMPservers[server].ConsoleMessage(f'{message.content[1:]}')
                    return True
            '''
            continue
    
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
            'maintenance' : servermaintenance
}

@client.command()
#This is the main handler for all Server related Functions
#'//server 'parameter[0]' 'parameter[1]' 'parameter[2]' 'parameter[3]'
#'//server (server) (funcs: whitelist,donator,role,channel,nickname,status) (options: add,remove,set) (parameter)
async def server(ctx,*parameter):
    if len(parameter) < 2:
        return await ctx.send(f'**Format**: //server server_name (function) (option) (parameter)',reference = ctx.message.to_reference())
    curserver = db.GetServer(Name= parameter[0])
    if curserver == None:
        response = f'**Server**: {parameter[0]} does not exists.'
    #checks if curserver is a server in the database.
    if 'help' in parameter[0:1]:
        return await ctx.send(', '.join(serverfuncs.keys()),reference = ctx.message.to_reference())
    if curserver != None:
            if parameter[1].lower() in serverfuncs:
                response = serverfuncs[parameter[1]](ctx,curserver,parameter) 
            else:
                response = f'The Command: {parameter[1]} is not apart of my list. Commands: {", ".join(serverfuncs.keys())}.' 
    return await ctx.send(response,reference= ctx.message.to_reference())

#Sends the console to the predefined channel
async def serverconsolemessage(chan, entry):
    try:
        await chan.send(entry)
    except Exception as e:
        botoutput(e)

#Sends the chat messages to the predefined channel
async def serverchatmessage(chan, entry):
    try:
        await chan.send(entry)
    except Exception as e:
        botoutput(e)

#Handles the AMP Console Channels
def serverconsole(curdb):
    for server in AMPserverConsoles:
        curserver = curdb.GetServer(server)
        console = AMPserverConsoles[server].ConsoleUpdate()
        #All AMP functions return False if they are offline...
        if console == False:
            continue
        consolemsg = []
        #Walks through every entry of a Console Update
        for entry in console['ConsoleEntries']:
            #send off the server chat messages to a discord channel if enabled
            serverchat(curserver,entry)
            #Checks for User last login and updates the database.
            userlastlogin(curserver,entry)
            #Handles each entry of the console to update DB or filter messages.
            entry = consolescan.scan(curserver,colorstrip(entry))
            print(entry)
            #Supports different types of console suppression, see config.py and consolefilter.py
            entry = consolefilters.filters(entry)
            print(entry)
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
        if curserver.DiscordConsoleChannel != None:
            outputchan = client.get_channel(int(curserver.DiscordConsoleChannel))
            if len(consolemsg) > 0:
                bulkentry = ''
                for entry in consolemsg:
                    if len(bulkentry + entry) < 1500:
                        bulkentry = bulkentry + entry + '\n' 
                    else:
                        ret = asyncio.run_coroutine_threadsafe(serverconsolemessage(outputchan, bulkentry[:-1]), async_loop)
                        ret.result()
                        bulkentry = entry + '\n'
                if len(bulkentry):
                    ret = asyncio.run_coroutine_threadsafe(serverconsolemessage(outputchan, bulkentry[:-1]), async_loop)
                    ret.result()

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

#Console messages are checked by 'Source' and by 'Type' to be sent to a designated discord channel.
def serverchat(curserver,entry):
    consolemsg = []
    if entry['Source'].startswith('Async Chat Thread'):
        consolemsg.append(entry['Contents'])
    elif entry['Contents'].find('issued server command: /tellraw') != -1:
        #consolemsg.append(entry['Contents'][21:])
        print(entry['Contents'][21:])
    elif entry['Type'] == 'Chat':
        #Changes their IGN to their discord_name when it is send to the discord channel
        if dbconfig.GetSetting('ConvertIGN'):
            user = userIGNdiscord(entry['Source'])
        else:
            user = entry['Source']
        consolemsg.append(f"{user}: {entry['Contents']}")
    else:
        return

    if curserver.DiscordChatChannel != None:
        outputchan = client.get_channel(int(curserver.DiscordChatChannel))
        if len(consolemsg) > 0:
            bulkentry = ''
            for entry in consolemsg:
                if len(bulkentry+entry) < 1500:
                    bulkentry = bulkentry + entry + '\n' 
                else:
                    ret = asyncio.run_coroutine_threadsafe(serverchatmessage(outputchan, bulkentry[:-1]), async_loop)
                    ret.result()
                    bulkentry = entry + '\n'
            if len(bulkentry):
                ret = asyncio.run_coroutine_threadsafe(serverchatmessage(outputchan, bulkentry[:-1]), async_loop)
                ret.result()

#Starts up seperate threads to handle each console for interaction and usage.
def serverconsoleinit():
    if (dbconfig.Autoconsole):
        for entry in AMPserverConsoles:
            status = AMPserverConsoles[entry].ConsoleUpdate()
            if status == False:
                continue
        print(f'Starting console threads...')
        reply = threading.Thread(target=serverconsolethreadloop)
        reply.start()

#Simple loop; helps keep the databases seperate for each check.
def serverconsolethreadloop():
    localdb = database.Database()
    while(1):
        time.sleep(1)
        serverconsole(localdb)

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
    print('User Info...')
    userinfractionslist = curuser.Infractions
    userservers = curuser.GetAllServers() 
    if curuser.GlobalBanExpiration != None:
        globalbanformat = curuser.GlobalBanExpiration['Date'].strftime('%Y/%m/%d Time: %X (UTC)')
    else:
        globalbanformat = curuser.GlobalBanExpiration
    response = f'**DiscordID**: {curuser.DiscordID}\n**DiscordName**: {curuser.DiscordName}\n**InGameName**: {curuser.IngameName}\n**Donator**: {bool(curuser.Donator)}\n**Banned**: {globalbanformat}'
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
            data = f'\n**Server**: {entry.GetServer().FriendlyName}\n\tWhitelisted: {bool(entry.Whitelisted)}\n\tSuspended: {Suspensionformat}\n\t**Last Login**: {lastloginformat}'
            response += data
    if len(userinfractionslist) != 0:
        for entry in userinfractionslist:
            dateformat = entry['Date'].strftime('%Y/%m/%d Time: %X (UTC)')
            if entry['Server'] == None:
                data = (f"\n**Infraction ID**: {entry['ID']}\n\tDate: {dateformat}\n\tWho Reported: {entry['DiscordName']}\n\tNotes: {entry['Note']}")
                response += data
            else:
                data = (f"\n**Infraction ID**: {entry['ID']}\n\tDate: {dateformat}\n\tWho Reported: {entry['DiscordName']}\n\tServer: {entry['Server']}\n\tNotes: {entry['Note']}")
                response += data
    return response

#add user to database (!!REQUIRES DISCORD ID!!)
#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'discordid' 'add'
def useradd(ctx,curuser,parameter = None):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    print('User add...')
    db.AddUser(DiscordID = str(curuser.id), DiscordName = curuser.name)
    response = f'Successfuly added {curuser.name} to database. (DiscordID: {curuser.id}).'
    return response

#gets the users infractions
#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'name'  4 'add/del' 'server' 'notes'
#/user 'name'  4 'del' 'ID'
def userinfractions(ctx,curuser,parameter):
    print('User Infractions Triggered...')
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    mod = db.GetUser(ctx.author.id)
    if 'help' in parameter[2:3].lower():
        return f"**Format**: //user {curuser.DiscordName} infraction (parameter) (ID:optional or server:optional) (notes:optional)"
    if len(parameter) >= 4:
        if parameter[2].lower() == 'add':
            server = db.GetServer(name = parameter[3])
            if server != None:
                notes = ' '.join(parameter[4:])
                curuser.AddInfraction(server = server, mod = mod, note = notes)
                response = f'Added Infraction on {curuser.DiscordName} for {server.FriendlyName} with the comment of "{notes}"'
            else:
                notes = ' '.join(parameter[3:])
                curuser.AddInfraction(server = None, mod = mod, note = notes)
                response = f'Added Infracton on {curuser.DiscordName} with comment of "{notes}"'
        elif parameter[2].lower() == 'del':
                curuser.DelInfraction(ID=parameter[3])
                response = f'Removed Infraction {parameter[3]} on {curuser.DiscordName}' 
    else:
        if len(parameter) >= 4:
            if parameter[2].lower() == 'del':
                response =f"**Format**: //user {curuser.DiscordName} infraction del InfractionID"
            if parameter[2].lower() == 'add':
                response =f"**Format**: //user {curuser.DiscordName} infraction add (server:optional) (notes:optional)"
        else:
            response = f"**Format**: //user {curuser.DiscordName} infraction (option:add or del) (ID:optional) (notes)"
    return response

# updates user parameters in database (donator)
#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'username' 'donator' 'true/false'
def userdonator(ctx,curuser,parameter):
    if not rolecheck(ctx, 'Moderator'):
        return 'User does not have permission.'
    print('User Donator...')
    if 'help' in parameter.lower():
        response = f'**Format**: //user {curuser} donator (True or False)'
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
    print('User Moderator...')
    if 'help' in parameter:
        response = f'**Format**: //user {curuser} mod (True or False)'
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
    print('User IGN...')
    if 'help' in parameter:
        response = f'**Format**: //user {curuser} IGN (True or False)'
    if len(parameter) == 3:
        ign_check = UUIDhandler.uuidcheck(parameter[2])
        if ign_check != False:
            curuser.InGameName = parameter[2]
            response = f'Set User: {curuser.DiscordName} Minecraft_IGN to {parameter[2]}'
        else:
            response = f'{parameter[2]} is not a registered **Minecraft IGN**.'
    else:
        response = 'The In-game Name cannot be blank.'
    return response

#User Authenticator #22/INFO
#parameter[0] 
#Updates the DB of the last login of users
def userlastlogin(curserver,entry):
    localdb = database.Database()
    if entry['Source'].startswith('User Authenticator'):
        print('User Last Login Triggered...')
        curtime = datetime.now()
        psplit = entry['Contents'].split(' ')
        user = localdb.GetUser(psplit[3])
        if user != None:
            serveruser = curserver.GetUser(user)
            if serveruser == None:
                botoutput(f'Adding user to Server: {curserver.FriendlyName} User: {user.DiscordName} IGN: {user.IngameName}')
                curserver.AddUser(user)
            try:
                serveruser = curserver.GetUser(user)
                serveruser.LastLogin = curtime
            except Exception as e:
                botoutput(e)
                botoutput('Issue finding serveruser in db...')
        else:
            botoutput(f'Failed to set Last Login for Server: {curserver.FriendlyName} User: {psplit[3]}. Please add the user to the database and set the users IGN via //user DiscordID ign {psplit[3]}')

#/user parameter[0] parameter[1] parameter[2] parameter[3]
#/user 'username' 'ban' 'time' 'reason'
async def userban(ctx,curuser,parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    print('User Ban...')
    discorduser = ctx.guild.get_member(int(curuser.DiscordID))
    if discorduser == None:
        return f'The User: {parameter[0]} is not apart of this guild.'
    bantime = timehandler.parse(dbconfig.GetSetting('bantimeout'))
    response = f'{curuser.DiscordName} has been banned until {bantime.strftime("%Y/%m/%d Time: %X (UTC)")}'
    if 'help' in parameter.lower():
        if parameter[1] == 'help':
            response = f'**Format**: //user {curuser.DiscordName} ban time(Days:# or Hours:#)(Optional) reason:(optional)'
        if parameter[2] == 'help':
            response = f'**Format**: //user {curuser.DiscordName} {parameter[1]} time(Days:# or Hours:#)(Optional) reason:(optional)'
        if parameter[3] == 'help':
            response = f'**Format**: //user {curuser.DiscordName} {parameter[1]} {parameter[2]} reason:(optional)'
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
             4 : userinfractions,
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
            if parameter[1] == 'add':
                return parameter[0]
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
                    continue
                if not user.Donator:
                    user.Donator == True
                    continue
            else:
                continue
    return

@client.command()
#/user 'parameter[0]' 'parameter[1]' 'parameter[2]' 'parameter[3]'
#user specific settings
async def user(ctx,*parameter):
    if len(parameter) < 2:
        return await ctx.send('**Format**: //user discord_id (function) (option) (parameter)',reference = ctx.message.to_reference())
    curuser = userparse(ctx,parameter)
    if 'help' in parameter[0:1]:
        return await ctx.send('**Functions**: ' + '`' ", ".join(userfuncs.keys()) + '`')
    elif parameter[1].lower() in userfuncs:
        if parameter[1].lower() == 'add':
            return await ctx.send(useradd(ctx,curuser,parameter))
        if curuser != None :
            cur_db_user = db.GetUser(curuser.id)
            try:
                response = await asyncio.gather(userfuncs[parameter[1]](ctx,cur_db_user,parameter))
            except:
                response = userfuncs[parameter[1]](ctx,cur_db_user,parameter)
        else:
            response = f'The User: {parameter[0]} does not exists in {ctx.guild.name}.'
    return await ctx.send(response,reference= ctx.message.to_reference()) 

#Adds the User to the Server Lists and updates their whitelist flags        
def serveruserWhitelistFlag(curserver,whitelist,localdb):
    print('Server User whitelist update...')
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
                continue
        else:
            #Helps prevent bot error spam if users are whitelisted without a discord account
            if entry['name'] not in non_dbusers:
                non_dbusers.append(entry['name'])
                botoutput(f'Failed to handle: Server: {AMPservers[curserver.InstanceID].FriendlyName} IGN: {entry["name"]} in whitelist file, adding user to non DB user list...')
            continue
    return

#Updates users whitelisted flags for each server
def serveruserWhitelistUpdate(curserver,whitelist):
    print('Server User whitelist name update...')
    serveruserlist = curserver.GetAllUsers()
    for serveruser in serveruserlist:
        curuser = serveruser.GetUser()
        for whitelist_user in whitelist:
            #Checks a users UUID agianst the whitelist file; if found verifies the users IGN.
            if curuser.UUID == whitelist_user['uuid']:
                #Names do not match; so lets update the name
                if curuser.IngameName != whitelist_user['name']:
                    mc_user_curname = UUIDhandler.uuidCurName(curuser.UUID)
                    curuser.IngameName = mc_user_curname['name']
                    botoutput(f'Updated User: {curuser.DiscordName} IGN: {mc_user_curname} in the database.')
                    continue
            if curuser.UUID != whitelist_user['uuid']:
                serveruser.Whitelisted = False
                botoutput(f'Set User: {curuser.DiscordName} Server: {curserver.FriendlyName} whitelist flag to False.')
                continue
    return
    
#Checks if a users ban is expired and pardons the user.
async def databasebancheck(localdb):
    print('Database User Banned Check...')
    user_dblist = localdb.GetAllUsers(GlobalBanExpiration=datetime.now())
    for user in user_dblist:
        banneduser = await client.fetch_user(user)
        curuser = localdb.GetUser(banneduser.id)
        curuser.GlobalBanExpiration = None
        await client.guild.unban(banneduser)
        botoutput(f'{banneduser.name} has been unbanned from Discord...')
    for server in AMPservers:
        if AMPservers[server].Running == False:
            continue 
        curserver = localdb.GetServer(AMPservers[server].InstanceID)
        server_userlist = curserver.GetAllUsers(SuspensionExpiration=datetime.now())
        for serveruser in server_userlist:
            serveruser.SuspensionExpiration = None
            AMPservers[server].ConsoleMessage(f'pardon {serveruser.IngameName}')
            botoutput(f'Unbanned: {serveruser.FriendlyName} on {server.FriendlyName}')
    return

#handles all ways of identifying a discrd_channel
def channelparse(ctx,parameter):
    print('Channel Parse...')
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
def botoutput(message,ctx = None):
    asyncio.run_coroutine_threadsafe(botawaitsend(message,ctx), async_loop)

#Handles the bot messages and tags the user if provided.
async def botawaitsend(message,ctx = None):
    print(message)
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
        print(e)
    if ctx == None:
        await boterror.send(content = message)
    else:
        await boterror.send(content = f'{ctx.author.name} ' + message)
    return

async def wlbotreply(channel, context = None):
    #context = {'User': user , 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message}
    channel = client.get_channel(int(channel))
    if config.Randombotreplies: #Default is True
        print('Random Reply...')
        replynum = random.randint(0,len(config.Botwhitelistreplies)-1)
        return await channel.send(config.Botwhitelistreplies[replynum], reference = context['Context'].to_reference())
    if not config.Randombotreplies:
        try:
            return await channel.send(config.Botwhitelistreplies[AMPservers[context['server'].InstanceID].Index], reference = context['Context'].to_reference())
        except Exception as e:
            botoutput(e)
            return await channel.send(f'{context.author.name} you have been whitelisted on {context["server"].FriendlyName}.', reference = context['Context'].to_reference())
    return


@client.event
async def on_ready():
    botoutput('I am the Key Master...')

@client.event
#this is a nickname change; shouldn't need to update the database. Maybe other functionality?
async def on_user_update(user_before,user_after):
    print(f'Discord User update...{user_before}')
    try:
        botoutput(f'{user_before.name} changed their discord info, updating database name to {user_after.name}')
        curuser = db.GetUser(user_before.id)
        curuser.DiscordName = user_after.name
    except:
        pass

@client.event
#remove user form database and remove whitelist on all servers
async def on_member_remove(member):
    botoutput(f'{member.name} with ID: {member.id} has left the guild.')
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
    commandlogger.logHandler(ctx,None,None,'bot')
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

botflags = ['autowhitelist','autogreet','autorole','autoreply','autoconsole','autodonator','convertign']
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
    commandlogger.logHandler(ctx,None,parameter,'bot')
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
        await ctx.send(f'**Example**: //botsetting bantimeout y:1 d:3')
        return await ctx.send(f'**Functions** : {functions}')
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
                response = f'**{parameter[0].capitalize()}** is now set to channel: {channel.name} ID: {channel.id}'
            else:
                response = f'Channel {parameter[0]} is not in this Discord, please try again.'
        else:
            response = f'**Format**: //botsetting {parameter[0]} (parameter)'
    #/botsettings autowhitelist True
    elif parameter[0].lower() in botflags:
        if len(parameter) == 2:
            try:
                value = strtobool(parameter[1])
                dbconfig.SetSetting(parameter[0], value)
                response = f'**{parameter[0].capitalize()}** is now set to {bool(value)}.'
                if parameter[0].lower() == 'autoconsole':
                    if value == True:
                        botoutput('Currently initiating Consoles...')
                        #Starts up the console functions
                        serverconsoleinit() 
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
    print('Role Set...')
    #currole is the discord_role object
    for role in roles:
        print(parameter[2],role['Name'])
        if parameter[2].lower() == role['Name'].lower():
            dbconfig.SetSetting(parameter[2], currole.id)
            return f'**Discord Role**: {currole.name} now has the Role: **{role["Name"]}**.'
    return f'The Role: {parameter[2]} is not apart of my roles.'

roles = [{'Name': 'Operator', 'Description': 'Full control over the bot, this is set during startup.'},
        {'Name': 'Admin', 'Description': 'Similar to Operator, Full Control over the bot.'},
        {'Name': 'Maintenance', 'Description': 'Full access to Bot commands/settings, AMP commands/settings and Console.'},
        {'Name': 'Moderator', 'Description': 'Full access to Bot commands/settings.'},
        {'Name': 'Staff', 'Description' : 'Full access to User commands and Ban/Pardon.'}
        ]

#role check
#will check user role and perms
def rolecheck(ctx,parameter):
    print('Role Check...')
    global roles
    if ctx == 'bot':
        return True
    user_roles = ctx.author.roles
    user_rolelist = []
    for role in user_roles:
        #print(role.id)
        user_rolelist.append(role.id) #List of users roles as discord_role_ids

    #parameter = Maintenance / index = 2
    for role in roles:
        dbrole = dbconfig.GetSetting(role['Name'])
        if dbrole == None:
            continue
        if dbrole in user_rolelist: #Contains Admins / index = 1
            #print('Role Check Passed.')
            print('Role Check Passed',ctx)
            return True
        if parameter == role['Name']:
            break

    botoutput('ERROR: Rolecheck failed', ctx)
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
            else:
                continue

@client.command()
#/role 'parameter[0] 'parameter[1]' 'parameter[2]'
#/role 'discordid' 'set' 'Moderator'
async def role(ctx,*parameter):
    commandlogger.logHandler(ctx,None,parameter,'bot')
    if 'help' in parameter[0:2]:
        role_display = []
        func_display = []
        for entry in roles:
            role_display.append(f'**{entry["Name"]}**: {entry["Description"]}')
        await ctx.send("**Roles**: \n" + '\n'.join(role_display))
        return await ctx.send("**Functions**: "+ '`' +",".join(rolefuncs.keys())+ '`',reference= ctx.message.to_reference())
    if len(parameter) < 3:
        response = f'**Format**: //role discrd_role set (role)'
        return await ctx.send(response,reference = ctx.message.to_reference()) 
    #gets a discord_role object
    role = parameter[2]
    #This allows a user to set a discord ID role to None
    if parameter[2] != 'None':
        role = roleparse(ctx,parameter[0])
        if role == None:
            response = f'The Role: {parameter[0]} does not exists in this server.'
            return await ctx.send(response,reference = ctx.message.to_reference()) 
    if parameter[1].lower() in rolefuncs:
        response = rolefuncs[parameter[1]](ctx,role,parameter)
        return await ctx.send(response,reference = ctx.message.to_reference())
    else:
        response = f'The Function: {parameter[1]} does not exists.'
    return await ctx.send(response,reference= ctx.message.to_reference())
    
#Gets a list of all AMP Instances, their Friendly Names and Database Nicknames
@client.command()
async def serverlist(ctx):
    if not rolecheck(ctx, 'General'):
        return 'User does not have permission.'
    print('Server List...')
    AMPinstancecheck()
    commandlogger.logHandler(ctx,None,None,'bot')
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
            if len(curserver.Nicknames) == 0:
                serverlist.append(serverinfo)
            else:
                serverlist.append(f'{serverinfo}\n\t**Nicknames**: {curservernick}')
    serverlist = '\n'.join(serverlist)
    return await ctx.send(serverlist, reference=ctx.message.to_reference())

@client.command()
#/banhammer parameter[0] parameter[1]
#/banhammer 'user' 'reason/note'
async def banhammer(ctx,*parameter):
    if not rolecheck(ctx, 'Staff'):
        return 'User does not have permission.'
    print('Ban Hammer...')
    commandlogger.logHandler(ctx,None,parameter,'bot')
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
    commandlogger.logHandler(ctx,None,parameter,'bot')
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
        print('Found /command.')
        return await client.process_commands(message)
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
        chatflag = serverchathandler(message)
        consoleflag = serverconsolehandler(message)  
        if chatflag != True or consoleflag != True:
            if dbconfig.Autoreply:
                if (message.content.lower() == 'help'):
                    response = config.helpmsg
                    botoutput(f'Auto-reply triggered. Message: {message.content}')
                    return await message.channel.send(response, reference=message.to_reference())
                if message.content.lower() == 'version' or message.content.lower() =='ip':
                    response = config.infomsg
                    botoutput(f'Auto-reply triggered. Message: {message.content}')
                    return await message.channel.send(response, reference=message.to_reference())
            else:
                pass

#Initial Setup to set Operator Role...
@client.command()
async def setup(ctx,*parameter):
    if len(parameter) < 1:
        return await ctx.send('**Format**: //setup discord_role_id',reference = ctx.message.to_reference())
    if dbconfig.Firststartup == True:
        print('Initializing...')
        role = roleparse(ctx,parameter[0]) #Verify the Discord_role_id exists
        if role == None:
            response = f'The role: {parameter[0]} does not exists.'
            return botoutput('**ERROR**: Setting Startup Role',ctx)
        #!!Set the Role for the Discord_role_id to 'Operator'
        dbconfig.Operator = role.id
        dbconfig.Firststartup = False
        response = f'First time startup completed. Operator role set to {role.name}'
       
    else:
        return await ctx.send('First time startup has been done already...', reference = ctx.message.to_reference())
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
    print('Whitelist file check in progress...')
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
                        serveruserWhitelistUpdate(curserver,whitelist_json)
                        #Adds the user to the server_user_list and updates their Whitelisted Flag.
                        serveruserWhitelistFlag(curserver,whitelist_json,localdb)
        else:
            continue

#Checks AMP for any new Instances...
def AMPinstancecheck(startup = False):
    global AMPservers, AMPserverConsoles
    print('Checking for any new Instances..')
    if startup == True:
        for server in AMPservers:
            cur_server = db.GetServer(server)
            if cur_server == None:
                cur_server = db.AddServer(InstanceID = AMPservers[server].InstanceID, FriendlyName = AMPservers[server].FriendlyName)
                blankwhitelistgenerator(cur_server)
                botoutput(f'Found a new Instance, adding it to the Database...{AMPservers[server].FriendlyName}')
        return
    AMPserverscheck = AMP.getInstances(checkup=True)
    time.sleep(1)
    AMP.sessionCleanup()
    response = f'Found no new Instances..'
    if AMPserverscheck.keys() != AMPservers.keys():
        AMPserverConsoles = AMP.getInstances()
        AMPservers = AMP.getInstances()
        for server in AMPservers:
            cur_server = db.GetServer(server)
            if cur_server == None:
                cur_server = db.AddServer(InstanceID = AMPservers[server].InstanceID, FriendlyName = AMPservers[server].FriendlyName)
                blankwhitelistgenerator(cur_server)
                botoutput(f'Found a new Instance, adding it to the Database...{AMPservers[server].FriendlyName}')
    #Updating the Instance Names
    print('Checking if names have been changed...')
    for server in AMPservers:
        cur_server = db.GetServer(server)
        if AMPservers[server].FriendlyName != cur_server.FriendlyName:
            botoutput(f'{cur_server.FriendlyName} has been updated too {AMPservers[server].FriendlyName}...')
            cur_server.FriendlyName = AMPservers[server].FriendlyName
    print(response)
    return 

#This sets the users discord role to that of the servers
#user = {'User': user , 'IGN': user.IngameName, 'timestamp' : curtime, 'server' : curserver, 'Context': message}
async def discordRoleSet(user):
    print(user['server'].DiscordRole)
    server_role = client.guild.get_role(int(user['server'].DiscordRole))
    print(user['context'])
    #cur_user = user['context'].author
    await user['context'].author.add_roles(server_role)
    return

#General thread loop for all recurring checks/events...
def threadloop():
    time.sleep(1)
    print('Thread Loop Initiated...\n')
    localdb = database.Database()
    updateinterval = datetime.now()
    while(1):
        if (updateinterval+timedelta(seconds=60)) < datetime.now():
            print(f'Updating and Saving...{datetime.now().strftime("%c")}')
            #Database check on bans
            asyncio.run_coroutine_threadsafe(databasebancheck(localdb), async_loop)
            time.sleep(.5)
            AMPinstancecheck()
            time.sleep(.5)
            #whitelist file check to update db for non whitelisted users
            whitelistfilecheck(localdb)
            #status = asyncio.run_coroutine_threadsafe(whitelist.whitelistListCheck(), async_loop)
            status = whitelist.whitelistListCheck()
            #whitelistListCheck returns False if it has no entries.
            if status != False:
                asyncio.run_coroutine_threadsafe(wlbotreply(dbconfig.Whitelistchannel,status), async_loop)
                asyncio.run_coroutine_threadsafe(discordRoleSet(status),async_loop)
            if config.donations:
                #Checks all user roles and updates the DB flags
                donatorcheck()
            updateinterval = datetime.now()
        time.sleep(.5)
    return

#Runs on startup...
def defaultinit():
    loop = threading.Thread(target=threadloop)
    loop.start()
    try:
        isconfigured = dbconfig.Isconfigured
        return 
    except:
        pass
    #Populated the Database with AMP server entries.
    for entry in AMPservers:
        db.AddServer(InstanceID= AMPservers[entry].InstanceID, FriendlyName= AMPservers[entry].FriendlyName)

    #CommandLogger 
    commandlogger.init()
    print('Setting up database')
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
serverconsoleinit()
whitelistfilecheck(db)
client.run(tokens.token)

