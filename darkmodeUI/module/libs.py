# -*- coding: utf-8 -*-
import os
from pathlib import Path 
import cv2
import numpy as np
import zipfile
import json
import fnmatch
import module.consts as consts


def get_default_mc_dir():
    appdata = os.getenv('APPDATA')
    if appdata:
        return os.path.join(appdata, ".minecraft")
    else:
        raise ValueError("APPDATA environment variable is not set. Please set it to the path of your Minecraft directory.")  

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
            # If output is a file without .zip extension, treat it as a directory and create the zip file there
             return p_out.with_suffix(".zip").resolve()
    else:
        # If no output directory is specified, use the current working directory
        return Path(consts.DEFAULT_PACK_NAME % version).resolve()

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

def get_jar_path(version: str, mc_path: str) -> Path:
    jar_path = Path(mc_path).resolve() / "versions" / version / f"{version}.jar"
    if not jar_path.exists():
        raise FileNotFoundError(f"{version}.jar not found in {str(jar_path.parent)}")
    return jar_path

def get_png_path_list(zip_file : zipfile.ZipFile):
    # asset_pathよりも下の階層にあるpngファイルのパスをすべてに抽出
    png_files = [str(p.filename) for p in zip_file.filelist if _is_match_path(p.filename, consts.ASSET_PATH_LIST)]
    return png_files

def _is_match_path(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern): return True
    return False

# 一枚の画像に対して色置換を行った画像データを返す関数
def color_replace(img : cv2.Mat | np.ndarray, color_beforeafter_list: list[list[list[int]]],  useAlpha:bool = True) -> cv2.Mat | np.ndarray: 
    dst = img.copy()
    if len(img.shape)==2 : # if grayscale
        for cb,ca in color_beforeafter_list :
            bb,ba = _brightness(cb[:3]), _brightness(ca[:3])
            dst[np.where((img == bb))] = ba
    else: # color
        for cb,ca in color_beforeafter_list :
            if (useAlpha and img.shape[2]==4) :
                dst[np.where((img == cb[:4]).all(axis=2))] = ca[:4]
            else :
                dst[np.where((img == cb[:3]).all(axis=2))] = ca[:3]
    return dst


def _brightness(rgb: list[int]) -> float:
    r, g, b = rgb
    return (r * 299 + g * 587 + b * 114) / 1000