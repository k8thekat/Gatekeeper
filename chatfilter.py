#Sentinel Bot - Chat filter
import discord

def scan(content):
    #Strips Unicode out of the message
    content = unicode(content)
    content = user(content)
    #Attempts to find discord emoji's and remove them
    while(1):
        start_bracket = content['message'].find('<:')
        end_bracket = content['message'].find('>',start_bracket)
        #print(start_bracket,end_bracket)
        if start_bracket == -1 or end_bracket == -1:
            return content
        msgpart = content['message'][0:start_bracket]
        msgpart += content['message'][end_bracket+1:]
        content['message'] = msgpart
    return content

def unicode(content):
    content = content['message'].encode("ascii","ignore")
    str_decode = content.decode()
    content = {'message': str_decode}
    return content

def user(content):
    user_find_start = content['message'].find('<@!')
    user_find_end = content['message'].find('>',user_find_start)
    userid = content['message'][user_find_start+3:user_find_end]
    username = discord.Client.get_user(int(userid))
    content['message'] = content['message'][0:user_find_start]+ username + content['message'][user_find_end+1:]
    return content