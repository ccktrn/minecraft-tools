# --  Minecraft >= 1.20.1   -- 
# 元のdescriptionの場所->newTitle,元のitemnameの場所->keyname(ex.graham)(固定),ファイル参照してcopy&rename
# config.jsonからinitialを取得可能,　defaultに戻すボタンあり

# ToDo >> タイトルを指定するか,titleエントリ無効化してファイル名で自動補完か,選択できるcheckbox

import os
import sys
import time
from pathlib import Path # path tool
import shutil # file tool
import tkinter as tk # gui tool
from tkinter import ttk #better tk
from tkinter import filedialog as fd # ファイル参照機能
import json
import subprocess # ffmpeg実行用

from const import RECORDS,VOLUME

def bundle_path()->Path:
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)/'bundle' # exe-> LocalTempの一時フォルダ(_MEI*****)内にできる"bundle"ディレクトリ
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
p_sounds = p_root/'assets/minecraft/sounds.json'
p_records = p_root/'assets/minecraft/sounds/records'

p_config =  filedir_path()/'config.json'


# -----------------------------------
class ScrollableFrame(ttk.Frame):

    def __init__(self, container):
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
            for k,v in RECORDS.items(): 
                self.config[k] = {
                    "title":v,
                    "srcfile":'' # エントリの初期値用の値
                }
            print(f"\"{p_config.name}\" is not found. recreated.")
        return self.config

    def copy_ogg(self):
        for k,v in self.strings.items():
            p_dst = p_records/(k+'.ogg')
            try:
                p_src = Path(v["srcfile"].get())
                if p_src.exists() and p_src!=Path(""):
                    res = self.conv_audio(p_src, p_dst)
                    if res.returncode :
                        tk.messagebox.showerror("error",f"ffmpeg.exe ends with code{res.returncode}. <<{k},{p_src}")
                else:
                    if p_dst.exists():
                        os.remove(p_dst)
            except Exception as e:
                tk.messagebox.showerror("error",e)

    def conv_audio(self,src,dst): 
        p_exe = bundle_path()/"bin/ffmpeg.exe"
        cmd = f"{p_exe} -y -i \"{str(src)}\" \"{str(dst)}\""
        return subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW )
    
    def dump_config(self):
        conf:dict={}
        for k,v in self.strings.items():
            conf[k]={}
            conf[k]["title"]= v["title"].get()
            conf[k]["srcfile"]= v["srcfile"].get()
        with open(p_config, 'w', encoding="utf_8") as f : #json出力
            json.dump(conf, f, indent="\t",ensure_ascii=False)
        

    def dump_lang(self):
        lang:dict = {}
        for k,v in self.strings.items():
            lang["item.minecraft.music_disc_"+k] = "\u00a77"+k
            lang["item.minecraft.music_disc_"+k+".desc"] = "\u00a7e"+v["title"].get()
        with open(p_lang, 'w', encoding="utf_8") as f : #json出力
            json.dump(lang, f, indent="\t",ensure_ascii=False)

    def dump_sounds(self):
        sounds:dict = {}
        for k,v in self.strings.items():
            sounds["music_disc."+k] = {
                "replace": True,
                "sounds": [
                    {
                        "name": "records/"+k,
                        "volume": VOLUME,
                        "stream": True
                    }
                ]
            }
        with open(p_sounds, 'w', encoding="utf_8") as f : #json出力
            json.dump(sounds, f, indent="\t",ensure_ascii=False)
    
        
    # GUI 関連 ----------

    def make_string_var(self) -> dict: # entriesの値操作用
        self.strings={}
        for k,v in RECORDS.items():
            self.strings[k] = {}
            self.strings[k]["title"] = tk.StringVar()
            self.strings[k]["srcfile"] = tk.StringVar()
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
                ("audio file ", "*.ogg;*.mp3;*.wav"),
                ("ogg file ", "*.ogg"),
                ("mp3 file ", "*.mp3"),
                ("wav file ", "*.wav")
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
            initialfile="recordChanger",
            defaultextension=""
        ))
        if p_zip.name : # 指定されたか否か
            self.dump_config()
            self.dump_lang()
            self.dump_sounds()
            self.copy_ogg()
            shutil.make_archive(p_zip.parent/p_zip.stem, format='zip', root_dir=p_root)
            print("create")
            tk.messagebox.showinfo("info", f"resource-pack was created in\n{p_zip}")
            

    def reset_entries(self): #self.configでセット
        for k,v in RECORDS.items():
            try:
                self.strings[k]["title"].set(self.config[k]["title"])   
            except KeyError as e: # self.configに存在しない
                self.strings[k]["title"].set("")
            try:
                self.strings[k]["srcfile"].set(self.config[k]["srcfile"])
            except KeyError as e: # self.configに存在しない
                self.strings[k]["srcfile"].set("")
                    
    def vanilla_entries(self): #RECORDSをもとにセット
        for k,v in RECORDS.items():
            try:
                self.strings[k]["title"].set(RECORDS[k])   
            except KeyError as e: # RECORDSに存在しない(プログラムエラー)
                self.strings[k]["title"].set("プログラムエラー")
            self.strings[k]["srcfile"].set("")

    # layout
    def layout(self):
        # rootFrame
        rootFrame = ttk.Frame(self.root_window)
        rootFrame.pack(expand=True)
        # leftFrame (scrollable) 
        leftFrame = ScrollableFrame(rootFrame)
        leftFrame.pack(side="left")
        # rightFrame
        rightFrame = ttk.Frame(rootFrame)
        rightFrame.pack(side="right")
        # entries["shape"]["paintings"], browseButtons["shape"]["paintings"]
        frames={}
        labels={}
        entries={}
        browseButtons={}
        i=0
        leftInfoLabel = ttk.Label(leftFrame.scrollable_frame, text="          \"key\"                  up: \"title\", down: \"srcfile\" \n ",width=30, justify="center")
        leftInfoLabel.bind("<MouseWheel>", leftFrame.mouse_y_scroll)
        leftInfoLabel.grid(row = i, column = 0, sticky="ew")
        i += 1
        for k,v in RECORDS.items():
            entries[k] = {}
            frames[k] = ttk.Frame(leftFrame.scrollable_frame)
            frames[k].bind("<MouseWheel>", leftFrame.mouse_y_scroll)
            frames[k].grid(row = i, column = 0, pady=5)

            labels[k] = ttk.Label(frames[k],text=k,width=13, font=("Arial", 9), anchor="center")
            entries[k]["title"] = ttk.Entry(frames[k], textvariable=self.strings[k]["title"],  width = 35)
            entries[k]["srcfile"] = ttk.Entry(frames[k], textvariable=self.strings[k]["srcfile"],  width = 35)
            browseButtons[k] = ttk.Button(frames[k],text="Browse",width=9,command=self.browse(self.strings[k]["srcfile"]))
            labels[k].bind("<MouseWheel>", leftFrame.mouse_y_scroll)
            entries[k]["title"].bind("<MouseWheel>", leftFrame.mouse_y_scroll)
            entries[k]["srcfile"].bind("<MouseWheel>", leftFrame.mouse_y_scroll)
            browseButtons[k].bind("<MouseWheel>", leftFrame.mouse_y_scroll)

            labels[k].grid(row = 0, column = 0, rowspan=2, sticky="ew")
            entries[k]["title"].grid(row = 0, column = 1)
            browseButtons[k].grid(row = 0, column = 2)
            entries[k]["srcfile"].grid(row = 1, column = 1, columnspan=2,sticky="ew")
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
        rightInfoLabel = ttk.Label(rightFrame, text=" When \"title\" or \"srcfile\" is empty,\nuse vanilla titles and musics.",width=30,justify="center")
        rightInfoLabel.pack(side="top", pady=15)

      
    def __init__(self):

        self.root_window = self.window(title="recordChanger setup",width=600,height=300, iconpath=p_icon)
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