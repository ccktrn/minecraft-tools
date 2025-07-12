
import sys
import time
import cv2
import numpy as np

#置換する色  [ before[r,g,b, a], after[r,g,b, a] ]   
color_pair_list=[
            [[198,198,198,255],[79,79,79,255]],
            [[139,139,139,255],[56,56,56,255]],
            [[255,255,255,255],[102,102,102,255]],
            [[55,55,55,255],[22,22,22,255]]
          ]


def color_replace(img, rgba_from, rgba_to, useAlpha:bool = True):
    if (useAlpha and img.shape[2]==4) :
        img[np.where((img == rgba_from[:4]).all(axis=2))] = rgba_to[:4]
    else :
        img[np.where((img == rgba_from[:3]).all(axis=2))] = rgba_to[:3]
    return

def gray_replace(img, bright_from, bright_to,):
    img[np.where((img == bright_from))] = bright_to
    return

#---メイン処理-----

if len(sys.argv) > 1:

    for filename in sys.argv[1:] :

        # 元画像取得
        img = cv2.imread(filename,cv2.IMREAD_UNCHANGED)

        if len(img.shape)==2 :
            # グレースケール画像
            for color_pair in color_pair_list:
               gray_replace(img, color_pair[0][0], color_pair[1][0])
        else :            
            # colorlistに従って色置換する
            for color_pair in color_pair_list:
                color_replace(img, color_pair[0], color_pair[1])

        # 画像ファイルとして出力
        cv2.imwrite(filename,img)

else:
    print("no arguments!")
