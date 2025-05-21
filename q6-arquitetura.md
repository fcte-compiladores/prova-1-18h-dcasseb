De modo abstrato, o compilador é um programa que converte código de uma
linguagem para outra. Como se fosse uma função do tipo `compilador(str) -> str`.
No caso de compiladores que emitem código de máquina ou bytecode, seria mais
preciso dizer `compilador(str) -> bytes`, mas a idéia básica é a mesma.

De forma geral o processo é dividido em etapas como abaixo

```python
def compilador(x1: str) -> str | bytes:
    x2 = lex(x1)        # análise léxica
    x3 = parse(x2)      # análise sintática
    x4 = analysis(x3)   # análise semântica
    x5 = optimize(x4)   # otimização
    x6 = codegen(x5)    # geração de código
    return x6
```

Defina brevemente o que cada uma dessas etapas realizam e marque quais seriam os
tipos de entrada e saída de cada uma dessas funções. Explique de forma clara o
que eles representam. Você pode usar exemplos de linguagens e/ou compiladores
conhecidos para ilustrar sua resposta. Salve sua resposta nesse arquivo.

# lex(x1: str) -> List[Token]

*Entrada (``):* str — o código-fonte bruto como texto.

*Saída:* List[Token] — uma lista de tokens (unidades léxicas).

*O que faz:*

- Divide o texto em tokens (palavras-chave, identificadores, literais, símbolos, etc.).

- Remove espaços em branco e comentários.

*Exemplo:* em um compilador C, transforma a string int x = 42; em uma lista: [Token(INT, "int"), Token(IDENT, "x"), Token(EQ, "="), Token(NUM, "42"), Token(SEMICOLON, ";")].
 
# parse(x2: List[Token]) -> AST

*Entrada (``):* List[Token] — tokens produzidos pelo analisador léxico.

*Saída:* AST — árvore sintática abstrata.

*O que faz:*

- Analisa a estrutura gramatical segundo a gramática da linguagem.

- Constrói uma árvore que representa a hierarquia de expressões e declarações.

*Exemplo:* para tokens de x + 1 * y, produz um AST com nó raiz +, filho esquerdo x, filho direito * com filhos 1 e y.

# analysis(x3: AST) -> AST_anotada

*Entrada (``):* AST — árvore sintática abstrata.

*Saída:* AST_anotada — AST com informações semânticas.

*O que faz:*

- Verifica propriedades semânticas: tipos, escopos, declarações, uso de variáveis.

- Gera tabelas de símbolos, checa coerência de tipos e vínculos.

*Exemplo:* no compilador Java, garante que operações aritméticas sejam entre tipos compatíveis e anota cada nó do AST com seu tipo.

# optimize(x4: AST_anotada) -> IR

*Entrada (``):* AST_anotada — árvore enriquecida semanticamente.

*Saída:* IR — representação intermediária (Intermediate Representation).

*O que faz:*

- Converte o AST anotado em uma ou mais formas de IR (por exemplo, Three-Address Code, SSA).

- Aplica otimizações: eliminação de código morto, propagação de constantes, inlining de funções, etc.

*Exemplo:* no GCC, gera o RTL ou GIMPLE e faz passagens de otimização nesse IR.

# codegen(x5: IR) -> str | bytes

*Entrada (``):* IR — código intermediário otimizado.

*Saída:* str ou bytes — código de saída, como assembly, bytecode ou binário.

*O que faz:*

- Traduz o IR para a linguagem alvo: assembly de máquina (ex: x86), bytecode JVM, WebAssembly, etc.

- Aloca registradores, gera instruções, cuida de alinhamento e convenções de chamada.

- Opcionalmente, já pode montar o binário ou o pacote de saída (objeto, DLL, JAR).

*Exemplo:* LLVM gera código para x86-64 ou ARM a partir de LLVM IR.