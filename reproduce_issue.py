import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from syntax.syntax2 import Parser
from lexer1 import get_tokens
from semantics.semantics1 import Interpreter

code = """HAI
WAZZUP
BTW variable dec
I HAS A monde
I HAS A num ITZ 17
VISIBLE SUM OF num AN hello
BUHBYE
GIMMEH monde

   VISIBLE SUM OF monde AN num
    VISIBLE monde

    GIMMEH num
    GIMMEH monde

    VISIBLE DIFF OF num AN monde
KTHXBYE"""

print("--- Tokens ---")
tokens = get_tokens(code)
for t in tokens:
    print(t)

print("\n--- Parsing ---")
parser = Parser(tokens)
ast = parser.parse()

if parser.errors:
    print("Errors:")
    for e in parser.errors:
        print(e)
else:
    print("AST generated successfully")
    # print(ast)

print("\n--- Executing ---")
interpreter = Interpreter()
result = interpreter.execute(ast)
print("Result:")
print(result)
