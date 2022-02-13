#Sentinel Bot - Chat filter

def scan(entry):
    if entry['Contents'].find('<:') and entry['Contents'].find('>'):
        print('Found an emoji')
    return entry