# ​Edite ​a​ ​classe  LoxTransformer nesse ​arquivo.​ Boa​ ​prova!
"""
Implementa o transformador da árvore sintática que converte entre as representações

    lark.Tree -> lox.ast.Node.

A resolução de vários exercícios requer a modificação ou implementação de vários
métodos desta classe.
"""

from typing import Callable

from lark import Transformer, v_args 

from . import runtime as op 
from .ast import * # O decorator @v_args deve estar na linha ANTERIOR à definição da classe
@v_args(inline=True)
class LoxTransformer(Transformer):
    # Programa
    def program(self, *stmts):
        return Program(list(stmts))

    # Operações 
    def mul(self, left, right): return BinOp(left, right, op.mul)
    def div(self, left, right): return BinOp(left, right, op.truediv)
    def sub(self, left, right): return BinOp(left, right, op.sub)
    def add(self, left, right): return BinOp(left, right, op.add)

    # Comparações
    def gt(self, left, right): return BinOp(left, right, op.gt)
    def lt(self, left, right): return BinOp(left, right, op.lt)
    def ge(self, left, right): return BinOp(left, right, op.ge)
    def le(self, left, right): return BinOp(left, right, op.le)
    def eq(self, left, right): return BinOp(left, right, op.eq)
    def ne(self, left, right): return BinOp(left, right, op.ne)

    def not_(self, expr):
        return UnaryOp(op.not_, expr)

    def neg(self, expr):
        return UnaryOp(op.neg, expr)

    # Outras expressões
    def call(self, callee: Expr, params: list | None): 
        callee_name = ""
        if isinstance(callee, Var):
            callee_name = callee.name
        else:
            # Isso pode precisar de um tratamento mais robusto se callee puder ser outra Expr
            # que avalia para uma função, mas para um Lox simples, Var é o esperado.
            raise TypeError(f"Callee da função deve ser um nome de variável, mas foi {type(callee)}")

        return Call(callee_name, params if params is not None else [])


    def params(self, *args: Expr): 
        return list(args)

    def assign(self, name: Var, value: Expr):
        return Assign(name.name, value)

    # Comandos
    def var_def(self, name: Var, expr: Expr | None = None):
        return VarDef(name.name, expr)

    def print_cmd(self, expr: Expr):
        return Print(expr)

    def block(self, *stmts: Stmt):
        return Block(list(stmts))

    def to_expr_stmt(self, expr_node: Expr): # Handles expr ";"
        return ExprStmt(expr_node)
    
    def while_stmt(self, condition: Expr, body: Stmt): 
        return While(condition=condition, body=body)

    # Conversores de Tokens para Nós AST
    def VAR(self, token):
        name = str(token)
        return Var(name)

    def NUMBER(self, token):
        num = float(token)
        return Literal(num)

    def STRING(self, token):
        text = str(token)[1:-1]
        # Tratamento básico de sequências de escape comuns
        text = text.replace("\\n", "\n")
        text = text.replace("\\t", "\t")
        text = text.replace('\\"', '"')
        text = text.replace("\\\\", "\\")
        return Literal(text)

    def NIL(self, _): 
        return Literal(None)

    def BOOL(self, token):
        return Literal(str(token) == "true")

    # Métodos para transformar tuplas
    def tuple_empty(self, _): 
        return Tuple(elems=[])

    def tuple_single(self, expr_node: Expr): 
        return Tuple(elems=[expr_node])

    def tuple_multi(self, *expr_nodes: Expr):
        return Tuple(elems=list(expr_nodes))