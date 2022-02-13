#Sentinel Bot - consolefilters
import config


def filters(entry):
    #print('Console Filters',entry)
    if config.CommandBlocks:
        if entry['Contents'].startswith('CommandBlock at'):
            #print(f'Console Filter triggered... Removed: {entry["Contents"]}')
            return True

    if config.WorldEdit:
        if entry['Contents'].find('issued server command: //') != -1:
            return True

    if config.Default:
        if entry['Contents'].startswith('Current Memory Usage:') and entry['Contents'].endswith('mb)'):
            #print(f'Console Filter triggered... Removed: {entry["Contents"]}')
            return True
        if entry['Source'] == 'Installer':
            return True
        if entry['Source'] == 'Server thread/Warn':
            return True

    if config.Debugging:
        if entry['Source'] == 'Server thread/ERROR':
            return True
        filtertable = ['\tat net.minecraft','\tat java.util','java.lang']
        for filter in filtertable:
            if entry['Contents'].startswith(filter):
                return True
    return entry