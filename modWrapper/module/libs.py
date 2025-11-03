# -*- coding: utf-8 -*-
import os
from pathlib import Path 
import cv2
import numpy as np
import zipfile
import json
import module.consts as consts


# 環境変数からMinecraftのデフォルトディレクトリを取得
def get_default_mc_dir():
    appdata = os.getenv('APPDATA')
    if appdata:
        return os.path.join(appdata, ".minecraft")
    else:
        raise ValueError("APPDATA environment variable is not set. Please set it to the path of your Minecraft directory.")  

# 出力先のパスを取得する関数
def get_pack_path(version: str, output: str | None) -> Path:
    if output:
        p_out = Path(output)
        if p_out.is_dir():
            # If output is a directory, create the zip file in that directory
            return (p_out / (consts.DEFAULT_PACK_NAME % version)).resolve()
        elif p_out.suffix == ".jar":
            # If output is a zip file, use it directly
            return p_out.resolve()
        else:
            # If output is a file without .zip extension, treat it as a basename and create the zip file there
             return p_out.with_suffix(".jar").resolve()
    else:
        # If no output directory is specified, use the current working directory
        return Path(consts.DEFAULT_PACK_NAME % version).resolve()
    
# pack.pngの画像を作成する関数
def create_pack_png (src: bytes) -> bytes:
    img = cv2.imdecode(np.frombuffer(src, np.uint8), cv2.IMREAD_UNCHANGED)
    if img is None: return src
    # 256x256以下の正方形に制限
    size = min(img.shape[0],img.shape[1], 256)
    img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
    # が層の明るさ2/5ver
    img_dark = cv2.convertScaleAbs(img, alpha=(2/5), beta=0)
    # 左下のマスク
    mask = np.zeros((size, size), dtype=np.uint8)
    tril_indices = np.tril_indices(size, k=size//4)
    mask[tril_indices] = 255
    # 2つをマスクを使って合成
    result = np.where(mask[:, :, np.newaxis] == 255, img_dark, img)
    # 画像の右下半分を明るさを2/5にする
    _, buffer = cv2.imencode('.png', result)
    return buffer.tobytes()


# Minecraftのjarファイルのパスを取得する関数
def get_jar_path(version: str, mc_path: str | None) -> Path:
    jar_path = Path(mc_path if mc_path else get_default_mc_dir()).resolve() / "versions" / version / f"{version}.jar"
    if not jar_path.exists():
        raise FileNotFoundError(f"{version}.jar not found in {str(jar_path.parent)}")
    return jar_path


###

def get_fabricmod_json (
        zip_file : zipfile.ZipFile,
        jarnames: list[str],
        id="mod-pack", name="ModPack",
        version="1.0.0", environment="*",
        authors=["me"],
        description="" ):
    
    
    data = zip_file.read("version.json")
    if not data:
        raise FileNotFoundError("version.json not found in the zip file")
    version_info = json.loads(data)

    version = version_info.get("id", "unknown")


    jsons:dict = {}
    jsons["schemaVersion"] = 1
    jsons["id"] = id
    jsons["name"] = name
    jsons["version"] = version
    jsons["environment"] = environment
    jsons["license"] = "None"
    jsons["icon"] = "mod.png"
    jsons["authors"] = authors
    jsons["depends"] = {
        "minecraft": f">={version}"
    }
    jsons["description"] = description
    # jars 
    jsons["jars"] = [{ "file" : f"jars/{j}" } for j in jarnames ]

    return json.dumps(jsons, ensure_ascii=False, indent="  ")

