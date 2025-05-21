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
from .ast import *


def op_handler(op_func: Callable): # Renomeado parâmetro para evitar conflito com módulo op
    """
    Fábrica de métodos que lidam com operações binárias na árvore sintática.

    Recebe a função que implementa a operação em tempo de execução.
    """

    def method(self, children): # Modificado para aceitar 'children' como padrão do Lark
        left, right = children
        return BinOp(left, right, op_func)

    return method


@v_args(inline=True)
class LoxTransformer(Transformer):
    # Programa
    def program(self, *stmts):
        return Program(list(stmts))

    # Operações matemáticas básicas
    # Para operações binárias, v_args(inline=True) passará os filhos diretamente.
    # Ex: mul(self, left_expr_node, right_expr_node)
    # A função op_handler precisa ser ajustada se os métodos do transformer
    # recebem os filhos diretamente como argumentos separados devido a inline=True.
    # Por simplicidade, e consistência com outros métodos, vamos assumir que op_handler
    # é chamado por métodos que já desempacotam os filhos ou que a gramática/Lark
    # passa uma lista de 2 filhos.
    # A forma original do op_handler com (self, left, right) espera que os métodos
    # da classe sejam tipo `def mul(self, left, right): return BinOp(left, right, op.mul)`
    # Ou, se a regra na gramática é `factor "*" term -> mul`, e `inline=True`,
    # o método `mul` receberia `factor` e `term` transformados.
    # Vamos ajustar para o uso comum com `v_args(inline=True)` onde os filhos são argumentos diretos.

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
    def call(self, name_or_callee: Expr, params: list): # 'name' pode ser uma Var ou outra Expr se callee for mais geral
        # A gramática original tem `call: call "(" params ")" | atom`.
        # Se `call` for o primeiro filho, é uma chamada recursiva. `atom` é a base.
        # Assumindo que `name_or_callee` é o nó da expressão que resulta na função (ex: Var)
        # e `params` é a lista de nós de expressão dos parâmetros já transformados pela regra `params`.
        if isinstance(name_or_callee, Var):
            return Call(name_or_callee.name, params if params is not None else [])
        # Se a linguagem suportasse chamadas mais complexas (ex: obj.method()), `name_or_callee` seria mais geral.
        # Para o Lox atual, o callee é provavelmente sempre um Var (nome de função).
        # Se `params` pode ser None vindo de Lark para `()` vazios em `call(f, ())`, ajustamos.
        # A regra `params: [ expr ("," expr )* ]` produz uma lista, que pode ser vazia.
        return Call(str(name_or_callee), params if params is not None else [])


    def params(self, *args): # Se params estiver vazio, args será vazio.
        return list(args)

    def assign(self, name: Var, value: Expr):
        return Assign(name.name, value)

    # Comandos
    def var_def(self, name: Var, expr: Expr | None = None): # expr pode não estar presente se Lark permitir (ex: var x;)
        return VarDef(name.name, expr)

    def print_cmd(self, expr):
        return Print(expr)

    def block(self, *stmts: Stmt):
        return Block(list(stmts))

    # Conversores de Tokens para Nós AST
    def VAR(self, token):
        name = str(token)
        return Var(name)

    def NUMBER(self, token):
        num = float(token)
        return Literal(num)

    def STRING(self, token):
        text = str(token)[1:-1].replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t') # Adicionado escape básico
        return Literal(text)

    def NIL(self, _): # _ geralmente significa que o valor do token não é usado
        return Literal(None)

    def BOOL(self, token):
        return Literal(str(token) == "true") # Convertendo token para string antes de comparar

    # Novos métodos para transformar tuplas
    def tuple_empty(self, _): # _ para ignorar os tokens "(" e ")" se passados
        return Tuple(elems=[])

    def tuple_single(self, expr_node): # Recebe o nó da expressão já transformado
        return Tuple(elems=[expr_node])

    # A regra é `expr ("," expr)+`. Com inline=True, isso passará todos os exprs como args.
    def tuple_multi(self, *expr_nodes: Expr):
        return Tuple(elems=list(expr_nodes))