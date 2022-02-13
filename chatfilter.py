#Sentinel Bot - Chat filter
import discord

def scan(content,client):
    while(1):
        #Replaces @User calls in Discord with just the Name
        content = user(content,client)
        #Attempts to find discord emoji's and remove them
        content = emoji(content)
        #Strips Unicode out of the message
        content = unicode(content)
    return content

def unicode(content):
    content = content.encode("ascii","ignore")
    content = content.decode()
    return content

def user(content,client):
    user_find_start = content.find('<@!')
    user_find_end = content.find('>',user_find_start)
    if user_find_start != -1 and user_find_end != -1:
        userid = content[user_find_start+3:user_find_end]
        username = client.get_user(id = int(userid))
        content = content[0:user_find_start]+ username.name + content[user_find_end+1:]
        return content
    else:
        return content

def emoji(content):
    start_bracket = content.find('<:')
    end_bracket = content.find('>',start_bracket)
    if start_bracket == -1 or end_bracket == -1:
        return content
    msgpart = content[0:start_bracket]
    msgpart += content[end_bracket+1:]
    content = msgpart
    return content