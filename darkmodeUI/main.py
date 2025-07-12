
import sys
from pathlib import Path
import time
import cv2
import numpy as np

#置換する色の指定  [ before[r,g,b, a], after[r,g,b, a] ]   
color_pair_list=[
            [[198,198,198,255],[79,79,79,255]],
            [[139,139,139,255],[56,56,56,255]],
            [[255,255,255,255],[102,102,102,255]],
            [[55,55,55,255],[22,22,22,255]]
          ]

#関数定義 
def color_replace(img, color_beforeafter_list,  useAlpha:bool = True):
    dst = img.copy()
    if len(img.shape)==2 : # gray
        for cb,ca in color_beforeafter_list :
            bb,ba = sum(cb[:2])/3 * cb[3]/255, sum(ca[:2])/3 * ca[3]/255
            dst[np.where((img == bb).all(axis=2))] = ba
    
    else: # color
        for cb,ca in color_beforeafter_list :
            if (useAlpha and img.shape[2]==4) :
                dst[np.where((img == cb[:4]).all(axis=2))] = ca[:4]
            else :
                dst[np.where((img == cb[:3]).all(axis=2))] = ca[:3]
    
    return dst


def find_all_img_path(root_path:list[str]) :
    res = []
    for path in root_path:
        paths = Path(root_path).glob("**/*.png")
        res.extend([ str(p.absolute()) for p in paths])
    return res



#---main-----
def main ():
    if len(sys.argv) > 1:
        filename_list = find_all_img_path(sys.argv[1:])  
        for filename in filename_list:
            # 元画像取得
            img = cv2.imread(filename,cv2.IMREAD_UNCHANGED)
            img = color_replace(img, color_pair_list)
            # 画像ファイルとして出力
            cv2.imwrite(filename,img)

    else:
        print("no arguments!")


if __name__ == "__main__":
    main()
