# -*- coding: utf-8 -*-
import os
from pathlib import Path 
import cv2
import numpy as np
import zipfile
import json
import re
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
        elif p_out.suffix == ".zip":
            # If output is a zip file, use it directly
            return p_out.resolve()
        else:
            # If output is a file without .zip extension, treat it as a basename and create the zip file there
             return p_out.with_suffix(".zip").resolve()
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
    # 右下半分のマスク
    mask = np.zeros((size, size), dtype=np.uint8)
    tril_indices = np.tril_indices(size, k=-1)
    mask[tril_indices] = 255
    # 2つをマスクを使って合成
    result = np.where(mask[:, :, np.newaxis] == 255, img_dark, img)
    # 画像の右下半分を明るさを2/5にする
    _, buffer = cv2.imencode('.png', result)
    return buffer.tobytes()

# pack.mcmetaの内容を作成する関数
def get_pack_meta(zip_file : zipfile.ZipFile) -> str:
    data = zip_file.read("version.json")
    if not data:
        raise FileNotFoundError("version.json not found in the zip file")
    version_info = json.loads(data)

    version = version_info.get("id", "unknown")
    pack_format = version_info.get("pack_version", {}).get("resource", 15)
    return json.dumps({
        "pack": {
            "pack_format": pack_format, 
            "supported_formats": {
                "min_inclusive": 15,
                "max_inclusive": 255
            },
            "description": f"Dark Mode UI for Minecraft {version}"
        }
    })

# Minecraftのjarファイルのパスを取得する関数
def get_jar_path(version: str, mc_path: str) -> Path:
    jar_path = Path(mc_path).resolve() / "versions" / version / f"{version}.jar"
    if not jar_path.exists():
        raise FileNotFoundError(f"{version}.jar not found in {str(jar_path.parent)}")
    return jar_path

# zipファイル内のpngファイルのパスを取得する関数
def get_png_path_list(zip_file : zipfile.ZipFile):
    # asset_pathよりも下の階層にあるpngファイルのパスをすべてに抽出
    png_files = [str(p.filename) for p in zip_file.filelist if _is_match_path(p.filename, consts.ASSET_PATH_LIST)]
    return png_files

# パスがASSET_PATH_LISTのいずれかのパターンにマッチするかを確認する関数
def _is_match_path(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        regex = _convert_shellpattern_to_regex(pattern)
        if re.match(regex, path): return True
    return False

# シェルスタイルのワイルドカードパターンを正規表現に変換する関数
def _convert_shellpattern_to_regex(pattern: str) -> str:
    # minecraftのパスなので＠(全角)がないこと前提
    pattern = pattern.replace('*', '＠') # いったん置き換え
    pattern = pattern.replace('.', r'\.') # Escape dots
    pattern = pattern.replace('?', '.') 
    pattern = pattern.replace('/＠＠', '(/.*)?') # 
    pattern = pattern.replace('＠', '[^/]*') #
    return f'^{pattern}$'

# 一枚の画像に対して色置換を行った画像データを返す関数
def color_replace(img : cv2.Mat | np.ndarray) -> cv2.Mat | np.ndarray: 
    dst = img.copy()
    # 要素の第２軸(各ピクセル)に対してconst.REPLACE_***_FUNCを適用
    if len(img.shape)==2 : # GrayScale image
        dst = consts.REPLACE_GRAY_FUNC(dst)
    elif img.shape[2] == 3:# RGB image
        dst = np.apply_along_axis(consts.REPLACE_RGB_FUNC, 2, dst)
    elif img.shape[2] == 4:# RGBA image
        dst = np.apply_along_axis(consts.REPLACE_RGBA_FUNC, 2, dst)
    return dst

# 画像の明るさを計算する関数
def _brightness(rgb: list[int]) -> int: 
    r, g, b = rgb
    return (r * 299 + g * 587 + b * 114) // 1000

