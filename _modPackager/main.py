# --  Minecraft >= 1.20.1   -- 
# [Todo] download jars from url

import os, sys, time, copy
from pathlib import Path # path tool
import shutil # file tool
import tkinter as tk # gui tool
from tkinter import ttk #better tk
from tkinter import filedialog as fd # file dialog
import json

# my const
import const as cs


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
p_root = bundle_path()/'mod_root'
p_jars = p_root/'jars'
p_fmod = p_root/'fabric.mod.json'

p_conf = filedir_path()/'config.json'




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

    
    def init_vars(self) -> dict: # 値保持用変数初期化 with config
        self.vars = {
            "id": tk.StringVar(value=self.config["id"]), # modid
            "name": tk.StringVar(value=self.config["name"]), # modname
            "version": tk.StringVar(value=self.config["version"]), # modversion
            "description": tk.StringVar(value=self.config["description"]), # description
            "jars" : [ #jar files
                tk.StringVar(value=path) for path in self.config["jars"]
            ],

            # 表示用

            "n_jars": tk.StringVar(), # jarファイルの数

        }

    # 各種処理
    def load_config(self) -> dict: 
        self.config:dict  = {} # 辞書型オブジェクト
        try:     
            with open(p_conf, 'r' , encoding="utf_8") as f : # jsonの読込
                self.config = json.load(f)
        except FileNotFoundError as e: #jsonファイルが存在しない
            self.config = {
                "id": "mod-package", # modid
                "name": "mod package", # modname
                "version": "0.1.1", # modversion
                
                "description": "description for mod package", # description

                "jars" : [ # jarファイル群
                    "/path/to/modfile.jar",
                ]
            }
            print(f"\"{p_conf.name}\" is not found. it will recreated when packaging mod jars.")
        return self.config

    # def copy_png(self):
    #     for s,p in self.var_jars.items():
    #         for k,v in p.items():
    #             p_dst = p_painting/(k+'.png')
    #             try:
    #                 p_src = Path(v["srcfile"].get())
    #                 res = self.conv_image(p_src, p_dst)
    #             except (PermissionError) as e:#srcfileが空欄または無効な値
    #                 if p_dst.exists():
    #                     os.remove(p_dst)
    
    # def conv_image(self,src,dst):
    #     # ほんとはちゃんと変換するべきなのだろうが、めんどいのでパス
    #         # srctype = src.suffix()
    #         # dsttype = dst.suffix()
    #     return shutil.copy(src,dst)
        
    
    def dump_config(self):
        self.config = {
            "id": self.vars["id"].get(), # modid
            "name": self.vars["name"].get(), # modname
            "version": self.vars["version"].get(), # modversion
            
            "description": self.vars["description"].get(), # description

            "jars" : [var.get() for var in self.vars["jars"] ] 
        }

        with open(p_conf, 'w', encoding="utf_8") as f : #json出力
            json.dump(self.config, f, indent="\t",ensure_ascii=False)
        print("create config file.")

    # 
        
    ######### GUI 関連 #########


        
    def window(self,title:str = "app", iconpath=None ,width:int = 600, height:int = 300) -> tk.Tk:
        app = tk.Tk() #Tkオブジェクト生成
        app.title(title) #GUIのタイトル名の決定
        if Path.exists(iconpath):
            app.iconbitmap(iconpath) # window-icon
        x,y = (0,0)
        app.geometry(f"{width}x{height}+{x}+{y}") #画面の大きさ,位置の決定
        print(f"window created : \"{title}\" with {width}x{height}")
        return app

    ## ButtonFuncs

    def click_browse(self,var, type:str="jar"): #ファイル参照
        def inner():
            iFilePath = fd.askopenfilename(
                filetype = cs.fTypes[type], 
                initialdir = None
              )
            if Path(iFilePath).is_file():
                var.set(iFilePath) 
        return inner
    
    def click_add(self,): # エントリ追加
        def inner():
            if len(self.ids_unused)==0: self.vars["jars"].append( tk.StringVar())
            self.layout_add_jarlist()
            self.layout_update_jarlist()
        return inner

    def click_remove(self, id): # エントリ削除
        def inner ():
            if len(self.ids) == 1 : return # 一つ以下にはしない
            self.vars["jars"][id].set("")
            self.layout_remove_jarlist(id)
            self.layout_update_jarlist()
        return inner
    
    def click_confirm(self):
        def inner():
            print("confirm")
            self.dump_config()
        return inner

    def click_cancel(self):
        def inner():
            print("cansel")
        return inner
    
    def click_reset(self):
        def inner():
            print("reset")
        return inner

    # def create_pack(self): # execute packaging
    #     p_zip = Path(fd.asksaveasfilename(
    #         title="Save as", 
    #         filetypes=cs.fTypes["jar"], 
    #         initialdir=filedir_path(), 
    #         initialfile="myModPack",
    #         defaultextension=""
    #     ))
    #     if p_zip.name : # 指定されたか否か
    #         try:
    #             self.initialize()
    #             shutil.make_archive(p_zip.parent/p_zip.stem, format='zip', root_dir=p_root)
    #             print("create")
    #             tk.messagebox.showinfo("info", f"resource-pack was created in\n{p_zip}")
    #         except Exception as e:
    #             print(e)
    #             tk.messagebox.showerror("error",e)



    ## layout
    
    def layout_baseinfo(self) : # RIGHT 
        topframe = ttk.Frame(self.rightFrame, width=10)
        topframe.pack(ipadx=5,ipady=5, side='top')
        bottomframe = ttk.Frame(self.rightFrame, width=10)
        bottomframe.pack(ipadx=5,ipady=5, side='bottom')

        for i, [key,size] in enumerate(cs.baseInfo.items()) :
            label = ttk.Label(topframe, text=key,width=13, font=("Arial", 9), anchor="center")
            label.grid(row = i, column = 0, columnspan=1,sticky="ew")
            entry = ttk.Entry(topframe, textvariable=self.vars[key],  width = 35)
            entry.grid(row = i, column = 1, rowspan=size, columnspan=3, sticky="ew")
        
        button_cancel = ttk.Button(bottomframe, text="cancel", command=self.click_cancel(), width=10)
        button_cancel.grid(row = 0, column = 0, columnspan=1,sticky="ew")
        button_reset = ttk.Button(bottomframe, text="reset", command=self.click_reset(), width=10)
        button_reset.grid(row = 0, column = 1, columnspan=1,sticky="ew")
        button_confirm = ttk.Button(bottomframe, text="confirm", command=self.click_confirm(), width=10)
        button_confirm.grid(row = 0, column = 2, columnspan=1,sticky="ew")

    def layout_jarslist(self) : # LEFT
        topframe = ttk.Frame(self.leftFrame, width=10)
        topframe.pack(ipadx=5,ipady=5, side='top')
        self.scrollrootFrame = ScrollableFrame(self.leftFrame, relief=tk.SUNKEN)
        self.scrollrootFrame.pack(ipadx=5, ipady=5, side='bottom')

        label = ttk.Label(topframe, textvariable=self.vars["n_jars"] ,width=20)    
        label.grid(row = 0, column = 0, columnspan=1,sticky="ew")    

        # jars list
        self.scrollFrame = ttk.Frame(self.scrollrootFrame.scrollable_frame)
        self.scrollFrame.bind("<MouseWheel>", self.scrollrootFrame.mouse_y_scroll)
        self.scrollFrame.pack(padx=5, pady=5)

        # layout manager
        self.ids=[] # ids[a] = b ... a番目にwidgetlist[b] を配置
        self.ids_unused=[] # add用未使用idリスト
        # jarlist widget
        self.jarlistFrames = []
        self.jarlistEntries = []
        self.jarlistBrowse = []  # browse Button
        self.jarlistRemove = [] # removeEntry Button

        self.addButton = ttk.Button(self.scrollFrame, text="add Entry", width=20)    
        self.addButton.bind("<MouseWheel>", self.scrollrootFrame.mouse_y_scroll)

        for i in range(len(self.vars["jars"])) :
            self.layout_add_jarlist()
        self.layout_update_jarlist()



    def layout_update_jarlist(self): # remap widgets
        for id in self.ids:
            self.jarlistFrames[id].pack(ipady=5)
            self.jarlistEntries[id].grid(row = 0, column = 0, columnspan=5,sticky="ew")
            self.jarlistBrowse[id].grid(row = 1, column = 1, columnspan=4,sticky="ew")
            self.jarlistRemove[id].grid(row = 1, column = 0, columnspan=1,sticky="ew")
        
        self.addButton.configure(command=self.click_add())
        self.addButton.pack(ipady=5, side='bottom')

        self.vars["n_jars"].set(f"Packaging {len(self.ids)} jar files ...")


    def layout_add_jarlist(self):
        try:
            id = self.ids_unused.pop(0) # add position
            flg = True
        except:
            id = len(self.ids) 
            flg = False

        frame = ttk.Frame(self.scrollFrame)    
        frame.bind("<MouseWheel>", self.scrollrootFrame.mouse_y_scroll)

        entry = ttk.Entry(frame, textvariable=self.vars["jars"][id], width=60)    
        entry.bind("<MouseWheel>", self.scrollrootFrame.mouse_y_scroll)
        browse = ttk.Button(frame, text="browse", command=self.click_browse(self.vars["jars"][id], type="jar"), width=10)    
        browse.bind("<MouseWheel>", self.scrollrootFrame.mouse_y_scroll)
        remove = ttk.Button(frame, text="remove", command=self.click_remove(id), width=5)    
        remove.bind("<MouseWheel>", self.scrollrootFrame.mouse_y_scroll)
        
        if flg :
            self.jarlistFrames[id] = frame ##
            self.jarlistEntries[id] = entry ##
            self.jarlistBrowse[id] = browse ##
            self.jarlistRemove[id] = remove ##
        else: 
            self.jarlistFrames.append( frame) ##
            self.jarlistEntries.append(entry) ##
            self.jarlistBrowse.append(browse) ##
            self.jarlistRemove.append(remove) ##

        # layout manager
        self.ids.append(id)


    def layout_remove_jarlist(self, id):
        self.jarlistEntries[id].destroy()
        self.jarlistBrowse[id].destroy()
        self.jarlistRemove[id].destroy()
        # self.jarlistEntries.pop(id) 
        # self.jarlistBrowse.pop(id) 
        # self.jarlistRemove.pop(id) 
        self.jarlistFrames[id].destroy()
        # self.jarlistFrames.pop(id)


        # layout manager
        self.ids.remove(id)
        self.ids_unused.append(id)

    def layout(self):
        # rootFrame
        self.rootFrame = ttk.Frame(self.root_window)
        self.rootFrame.pack(expand=True)
        # leftFrame
        self.leftFrame = ttk.Frame(self.rootFrame)
        self.leftFrame.pack(side="left" ,expand=1)
        # rightFrame
        self.rightFrame = ttk.Frame(self.rootFrame)
        self.rightFrame.pack(side="right" ,expand=1)
        
        self.entries, self.labels, self.frames ,self.buttons = dict(), dict(), dict(), dict()
        # baseinfo
        self.layout_baseinfo()
        self.layout_jarslist()

      
    def __init__(self):

        self.root_window = self.window(title="modPackager",width=750,height=350, iconpath=p_icon)
        self.root_window.resizable (False, False) 
        
        self.load_config()
        self.init_vars()
        self.layout()
        self.root_window.mainloop()


# ----------------------------------
if __name__ == "__main__":
    App()
else:
    print("this script nust be used only as main-script")