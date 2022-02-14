#Config file for Sentinel Bot
#Author: k8thekat
#Are you the gate keeper?! <3
import tokens
import database

#Database
db = database.Database()
dbconfig = db.GetConfig()

#Database Config Channels : ## DO NOT CHANGE ##
#These are set via //botsetting `channel` command usage. See Commands.md
whitelist = dbconfig.GetSetting('whitelistchannel')
faq = dbconfig.GetSetting('faqchannel')
support = dbconfig.GetSetting('supportchannel')
rules = dbconfig.GetSetting('ruleschannel')
info = dbconfig.GetSetting('infochannel')

#whitelist Format ## DO NOT CHANGE ##
#Users must use this format to request whitelist via auto-whitelist
WhitelistFormat = 'IGN: username \nSERVER: servername'

#Donator Feature - 
#Allows only users with donator flag to request whitelist and join donator only servers. 
# See `Commands-> User: Donator`
donations = False 
donatorID = '926688290504065026' #discord_role_id' or 'discord_role_name' 

#AMP Console - Login Info
#!!DO NOT CHANGE THIS INFO!!
AMPUser = tokens.AMPUser
AMPPassword = tokens.AMPPassword
AMPurl = tokens.AMPurl

#Plugin Command handling (Set to True if you use said Mod/Plugin)
Plugins = True  #Basic plugin support (Use this to Enable or Disable Plugin support)
Essentials = False #Currently supports (/tempban)

#All bot commands via discord are logged at this time and may stay as such...
#Populate with slash commands you want to monitor and log via in-game usage or AMP Console usage
CommandList = ['/tempban','/gmc','/whitelist','/deop','/pardon','/gmsp','/warp','/op']

#Console Suppresion flags (True = Filter/ False = Show)
#These settings control what messages are displayed in the Discord console channel.
Default = True #Basic console spamming messages (example: Current Memory Usage)
Debugging = True #Filters out ANY ERRORs that would show in the console
CommandBlocks = False #Anything related to command blocks will be suppressed.
WorldEdit = False #Filters out any worldedit commands that start with //

#World Reset/Dragon Fight handlers
#These settings are needed to allow the bot to reset a dragon fight and reset the world.
DragonReset = True
Multiverse_Core = True

#Auto-reply messages
#These settings control what message the bot will reply with.
# Format for channel links is #channel_name or <#channel_id>. 
# You can also use the channels set via //botsettings `channel` -- See Commands
helpmsg = f'Looking to whitelist? See <#{whitelist}>, need something else? Check <#{faq}> or <#{support}> channels.'
infomsg = f'Looking for server information? See <#{info}>, or try <#{faq}>.'

#Auto-Whitelist messages
# Format for channel links is #channel_name or <#channel_id>. 
# Set to `False` to have server specific bot replies. Else the bot will pick randomly throughout the entries of Botwhitelistreplies
Randombotreplies = True 
# These Entries correspond to a specific when `Randombotreplies = False`
# eg. Entry #1 in the list below would be the **FIRST** server in your AMP Instances, Entry #2 is AMP instance #2 etc...
Botwhitelistreplies = [ 
    f'Welcome, please see <#{info}> for IP and modpack versions~ Also take a look at <#{faq}> if you need help connecting- otherwise try <#{support}> !Happy Mining!',
    f'Whitelisted! Please see <#{info}> for IP and modpack versions~ Also take a look at our <#{faq}> ',
    'Hope your ready to earn your engineering degree! Have fun and blow stuff up~'
    ]