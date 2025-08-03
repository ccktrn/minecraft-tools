# Flet UI
import flet as ft
import os
import generate 
from enum import Enum

import module.consts as consts
import module.libs as libs


class PickerMode(Enum):
    OUT = 0
    MCDIR = 1

def main(page: ft.Page):
    page.title = "Minecraft darkmodeUI Pack Generator"  # タイトル
    page.theme = ft.Theme(color_scheme_seed="light_blue")  # テーマカラー
    page.theme_mode = ft.ThemeMode.DARK  # ダークモード

    ## layout values
    page.window.width = 650  # 幅
    page.window.height = 300  # 高さ
    page.padding = 20  # パディング
    # page.scroll = ft.ScrollMode.AUTO  # スクロールモード
    left_w = 200  # ラベルの幅
    right_w = 350  # 値の幅


    ### state
    pagestate = {"version": "", "outpath": "", "mcdir": ""}  # 入力値の状態
    pickerstate = {"mode": PickerMode.OUT}  # ファイルピッカーの状態

    ### actions
    # inputs
    def on_change_version(e):
        button_generate.disabled = not e.control.value.strip()  # 入力が空でない場合は有効
        pagestate["version"] = e.control.value.strip()  # 入力値を更新
        button_generate.update()
        # page.update()
    def on_change_mcdir(e): 
        pagestate["mcdir"] = e.control.value.strip()
    # buttons
    def on_click_mcdir_pick(e):
        pickerstate["mode"] = PickerMode.MCDIR
        picker.get_directory_path(initial_directory=pagestate["mcdir"] if pagestate["mcdir"] else libs.get_default_mc_dir())
        # page.update()
    def on_click_generate(e): 
        pickerstate["mode"] = PickerMode.OUT
        picker.save_file(file_type=ft.FilePickerFileType.CUSTOM, file_name=consts.DEFAULT_PACK_NAME % pagestate["version"], allowed_extensions=["zip"])
    def on_click_cancel(e): 
        page.window.close()


    def _on_click_dialogOK(e):
        dialog.open = False
        dialog.update()
    
    ### picker
    def on_picker_result(e: ft.FilePickerResultEvent):
        if not e.path: return
         
        if e.control.data["mode"] == PickerMode.OUT:
            pagestate["outpath"] = e.path
            if pagestate["version"].strip() == "" or pagestate["outpath"].strip() == "" : return
            arg = ["generate.py", pagestate["version"], pagestate["outpath"]]
            if not pagestate["mcdir"].strip() == "":
                arg.append(pagestate["mcdir"]) 
            print(f"Generating with args: {arg}")
            # loading open
            dialog.open = True  # ダイアログを開く
            dialog.title = None  # ダイアログのタイトル
            dialog.content = ft.Row([ ft.ProgressRing(), ft.Text("Generating...")], alignment=ft.MainAxisAlignment.SPACE_AROUND)  # 結果をダイアログに表示
            dialog.actions = None  # ボタンはなし
            dialog.update()
            res = generate.generate(arg)  # 引数を渡して生成
            dialog.title = "Result: successed" if res[0] else "Result: failed"  # ダイアログのタイトル
            dialog.content = ft.Text(res[1])  # 結果をダイアログに表示
            dialog.actions = [ft.TextButton("OK", on_click=_on_click_dialogOK)]  # OKボタンを追加
            dialog.update()

        elif e.control.data["mode"] == PickerMode.MCDIR:
            pagestate["mcdir"] = e.path
            input_mcdir.value = pagestate["mcdir"]
            input_mcdir.update()

    ### Inputs
    input_version = ft.TextField(hint_text="1.20.1", width=right_w, hint_style=ft.TextStyle(color=ft.Colors.WHITE38), on_change=on_change_version, value=pagestate["version"])
    input_mcdir = ft.TextField(hint_text="%AppData%\\.minecraft", hint_style=ft.TextStyle(color=ft.Colors.WHITE38), on_change=on_change_mcdir, value=pagestate["mcdir"])
    ### buttons
    button_pick_mcdir = ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=on_click_mcdir_pick)
    button_cancel = ft.ElevatedButton("Cancel", on_click=on_click_cancel)
    button_generate = ft.ElevatedButton("Generate!", on_click=on_click_generate, disabled=True)
    ### overlays
    picker = ft.FilePicker(on_result=on_picker_result, data=pickerstate)
    dialog = ft.AlertDialog(title=None, content=ft.Text(""), actions=None, modal=True, ) # modal:閉じれないように

    ### layout
    page.overlay.append(picker)  # オーバーレイにファイルピッカーを追加
    page.overlay.append(dialog)  # オーバーレイにダイアログを追加
    page.add(
        ft.Column(
            [
                ft.Text("Select Target Version. if you need, select also .minecraft directory", style=ft.TextStyle(weight=ft.FontWeight.BOLD), text_align=ft.TextAlign.CENTER, height=50),
                ft.Row(
                    [ ft.Text("Minecraft Version (Required):", width=left_w), ft.Row([input_version], width=right_w) ], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [ ft.Text("Minecraft Directory (Optional):", width=left_w), ft.Row([input_mcdir, button_pick_mcdir], width=right_w) ], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [ button_cancel, button_generate ], 
                    alignment=ft.MainAxisAlignment.END,
                    height=50
                ),
            ]
        )
    )


ft.app(target=main)