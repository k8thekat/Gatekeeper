# The Level.dat End Reset Script
import nbtlib

def dragonfightreset():
    nbt_file = nbtlib.load('level.dat')
    test_path = nbt_file['']['Data']['DragonFight']
    del_list = []
    for entry in test_path:
        del_list.append(entry)
    for entry in del_list:
        del test_path[entry]
    nbt_file.save()
    return
dragonfightreset()

import os
import shutil
def worldremove():
    cwd = os.getcwd()
    file_name = '\DIM1'
    if os.path.isdir(cwd + file_name):
        try:
            shutil.rmtree(cwd + file_name)
        except Exception as e:
            print(e)
    return
worldremove()