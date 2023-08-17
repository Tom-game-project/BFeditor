import tkinter as tk

def immutable():
    checkbutton.configure(
        state="disabled"
    )
def mmutable():
    checkbutton.configure(
        state="normal"
    )

root = tk.Tk()
root.title("Immutable Checkbutton")

# Checkbuttonを作成し、初期状態を選択しない（disabled）に設定
checkbutton = tk.Checkbutton(root, text="これはチェックボックスです")
checkbutton.pack()

# ボタンを作成し、チェックボックスの状態を切り替える関数を関連付け
toggle_button0 = tk.Button(root, text="immutable", command=immutable)
toggle_button0.pack()
toggle_button1 = tk.Button(root, text="mutable", command=mmutable)
toggle_button1.pack()


root.mainloop()