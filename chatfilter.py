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
#Gatekeeper Bot - Chat filter
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
                print(len(content))
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
        user = client.get_user(id = int(userid))
        content = content[0:user_find_start] + user.name + content[user_find_end+1:]
        return content
    else:
        return False

def channel(content,client):
    channel_find_start = content.find('<#')
    channel_find_end = content.find('>',channel_find_start)
    if channel_find_start != -1 and channel_find_end != -1:
        channelid = content[channel_find_start+2:channel_find_end]
        channel = client.get_channel(id = int(channelid))
        content = content[0:channel_find_start] + channel.name + content[channel_find_end+1:]
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