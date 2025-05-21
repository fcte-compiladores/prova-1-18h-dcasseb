Nesse exercício, vamos extender a gramática de Lox para suportar tuplas. Para
manter a simplicidade, vamos assumir que uma tupla é delimitada por parênteses e
cada elemento é separado por vírgulas, como abaixo:

```lox
(1, x, 40 + 2, "string")
```

Lembre-se de suportar tuplas vazias

```lox
()
```

e tuplas dentro de tuplas

```lox
((1, 2, (3, 4)), 10)
```

Na nossa notação, uma tupla de 1 elemento é indistinguível de uma expressão
entre parênteses. Para distinguir ambos, faremos como em Python: uma tupla de 1
elemento deve ter uma vírgula solta no final: `(single,)`.

Essa vírgula só é válida em tuplas de um único elemento. Portanto `(x, y,)`
seria um comando ilegal. Assim como a tupla com uma única vírgula perdida `(,)`.

Você deve implementar suporte a tuplas na gramática e implementar o método eval
mais ou menos da seguinte forma:

```python
@dataclass
class Tuple(Expr):
    elems: list[Expr]

    def eval(self, ctx: Ctx):
        value = []
        for elem in self.elems: # ou outro meio de produzir os elementos da tupla
            value.append(elem.eval(ctx))
        return tuple(value)
```