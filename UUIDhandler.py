'''
   Copyright (C) 2021-2022 Katelynn Cadwallader.

   This file is part of Sentinel, the AMP Minecraft Discord Bot.

   Sentinel is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.

   Sentinel is distributed in the hope that it will be useful, but WITHOUT
   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
   or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
   License for more details.

   You should have received a copy of the GNU General Public License
   along with Sentinel; see the file COPYING.  If not, write to the Free
   Software Foundation, 51 Franklin Street - Fifth Floor, Boston, MA
   02110-1301, USA. 
'''
#UUIDhandler
import json
import requests

#Minecraft username UUID check
def uuidcheck(name):
    url = 'https://api.mojang.com/profiles/minecraft'
    header = {'Content-Type': 'application/json'}
    jsonhandler = json.dumps(name)
    post_req = requests.post(url, headers=header, data=jsonhandler)
    minecraft_user = post_req.json()
    if len(minecraft_user) != 0: #True if it exists and False if it doesnt.
        return True, minecraft_user #returns [{'id': 'uuid', 'name': 'name'}] 
    else:
        return False, None

#Minecrat username history check
def uuidCurName(mc_user):
    mc_user_uuid = mc_user[0]['id']
    url = f'https://api.mojang.com/user/profiles/{mc_user_uuid}/names'
    post_req = requests.get(url)
    return post_req.json()[-1]
