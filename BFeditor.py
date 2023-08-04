"""
software:
name :BFeditor

"""

import tkinter as tk
from tkinter import filedialog,ttk,messagebox
import os
import hashlib #テキストが変更されたかどうかを確かめたい
from bf import BrainFuck
from enum import Enum

import webbrowser

class BFlags(Enum):
    INACTIVE:int = 0
    ACTIVE:int = 1


class BFeditor:
    def __init__(self) -> None:

        self.root = tk.Tk()
        self.root.title("BFeditor")
        self.root.geometry('600x500')

        #root.destroyをするさいの保存確認
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        #menubar
        self.menu_bar = tk.Menu()
        self.root.config(menu=self.menu_bar)

        #メニューに親メニュー（ファイル）を作成する
        self.menu_file = tk.Menu(self.root, tearoff=False)
        self.menu_bar.add_cascade(label='File', menu=self.menu_file)
        self.menu_file.add_command(label='Open', command=self.open_File)
        ## save ショートカットキーによる保存はraw_code_textでバインドで監視
        self.menu_file.add_command(label='Save', command=self.save_File)
        self.menu_file.add_command(label='Save As', command=self.save_as_File)
        self.menu_file.add_command(label='Close', command=self.root.destroy)
        #メニューに親メニュー（ファイル）を作成する
        self.menu_manage = tk.Menu(self.root, tearoff=False)
        self.menu_bar.add_cascade(label='Manage', menu=self.menu_manage)
        self.menu_manage.add_command(label='rule', command=self.open_rule_set_window)
        #メニューに親メニュー（ファイル）を作成する
        self.menu_help = tk.Menu(self.root, tearoff=False)
        self.menu_bar.add_cascade(label='Help', menu=self.menu_help)
        self.menu_help.add_command(label='ASCII code table', command=self.open_ascii_code_table)
        self.menu_help.add_command(label='See README.md on github', command=lambda :webbrowser.open("https://github.com/Tom-game-project/BFeditor"))


        # PanedWindowを作成
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.text_frame = ttk.Labelframe(self.paned_window,text="Editor")
        self.text_frame.grid_columnconfigure(0,weight=1)
        self.text_frame.grid_rowconfigure(0,weight=1)
        self.paned_window.add(self.text_frame)
        self.memory_frame = ttk.LabelFrame(self.paned_window,text="Memory")
        self.memory_frame.grid_columnconfigure(0,weight=1)
        self.memory_frame.grid_rowconfigure(0,weight=1)
        self.paned_window.add(self.memory_frame)
        self.code_frame = ttk.LabelFrame(self.paned_window,text="Code")
        self.code_frame.grid_columnconfigure(0,weight=1)
        self.code_frame.grid_rowconfigure(0,weight=1)
        self.paned_window.add(self.code_frame)
        self.operation_frame = ttk.LabelFrame(self.paned_window, text="operation")
        self.paned_window.add(self.operation_frame)
        self.output_frame = ttk.LabelFrame(self.paned_window,text="Output")
        self.paned_window.add(self.output_frame)

        # operation(オペレーションフレーム)
        self.operation_operation_frame = ttk.Frame(self.operation_frame)
        self.operation_operation_frame.grid(row=0,column=0)
        ## 実行スピード
        self.operation_executionspeed_frame = ttk.LabelFrame(self.operation_frame, text="execution speed")
        self.operation_executionspeed_frame.grid(row=0,column=1)
        ## 操作ボタン
        self.operation_RUN_button=ttk.Button(self.operation_operation_frame, text="RUN",command=self.run)
        self.operation_RUN_button.grid(row=0, column=0)
        self.operation_FORWARD=ttk.Button(self.operation_operation_frame,text="FORWARD",command=self.forward)
        self.operation_FORWARD.grid(row=0,column=1)
        self.operation_HALT_button=ttk.Button(self.operation_operation_frame, text="HALT", command=self.halted)
        self.operation_HALT_button.grid(row=0,column=2)
        self.operation_STEP_label = tk.Label(self.operation_operation_frame,text="Steps: 0")
        self.operation_STEP_label.grid(row=1,column=0,columnspan=2)
        self.operation_combox = ttk.Combobox(self.operation_executionspeed_frame, values=[str(i*10)+"ms" for i in range(10)]+[str(i*100)+"ms" for i in range(1,11)],state="readonly")
        # 最初実行速度は10msに設定する
        self.operation_combox.current(1)
        self.operation_combox.pack()
        self.operation_input_frame = ttk.LabelFrame(self.operation_frame,text="Input")
        self.operation_input_frame.grid(row=1,column=0,columnspan=2)
        
        #text_frame
        self.raw_code_text = tk.Text(self.text_frame, height=0, bg="black", fg="#24ff2b",insertbackground="white",insertwidth=5)
        #event設定
        self.raw_code_text.bind("<<TextModified>>", self.raw_code_text_on_modified)
        #保存のためのショートカットキー
        self.raw_code_text.bind("<Control-s>",self.save_File)
        # スクロールバーの作成
        self.text_scrollbar = tk.Scrollbar(
            self.text_frame, orient=tk.VERTICAL, command=self.raw_code_text.yview)
        # スクロールバーをListboxに反映
        self.raw_code_text["yscrollcommand"] = self.text_scrollbar.set
        # 各種ウィジェットの設置
        self.raw_code_text.grid(row=0, column=0,sticky=(tk.N, tk.S,tk.W,tk.E))
        self.text_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        #raw_code_textのポップアップの設定
        self.popup_menu = tk.Menu(self.raw_code_text,tearoff=False)
        self.popup_menu.add_command(label="Copy",command=self.clipboard_copy)
        self.popup_menu.add_command(label="Paste",command=self.clipboard_paste)
        self.raw_code_text.bind("<Button-3>",self.show_popup_menu)

        #memory_frame
        self.memory_text = tk.Text(self.memory_frame,height=0,wrap="none")
        # スクロールバーの作成
        self.memory_scrollbar_vertical = tk.Scrollbar(
            self.memory_frame, orient=tk.VERTICAL,
            command=self.memory_text.yview
            )
        # スクロールバーをListboxに反映
        self.memory_text["yscrollcommand"] = self.memory_scrollbar_vertical.set
        self.memory_scrollbar_horizontal = tk.Scrollbar(
            self.memory_frame, orient=tk.HORIZONTAL,
            command=self.raw_code_text.xview
            )
        self.memory_text["xscrollcommand"] = self.memory_scrollbar_horizontal.set
        # 各種ウィジェットの設置

        self.memory_text.configure(state="disabled")
        self.memory_text.grid(row=0,column=0,sticky=(tk.N, tk.S,tk.W,tk.E))
        self.memory_scrollbar_vertical.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.memory_scrollbar_horizontal.grid(row=1,column=0,sticky=(tk.E,tk.W))

        #code_frame
        self.code_text = tk.Text(self.code_frame,height=0)
        # スクロールバーの作成
        self.code_scrollbar = tk.Scrollbar(self.code_frame, orient=tk.VERTICAL, command=self.code_text.yview)
        # スクロールバーをListboxに反映
        self.code_text["yscrollcommand"] = self.code_scrollbar.set
        self.code_text.configure(state="disabled")
        self.code_text.grid(row=0,column=0,sticky=(tk.N,tk.S,tk.W,tk.E))
        self.code_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        #Input_frame
        self.input_text = tk.Text(self.operation_input_frame,height=5)
        self.input_text.grid(row=0,column=0)
        
        # スクロールバーの作成
        self.input_scrollbar = tk.Scrollbar(self.operation_input_frame, orient=tk.VERTICAL, command=self.input_text.yview)
        # スクロールバーをListboxに反映
        self.input_text["yscrollcommand"] = self.input_scrollbar.set
        self.input_text.grid(row=0,column=0)
        self.input_scrollbar.grid(row=0,column=1)
        #output_frame
        self.output_text = tk.Text(self.output_frame,height=5)
        # スクロールバーの作成
        self.output_scrollbar = tk.Scrollbar(self.output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        # スクロールバーをListboxに反映
        self.output_text["yscrollcommand"] = self.output_scrollbar.set
        self.output_text.configure(state="disabled")
        self.output_text.grid(row=0,column=0)
        self.output_scrollbar.grid(row=0,column=1)

        #設定ファイル
        """
        デフォルト設定
        memory size:100
        speed:10ms
        """
        self.text_length:int = 4
        self.row_length:int = 10

        #最初はfilenameが何も設定されていない状態にする
        """
        ファイル操作に必要なもの一式
        """
        self.filename:str = None
        self.saved:bool = True
        
        #process state 進捗状況->コードの実行状況を表す。デフォルトは
        self.process_state = BFlags.INACTIVE
        self.forward_flag:bool = False
        self.halt_bool:bool=False
        self.stoped_bool:bool = False
    #util
    def chunked(self,list_,chunk):
        return (list_[i:i+chunk] for i in range(0,chunk*(len(list_)//chunk)+1,chunk))
    def initialization(self):
        self.process_state = BFlags.ACTIVE
        self.halt_bool:bool=False
        if self.stoped_bool:
            self.operation_RUN_button.configure(text="RESUME",command=self.resume)
        else:
            self.operation_RUN_button.configure(text="STOP",command=self.stoped)
        self.input_text.configure(state="disabled")
        #brainfuckオブジェクトを生成する
        text = self.raw_code_text.get("1.0", tk.END)
        self.brain_fuck = BrainFuck(text)
        self.brain_fuck.set_input_stream(self.input_text.get("1.0",tk.END)[:-1])
        #codetext （コメントを抜いたテキストを作成する）
        self.code_text.configure(state="normal")
        self.code_text.delete("1.0",tk.END)
        self.code_text.insert("1.0",self.brain_fuck.code)
        self.code_text.configure(state="disabled")
        #outputのクリア
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0",tk.END)
        self.output_text.configure(state="disabled")
        #step表示初期化
        self.operation_STEP_label.configure(text="Steps: 0")
        #generatorの作成
        self.bf_generator=self.brain_fuck.run_generator()
        #memory textの初期化をする
        self.memory_init()
        self.code_highlight(0)
        self.memory_change(0,0)
    def process(self):
        i,j = next(self.bf_generator)
        self.memory_change(*self.brain_fuck.state())
        self.code_highlight(i)
        self.operation_show()
        self.output(j)
    def end(self):
        print("終了")
        self.process_state = BFlags.INACTIVE
        self.operation_RUN_button.configure(text="RUN",command=self.run)
        self.input_text.configure(state="normal")
    def loop(self):
        """
        描画処理をする
        """
        try:
            if self.stoped_bool:
                self.root.after_cancel(self.run_id)
            elif self.halt_bool:
                self.root.after_cancel(self.run_id)
            else:
                #止められてないとき
                self.process()
                self.root.after(int(self.operation_combox.get()[:-2]), self.loop)
        except StopIteration:
            self.end()
            self.root.after_cancel(self.run_id)
    def run(self):
        """
        run buttonが押されたら...
        """
        
        self.stoped_bool:bool = False
        self.initialization()
        #loopを開始する
        self.run_id = self.root.after(int(self.operation_combox.get()[:-2]), self.loop)
    def operation_show(self):
        self.operation_STEP_label.configure(text=f"Steps: {self.brain_fuck.step}")
    def output(self,obj):
        if obj !=None:
            self.output_text.configure(state="normal")
            self.output_text.insert(tk.END,obj)
            self.output_text.configure(state="disabled")
        else:
            pass
    def code_highlight(self,i):
        """
        次のステップで実行される処理をハイライトします。
        現時点でハイライトされている処理は次のステップでメモリやインプット、アウトプットに反映されます。
        """
        self.code_text.tag_delete("codehighlight")
        self.code_text.tag_add("codehighlight", f"1.{i}", f"1.{i+1}")
        self.code_text.tag_config("codehighlight", background="black", foreground="white")
    def memory_init(self):
        self.memory_text.configure(state="normal")
        self.memory_text.delete("1.0",tk.END)
        self.memory_text.configure(state="disabled")
        for i,j in enumerate(self.chunked(self.brain_fuck.memory,self.row_length)):
            self.memory_text.configure(state="normal")
            self.memory_text.insert(f"{i+1}.0"," ".join([str(k).rjust(self.text_length,"0") for k in j])+"\n")
            self.memory_text.configure(state="disabled")
    def memory_change(self,pointer,newdata):
        """
        メモリテキストの破壊的変更を防ぎ一部のみ変更するための関数
        セルサイズとうまく調整して合わせる
        どうじ
        """
        a,b=divmod(pointer,self.row_length)
        self.memory_text.configure(state="normal")
        start = f"{a+1}.{(self.text_length+1)*b}"
        end = f"{a+1}.{(self.text_length+1)*b+self.text_length}"
        self.memory_text.delete(start,end)
        self.memory_text.insert(start,str(newdata).rjust(self.text_length,"0"))
        self.memory_text.tag_delete("memoryhighlight")
        self.memory_text.tag_add("memoryhighlight",start,end)
        self.memory_text.tag_config("memoryhighlight", background="black", foreground="white")
        self.memory_text.configure(state="disabled")

    #mainloop
    def mainloop(self):
        self.root.mainloop()

    #trivial functions
    def title_filename_setter(self):
        """
        # title_filename
        ファイルネームが設定されているのか。はたまたそれが保存されているのかによって返すタイトル名が違います。
        windowsのテキストエディタのようなタイトル画面を再現し、保存されているのかそうでないのかをわかりやすくします。
        """
        splited_filename = os.path.split(self.filename)[-1]
        return "BFeditor" if splited_filename == None else f"{splited_filename} - Bfeditor" if self.saved else f"*{splited_filename} - BFeditor"
    #on some event
    def stoped(self):
        """
        # 一時停止する
        active状態は継続
        """
        #self.root.after_cancel(self.run_id)
        self.operation_RUN_button.configure(text="RESUME",command=self.resume)
        self.stoped_bool:bool= True
    def halted(self):
        """
        # プロセスを中断する
        """
        self.operation_RUN_button.configure(text="RUN",command=self.run)
        self.input_text.configure(state="normal")
        #self.root.after_cancel(self.run_id)
        self.process_state = BFlags.INACTIVE
        self.halt_bool = True
        self.operation_RUN_button.configure(text="RUN",command=self.run)
    def forward(self):
        """
        # 1プロセス進める
        """
        self.operation_RUN_button.configure(text="RESUME",command=self.resume)
        self.stoped_bool=True
        if self.process_state==BFlags.INACTIVE:
            self.initialization()
            #self.process()
        else:
            if self.stoped_bool:
                try:
                    self.process()
                except StopIteration:
                    self.end()
    def resume(self):
        """
        # プロセスの再開
        """
        self.operation_RUN_button.configure(text="STOP",command=self.stoped)
        self.stoped_bool:bool=False
        self.run_id = self.root.after(int(self.operation_combox.get()[:-2]), self.loop)
    def on_closing(self):
        """
        X buttonが押されウィンドウが閉じられようとしたとき。
        """
        if self.saved:#保存されている場合
            self.root.destroy()
        else:#保存が終わっている場合には終了する
            if self.filename is not None:#すでにファイルとして存在していて、そのファイルを上書き保存する場合
                r = messagebox.askyesnocancel(title="Bfeditor",message=f"Save changes to {os.path.split(self.filename)[-1]}?")
                match r:
                    case True:#上書き保存する
                        self.save_File()
                    case False:#現在書いてるcodeは保存しない
                        self.root.destroy()
                    case None:#そもそも閉じない
                        pass
                    case _:#絶対に生じないはず
                        raise BaseException("予期せぬエラー")
            else:#None
                r = messagebox.askokcancel(title="BFeditor",message=f"Changes are not saved\nSave changes?")
                match r:
                    case True:#初めての保存（名前を付けて保存）
                        self.save_as_File()
                    case False:#保存しない
                        self.root.destroy()
                    case None:
                        pass
                    case _:
                        raise BaseException("予期せぬエラー")
    def open_File(self):
        self.filename = filedialog.askopenfilename(
            title="open brainfuck file",
            filetypes=[("Brainfuck", ".b .bf .brainfuck")],  # ファイルフィルタ
            initialdir="./"  # 自分自身のディレクトリ
        )
        with open(self.filename,mode="r",encoding="utf-8")as f:
            self.raw_code_text.delete("1.0",tk.END)
            self.raw_code_text.insert("1.0",f.read())
            self.saved:bool = True
            self.root.title(self.title_filename_setter())
    def save_File(self,*_):
        """
        # 一般的な保存
        menu_barからのアクセス
        ショートカットキー
        ctrl + Sからのアクセスと両方可能
        """
        if self.filename == None:
            """
            # 名前を付けて保存
            もし、`self.filename`が`None`であるなら名前を付けて保存に変更する
            """
            self.save_as_File()
        else:
            """
            # 上書き保存
            """
            with open(self.filename,mode="w",encoding="utf-8")as f:
                f.write(self.raw_code_text.get("1.0",tk.END))
                self.saved:bool=True
                self.root.title(self.title_filename_setter())
    def save_as_File(self):
        """
        # 名前を付けて保存
        `self.filename`が`None`でない場合でも名前を付けて保存をすることは可能
        """
        with filedialog.asksaveasfile(mode="w",filetypes=[("bf file","*.b"),("bf file","*.bf")],defaultextension=".b") as f:
            f.write(self.raw_code_text.get("1.0",tk.END))
            self.saved:bool=True
            self.filename:str = f.name
            self.root.title(self.title_filename_setter())
    def raw_code_text_on_modified(self,e):
        """
        工事中、onmodifiedは最初から実装されていないので自分で実装する必要がある。前回と比較して、変更されたか否かのみが知りたい。hashを比較することによって変更されたか否かの情報のみを取得できる
        ```python
        hs = hashlib.sha224("こんにちは".encode()).hexdigest()
        ```
        """
        print(self.filename,self.saved)
        if self.filename==None:
            pass
        else:
            self.saved:bool = False
            self.root.title(self.title_filename_setter())
    #sub windows
    def open_ascii_code_table(self):
        """
        # ascii code table
        編集補助ツール
        """
        self.ascii_code_table = tk.Toplevel(self.root)
        self.ascii_code_table.geometry("650x600")
        self.ascii_code_table_canvas = tk.Canvas(self.ascii_code_table,bg="black",width=600,height=600)
        self.ascii_code_table_frame = tk.Frame(self.ascii_code_table_canvas)
        self.ascii_code_table_canvas_scrollbar = tk.Scrollbar(
            self.ascii_code_table_canvas,
            orient=tk.VERTICAL,
            command=self.ascii_code_table_canvas.yview
        )
        self.ascii_code_table_canvas.configure(scrollregion=(0, 0, 600, 1200))
        self.ascii_code_table_canvas.configure(yscrollcommand=self.ascii_code_table_canvas_scrollbar.set)
        self.ascii_code_table_canvas_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ascii_code_table_canvas.pack(expand=True, fill=tk.BOTH)
        self.ascii_code_table_canvas.create_window((0, 0), window=self.ascii_code_table_frame, anchor="nw",width=650,height=1200)

        #表の作成
        self.index_labels=[]
        self.ascii_labels=[]
        ascii_index_list=[(i,repr(chr(i))[1:-1]) for i in range(256)]
        width=20
        for i,j in enumerate(self.chunked(ascii_index_list,width)):
            for k,l in enumerate(j):
                self.index_labels.append(tk.Label(self.ascii_code_table_frame,text=l[0],background="#c7c7c7"))
                self.ascii_labels.append(tk.Label(self.ascii_code_table_frame,text=l[1],background="#dedede"))
                self.index_labels[i*width+k].grid(row=2*i,column=k,sticky=tk.E+tk.W)
                self.ascii_labels[i*width+k].grid(row=2*i+1,column=k,sticky=tk.E+tk.W)
    def open_rule_set_window(self):
        """
        # rule book を開く
        サブウィンドウを開き設定を変更できる
        . 内部的なインタープリターの設定
        . インタープリターのデザインの設定
        . 
        """
        self.rule_set_window = tk.Toplevel(self.root)
        self.rule_set_window.title("BFeditor RuleBook")
        self.rule_set_window_notebook = ttk.Notebook(self.rule_set_window)
        self.rule_set_window_notebook.pack()

        #tab: Interpreter
        self.rule_set_window_interpreter_tab = ttk.Frame(self.rule_set_window)
        self.rule_set_window_notebook.add(self.rule_set_window_interpreter_tab,text="Interpreter")
        
        self.rule_set_window_interpreter_tab_frame1 = tk.LabelFrame(self.rule_set_window_interpreter_tab,text="cell max")
        self.rule_set_window_interpreter_tab_frame1.pack()
        self.rule_set_window_interpreter_tab_frame2 = tk.LabelFrame(self.rule_set_window_interpreter_tab,text="cell type")
        self.rule_set_window_interpreter_tab_frame2.pack()
        self.rule_set_window_interpreter_tab_frame3 = tk.LabelFrame(self.rule_set_window_interpreter_tab,text="memory max range")
        self.rule_set_window_interpreter_tab_frame3.pack()
        self.rule_set_window_interpreter_tab_frame4 = tk.LabelFrame(self.rule_set_window_interpreter_tab,text="memory type")
        self.rule_set_window_interpreter_tab_frame4.pack()
        ##frame1
        """
        セルの最大値を設定する
        メモリの最大値を決める。
        デフォルトは255
        radioボタンでInfinity
        """
        self.rule_set_window_interpreter_tab_frame1_entry = ttk.Entry(self.rule_set_window_interpreter_tab_frame1)
        self.rule_set_window_interpreter_tab_frame1_entry.pack()
        self.rule_set_window_interpreter_tab_frame1_entry.insert("0",255)

        ##frame2
        """
        セルタイプを選択する
        Strict : range(0~cell_max) 範囲外を指定すると Error:memory index out of range をoutputエリアに赤文字で出力する
        Loop   : range(0~cell_max) ex. cell_max+1 -> 0, -1 ->cell_max
        Integer: range(-cell_max~cell_max) 
        """
        self.rule_set_window_interpreter_tab_frame2_combobox = ttk.Combobox(self.rule_set_window_interpreter_tab_frame2, values=["Strict", "Loop", "Integer"],state="readonly")
        self.rule_set_window_interpreter_tab_frame2_combobox.current(2)
        self.rule_set_window_interpreter_tab_frame2_combobox.pack()
        #tab: Editor
        self.rule_set_window_Editor_tab = tk.Frame(self.rule_set_window)
        self.rule_set_window_notebook.add(self.rule_set_window_Editor_tab,text="Editor")
    def show_popup_menu(self,e):
        """
        ポップアップメニュー
        """
        if self.selected_text() is None:
            #何も選択されていない場合
            self.popup_menu.entryconfig("Copy",state="disabled")
        else:
            self.popup_menu.entryconfig("Copy",state="normal")
        #クリップボードを取得する
        text=self.clipboard_text()
        if text:
            #クリップボードに何かしらある場合。
            self.popup_menu.entryconfig("Paste",state="normal")
        else:
            #クリップボードに何にもない場合
            self.popup_menu.entryconfig("Paste",state="disabled")
        self.popup_menu.post(e.x_root,e.y_root)
    def clipboard_copy(self):
        #コピー
        self.root.clipboard_clear()
        self.root.clipboard_append(self.selected_text())
    def clipboard_paste(self):
        #貼り付け
        text_from_clipboard:str=self.clipboard_text()
        index=self.raw_code_text.index(tk.INSERT)
        self.raw_code_text.insert(index,text_from_clipboard)
    def clipboard_text(self):
        try:
            return self.root.clipboard_get()
        except tk.TclError:
            return None

    def selected_text(self):
        """
        raw code textで選択されたテキストを返す
        """
        try:
            return self.raw_code_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            return None


bfeditor=BFeditor()
bfeditor.mainloop()