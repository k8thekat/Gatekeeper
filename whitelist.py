#Sentinel Bot - whitelist.py
from datetime import datetime
import base64
import json

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
    print('User to Database...')
    print(message.author.id,message.author.name)
    global WhitelistWaitList 
    curtime = datetime.now()
    user = db.GetUser(str(message.author.id)) 
    wl_request = parse.ParseIGNServer(message.content)
    IGN,sel_server = wl_request
    if user == None:
        print('New User Setup...')
        curuser = db.AddUser(DiscordID = str(message.author.id), DiscordName = message.author.name)
        if wl_request == None:
            return True, f'**Unable to process**: {message.content} Please manually whitelist this user and update their IGN via //user {message.author.id} ign MC_name'
        ign_check = UUIDhandler.uuidcheck(IGN)
        #IGN check...
        if ign_check[0] != True:
            return False, f'Your IGN: {IGN} is not correct, please double check your IGN...'
        #Updates the DB users IGN
        curuser.IngameName = IGN
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
        print('Found Exisitng user...')
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
            print('Found Existing User without an IGN...')
            #If no IGN; check the message for IGN and check its validity.
            ign_check = UUIDhandler.uuidcheck(IGN)
            if ign_check[0] != True:
                return False, f'Your IGN: {IGN} is not correct, please double check your IGN...'
            #Updates the DB users IGN
            user.IngameName = IGN
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
    print('Whitelist Wait List Check...')
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
                print(discord_user)
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
            print(discord_user)
            WhitelistWaitList.remove(user)
            return user

#This checks if the user is already whitelisted on the server...
def whitelistUserCheck(server,user):
    print('Whitelist User Check...')
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
    print('Whitelist Update...')
    global WhitelistWaitList
    if var.lower() == 'leave':
        for entry in WhitelistWaitList:
            if entry['User'].DiscordName == user.name:
                WhitelistWaitList.remove(entry)