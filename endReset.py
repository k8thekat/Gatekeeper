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