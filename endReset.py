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
# SentinelBot - The Level.dat End Reset Script
import nbtlib
import config
import io
import base64
import gzip

def init(AMPservers,curserver):
    leveldat = AMPservers[curserver].getFileChunk('world\leveltest.dat',0,33554432)
    newlevel = dragonReset(base64.b64decode(leveldat['result']['Base64Data']))
    newdata = base64.b64encode(newlevel).decode('utf-8')
    AMPservers[curserver].writeFileChunk('world\leveltest.dat',0,newdata)
    worldremove(AMPservers,curserver)
    return True

def dragonReset(leveldat):
    print('Attempting to reset the Dragon Fight in level.dat...')
    fakefile = io.BytesIO()
    fakefile.write(leveldat)
    fakefile.seek(0)
    if leveldat[0:2] == b"\x1f\x8b":
       fakefile = gzip.GzipFile(fileobj=fakefile)
    nbtdata = nbtlib.File.from_fileobj(fakefile, "big")
    dragon_path = nbtdata['']['Data']['DragonFight']
    del_list = []
    for entry in dragon_path:
        del_list.append(entry)
    for entry in del_list:
        print(entry)
        del dragon_path[entry]
    fakefile = io.BytesIO()
    nbtdata.write(fakefile)
    fakefile.seek(0)
    newdata = fakefile.read()
    return newdata

def worldremove(AMPservers,curserver):
    print('Removing the End World file...')
    if config.Multiverse_Core:
        worlddir = AMPservers[curserver].TrashDirectory('world_the_end')
        print(worlddir)
    else:
        worlddir = AMPservers[curserver].TrashDirectory('world\DIM-1')
        print(worlddir)
    return