

import sys, os
from pathlib import Path
import cv2
import numpy as np
import zipfile

import module.consts as consts
import module.libs as libs



#---main-----
def generate (
    mc_ver: str,
    output_jar_path: str | None,
    minecraft_dir_path: str | None,
    package_jar_paths: list[str] = []
) -> tuple[bool, str]:
    try:
        res = None
        pack_path = libs.get_pack_path(mc_ver, output_jar_path)
        jar_path = libs.get_jar_path(mc_ver, minecraft_dir_path)
        jar_names = [Path(jar_path).name for jar_path in package_jar_paths]
        with zipfile.ZipFile(pack_path, "w") as dst_zip: # 出力先のzipファイルを開く
            with zipfile.ZipFile(jar_path, "r") as src_zip: # Minecraftのjarファイルを開く
                # fabric.mod.json, pack.pngの追加
                dst_zip.writestr("fabric.mod.json", libs.get_fabricmod_json(src_zip, jarnames=jar_names))
                dst_zip.writestr("mod.png", libs.create_pack_png(src_zip.read("pack.png"))) # pack.pngを作成
            # copy jars tp /jars/*.jar
            success, failed = 0, 0
            for jar_name, jar_path in zip(jar_names, package_jar_paths):
                try: 
                    with open(jar_path, "rb") as jar_file:
                        dst_zip.writestr(f"jars/{jar_name}", jar_file.read())
                    success += 1
                except Exception as e:
                    failed += 1


            res1 = f"Processed {len(jar_names)} jars: {success} succeeded, {failed} failed."
            res2 = f"Output jar file created at: {pack_path}"
            print(f"{res1}\n{res2}")
            res = (True, f"{res1}\n{res2}")
        return res
    except Exception as e:
        print(f"An error occurred: {e}")
        return (False, str(e))

