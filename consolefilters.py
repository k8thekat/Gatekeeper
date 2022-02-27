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
#Gatekeeper Bot - consolefilters
import config
import logging

def filters(entry):
    if type(entry) == dict:
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
            if entry['Source'].lower() == 'installer':
                return True
            if entry['Source'].lower() == 'server thread/warn':
                return True

        if config.Debugging:
            #if entry['Source'].lower() == 'server thread/info':
               # return True
            if entry['Source'].lower() == 'server thread/error':
                return True
            #!! Needs to be Adressed; find out console filter solutions for mod loading.
            filtertable = ['\\tat net.minecraft','\\tat java.util','java.lang','java.io','com.google']
            for filter in filtertable:
                if entry['Contents'].lower().startswith(filter):
                    return True
        return entry
    else:
        return entry

#Removed the odd character for color idicators on text
def colorstrip(entry):
    char =  '�'
    if entry['Contents'].find(char) != -1:
        logging.info('Color strip triggered...')
        index = 0
        while 1:
            index = entry['Contents'].find(char,index)
            if index == -1:
                break
            newchar = entry['Contents'][index:index+2]
            entry['Contents'] = entry['Contents'].replace(newchar,'')
        return entry
    return entry
