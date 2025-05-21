#​ Edite  as classes nesse arquivo.​ ​Boa prova!
from abc import ABC
from dataclasses import dataclass
from typing import Callable, List # Adicionado List para type hinting

from . import runtime
from .ctx import Ctx

# Declaramos nossa classe base num módulo separado para esconder um pouco de
# Python relativamente avançado de quem não se interessar pelo assunto.
#
# A classe Node implementa um método `pretty` que imprime as árvores de forma
# legível. Também possui funcionalidades para navegar na árvore usando cursores
# e métodos de visitação.
from .node import Node

#
# TIPOS BÁSICOS
#

# Tipos de valores que podem aparecer durante a execução do programa
Value = bool | str | float | None # Tuplas avaliadas não estão aqui, mas o retorno de Tuple.eval será um tuple do Python


class Expr(Node, ABC):
    """
    Classe base para expressões.

    Expressões são nós que podem ser avaliados para produzir um valor.
    Também podem ser atribuídos a variáveis, passados como argumentos para
    funções, etc.
    """


class Stmt(Node, ABC):
    """
    Classe base para comandos.

    Comandos são associdos a construtos sintáticos que alteram o fluxo de
    execução do código ou declaram elementos como classes, funções, etc.
    """
    # Adicionando um método eval abstrato para Stmt para consistência,
    # embora não seja estritamente necessário pelo exercício se todos os Stmts o implementam.
    def eval(self, ctx: Ctx):
        raise NotImplementedError


@dataclass
class Program(Node):
    """
    Representa um programa.

    Um programa é uma lista de comandos.
    """

    stmts: list[Stmt]

    def eval(self, ctx: Ctx):
        for stmt in self.stmts:
            stmt.eval(ctx)


#
# EXPRESSÕES
#
@dataclass
class BinOp(Expr):
    """
    Uma operação infixa com dois operandos.

    Ex.: x + y, 2 * x, 3.14 > 3 and 3.14 < 4
    """

    left: Expr
    right: Expr
    op: Callable[[Value, Value], Value]

    def eval(self, ctx: Ctx):
        left_value = self.left.eval(ctx)
        right_value = self.right.eval(ctx)
        return self.op(left_value, right_value)


@dataclass
class Var(Expr):
    """
    Uma variável no código

    Ex.: x, y, z
    """

    name: str

    def eval(self, ctx: Ctx):
        try:
            return ctx[self.name]
        except KeyError:
            raise NameError(f"variável {self.name} não existe!")


@dataclass
class Literal(Expr):
    """
    Representa valores literais no código, ex.: strings, booleanos,
    números, etc.

    Ex.: "Hello, world!", 42, 3.14, true, nil
    """

    value: Value

    def eval(self, ctx: Ctx):
        return self.value


@dataclass
class UnaryOp(Expr):
    """
    Uma operação prefixa com um operando.

    Ex.: -x, !x
    """

    op: Callable[[Value], Value]
    expr: Expr

    def eval(self, ctx: Ctx):
        value = self.expr.eval(ctx)
        return self.op(value)


@dataclass
class Call(Expr):
    """
    Uma chamada de função.

    Ex.: fat(42)
    """

    name: str # Mantido como str para simplicidade, conforme original
    params: list[Expr]

    def eval(self, ctx: Ctx):
        # O nome da função é avaliado como uma Var para obter o callable do contexto
        # Se Call.name fosse uma Expr (ex: Var("nome_func")), isso já estaria correto.
        # Assumindo que o contexto (ctx) mapeia nomes de string para funções.
        # Se 'name' fosse para ser uma expressão mais complexa (ex: obj.method),
        # Call.name (ou Call.callee) seria do tipo Expr.
        # Pela simplicidade do Lox atual, ctx[self.name] deve funcionar.
        
        func_val = ctx.get(self.name) # Usando get para melhor tratamento de erro
        if func_val is None:
            raise NameError(f"Função ou variável '{self.name}' não definida.")

        evaluated_params = []
        for param in self.params:
            evaluated_params.append(param.eval(ctx))

        if callable(func_val):
            return func_val(*evaluated_params) 
        raise TypeError(f"'{self.name}' não é uma função!")


@dataclass
class Assign(Expr):
    """
    Atribuição de variável.

    Ex.: x = 42
    """

    name: str
    value: Expr

    def eval(self, ctx: Ctx):
        val_to_assign = self.value.eval(ctx) # Corrigido para val_to_assign
        ctx[self.name] = val_to_assign
        return val_to_assign


@dataclass
class Tuple(Expr): 
    """
    Representa uma expressão de tupla.

    Ex.: (), (1,), (1, 2), (1, (2, 3))
    """
    elems: List[Expr] 

    def eval(self, ctx: Ctx):
        value = []
        for elem in self.elems: 
            value.append(elem.eval(ctx))
        return tuple(value)


#
# COMANDOS E DECLARAÇÕES
#

@dataclass
class ExprStmt(Stmt): # Novo: Comando de Expressão
    """
    Representa uma expressão usada como um comando.
    O valor da expressão é descartado.

    Ex: x + 1; // calcula x + 1, mas não faz nada com o resultado
        call_func();
    """
    expr: Expr

    def eval(self, ctx: Ctx):
        self.expr.eval(ctx) # Avalia pela expressão por seus efeitos colaterais


@dataclass
class Print(Stmt):
    """
    Representa uma instrução de impressão.

    Ex.: print "Hello, world!";
    """

    expr: Expr

    def eval(self, ctx: Ctx):
        value = self.expr.eval(ctx)
        runtime.print(value, end="\n")


@dataclass
class VarDef(Stmt):
    """
    Representa uma declaração de variável.

    Ex.: var x = 42;
    """

    name: str
    value: Expr | None

    def eval(self, ctx: Ctx):
        val_to_assign = None # Corrigido para val_to_assign
        if self.value is not None:
            val_to_assign = self.value.eval(ctx)
        ctx[self.name] = val_to_assign


@dataclass
class Block(Stmt): # Modificado: Block agora é um Stmt para simplificar o corpo do While
    """
    Representa bloco de comandos.
    Um bloco pode introduzir um novo escopo. (Não tratado explicitamente aqui, mas em Ctx)

    Ex.: { var x = 42; print x;  }
    """

    stmts: list[Stmt]

    def eval(self, ctx: Ctx): 
        # Para escopo léxico, um novo Ctx aninhado seria criado aqui.
        # new_ctx = Ctx(outer=ctx)
        # for stmt in self.stmts:
        #     stmt.eval(new_ctx)
        # Por simplicidade, e como eval não foi pedido para while,
        # vamos manter a avaliação no contexto atual.
        for stmt in self.stmts:
            stmt.eval(ctx)


@dataclass
class While(Stmt):
    """
    Representa um laço de repetição.

    Ex.: while (x > 0) { ... }
    """
    condition: Expr
    body: Stmt # O corpo pode ser um Block ou outro Stmt (como Print, ExprStmt)

    # O método eval não é para ser implementado nesta questão.
    # def eval(self, ctx: Ctx):
    #     while _truthy(self.condition.eval(ctx)): # _truthy seria uma função auxiliar
    #         self.body.eval(ctx)
    pass