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
    #print(minecraft_user,len(minecraft_user))
    if len(minecraft_user) != 0: #True if it exists and False if it doesnt.
        return True, minecraft_user
    else:
        return False, None

#Minecrat username history check
def uuidCurName(mc_user):
    mc_user_uuid = mc_user[0]['id']
    url = f'https://api.mojang.com/user/profiles/{mc_user_uuid}/names'
    post_req = requests.get(url)
    return post_req.json()[-1]
