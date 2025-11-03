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
    JARS = 2

def main(page: ft.Page):
    page.title = "Minecraft darkmodeUI Pack Generator"  # タイトル
    page.theme = ft.Theme(color_scheme_seed="light_blue")  # テーマカラー
    page.theme_mode = ft.ThemeMode.DARK  # ダークモード

    ## layout values
    page.window.width = 650  # 幅
    page.window.height = 500  # 高さ
    page.padding = 20  # パディング
    # page.scroll = ft.ScrollMode.AUTO  # スクロールモード
    left_w = 200  # ラベルの幅
    right_w = 350  # 値の幅
    jar_input_w = 500  # JARファイルの入力フィールドの幅


    ### state
    pagestate = {
        "version": "1.21.8", 
        "outpath": "",
        "mcdir": "",
        "jars": [] 
    }  # 入力値の状態(初期値)
    pickerstate = {
        "mode": PickerMode.OUT,
        "index": 0
    }  # ファイルピッカーの状態

    ### actions
    # inputs
    def on_change_version(e):
        button_generate.disabled = not e.control.value.strip()  # 入力が空でない場合は有効
        pagestate["version"] = e.control.value.strip()  # 入力値を更新
        button_generate.update()
        # page.update()
    def on_change_mcdir(e): 
        pagestate["mcdir"] = e.control.value.strip()

    def on_change_jar(e, i:int):
        pagestate["jars"][i] = e.control.value.strip()  # 入力値を更新
        input_list_jars.update()  # 入力値を更新

    # buttons
    def on_click_mcdir_pick(e):
        pickerstate["mode"] = PickerMode.MCDIR
        picker.get_directory_path(initial_directory=pagestate["mcdir"] if pagestate["mcdir"] else libs.get_default_mc_dir())
        # page.update()
    def on_click_generate(e): 
        pickerstate["mode"] = PickerMode.OUT
        picker.save_file(file_type=ft.FilePickerFileType.CUSTOM, file_name=consts.DEFAULT_PACK_NAME % pagestate["version"], allowed_extensions=["jar"])
    def on_click_cancel(e): 
        page.window.close()
    
    def on_click_jar_pick(e, i:int):
        pickerstate["mode"] = PickerMode.JARS
        pickerstate["index"] = i
        picker.pick_files(
            initial_directory=pagestate["jars"][i] if pagestate["jars"][i] else None,
            allowed_extensions=["jar"]
        )
    def on_click_add_jar(e):
        pagestate["jars"].append("")
        update_jar_inputs()
    def on_click_remove_jar(e, i:int):
        pagestate["jars"].pop(i)
        update_jar_inputs()

    def _on_click_dialogOK(e):
        dialog.open = False
        dialog.update()
    
    ### picker
    def on_picker_result(e: ft.FilePickerResultEvent):
        if e.control.data["mode"] == PickerMode.OUT:
            if not e.path: return
            pagestate["outpath"] = e.path
            if pagestate["version"].strip() == "" or pagestate["outpath"].strip() == "" : return
            # loading open
            dialog.open = True  # ダイアログを開く
            dialog.title = None  # ダイアログのタイトル
            dialog.content = ft.Row([ ft.ProgressRing(), ft.Text("Generating...")], alignment=ft.MainAxisAlignment.SPACE_AROUND)  # 結果をダイアログに表示
            dialog.actions = None  # ボタンはなし
            dialog.update()
            res = generate.generate(
                mc_ver=pagestate["version"],
                output_jar_path=pagestate["outpath"] if pagestate["outpath"] != "" else None,
                minecraft_dir_path=pagestate["mcdir"] if pagestate["mcdir"] != "" else None,
                package_jar_paths=pagestate["jars"] 
            )  # 引数を渡して生成
            dialog.title = "Result: successed" if res[0] else "Result: failed"  # ダイアログのタイトル
            dialog.content = ft.Text(res[1])  # 結果をダイアログに表示
            dialog.actions = [ft.TextButton("OK", on_click=_on_click_dialogOK)]  # OKボタンを追加
            dialog.update()

        elif e.control.data["mode"] == PickerMode.MCDIR:
            if not e.path: return
            pagestate["mcdir"] = e.path
            input_mcdir.value = pagestate["mcdir"]
            input_mcdir.update()
        
        elif e.control.data["mode"] == PickerMode.JARS:
            if not e.files: return
            i = e.control.data["index"]
            pagestate["jars"][i] = e.files[0].path
            update_jar_inputs()


    ### Inputs
    input_version = ft.TextField(hint_text="1.20.1", width=right_w, hint_style=ft.TextStyle(color=ft.Colors.WHITE38), on_change=on_change_version, value=pagestate["version"])
    input_mcdir = ft.TextField(hint_text="%AppData%\\.minecraft", hint_style=ft.TextStyle(color=ft.Colors.WHITE38), on_change=on_change_mcdir, value=pagestate["mcdir"])
    input_list_jars = ft.Column([
        ft.Text("Minecraft Jar Files (Optional):", width=left_w),
        ft.Column([], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, scroll=ft.ScrollMode.AUTO, height=150),
    ]) # update_jar_inputs で更新される入力フィールドのリスト
    ### buttons
    button_pick_mcdir = ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=on_click_mcdir_pick)
    button_cancel = ft.ElevatedButton("Cancel", on_click=on_click_cancel)
    button_generate = ft.ElevatedButton("Generate!", on_click=on_click_generate, disabled=False)
    ### overlays
    picker = ft.FilePicker(on_result=on_picker_result, data=pickerstate)
    dialog = ft.AlertDialog(title=None, content=ft.Text(""), actions=None, modal=True, ) # modal:閉じれないように

    
    def update_jar_inputs():
        input_list_jars.controls = [
            ft.Text("Minecraft Jar Files (Optional):", width=left_w),
            ft.Column(
                [ft.Row([
                    ft.TextField(hint_text="path_to_jar",hint_style=ft.TextStyle(color=ft.Colors.WHITE38), on_change=lambda e: on_change_jar(e, i), value=os.path.basename(jar), width=jar_input_w),
                    ft.IconButton(ft.Icons.FILE_OPEN, on_click=lambda e, i=i: on_click_jar_pick(e, i), tooltip="Add another inputfield"),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, i=i: on_click_remove_jar(e, i), tooltip="Remove this inputfield"),
                ]) for i, jar in enumerate(pagestate["jars"])],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                scroll=ft.ScrollMode.AUTO,
                height=150
            ),
        ]
        input_list_jars.update()


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
                input_list_jars,
                ft.Row(
                    [ 
                        ft.IconButton(ft.Icons.ADD, on_click=on_click_add_jar, tooltip="Add another inputfield"),
                        ft.Row([button_cancel, button_generate], alignment=ft.MainAxisAlignment.END),
                    ], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    height=50
                ),
            ]
        )
    )



ft.app(target=main)