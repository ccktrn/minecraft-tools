

import sys, os
from pathlib import Path
import cv2
import numpy as np
import zipfile

import module.consts as consts
import module.libs as libs



#---main-----
def generate (argv:list[str]) -> tuple[bool, str]:
    try:
        res = None
        if len(argv) <= 1:
            print("Usage:")
            print("\t> main.py <mc_version> [<output_zip_path> <.minecraft_dir_path>]")
            print("Args:")
            print("\t<mc_version>: Minecraft version (e.g., 1.20.1)")
            print("\t<output_zip_path>: Path to the output zip file (default: <current directory>/darkmodeUI_<mc_version>.zip)")
            print("\t<.minecraft_dir_path>: Path to the .minecraft directory (default: %APPDATA%\\.minecraft)")
            print("Example:")
            print("\t main.py 1.20.2 dist/MyPack.zip")
            res = (False, "Invalid arguments. Please check the usage.")
            return res
        mc_ver = argv[1]
        pack_path = libs.get_pack_path(mc_ver, argv[2] if len(argv) > 2 else None)
        jar_path = libs.get_jar_path(mc_ver, argv[3] if len(argv) > 3 else libs.get_default_mc_dir())
        with zipfile.ZipFile(pack_path, "w") as dst_zip: # 出力先のzipファイルを開く
            with zipfile.ZipFile(jar_path, "r") as src_zip: # Minecraftのjarファイルを開く
                # pack.mcmeta, pack.pngの追加
                dst_zip.writestr("pack.mcmeta", libs.get_pack_meta(src_zip))
                dst_zip.writestr("pack.png", libs.create_pack_png(src_zip.read("pack.png"))) # pack.pngを作成

                # テクスチャの置換, 追加
                img_on_zip_list = libs.get_png_path_list(src_zip)
                num_images = len(img_on_zip_list)
                num_skipped, num_success = 0, 0
                for img_path in img_on_zip_list:
                    # 元画像取得
                    with src_zip.open(img_path, "r") as img_file:
                        img = cv2.imdecode(np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
                        if img is None:
                            print(f"Failed to decode image {img_path}. Skipping...")
                            num_skipped += 1
                            continue
                        img = libs.color_replace(img)
                        # 画像ファイルとして出力
                        dst_zip.writestr(img_path, cv2.imencode('.png', img)[1].tobytes())
                        num_success += 1
                res1 = f"Processed {num_images} images: {num_success} succeeded, {num_skipped} failed."
                res2 = f"Output zip file created at: {pack_path}"
                print(f"{res1}\n{res2}")
                res = (True, f"{res1}\n{res2}")
        return res
    except Exception as e:
        print(f"An error occurred: {e}")
        return (False, str(e))

if __name__ == "__main__":
    generate(sys.argv)
