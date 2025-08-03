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


bright_rate = 0.5 # グレーの明るさを 0.5 倍にする
# グレースケール画像に対して適用する置換関数 : int -> int
REPLACE_GRAY_FUNC = lambda bright : bright * bright_rate
# 不透過カラー画像に対して適用する置換関数 : [int*3] -> [int*3]
REPLACE_RGB_FUNC = lambda rgb : rgb * bright_rate if rgb[0] == rgb[1] == rgb[2] else rgb
# 透過カラー画像に対して適用する置換関数 : [int*4] -> [int*4]
REPLACE_RGBA_FUNC = lambda rgba : [*(rgba[:3] * bright_rate), rgba[3]] if rgba[0] == rgba[1] == rgba[2] else rgba
