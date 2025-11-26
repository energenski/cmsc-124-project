import sys
import os
sys.path.append(os.path.abspath("syntax"))
from syntax2 import Parser
from lexer1 import get_tokens

code = """
HAI
WAZZUP
I HAS A var ITZ 10
BUHBYE
VISIBLE var
KTHXBYE
"""

tokens = get_tokens(code)
parser = Parser(tokens)
ast = parser.parse()
print(ast)
