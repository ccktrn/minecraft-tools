# -*- coding: utf-8 -*-
# minecraft fabric.mod.json generator
# thisfile.py must be placed on FabricModRootDir 

import os
import sys
import itertools
import json
from pathlib import Path


def main(p_mod: Path, p_icon: Path, p_jars: Path, p_fabmod=None) :

    # [Todo (optional)] mod jar files download from https://cdn.modrinth.com/
    # [Todo ] automatically configure dependancies,environment,authors


    jsons:dict = create_fabricmod( # setting mod info
            p_mod, p_icon, p_jars,

            id="basic-pack",
            name="BasicPack",
            version="0.1.1-1.21",
            depends={
                "minecraft": ">=1.21-",
                "fabricloader": ">=0.15.11"
            },
            description="Basic optimizer mods, for fabric 1.21.0",
        )
    
    with open(p_mod ,"w", encoding="utf_8") as fp: 
        json.dump(jsons,fp,ensure_ascii=False,indent="  ")



# def 
def create_fabricmod (
        p_mod:Path,
        p_icon:Path|str = "icon.png",
        p_jars:Path|str = "jars",
        schemaVersion=1, id="mod-pack", name="ModPack",
        version="1.0.0", environment="*", license="None",
        authors=["me"], depends = {},
        description="" ):
    
    if isinstance(p_icon,str) : # to Path()
        p_icon = Path(p_mod)/p_icon
    if isinstance(p_jars,str) :
        p_jars = Path(p_mod)/p_jars

    iconpath = str(p_icon.relative_to(p_mod))
    jarspath = str(p_jars.relative_to(p_mod))

    jsons:dict = {}
    jsons["schemaVersion"] = schemaVersion
    jsons["id"] = id
    jsons["name"] = name
    jsons["version"] = version
    jsons["environment"] = environment
    jsons["license"] = license
    jsons["icon"] = iconpath
    jsons["authors"] = authors
    jsons["depends"] = depends
    jsons["description"] = description
    # jars 
    jar_list = os.listdir(p_jars)
    jsons["jars"] = [{ "file" : f"{jarspath}/{j}" } for j in jar_list ]

    return jsons


#################################### 
if __name__ == "__main__":
    pass