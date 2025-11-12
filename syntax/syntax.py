import sys
try:
    from lexer import lexer, Token
except ImportError:
    print("Error: Could not import 'lexer.py'. Make sure it's in the same directory.", file=sys.stderr)
    sys.exit(1)


class Parser:
    # init parser
    def __init__(self, tokens):
        # list of tokens
        self.tokens = tokens
        # current position
        self.current_index = 0
        # error handler
        self.errors = []

    # get current token
    def current_token(self):
        """Returns the current token."""
        return self.tokens[self.current_index] if self.current_index < len(self.tokens) else None

    # move to the next token
    def advance(self):
        """Moves to the next token."""
        self.current_index += 1

    # record and handle syntax errors
    def error(self, expected_types):
        """Records a syntax error."""
        token = self.current_token()
        expected_str = ' or '.join(expected_types)
        error_msg = (
            f"Syntax Error on line {token.line}, column {token.column}: "
            f"Expected {expected_str}, but found **{token.value}** ({token.label} - {token.type})."
        )
        self.errors.append(error_msg)
        # Simple error recovery: skip the bad token
        self.advance() 

    # consume a token if it nagmamatch sa expected type
    def consume(self, expected_type):
        """Consumes the current token if it matches the expected type, otherwise reports an error."""
        token = self.current_token()
        if token.type == expected_type:
            self.advance()
            return token
        else:
            self.error([expected_type])
            return None 

    # parse yung overall program structure
    def parse_program(self):
        """
        <Program> ::= HAI (VERSION <Numbr Literal>)? <CodeBlock> KTHXBYE
        """
        print("Starting Parsing: <Program>")
        
        # must start with HAI
        self.consume("HAI")
        
        # Optional version keyword followed by a number literal
        if self.current_token().type == "VERSION":
            self.advance()
            # Vexpecting a numeric literal (int or float)
            if self.current_token().type in ("FLOAT_LITERAL", "INTEGER_LITERAL"):
                self.advance()
            else:
                 self.error(["FLOAT_LITERAL", "INTEGER_LITERAL"])
        
        self.parse_code_block()
        # end of program marker 'KTHXBYTE'
        self.consume("KTHXBYE")
        # ensure na na-end yung file ng maayos
        self.consume("EOF")

        # if walang syntax error then parsing was successful
        if not self.errors:
            print("\nParsing Successful! No syntax errors found.")
        else:
            print("\nParsing Failed with the following syntax errors:")
            for err in self.errors:
                print(err)
    
    # Parse a code block which contains one or more statements
    def parse_code_block(self):
        """
        <CodeBlock> ::= (<Statement>)*
        """
        print("  | Parsing: <CodeBlock>")
        
        # Parse statements until a block delimiter or EOF
        while self.current_token().type not in ("KTHXBYE", "EOF", "BUHBYE", "OIC", "OMG", "OMGWTF", "TLDR", "YA_RLY", "MEBBE", "NO_WAI", "IM_OUTTA_YR"):
            
            start_index = self.current_index
            self.parse_statement()
            
            # Error recovery: prevent infinite loops if a statement fails to advance tokens
            if self.current_index == start_index:
                print(f"  | Attempting recovery by skipping token: {self.current_token().value}")
                self.advance()
                
    # determine if what kind of statement to parse based sa current token
    def parse_statement(self):
        """
        <Statement> ::= <VariableDecl> | <Assignment> | <OutputStatement> | <InputStatement> | <IfStatement> | <LoopStatement> | ...
        """
        token_type = self.current_token().type
        
        if token_type == "I_HAS_A":
            self.parse_variable_decl()
        elif token_type == "VISIBLE":
            self.parse_output_statement()
        elif token_type == "GIMMEH":
            self.parse_input_statement()
        elif token_type in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", "NOT"):
            # A calculation/operation being performed standalone
            self.parse_operation()
        elif token_type == "IDENTIFIER":
            # Assume it's an assignment starting with a variable name
            self.parse_assignment()
        elif token_type == "ORLY":
            # If-Then statement
            self.parse_if_statement()
        # Add other statement parsers here (WTF, IM_IN_YR, etc.)
        else:
            self.error(["I_HAS_A", "VISIBLE", "GIMMEH", "IDENTIFIER", "Operation", "ORLY", "..."]) 

    # Parse literal values (strings, numbers, booleans)
    def parse_literal(self):
        """
        <Literal> ::= <String> | <Integer Literal> | <Float Literal> | <Troof Literal>
        """
        token_type = self.current_token().type
        if token_type in ("STRING", "INTEGER_LITERAL", "FLOAT_LITERAL", "TROOF_LITERAL"):
            self.advance()
            return True
        else:
            self.error(["STRING", "INTEGER_LITERAL", "FLOAT_LITERAL", "TROOF_LITERAL"])
            return False

    # Parse either a variable, literal, or the keyword 'IT'
    def parse_variable_or_literal(self):
        """
        <VariableOrLiteral> ::= <Identifier> | <Literal> | IT
        """
        token_type = self.current_token().type
        if token_type == "IDENTIFIER":
            return self.consume("IDENTIFIER")
        elif token_type == "IT":
            return self.consume("IT")
        elif token_type in ("STRING", "INTEGER_LITERAL", "FLOAT_LITERAL", "TROOF_LITERAL"):
            return self.parse_literal()
        else:
            self.error(["IDENTIFIER", "Literal", "IT"])
            return None
    # Parse general expressions (variables, literals, or operations)
    def parse_expression(self):
        """
        <Expression> ::= <VariableOrLiteral> | <Operation>
        (Recursively calls parse_operation for complex expressions)
        """
        token_type = self.current_token().type
        # If it's an operation keyword, parse operation recursively
        if token_type in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "BIGGR_OF", "BOTH_OF", "NOT", "BOTH_SAEM", "DIFFRINT"):
            self.parse_operation()
            return True
        else:
            # Otherwise, treat as variable/literal
            return self.parse_variable_or_literal()

    # Parse arithmetic/logical operations
    def parse_operation(self):
        """
        <Operation> ::= <BinaryOp> <Expression> AN <Expression> | <UnaryOp> <Expression>
        """
        op_type = self.current_token().type
        print(f"    - Parsing: <Operation> ({op_type})")

        # Binary Operations (SUM_OF, BOTH_OF, etc.)
        if op_type in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", "BIGGR_OF", "SMALLR_OF", 
                       "BOTH_OF", "EITHER_OF", "WON_OF", "BOTH_SAEM", "DIFFRINT"):
            self.advance()
            self.parse_expression() # Operand 1
            self.consume("AN")
            self.parse_expression() # Operand 2
        
        # Unary Operations (NOT)
        elif op_type == "NOT":
            self.advance()
            self.parse_expression() # Operand
            
        else:
            self.error(["Binary Operator", "NOT"])
    # Parse variable declarations
    def parse_variable_decl(self):
        """
        <VariableDecl> ::= I HAS A <Identifier> (ITZ <Expression>)?
        """
        print("    - Parsing: <VariableDecl>")
        self.consume("I_HAS_A")
        self.consume("IDENTIFIER")
        
        # Optional initialization with ITZ
        if self.current_token().type == "ITZ":
            self.advance() # Consume ITZ
            self.parse_expression() # Initial value

    # Parse variable assignments
    def parse_assignment(self):
        """
        <Assignment> ::= <Identifier> R <Expression>
        """
        print("    - Parsing: <Assignment>")
        self.consume("IDENTIFIER")
        self.consume("R")
        self.parse_expression()
        
    # Parse print/output statements
    def parse_output_statement(self):
        """
        <OutputStatement> ::= VISIBLE <Expression> (AN <Expression>)*
        """
        print("    - Parsing: <OutputStatement>")
        self.consume("VISIBLE")
        
        # Must have at least one expression
        self.parse_expression()
        
        # Check for multiple expressions separated by AN
        while self.current_token().type == "AN":
            self.advance()
            self.parse_expression()

     # Parse input statements       
    def parse_input_statement(self):
        """
        <InputStatement> ::= GIMMEH <Identifier>
        """
        print("    - Parsing: <InputStatement>")
        self.consume("GIMMEH")
        self.consume("IDENTIFIER")
    # Parse conditional (if-else) statements
    def parse_if_statement(self):
        """
        <IfStatement> ::= ORLY <YaRly> (<Mebbe>)* (<NoWai>)? OIC
        <YaRly> ::= YA RLY <CodeBlock>
        <Mebbe> ::= MEBBE <Expression> <CodeBlock>
        <NoWai> ::= NO WAI <CodeBlock>
        """
        print("    - Parsing: <IfStatement> (ORLY)")
        self.consume("ORLY")
        
        # YA RLY Block (Mandatory)
        self.consume("YA_RLY")
        self.parse_code_block()
        
        # MEBBE Blocks (Zero or More)
        while self.current_token().type == "MEBBE":
            self.advance()
            self.parse_expression() # Condition for MEBBE
            self.parse_code_block()
            
        # NO WAI Block (Optional)
        if self.current_token().type == "NO_WAI":
            self.advance()
            self.parse_code_block()
            
        self.consume("OIC") # End of the IF block


# main function
def main():
    # Ensure correct usage
    if len(sys.argv) != 2:
        print("Usage: python parser.py <lolcode_file.lol>", file=sys.stderr)
        sys.exit(2)
    
    path = sys.argv[1] 
    code = ""

     # Allow reading from stdin using '-'
    if path == "-":
        code = sys.stdin.read()
    else:
         # Allow reading from stdin using '-'
        if not path.lower().endswith(".lol"):
            print("Error: Input file is not a LOLCODE file (.lol)", file=sys.stderr)
            sys.exit(2)
         # Attempt to open and read file
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            sys.exit(1)
    # Generate tokens using lexer
    tokens = lexer(code)

    # start synatax analysis
    print("\n--- 2. Syntax Analysis ---")
    parser = Parser(tokens)
    parser.parse_program()

if __name__ == "__main__":
    main()