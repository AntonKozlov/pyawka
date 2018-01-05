import ast
import sys
import builtins
from collections import defaultdict, ChainMap

from parseprint import parseprint

class NameTrasformer(ast.NodeTransformer):
    def visit_Name(self, node):
        n = ast.copy_location(ast.Subscript(
                value=ast.copy_location(ast.Name(id='__PYAWKA__', ctx=ast.Load()), node),
                slice=ast.copy_location(ast.Index(value=ast.copy_location(ast.Str(s=node.id), node)), node),
                ctx=node.ctx,
            ), node)
        n.orig_name=node.id
        return n

class AwkaTrasformer(ast.NodeTransformer):
    def __init__(self):
        self.prog = dict()
        self.prog['cases'] = list()

    def visit_With(self, node):
        if len(node.items) != 1:
            raise ParseError(node)
        item = node.items[0]
        orig_name = getattr(item.context_expr, 'orig_name', None)
        body = compile(ast.Module(node.body), '<pyawka>', 'exec')
        if orig_name in [ 'BEGIN', 'END' ]:
            self.prog[orig_name] = body
        else:
            cond = compile(ast.Expression(item.context_expr), '<pyawka>', 'eval')
            self.prog['cases'].append((cond, body))
        return None

class constdict(defaultdict):
    def __init__(self, const):
        self.const = const
    def __missing__(self, key):
        return self.const

def dd(fields):
    return defaultdict(lambda: None, enumerate(fields))

def main(prog, inputs):
    
    d = ChainMap(globals(), vars(builtins), constdict(None))

    tree = ast.parse(prog)

    nt = NameTrasformer()
    nt.visit(tree)

    t = AwkaTrasformer()
    t.visit(tree)

    global __PYAWKA__
    __PYAWKA__ = d
    
    begin = t.prog.get('BEGIN')
    if begin:
        exec(begin)

    cases = t.prog['cases']

    if not inputs:
        inputs = [ '-' ]

    for inp in inputs:
        try:
            f = sys.stdin if inp == '-' else open(inp, 'r')

            for line in f:
                d['F'] = dd([line.strip()] + line.split())
                for cond, body in cases:
                    if eval(cond):
                        exec(body)
        finally:
            if f is not sys.stdin:
                f.close()

    if 'F' in d:
        del d['F']
    end = t.prog.get('END')
    if end:
        exec(end)
