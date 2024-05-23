import re

TOKEN_SPECIFICATION = [
    ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
    ('PLUS',     r'\+'),           # Plus operator
    ('MINUS',    r'-'),            # Minus operator
    ('MUL',      r'\*'),           # Multiplication operator
    ('DIV',      r'/'),            # Division operator
    ('LPAREN',   r'\('),           # Left parenthesis
    ('RPAREN',   r'\)'),           # Right parenthesis
    ('SKIP',     r'[ \t]+'),       # Skip spaces and tabs
    ('MISMATCH', r'.'),            # Any other character
]

class Lexer:
    def __init__(self, code):
        self.tokens = []
        self.tokenize(code)
    
    def tokenize(self, code):
        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)
        get_token = re.compile(tok_regex).match
        line_num = 1
        pos = line_start = 0
        match = get_token(code)
        while match is not None:
            type_ = match.lastgroup
            if type_ == 'NEWLINE':
                line_start = pos
                line_num += 1
            elif type_ != 'SKIP' and type_ != 'MISMATCH':
                value = match.group(type_)
                self.tokens.append((type_, value))
            pos = match.end()
            match = get_token(code)
        if pos != len(code):
            raise RuntimeError(f'Unexpected character {code[pos]} on line {line_num}')
        self.tokens.append(('EOF', 'EOF'))

    def next_token(self):
        return self.tokens.pop(0)
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()
    
    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.current_token = self.lexer.next_token()
        else:
            raise ValueError(f"Unexpected token: {self.current_token}")

    def factor(self):
        token = self.current_token
        if token[0] == 'NUMBER':
            self.eat('NUMBER')
            return ('NUM', float(token[1]))
        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node

    def term(self):
        node = self.factor()
        while self.current_token[0] in ('MUL', 'DIV'):
            token = self.current_token
            if token[0] == 'MUL':
                self.eat('MUL')
            elif token[0] == 'DIV':
                self.eat('DIV')
            node = (token[0], node, self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token[0] in ('PLUS', 'MINUS'):
            token = self.current_token
            if token[0] == 'PLUS':
                self.eat('PLUS')
            elif token[0] == 'MINUS':
                self.eat('MINUS')
            node = (token[0], node, self.term())
        return node

    def parse(self):
        return self.expr()
from llvmlite import ir, binding

class CodeGenerator:
    def __init__(self):
        self.module = ir.Module(name="my_module")
        self.builder = None
        self.func = None
        self.block = None
    
    def generate(self, node):
        self._create_entry_point()
        return self._compile(node)

    def _create_entry_point(self):
        func_type = ir.FunctionType(ir.DoubleType(), ())
        self.func = ir.Function(self.module, func_type, name="main")
        self.block = self.func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(self.block)
    
    def _compile(self, node):
        if node[0] == 'NUM':
            return ir.Constant(ir.DoubleType(), node[1])
        elif node[0] in ('PLUS', 'MINUS', 'MUL', 'DIV'):
            left = self._compile(node[1])
            right = self._compile(node[2])
            if node[0] == 'PLUS':
                return self.builder.fadd(left, right, name="addtmp")
            elif node[0] == 'MINUS':
                return self.builder.fsub(left, right, name="subtmp")
            elif node[0] == 'MUL':
                return self.builder.fmul(left, right, name="multmp")
            elif node[0] == 'DIV':
                return self.builder.fdiv(left, right, name="divtmp")

    def get_ir(self):
        self.builder.ret(self._compile(self.node))
        return str(self.module)
def main():
    code = "3 + 4 * 2 / (1 - 5)"
    lexer = Lexer(code)
    parser = Parser(lexer)
    ast = parser.parse()
    
    codegen = CodeGenerator()
    llvm_ir = codegen.generate(ast)
    
    print(llvm_ir)
    
    # Compile and execute LLVM IR
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()

    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()

    mod = binding.parse_assembly(llvm_ir)
    mod.verify()

    with binding.create_mcjit_compiler(mod, target_machine) as ee:
        ee.finalize_object()
        ee.run_static_constructors()
        func_ptr = ee.get_function_address("main")
        
        from ctypes import CFUNCTYPE, c_double
        main_func = CFUNCTYPE(c_double)(func_ptr)
        result = main_func()
        print("Result:", result)

if __name__ == "__main__":
    main()
