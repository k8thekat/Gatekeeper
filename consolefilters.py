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
#Sentinel Bot - consolefilters
import config


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
    else:
        return entry