# --  Minecraft >= 1.20.1   -- 
# 元のauthorの場所->newTitle,元のtitleの場所->keyname(ex.graham)(固定),ファイル参照してcopy&rename
# config.jsonからinitialを取得可能,　defaultに戻すボタンあり
#

import os
import sys
import time
from pathlib import Path # path tool
import shutil # file tool
import tkinter as tk # gui tool
from tkinter import ttk #better tk
from tkinter import filedialog as fd # file dialog
import json

from const import PAINTINGS # const.py


def bundle_path()->Path:
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)/'bundle' # exe-> LocalTempの一時フォルダ内にできる"bundle"ディレクトリ
    else:
        return Path(__file__).parent/'bundle' # py-> .pyファイルと同じ階層にある"bundle"ディレクトリ
def filedir_path()->Path:
    if hasattr(sys, '_MEIPASS'):
        return Path(sys.argv[0]).resolve().parent # exeがあるディレクトリのパス
    else:
        return Path(__file__).parent # pyがあるディレクトリのパス

p_icon = bundle_path()/'icon.ico'
p_root = bundle_path()/'pack_root'
p_lang = p_root/'assets/minecraft/lang/ja_jp.json'
p_painting = p_root/'assets/minecraft/textures/painting'

p_config =  filedir_path()/'config.json'



# -----------------------------------
class ScrollableFrame(ttk.Frame):

    def __init__(self, container, relief):
        super().__init__(container)
        self.canvas = tk.Canvas(self)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<MouseWheel>", self.mouse_y_scroll)
        self.scrollable_frame.bind(
            "<Configure>",
            func=lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        self.canvas.pack()

    def mouse_y_scroll(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')


class App : 
    # file 関連
    def load_config(self) -> dict: 
        self.config:dict  = {} # 辞書型オブジェクト
        try:     
            with open(p_config, 'r' , encoding="utf_8") as f : # jsonの読込
                self.config = json.load(f)
        except FileNotFoundError as e: #jsonファイルが存在しない
            for s,p in PAINTINGS.items():
                self.config[s] = {}
                for k,v in p.items(): 
                    self.config[s][k] = {
                        "title":v,
                        "srcfile":'' # エントリの初期値用の値
                    }
            print(f"\"{p_config.name}\" is not found. recreated.")
        return self.config

    def copy_png(self):
        for s,p in self.strings.items():
            for k,v in p.items():
                p_dst = p_painting/(k+'.png')
                try:
                    p_src = Path(v["srcfile"].get())
                    res = self.conv_image(p_src, p_dst)
                except (PermissionError) as e:#srcfileが空欄または無効な値
                    if p_dst.exists():
                        os.remove(p_dst)
    
    def conv_image(self,src,dst):
        # ほんとはちゃんと変換するべきなのだろうが、めんどいのでパス
            # srctype = src.suffix()
            # dsttype = dst.suffix()
        return shutil.copy(src,dst)
        
    
    def dump_config(self):
        conf:dict={}
        for s,p in self.strings.items():
            conf[s]={}
            for k,v in p.items():
                conf[s][k]={}
                conf[s][k]["title"]= v["title"].get()
                conf[s][k]["srcfile"]= v["srcfile"].get()
        with open(p_config, 'w', encoding="utf_8") as f : #json出力
            json.dump(conf, f, indent="\t",ensure_ascii=False)
        
    # GUI 関連 ----------

    def dump_lang(self):
        lang:dict = {}
        for s,p in self.strings.items():
            for k,v in p.items():
                lang["painting.minecraft."+k+".title"] = "\u00a77"+k
                lang["painting.minecraft."+k+".author"] = "\u00a7e"+v["title"].get()
        with open(p_lang, 'w', encoding="utf_8") as f : #json出力
            json.dump(lang, f, indent="\t",ensure_ascii=False)
        
    # GUI 関連 ----------

    def make_string_var(self) -> dict: # entriesの値操作用
        self.strings={}
        for s,p in PAINTINGS.items():
            self.strings[s]={}
            for k,v in p.items():
                self.strings[s][k] = {}
                self.strings[s][k]["title"] = tk.StringVar()
                self.strings[s][k]["srcfile"] = tk.StringVar()
        return self.strings
    
    def window(self,title:str = "app",iconpath=None ,width:int = 600, height:int = 300) -> tk.Tk:
        app = tk.Tk() #Tkオブジェクト生成
        app.title(title) #GUIのタイトル名の決定
        if Path.exists(iconpath):
            app.iconbitmap(iconpath) # window-icon
        x,y = (0,0)
        app.geometry(f"{width}x{height}+{x}+{y}") #画面の大きさ,位置の決定
        print(f"window created : \"{title}\" with {width}x{height}")
        return app


    def browse(self,stringvar): #ファイル参照
        def inner():
            fTyp = [
                ("image file ", "*.png;*.PNG;*.jpg;*.jpeg;*.JPG;*.JPEG;*.webp"),
                ("png file ", "*.png;*.PNG"),
                ("jpeg file ", "*.jpg;*.jpeg;*.JPG;*.JPEG"),
                ("webp file ", "*.webp")
            ]
            iFilePath = fd.askopenfilename(filetype = fTyp, initialdir = None)
            if Path(iFilePath).is_file():
                stringvar.set(iFilePath) 
        return inner
    
    def create_pack(self):
        p_zip = Path(fd.asksaveasfilename(
            title="Save as", 
            filetypes=[("archive file","*.zip")], 
            initialdir=filedir_path(), 
            initialfile="paintingChanger",
            defaultextension=""
        ))
        if p_zip.name : # 指定されたか否か
            try:
                self.dump_config()
                self.dump_lang()
                self.copy_png()
                shutil.make_archive(p_zip.parent/p_zip.stem, format='zip', root_dir=p_root)
                print("create")
                tk.messagebox.showinfo("info", f"resource-pack was created in\n{p_zip}")
            except Exception as e:
                print(e)
                tk.messagebox.showerror("error",e)

    def reset_entries(self): #self.configでセット
        for s,p in PAINTINGS.items():
            for k,v in p.items():
                try:
                    self.strings[s][k]["title"].set(self.config[s][k]["title"])   
                except KeyError as e: # self.configに存在しない
                    self.strings[s][k]["title"].set("")
                try:
                    self.strings[s][k]["srcfile"].set(self.config[s][k]["srcfile"])
                except KeyError as e: # self.configに存在しない
                    self.strings[s][k]["srcfile"].set("")
                    
    def vanilla_entries(self): #PAINTINGSをもとにセット
        for s,p in PAINTINGS.items():
            for k,v in p.items():
                try:
                    self.strings[s][k]["title"].set(PAINTINGS[s][k])   
                except KeyError as e: # PAINTINGSに存在しない(プログラムエラー)
                    self.strings[s][k]["title"].set("プログラムエラー")
                self.strings[s][k]["srcfile"].set("")

    # layout
    def layout(self):
        # rootFrame
        rootFrame = ttk.Frame(self.root_window)
        rootFrame.pack(expand=True)
        # leftFrame (scrollable) 
        leftFrame = ScrollableFrame(rootFrame, relief=tk.RIDGE)
        leftFrame.pack(side="left")
        # rightFrame
        rightFrame = ttk.Frame(rootFrame)
        rightFrame.pack(side="right")
        # entries["shape"]["paintings"], browseButtons["shape"]["paintings"]
        frames={}
        labels={}
        entries = {}
        browseButtons={}
        i=0
        leftInfoLabel = ttk.Label(leftFrame.scrollable_frame, text="          \"key\"                  up: \"title\", down: \"srcfile\" \n ",width=30, justify="center")
        leftInfoLabel.bind("<MouseWheel>", leftFrame.mouse_y_scroll)
        leftInfoLabel.grid(row = i, column = 0, sticky="ew")
        i += 1
        for s,p in PAINTINGS.items():
            frames[s]={}
            labels[s] = {}
            entries[s] = {}
            browseButtons[s] = {}
            labels[s]["shape"]= ttk.Label(leftFrame.scrollable_frame,text=("  "+s+"  ").center(50,"~"), font=(None, 9, "bold"), anchor="center")
            labels[s]["shape"].bind("<MouseWheel>", leftFrame.mouse_y_scroll)

            labels[s]["shape"].grid(row = i, column = 0,sticky="ew")
            i += 1

            for k,v in p.items():
                entries[s][k] = {}

                frames[s][k] = ttk.Frame(leftFrame.scrollable_frame)
                frames[s][k].bind("<MouseWheel>", leftFrame.mouse_y_scroll)
                frames[s][k].grid(row = i, column = 0, pady=5)

                labels[s][k] = ttk.Label(frames[s][k],text=k,width=13, font=("Arial", 9), anchor="center")
                entries[s][k]["title"] = ttk.Entry(frames[s][k], textvariable=self.strings[s][k]["title"],  width = 35)
                entries[s][k]["srcfile"] = ttk.Entry(frames[s][k], textvariable=self.strings[s][k]["srcfile"],  width = 35)
                browseButtons[s][k] = ttk.Button(frames[s][k],text="Browse",width=9,command=self.browse(self.strings[s][k]["srcfile"]))
                labels[s][k].bind("<MouseWheel>", leftFrame.mouse_y_scroll)
                entries[s][k]["title"].bind("<MouseWheel>", leftFrame.mouse_y_scroll)
                entries[s][k]["srcfile"].bind("<MouseWheel>", leftFrame.mouse_y_scroll)
                browseButtons[s][k].bind("<MouseWheel>", leftFrame.mouse_y_scroll)

                labels[s][k].grid(row = 0, column = 0, rowspan=2, sticky="ew")
                entries[s][k]["title"].grid(row = 0, column = 1)
                browseButtons[s][k].grid(row = 0, column = 2)
                entries[s][k]["srcfile"].grid(row = 1, column = 1, columnspan=2,sticky="ew")
                i += 1

        # createButton
        createButton = ttk.Button(rightFrame,text="Done",width=15,command=self.create_pack)
        createButton.pack(side="bottom", pady=10)
        # resetButton
        resetButton = ttk.Button(rightFrame,text="Reset",width=15,command=self.reset_entries)
        resetButton.pack(side="bottom", pady=10)
        # vanillaButton
        vanillaButton = ttk.Button(rightFrame,text="Vanilla",width=15,command=self.vanilla_entries)
        vanillaButton.pack(side="bottom", pady=10)
        # infoLabel
        rightInfoLabel = ttk.Label(rightFrame, text=" When \"title\" or \"srcfile\" is empty,\nuse vanilla titles and images.",width=30,justify="center")
        rightInfoLabel.pack(side="top", pady=15)

      
    def __init__(self):

        self.root_window = self.window(title="paintingChanger setup",width=600,height=300, iconpath=p_icon)
        self.root_window.resizable (False, False) 
        
        self.make_string_var()
        self.load_config()
        self.layout()
        self.reset_entries()
        self.root_window.mainloop()


# ----------------------------------
if __name__ == "__main__":
    App()
else:
    print("this script nust be used only as main-script")