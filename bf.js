
class BrainFuck{
    constructor(code,memory_size=100){
        this.code = this.code_extractor(code);
        this.memory_size = memory_size; 
        this.memory = new Uint8Array(
                [...Array(this.memory_size)].map(_ => 0)
            )
        this.pointer = 0;
        this.input_list = [];
        this.output = [];      //ひたすらchrが並んでいる状態
        this.step = 0;

    }

    //イテレータ
    *input_stream(){
        for (const i of this.input_list){
            yield i;
        }
        yield null;
    }
    set_input_stream(){
        //イテレータをセット
        this.input_ = this.input_stream()
    }
    process(index){
        let i = index;
        let j = null
        let instruction = this.code[i];
        switch(instruction){
            case ">":
                this.pointer++;
                break;
            case "<":
                this.pointer--;
                break;
            case "+":
                this.memory[this.pointer] = (this.memory[this.pointer]+1)%256;
                break;
            case "-":
                this.memory[this.pointer] = (this.memory[this.pointer]-1)%256;
                break;
            case ".":
                j = String.fromCharCode(this.memory[this.pointer]);
                this.output.push(this.memory[this.pointer]);
                break;
            case ",":
                if (! this.eof_reached){
                    let char = this.input_.next();
                    if (char===null){
                        this.memory[this.pointer] = 0;
                        this.eof_reached = 1; 
                        /*
                        EOFは一回のみ許される。
                        二回目以降のEOFは許されずloopを強制的に抜けさせられる
                        */
                    }else{
                        this.memory[this.pointer] = char.charCodeAt();
                    }
                }else{
                    i = this.code.length;
                }
                break;
            case "[":
                if (this.memory[this.pointer]==0){
                    let depth = 1;
                    while (depth>0){
                        i++;
                        if (this.code[i]=="["){
                            depth++;
                        }else if (this.code[i]=="]"){
                            depth--;
                        }
                    }
                }else{
                    this.stack.push(i);
                }
                break;
            case "]":
                if (this.memory[this.pointer]!=0){
                    i = this.stack[this.length  -1 ]
                }else{
                    this.stack.pop()
                }
                break;
        }
        this.step++;
        i++;
        return [i,j];
    }
    run(){
        this.stack=[];
        let i = 0;
        this.eof_reached = 0;
        while (i < this.code.length){
            [i,j] = this.process(i);
        }
    }
    *run_generator(){
        this.stack=[];
        let i=0;
        let j;
        this.eof_reached=0;
        while (i<this.code.length){
            [i,j]=this.process(i);
            yield [i,j];
        }
    }
    state(){
        //現在のポインターとそれが指す値
        return [this.pointer,this.memory[this.pointer]]
    }
    code_extractor(code){
        return [...code].filter(i=>['>', '<', ',', '.', '+', '-', '[', ']'].includes(i))
    }

}


function main(){
    const bf = new BrainFuck("(++++++)>(++++)[<+>-]");
    console.log(
        bf.code
    )
    for (const i of bf.run_generator()){
        
        console.log(`${i}${bf.pointer}`)
    }
    console.log(
        bf.memory
    )
}






main();