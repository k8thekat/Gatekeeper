#Time Ranks
#Ranks based on how much time you have spent on a single server.


def amateurRank():
    # Amateur | 10 Hours
    # - 2 Homes
    # - 105 Claim Chunks
    # - 1 Loaded Chunk
    return

def experiencedRank():
    # Experienced | 20 Hours
    # - 2 Homes
    # - 110 Claim Chunks
    # - 1 Loaded Chunk
    return

def wellknownRank():
    # Well-Known | 50 Hours
    # - 2 Homes
    # - 115 Claim Chunks
    # - 1 Loaded Chunk
    return

def addictedRank():
    # Addicted | 150 Hours
    # - 2 Homes
    # - 120 Claim Chunks
    # - /nickname
    # - 1 Loaded Chunk
    return

def overlordRank():
    # Overlord | 200 Hours
    # - 2 Homes
    # - 125 Claim Chunks
    # - /nickname
    # - 2 Loaded Chunks
    return

def omegaRank():
    # Omega | 500 Hours
    # - 2 Homes
    # - 130 Claim Chunks
    # - /nickname
    # - 2 Loaded Chunks
    return

def nolifeRank():
    # No-Life | 800 Hours
    # - 2 Homes
    # - 135 Claim Chunks
    # - /nickname
    # - 2 Loaded Chunks
    return

def hacksRank():
    # Hacks | 1000 Hours
    # - 2 Homes
    # - 140 Claim Chunks
    # - /nickname
    # - 2 Loaded Chunks
    return

ranks = {'Amateur': {'start_value': 600,'stop_value': 1199, 'func': amateurRank},
        'Experienced': {'start_value': 1200,'stop_value': 3499, 'func': experiencedRank},
        'Well-Known': {'start_value': 3500,'stop_value': 8999, 'func': wellknownRank},
        'Addicted': {'start_value': 9000,'stop_value': 11999, 'func': addictedRank},
        'Overlord': {'start_value': 12000,'stop_value': 29999, 'func': overlordRank},
        'Omega': {'start_value': 30000,'stop_value': 47999, 'func': omegaRank},
        'No-Life': {'start_value': 48000,'stop_value': 59999, 'func': nolifeRank},
        'Hacks': {'start_value': 60000,'stop_value': -1, 'func': hacksRank}}

import database
import logging
import datetime
db = database.Database()

def init(Gatekeeper_AMP,Gatekeeper_AMPservers):
    global AMP, AMPservers
    AMP = Gatekeeper_AMP
    AMPservers = Gatekeeper_AMPservers
    return


timecheck = datetime.datetime.now()

def timeUpdate(console_entry):
    global timecheck
   # 'Source': 'Server thread/INFO', 'Type': 'Console', 'Contents': 'There are 10 of a max of 20 players online: Kaymorin, Oxyorum, MoonRacco0n, Alain, Ayvalen, umbrellawarrior, Mouseas, DocScott18 - odog221, Scavable, Spontaneo'
    user_list = console_entry['Contents'].find('players online:')
    if user_list != -1:
        print(timecheck + datetime.timedelta(minutes = 5),datetime.datetime.now(),user_list)
        if timecheck + datetime.timedelta(minutes = 5) <= datetime.datetime.now():
            user_list = console_entry['Contents'][user_list+16:].split(', ')
            for user in user_list:
                if user.find(' - ') != -1:
                    nickname = user.split(' - ')
                    user = nickname[1]
                print(user)   
                db_user = db.GetUser(user)
                if db_user != None:
                    if db_user.TimePlayed == None:
                        db_user.TimePlayed = 5
                    else:
                        db_user.TimePlayed += 5
                    logging.info(f'Increased {db_user.DiscordName} Total Time Played by 5 Minutes. **TOTAL**: {db_user.TimePlayed}')  
            return
    return







