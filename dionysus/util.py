import os

from dionysus.constants import editor

def initiate_editor(path):
    os.system(f"{editor} \"{path}\"")