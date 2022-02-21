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
#Gatekeeper Bot - Console Scanning
import commandlogger
import config
import plugin_commands
from datetime import datetime, timedelta
import traceback
import database

#Database
db = database.Database()

#Handles each entry of the console to update DB or filter messages/etc.
def scan(curserver,entry):
    curtime = datetime.now()
    #Finding in game issued server commands
    if entry['Contents'].find('issued server command:') != -1:
        commandlogger.logHandler(None,curserver,entry,'console')
        entry_split = entry['Contents'].split(' ')
        command_user = entry_split[0]
        command = entry_split[4]
        #Catchs manual ban and pardon commands, updates db
        if command == '/ban' or command == '/pardon':
            target_user = entry_split[-1]
            curserveruser = curserver.GetUser(target_user)
            if curserveruser != None:
                if command == '/ban':
                    curserveruser.SuspensionExpiration = curtime + timedelta(days=9999)
                    curserveruser.Whitelisted = False
                else:
                    curserveruser.SuspensionExpiration = None
        #catchs manual whitelist command, updates db   
        if command == '/whitelist':
            target_user = entry_split[-1]
            curserveruser = curserver.GetUser(target_user)
            if len(entry_split) == 5:
                command_func = entry_split[5]
            if curserveruser != None:
                if command_func == 'remove':
                    curserveruser.Whitelisted = False
                else:
                    curserveruser.Whitelisted = True
        #below here will be a script to handle common plugin commands (eg. /tempban) See config.py and plugin_commands.py
        if config.Plugins:
            if config.Essentials:
                time_out,IGN = plugin_commands.Essentials(entry)
                curserveruser = curserver.GetUser(IGN)
                curserveruser.SuspensionExpiration = curtime + time_out
    #Player�c Console �6banned�c k8_thekat �6for: �c�cYou have been banned:
    if entry['Contents'].startswith('Player Console banned') and entry['Contents'].endswith('You have been banned:'):
        print('User has been banned via console...')
        commandlogger.logHandler(None,curserver,entry,'console')
        entry_split = entry['Contents'].split(' ')
        try:
            curserver.GetUser(entry_split[3]).SuspensionExpiration = curtime + timedelta(days=9999)
            curserver.GetUser(entry_split[3]).Whitelisted = False
        except Exception as e:
            print(e)
            traceback.print_exc()
            return True, f'Unable to update User: {entry_split[3]} banned status in the database!'
    #�6Player�c Console �6unbanned�c k8_thekat
    if entry['Contents'].startswith('Player Console unbanned'):
        print('User has been unbanned via console...')
        commandlogger.logHandler(None,curserver,entry,'console')
        entry_split = entry['Contents'].split(' ')
        try:
            curserver.GetUser(entry_split[3]).SuspensionExpiration = None
            #curserver.GetUser(entry_split[3]).Whitelisted = True
            #AMPservers[curserver.InstanceID].ConsoleMessage(f'whitelist add {entry_split[3]}')
        except Exception as e:
            print(e)
            traceback.print_exc()
            return True, f'Unable to update User: {entry_split[3]} banned status in the database!'
    #Added k8_thekat to the whitelist
    if entry['Contents'].startswith('Added') and entry['Contents'].endswith('to the whitelist'):
        print('User added to Whitelist via console..')
        commandlogger.logHandler(None,curserver,entry,'console')
        entry_split = entry['Contents'].split(' ')
        try:
            curserver.GetUser(entry_split[1]).Whitelisted = True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return True, f'Unable to update User: {entry_split[1]} whitelisted status in the database!'
    #Removed k8_thekat from the whitelist
    if entry['Contents'].startswith('Removed') and entry['Contents'].endswith('from the whitelist'):
        print('User removed from Whitelist via console..')
        commandlogger.logHandler(None,curserver,entry,'console')
        entry_split = entry['Contents'].split(' ')
        try:
            curserver.GetUser(entry_split[1]).Whitelisted = False
        except Exception as e:
            print(e)
            traceback.print_exc()
            return True, f'Unable to update User: {entry_split[1]} whitelisted status in the database!'
    #User Lastlogin Stuff
    if entry['Source'].startswith('User Authenticator'):
            #if entry['Source'].startswith('Server thread/INFO') and entry[''].startswith()
        print('User Last Login Triggered...')
        curtime = datetime.now()
        psplit = entry['Contents'].split(' ')
        user = db.GetUser(psplit[3])
        if user != None:
            serveruser = curserver.GetUser(user)
            if serveruser == None:
                curserver.AddUser(user)
            try:
                serveruser = curserver.GetUser(user)
                serveruser.LastLogin = curtime
                return True, f'Adding user to Server: {curserver.FriendlyName} User: {user.DiscordName} IGN: {user.IngameName}'
            except Exception as e:
                print(e)
                traceback.print_exc()
                return True, f'Failed to set Last Login for Server: {curserver.FriendlyName} User: {psplit[3]}. Please add the user to the database and set the users IGN via //user DiscordID ign {psplit[3]}'
    #User Played Time
    if entry['Source'] == 'Server thread/INFO' and entry['Contents'].endswith('has left the game!'):
        time_online = datetime.fromtimestamp(float(entry['Timestamp'][6:-2])/1000)
        entry = entry['Contents'].split(' ') #Prep to help me get the user out of the 'Contents'
        user = entry[0]
        if user == None:
            return True, f'Failed to get User: {entry[0]}; please attempt to add them or update their IGN manually.'
            
        lastlogin = curserver.GetUser(entry[0]).LastLogin #Gets the datetime object of the ServerUser last login
        timeplayed = curserver.GetUser(entry[0]).TimePlayed #Gets the time played of the ServerUser
        time_online = (time_online/60) #Turn our value into minutes.
        timeplayed += (lastlogin - time_online) #Add's the play time to their current accured amount of play time..
        return True, f'Updated User: {entry[0]} played time increased by {time_online} Minutes. Total: {timeplayed} Minutes.'

    return False, entry