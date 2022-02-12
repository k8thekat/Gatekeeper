#Sentinel Bot - plugin commands
import config
import timehandler

def Essentials(entry):
    if config.Essentials:
        #Vanilla_Minecraft {'Timestamp': '/Date(1640909000232)/', 'Source': 'Server thread/INFO', 'Type': 'Console', 'Contents': 'WolfDevilAngel issued server command: /tempban DragousVirg 6m take a break'}
        if entry['Contents'].find('issued server command: /tempban') != -1:
            entry = entry.split('')
            time_out = timehandler.parse(entry[6])
            IGN = entry[5]
            return time_out,IGN

