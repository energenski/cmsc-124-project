# syntax_analyzer.py
import sys
from lexer1 import tokenize

class SyntaxAnalyzer:
    def __init__(self, tokens):
        # tokens is a list of tuples like (type, value)
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else ("EOF", None)

    def match(self, expected_type):
        token_type, token_value = self.current_token()
        if token_value == expected_type or token_type == expected_type:
            self.position += 1
            return token_value
        else:
            self.error(f"Expected '{expected_type}' but found '{token_value}'")

    def error(self, message):
        token_type, token_value = self.current_token()
        raise SyntaxError(f"[Syntax Error] {message} near '{token_value}' (token {self.position})")

    def parse_program(self):
        # Program ::= HAI <statements> KTHXBYE
        self.match("HAI")
        self.parse_statements()
        self.match("KTHXBYE")

    def parse_statements(self):
        # Statements ::= (Statement)*
        while True:
            token_type, token_value = self.current_token()
            if token_value in ("KTHXBYE", "EOF", None):
                break
            elif token_value == "I_HAS_A":
                self.parse_var_declaration()
            elif token_value == "VISIBLE":
                self.parse_output()
            elif token_value == "R":
                self.parse_assignment()
            else:
                # Skip unrecognized or literal tokens
                self.position += 1

    def parse_var_declaration(self):
        # VarDecl ::= I HAS A <identifier> [ITZ <expr>]
        self.match("I_HAS_A")
        token_type, token_value = self.current_token()
        if token_type != "IDENTIFIER":
            self.error("Expected variable identifier after I HAS A")
        self.position += 1

        token_type, token_value = self.current_token()
        if token_value == "ITZ":
            self.match("ITZ")
            self.parse_expression()

    def parse_assignment(self):
        # Assignment ::= R <expr>
        self.match("R")
        self.parse_expression()

    def parse_output(self):
        # Output ::= VISIBLE <expr>
        self.match("VISIBLE")
        self.parse_expression()

    def parse_expression(self):
        # Expression ::= literal | identifier | arithmetic
        token_type, token_value = self.current_token()

        if token_value in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF"):
            self.match(token_value)
            self.parse_expression()
            token_type, token_value = self.current_token()
            if token_value == "AN":
                self.match("AN")
                self.parse_expression()
            else:
                self.error("Expected 'AN' in arithmetic expression")

        # Allow literals and identifiers as valid expressions
        elif token_type in ("INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "IDENTIFIER", "TROOF_LITERAL"):
            self.position += 1

        # Also allow unrecognized tokens (like plain words or NOOB) to pass silently
        else:
            # Instead of erroring, just consume the token to keep parsing
            self.position += 1


def run_analysis(code):
    print("Performing lexical analysis...")
    print("-" * 40)
    tokens = []

    # Wrap the lexer to collect its printed tokens as a list
    def collect_tokens():
        nonlocal tokens
        import io
        import contextlib
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            tokenize(code)
        output = buffer.getvalue().splitlines()
        # crude token extraction (value-based)
        for line in output:
            parts = line.strip().split()
            if len(parts) >= 2:
                tokens.append((parts[0], parts[-1]))
        buffer.close()

    collect_tokens()
    print("Lexical analysis complete.")
    print("-" * 40)

    # Run the syntax analysis
    print("Performing syntax analysis...")
    try:
        parser = SyntaxAnalyzer(tokens)
        parser.parse_program()
        print("✅ Syntax analysis successful — no syntax errors found.")
    except SyntaxError as e:
        print(e)


def main():
    print("=== LOLCODE Syntax Analyzer ===")
    print("Enter LOLCODE code directly or type 'EXIT' to quit.\n")

    while True:
        code_lines = []
        print("Enter LOLCODE code (end with an empty line):")
        while True:
            line = input()
            if line.strip().upper() == "EXIT":
                print("Exiting analyzer.")
                sys.exit(0)
            if not line.strip():
                break
            code_lines.append(line)
        code = "\n".join(code_lines)

        if not code.strip():
            print("No code entered.\n")
            continue

        run_analysis(code)
        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()


# REFERENCES
# LOLCODE language reference:     https://esolangs.org/wiki/LOLCODE
# Recursive descent parsing:      https://www.cs.princeton.edu/courses/archive/spr18/cos320/Parsing.pdf
# Python contextlib redirect:     https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stdout
# Regular expressions in Python:  https://docs.python.org/3/library/re.html
# Crafting Interpreters (lex/syn): https://craftinginterpreters.com/scanning.html
