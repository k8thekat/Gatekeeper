#Sentinel Bot - Console Scanning
import commandlogger
import config
import plugin_commands
from datetime import datetime, timedelta

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
            return True, f'Unable to update User: {entry_split[1]} whitelisted status in the database!'
    #Removed k8_thekat from the whitelist
    if entry['Contents'].startswith('Removed') and entry['Contents'].endswith('from the whitelist'):
        print('User removed from Whitelist via console..')
        commandlogger.logHandler(None,curserver,entry,'console')
        entry_split = entry['Contents'].split(' ')
        print(curserver)
        try:
            curserver.GetUser(entry_split[1]).Whitelisted = False
        except Exception as e:
            print(e)
            return True, f'Unable to update User: {entry_split[1]} whitelisted status in the database!'
    return False, entry

