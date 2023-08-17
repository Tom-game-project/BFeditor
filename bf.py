from enum import Enum

class mode(Enum):
    #interpreter
    STRICT=0
    LOOP=1
    INTEGER=2


class BrainFuck():
    def __init__(self,code:str,memory_size=100):
        """
        ```brainfuck
        
        ```
        output -> hello world
        """
        self.code=self.code_extractor(code)
        self.memory_size=memory_size
        self.memory=[0 for i in range(memory_size)]
        self.pointer:int=0
        self.input_list:list=list()
        
        #self.input_count:int=0
        #self.input_newline_count:int = 1
        self.init_input_counter()

        self.output:list=[]
        self.step=0
    def set_input_stream(self,list_):
        """
        # input stream
        brainfuckはinputをそのつど（一文字ずつ）要求する仕組みだが、inputする内容またはしたい内容はすでに決まっている場合が多い。
        そこでこの関数では、","（input）のたびに質問ダイアログを飛ばしたり、入力を要求することを防ぐように、
        最初に全ての入力を決めてgeneratorとして実行ループの中に入力を送出できる仕組みを提供する。
        繰り返し入力を要求するようなプログラムの中で、入力の終了には0を返す。
        """
        self.input_ = self.input_iter(list_)
    def input_iter(self,list_):
        for i in list(list_)+[None]:
            if i=="\n":
                self.input_count=0
                self.input_newline_count+=1
                self.input_newline_count_list.append(0)
            else:
                self.input_count+=1
                self.input_newline_count_list[self.input_newline_count] = self.input_count
            yield i
    def init_input_counter(self):
        self.input_count:int=0
        self.input_newline_count:int=0
        self.input_newline_count_list:list=[0]#一行目から始まるため
    
    def process(self,index):
        i=index
        j=None
        instruction = self.code[i]
        if instruction == '>':
            self.pointer += 1
        elif instruction == '<':
            self.pointer -= 1
        elif instruction == '+':
            self.memory[self.pointer]+=1
            self.memory[self.pointer]%=256
        elif instruction == '-':
            self.memory[self.pointer]-=1
            self.memory[self.pointer]%=256
        elif instruction == '.':
            """
            # output
            """
            j=chr(self.memory[self.pointer])
            self.output.append(chr(self.memory[self.pointer]))
        elif instruction == ',':
            """
            # input
            """
            # Assume input is provided as ASCII characters
            if not self.eof_reached:
                char=next(self.input_)
                if char == None:  # EOF
                    self.memory[self.pointer] = 0
                    self.eof_reached = 1
                    """
                    EOFは一回のみ許される。
                    二回目以降のEOFは許されずloopを強制的に抜けさせられる
                    """
                else:
                    self.memory[self.pointer] = ord(char)
            else:
                i=len(self.code)

        elif instruction == '[':
            if self.memory[self.pointer] == 0:
                # Find the matching closing bracket
                depth = 1
                while depth > 0:
                    i += 1
                    if self.code[i] == '[':
                        depth += 1
                    elif self.code[i] == ']':
                        depth -= 1
            else:
                self.stack.append(i)
        elif instruction == ']':
            if self.memory[self.pointer]:
                i = self.stack[-1]
            else:
                self.stack.pop()
        self.step+=1
        i += 1
        return i,j
    def run(self):
        self.stack = []
        i = 0
        self.eof_reached=0
        while i < len(self.code):
            i,_ = self.process(i)
    def run_generator(self):
        """
        iはcode上のどこの位置を指すか
        jは出力、出力がない場合はNoneを返す
        """
        self.stack = []
        i = 0
        self.eof_reached=0
        self.init_input_counter()
        while i < len(self.code):
            i,j = self.process(i)
            yield i,j
    def state(self)->tuple[int,int]:
        return self.pointer,self.memory[self.pointer]
    def code_extractor(self,code)->str:
        return "".join([i for i in code if i in [">","<",",",".","+","-","[","]"]])



if __name__=="__main__":
    bf = BrainFuck(
    """
(++++++)>(++++)[<+>-]
    """,memory_size=100
    )
    bf.run()
    print(
        bf.memory
    )
    #brainfuck
    #ADD(++++++)>(++++)[<+>-]
    #SUB(++++++)>(++++)[<->-]
    #MUL(++)[->(+++)<]>[-<+>]
    #
    #
    #MOV +++[->+>+<<]>>[-<<+>>]
