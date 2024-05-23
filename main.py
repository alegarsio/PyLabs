import netlab
from netlab import STD
from llvmlite import ir , binding
from compiler import Parser , CodeGenerator

def __init__ ():
    root = netlab.tk.Tk()
    app = netlab.STD(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        __init__()
    except Exception as e:
        print(e)