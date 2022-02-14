#Sentinel Bot - Chat filter

def scan(content,client):
    content = unicode(content)
    while(1):
        userstatus = user(content,client)
        emojistatus = emoji(content)
        channelstatus = channel(content,client)
        if userstatus != False:
            content = userstatus  
        elif emojistatus != False:
            content = emojistatus 
        elif channelstatus != False:
            content = channelstatus
        else:
            if userstatus == False and emojistatus == False and channelstatus == False:
                content = content.strip()
                if len(content) == 0:
                    return True
                else:
                    return content

#Strips Unicode out of the message
def unicode(content):
    content = content.encode("ascii","ignore")
    content = content.decode()
    return content

#Replaces @User calls in Discord with just the Name
def user(content,client):
    user_find_start = content.find('<@!')
    user_find_end = content.find('>',user_find_start)
    if user_find_start != -1 and user_find_end != -1:
        userid = content[user_find_start+3:user_find_end]
        username = client.get_user(id = int(userid))
        content = content[0:user_find_start] + username.name + content[user_find_end+1:]
        return content
    else:
        return False

def channel(content,client):
    channel_find_start = content.find('<#')
    channel_find_end = content.find('>',channel_find_start)
    if channel_find_start != -1 and channel_find_end != -1:
        channelid = content[channel_find_start+3:channel_find_end]
        channelname = client.get_channel(id = int(channelid))
        content = content[0:channel_find_start] + channelname.name + content[channel_find_end+1:]
        return content
    else:
        return False

#Attempts to find discord emoji's and remove them
def emoji(content):
    start_bracket = content.find('<:')
    end_bracket = content.find('>',start_bracket)
    if start_bracket != -1 and end_bracket != -1:
        msgpart = content[0:start_bracket]
        msgpart += content[end_bracket+1:]
        content = msgpart
        return content
    else:
        return False