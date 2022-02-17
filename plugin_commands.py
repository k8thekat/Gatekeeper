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
#Gatekeeper Bot - plugin commands
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

