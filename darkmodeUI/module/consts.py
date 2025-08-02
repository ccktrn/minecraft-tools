# -*- coding: utf-8 -*-

DEFAULT_PACK_NAME = "darkmodeUI_%s.zip" # 出力先のzipファイル名

# 置換対象のpngファイルのパスリスト (1.xx.x.jarの直下からの相対パス)
# ここに指定したパスに合致するものを置換対象とする
ASSET_PATH_LIST = [ # Minecraft 1.21.8 のパス
    "assets/minecraft/textures/gui/*.png",
    "assets/minecraft/textures/gui/container/**/*.png",
    "assets/minecraft/textures/gui/sprites/container/**/*.png",
    "assets/minecraft/textures/gui/sprites/advancements/*.png",
    "assets/minecraft/textures/gui/sprites/recipe_book/*.png",
    "assets/minecraft/textures/gui/sprites/dialog/**/*.png",
    "assets/minecraft/textures/gui/sprites/widget/**/*.png",
    "assets/minecraft/textures/gui/sprites/toast/**/*.png",
]

#置換する色(上から置換)  [ before[r,g,b, a], after[r,g,b, a] ]   
COLOR_PAIR_LIST=[
  [[198,198,198,255],[79,79,79,255]],
  [[139,139,139,255],[56,56,56,255]],
  [[255,255,255,255],[102,102,102,255]],
  [[55,55,55,255],[22,22,22,255]]
]
