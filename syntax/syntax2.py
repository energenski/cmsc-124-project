import sys
import os

# Add parent directory to path to import lexer1
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lexer1 import get_tokens, Token
except ImportError:
    print("Error: Could not import 'lexer1.py'. Make sure it's in the parent directory.", file=sys.stderr)
    sys.exit(1)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.errors = []

    def current_token(self):
        return self.tokens[self.current_index] if self.current_index < len(self.tokens) else None

    def advance(self):
        self.current_index += 1

    def error(self, expected_types):
        token = self.current_token()
        if token:
            expected_str = ' or '.join(expected_types)
            error_msg = (
                f"Syntax Error on line {token.line}, column {token.column}: "
                f"Expected {expected_str}, but found **{token.value}** ({token.label})."
            )
        else:
            error_msg = "Syntax Error: Unexpected End of File"
        self.errors.append(error_msg)
        self.advance()

    def consume(self, expected_type):
        token = self.current_token()
        if token and token.type == expected_type:
            self.advance()
            return token
        else:
            self.error([expected_type])
            return None

    def parse_program(self):
        print("Starting Parsing: <Program>")
        self.consume("HAI")
        
        if self.current_token() and self.current_token().type == "VERSION":
            self.advance()
            if self.current_token().type in ("FLOAT_LITERAL", "INTEGER_LITERAL"):
                self.advance()
            else:
                self.error(["FLOAT_LITERAL", "INTEGER_LITERAL"])
        
        self.parse_code_block()
        self.consume("KTHXBYE")
        
        if not self.errors:
            print("\nParsing Successful! No syntax errors found.")
        else:
            print("\nParsing Failed with the following syntax errors:")
            for err in self.errors:
                print(err)

    def parse_code_block(self):
        print("  | Parsing: <CodeBlock>")
        # Stop at block delimiters
        while self.current_token() and self.current_token().type not in (
            "KTHXBYE", "EOF", "BUHBYE", "OIC", "OMG", "OMGWTF", "TLDR", "YA_RLY", "MEBBE", "NO_WAI", "IM_OUTTA_YR"
        ):
            start_index = self.current_index
            self.parse_statement()
            
            if self.current_index == start_index:
                # Force advance if stuck
                print(f"  | Stuck on token: {self.current_token().value}. Skipping.")
                self.advance()

    def parse_statement(self):
        token = self.current_token()
        if not token:
            return

        print(f"  | Parsing Statement starting with {token.type}")

        if token.type == "I_HAS_A":
            self.parse_variable_decl()
        elif token.type == "VISIBLE":
            self.parse_output_statement()
        elif token.type == "GIMMEH":
            self.parse_input_statement()
        elif token.type in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", 
                            "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", 
                            "NOT", "ALL_OF", "ANY_OF", "BOTH_SAEM", "DIFFRINT", "SMOOSH", "MAEK"):
            self.parse_expression()
        elif token.type == "IDENTIFIER":
            # Could be assignment or just an expression
            # Lookahead to see if it's assignment (R) or type cast (IS NOW A)
            if self.current_index + 1 < len(self.tokens):
                next_token = self.tokens[self.current_index + 1]
                if next_token.type == "R":
                    self.parse_assignment()
                elif next_token.type == "IS_NOW_A":
                    self.parse_type_cast()
                else:
                    self.parse_expression()
            else:
                self.parse_expression()
        elif token.type == "ORLY":
            self.parse_if_statement()
        elif token.type == "WTF":
            self.parse_switch_statement()
        elif token.type == "IM_IN_YR":
            self.parse_loop_statement()
        else:
            # If it's a literal, it's an expression statement
            if token.type in ("INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL"):
                self.parse_expression()
            else:
                self.error(["Statement"])

    def parse_variable_decl(self):
        print("    - Parsing: <VariableDecl>")
        self.consume("I_HAS_A")
        self.consume("IDENTIFIER")
        if self.current_token().type == "ITZ":
            self.advance()
            self.parse_expression()

    def parse_assignment(self):
        print("    - Parsing: <Assignment>")
        self.consume("IDENTIFIER")
        self.consume("R")
        self.parse_expression()

    def parse_type_cast(self):
        print("    - Parsing: <TypeCast>")
        self.consume("IDENTIFIER")
        self.consume("IS_NOW_A")
        self.consume("TYPE")

    def parse_output_statement(self):
        print("    - Parsing: <OutputStatement>")
        self.consume("VISIBLE")
        self.parse_expression()
        while self.current_token() and self.current_token().type == "AN": # Visible can take multiple args? usually implicit concatenation or +
             # The grammar usually implies VISIBLE <expr>+
             # But lexer has AN. Let's support AN or just multiple expressions if they follow?
             # Standard LOLCODE VISIBLE takes varargs.
             # For now, let's assume AN separator or just expressions.
             # Actually, usually VISIBLE "A" "B" is valid.
             # But let's stick to simple recursion or loop.
             # If next token is expression start, parse it.
             pass
             # For this implementation, let's just parse one expression or handle + (SMOOSH)
             # If we want to support VISIBLE A B C, we need to check if next token starts expression.
             # Simplified:
        # Check for more expressions (simplified)
        while self.current_token() and self.is_expression_start(self.current_token().type):
             self.parse_expression()

    def parse_input_statement(self):
        print("    - Parsing: <InputStatement>")
        self.consume("GIMMEH")
        self.consume("IDENTIFIER")

    def parse_if_statement(self):
        print("    - Parsing: <IfStatement>")
        self.consume("ORLY")
        self.consume("YA_RLY")
        self.parse_code_block()
        
        while self.current_token() and self.current_token().type == "MEBBE":
            self.advance()
            self.parse_expression()
            self.parse_code_block()
            
        if self.current_token() and self.current_token().type == "NO_WAI":
            self.advance()
            self.parse_code_block()
            
        self.consume("OIC")

    def parse_switch_statement(self):
        print("    - Parsing: <SwitchStatement>")
        self.consume("WTF")
        self.consume("OMG")
        self.parse_literal() # Case literal
        self.parse_code_block()
        
        while self.current_token() and self.current_token().type == "OMG":
            self.consume("OMG")
            self.parse_literal()
            self.parse_code_block()
            
        if self.current_token() and self.current_token().type == "OMGWTF":
            self.consume("OMGWTF")
            self.parse_code_block()
            
        self.consume("OIC")

    def parse_loop_statement(self):
        print("    - Parsing: <LoopStatement>")
        self.consume("IM_IN_YR")
        self.consume("IDENTIFIER") # Loop label
        
        # Operation (UPPIN/NERFIN)
        if self.current_token().type in ("UPPIN", "NERFIN"):
            self.advance()
            self.consume("YR")
            self.consume("IDENTIFIER")
            
        # Condition (TIL/WILE)
        if self.current_token().type in ("TIL", "WILE"):
            self.advance()
            self.parse_expression()
            
        self.parse_code_block()
        
        self.consume("IM_OUTTA_YR")
        self.consume("IDENTIFIER") # Loop label

    def parse_expression(self):
        token = self.current_token()
        if not token:
            return

        if token.type in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", 
                          "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", 
                          "BOTH_SAEM", "DIFFRINT"):
            self.advance()
            self.parse_expression()
            self.consume("AN")
            self.parse_expression()
        elif token.type in ("ALL_OF", "ANY_OF"):
            self.advance()
            self.parse_expression()
            while self.current_token() and self.current_token().type == "AN":
                self.advance()
                self.parse_expression()
            # Ends implicitly or with MKAY? regex doesn't have MKAY yet.
        elif token.type == "NOT":
            self.advance()
            self.parse_expression()
        elif token.type == "SMOOSH":
            self.advance()
            self.parse_expression()
            while self.current_token() and self.current_token().type == "AN":
                self.advance()
                self.parse_expression()
        elif token.type == "MAEK":
            self.advance()
            self.parse_expression()
            if self.current_token().type == "A":
                self.advance()
            self.consume("TYPE")
        elif token.type in ("IDENTIFIER", "IT"):
            self.advance()
        elif token.type in ("INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL"):
            self.advance()
        else:
            self.error(["Expression"])

    def parse_literal(self):
        if self.current_token().type in ("INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL"):
            self.advance()
        else:
            self.error(["Literal"])

    def is_expression_start(self, type):
        return type in ("IDENTIFIER", "IT", "INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL",
                        "SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", 
                        "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", 
                        "NOT", "ALL_OF", "ANY_OF", "BOTH_SAEM", "DIFFRINT", "SMOOSH", "MAEK")


def main():
    if len(sys.argv) != 2:
        print("Usage: python syntax2.py <lolcode_file.lol>", file=sys.stderr)
        sys.exit(2)
    
    path = sys.argv[1]
    code = ""
    
    if path == "-":
        code = sys.stdin.read()
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            sys.exit(1)

    tokens = get_tokens(code)
    parser = Parser(tokens)
    parser.parse_program()

if __name__ == "__main__":
    main()
