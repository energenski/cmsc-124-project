import sys
import os

# Add parent directory to path to import lexer1
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lexer1 import get_tokens, Token
except ImportError:
    try:
        from lexer1 import get_tokens, Token
    except ImportError:
        print("Error: Could not import 'lexer1.py'. Make sure it's in the parent directory.", file=sys.stderr)
        sys.exit(1)

import re

VAR_NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []
        self.variables_declared = set()
        self.in_wazzup = False

    def current(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else Token("EOF", "", -1, -1)

    def peek(self):
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return Token("EOF", "", -1, -1)

    def eat(self, token_type):
        if self.current().type == token_type:
            self.position += 1
        else:
            self.record_error(f"Expected {token_type}, got {self.current().type}", self.current())
            self.position += 1

    def record_error(self, message, token):
        self.errors.append(f"Line {token.line}: {message} (token: '{token.value}')")

    def parse(self):
        self.skip_comments()
        self.program()
        if self.current().type != "EOF":
            self.record_error("Unexpected tokens after program end", self.current())

    def skip_comments(self):
        while self.current().type in ("BTW", "OBTW"):
            self.position += 1

    def program(self):
        if self.current().type != "HAI":
            self.record_error("Program must start with HAI", self.current())
            if self.current().type != "HAI":
                 self.position += 1
        else:
            self.eat("HAI")
            if self.current().type == "VERSION":
                self.eat("VERSION") 

        if self.current().type == "WAZZUP":
            self.in_wazzup = True
            self.eat("WAZZUP")
            while self.current().type != "BUHBYE" and self.current().type != "EOF":
                self.statement()
            if self.current().type != "BUHBYE":
                self.record_error("Missing BUHBYE after WAZZUP", self.current())
            else:
                self.eat("BUHBYE")
            self.in_wazzup = False

        while self.current().type != "KTHXBYE" and self.current().type != "EOF":
            self.statement()

        if self.current().type != "KTHXBYE":
            self.record_error("Program must end with KTHXBYE", self.current())
        else:
            self.eat("KTHXBYE")

    def statement(self):
        tok = self.current().type
        if tok == "I_HAS_A":
            self.var_declaration()
        elif tok == "IDENTIFIER":
            if self.peek().type == "R":
                self.assignment()
            elif self.peek().type == "IS_NOW_A":
                self.type_cast()
            else:
                self.parse_expression()
        elif tok == "VISIBLE":
            self.output_statement()
        elif tok == "GIMMEH":
            self.input_statement()
        elif tok == "ORLY":
            self.if_statement()
        elif tok == "IM_IN_YR":
            self.loop_statement()
        elif tok == "HOW_IZ_I":
            self.function_def()
        elif tok == "WTF":
            self.switch_statement()
        elif tok == "GTFO":
            self.eat("GTFO")
        elif tok == "FOUND_YR":
            self.return_statement()
        elif tok == "I_IZ":
            self.function_call()
        elif tok in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", 
                     "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", 
                     "NOT", "ALL_OF", "ANY_OF", "BOTH_SAEM", "DIFFRINT", "SMOOSH", "MAEK",
                     "INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL"):
            self.parse_expression()
        else:
            self.record_error(f"Unexpected token {tok} in statement", self.current())
            self.position += 1

    def var_declaration(self):
        self.eat("I_HAS_A")
        if self.current().type != "IDENTIFIER":
            self.record_error("Invalid variable name in declaration", self.current())
        else:
            if not VAR_NAME_REGEX.match(self.current().value):
                 self.record_error(f"Invalid variable name format '{self.current().value}'", self.current())
            self.variables_declared.add(self.current().value)
            self.eat("IDENTIFIER")
        
        if self.current().type == "ITZ":
            self.eat("ITZ")
            self.parse_expression()

    def assignment(self):
        self.eat("IDENTIFIER")
        self.eat("R")
        self.parse_expression()

    def type_cast(self):
        self.eat("IDENTIFIER")
        self.eat("IS_NOW_A")
        self.eat("TYPE") 

    def input_statement(self):
        self.eat("GIMMEH")
        if self.current().type != "IDENTIFIER":
            self.record_error("GIMMEH must be followed by variable", self.current())
        else:
            self.eat("IDENTIFIER")

    def output_statement(self):
        self.eat("VISIBLE")
        self.parse_expression()
        while self.current().type in ("AN", "PLUS") or self.is_expression_start(self.current().type):
            if self.current().type in ("AN", "PLUS"):
                self.eat(self.current().type)
            if self.is_expression_start(self.current().type):
                self.parse_expression()

    def if_statement(self):
        self.eat("ORLY")
        if self.current().type != "YA_RLY":
            self.record_error("Missing YA_RLY after ORLY", self.current())
        else:
            self.eat("YA_RLY")
        
        while self.current().type not in ("NO_WAI", "OIC", "MEBBE", "EOF"):
            self.statement()
            
        while self.current().type == "MEBBE":
            self.eat("MEBBE")
            self.parse_expression()
            while self.current().type not in ("NO_WAI", "OIC", "MEBBE", "EOF"):
                self.statement()

        if self.current().type == "NO_WAI":
            self.eat("NO_WAI")
            while self.current().type not in ("OIC", "EOF"):
                self.statement()
        
        if self.current().type != "OIC":
            self.record_error("Missing OIC at end of IF block", self.current())
        else:
            self.eat("OIC")

    def switch_statement(self):
        self.eat("WTF")
        if self.current().type != "OMG":
             self.record_error("Expected OMG after WTF", self.current())
        
        while self.current().type == "OMG":
            self.eat("OMG")
            self.parse_literal()
            while self.current().type not in ("OMG", "OMGWTF", "OIC", "EOF"):
                self.statement()
        
        if self.current().type == "OMGWTF":
            self.eat("OMGWTF")
            while self.current().type not in ("OIC", "EOF"):
                self.statement()
        
        self.eat("OIC")

    def loop_statement(self):
        self.eat("IM_IN_YR")
        if self.current().type == "IDENTIFIER":
            self.eat("IDENTIFIER")
        
        if self.current().type in ("UPPIN", "NERFIN"):
            self.eat(self.current().type)
            if self.current().type == "YR":
                self.eat("YR")
                self.eat("IDENTIFIER")
        
        if self.current().type in ("TIL", "WILE"):
            self.eat(self.current().type)
            self.parse_expression()
            
        while self.current().type not in ("IM_OUTTA_YR", "EOF"):
            self.statement()
            
        if self.current().type != "IM_OUTTA_YR":
            self.record_error("Missing IM_OUTTA_YR at end of loop", self.current())
        else:
            self.eat("IM_OUTTA_YR")
            if self.current().type == "IDENTIFIER":
                self.eat("IDENTIFIER")

    def function_def(self):
        self.eat("HOW_IZ_I")
        if self.current().type != "IDENTIFIER":
            self.record_error("Invalid function name", self.current())
        else:
            self.eat("IDENTIFIER")
        
        while self.current().type == "YR":
            self.eat("YR")
            self.eat("IDENTIFIER")
            if self.current().type == "AN":
                self.eat("AN")
        
        while self.current().type not in ("IF_U_SAY_SO", "EOF"):
            self.statement()
            
        if self.current().type == "IF_U_SAY_SO":
            self.eat("IF_U_SAY_SO")
        else:
            self.record_error("Missing IF U SAY SO at end of function", self.current())

    def function_call(self):
        self.eat("I_IZ")
        if self.current().type != "IDENTIFIER":
            self.record_error("Invalid function name in call", self.current())
        else:
            self.eat("IDENTIFIER")
        
        # Arguments? YR x AN YR y ...
        while self.current().type == "YR":
            self.eat("YR")
            self.parse_expression()
            if self.current().type == "AN":
                self.eat("AN")
        
        # MKAY?
        if self.current().type == "MKAY":
            self.eat("MKAY")

    def return_statement(self):
        self.eat("FOUND_YR")
        self.parse_expression()

    def parse_expression(self):
        tok = self.current().type
        if tok in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", 
                   "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", 
                   "BOTH_SAEM", "DIFFRINT"):
            self.eat(tok)
            self.parse_expression()
            if self.current().type == "AN":
                self.eat("AN")
            self.parse_expression()
        elif tok in ("ALL_OF", "ANY_OF"):
            self.eat(tok)
            self.parse_expression()
            while self.current().type == "AN":
                self.eat("AN")
                self.parse_expression()
            if self.current().type == "MKAY":
                self.eat("MKAY")
        elif tok == "NOT":
            self.eat("NOT")
            self.parse_expression()
        elif tok == "SMOOSH":
            self.eat("SMOOSH")
            self.parse_expression()
            while self.current().type == "AN":
                self.eat("AN")
                self.parse_expression()
        elif tok == "MAEK":
            self.eat("MAEK")
            self.parse_expression()
            if self.current().type == "A":
                self.eat("A")
            self.eat("TYPE") 
        elif tok in ("IDENTIFIER", "IT"):
            self.eat(tok)
        elif tok in ("INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL"):
            self.eat(tok)
        else:
            self.record_error(f"Unexpected token in expression: {tok}", self.current())
            self.position += 1

    def parse_literal(self):
        if self.current().type in ("INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL"):
            self.eat(self.current().type)
        else:
            self.record_error("Expected literal", self.current())

    def is_expression_start(self, type):
        return type in ("IDENTIFIER", "IT", "INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL",
                        "SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", 
                        "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", 
                        "NOT", "ALL_OF", "ANY_OF", "BOTH_SAEM", "DIFFRINT", "SMOOSH", "MAEK")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python syntax2.py <lolcode_file.lol>", file=sys.stderr)
        sys.exit(2)

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)

    tokens = get_tokens(code)
    parser = Parser(tokens)
    parser.parse()

    if parser.errors:
        print("\n--- ERRORS DETECTED ---")
        for err in parser.errors:
            print(err)
        print(f"Total errors: {len(parser.errors)}")
        sys.exit(1)
    else:
        print("No errors found.")
