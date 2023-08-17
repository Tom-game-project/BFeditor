import tkinter as tk

def on_radio_button_selected():
    selected_option = selected_option_var.get()
    print(f"選択されたオプション: {selected_option}")

# tkinterウィンドウの作成
root = tk.Tk()
root.title("ラジオボタン")

# 選択されたオプションを保持するための変数
selected_option_var = tk.StringVar()

# ラジオボタンのオプションを定義
options = ["bin", "decimal", "hex"]

# ラジオボタンを作成して配置
for option in options:
    tk.Radiobutton(
        root,
        text=option,
        variable=selected_option_var,
        value=option, command=on_radio_button_selected).pack(anchor=tk.W)
selected_option_var.set("オプション2")
# ウィンドウを表示
root.mainloop()
