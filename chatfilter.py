#Sentinel Bot - Chat filter
import discord

def scan(content):
    print(content)
    #Strips Unicode out of the message
    content = unicode(content)
    content = user(content)
    #Attempts to find discord emoji's and remove them
    while(1):
        start_bracket = content.find('<:')
        end_bracket = content.find('>',start_bracket)
        if start_bracket == -1 or end_bracket == -1:
            return content
        msgpart = content[0:start_bracket]
        msgpart += content[end_bracket+1:]
        content = msgpart
    return content

def unicode(content):
    content = content.encode("ascii","ignore")
    content = content.decode()
    return content

def user(content):
    user_find_start = content.find('<@!')
    user_find_end = content.find('>',user_find_start)
    if user_find_start != -1 and user_find_end != -1:
        userid = content[user_find_start+3:user_find_end]
        print(userid)
        username = discord.Client.get_user(int(userid))
        #username = 'k8_thekat'
        content = content[0:user_find_start]+ username + content[user_find_end+1:]
        return content
    else:
        return content