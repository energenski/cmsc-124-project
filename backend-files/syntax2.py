import sys
import os

# Add parent directory to path to import lexer1
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importing
try:
    from lexer1 import get_tokens, Token
except ImportError:
    try:
        from lexer1 import get_tokens, Token
    except ImportError:
        print("Error: Could not import 'lexer1.py'. Make sure it's in the parent directory.", file=sys.stderr)
        sys.exit(1)

# import regex
import re

VAR_NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

class Parser:
    # take a list of tokens
    def __init__(self, tokens):
        # store
        self.tokens = tokens
        self.position = 0
        # list to store any syntax errors
        self.errors = []
        # to  track declared var
        self.variables_declared = set()
        # flagg
        self.in_wazzup = False

    # returns the current token
    def current(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else Token("EOF", "", -1, -1)

    # returns the token aftre the current one
    def peek(self):
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return Token("EOF", "", -1, -1)

    # eat or consume the current token if nag-mamatch sa expected type
    def eat(self, token_type):
        if self.current().type == token_type:
            token = self.current()
            self.position += 1
            return token
        # if hindi nagmamatch
        else:
            self.record_error(f"Expected {token_type}, got {self.current().type}", self.current())
            self.position += 1
            return None

    # function to format and record a syntax error
    def record_error(self, message, token):
        self.errors.append(f"Line {token.line}: {message} (token: '{token.value}')")

    # main function for parsing process
    def parse(self):
        self.skip_comments()
        program_node = self.program()
        if self.current().type != "EOF":
            self.record_error("Unexpected tokens after program end", self.current())
        return program_node

    # skips over BTW (single-line) and OBTW/TLDR (multi-line) comments
    def skip_comments(self):
        while self.current().type in ("BTW", "OBTW"):
            if self.current().type == "BTW":
                self.position += 1
            elif self.current().type == "OBTW":
                self.position += 1
                while self.current().type != "TLDR" and self.current().type != "EOF":
                    self.position += 1
                if self.current().type == "TLDR":
                    self.position += 1

    # parses the main LOLCODE program structure
    def program(self):
        nodes = []
        if self.current().type != "HAI":
            self.record_error("Program must start with HAI", self.current())
            if self.current().type != "HAI":
                 self.position += 1
        # if 'HAI' is founnd
        else:
            self.eat("HAI")
            if self.current().type == "VERSION":
                self.eat("VERSION") 

        # checks for the optional variable declaration blockk
        if self.current().type == "WAZZUP":
            self.in_wazzup = True
            self.eat("WAZZUP")
            var_block = []
            while self.current().type != "BUHBYE" and self.current().type != "EOF":
                stmt = self.statement()
                if stmt:
                    var_block.append(stmt)
            
            nodes.append({"node_type": "var_block", "body": var_block, "line": self.current().line})

            # check for closing token of the variable block
            if self.current().type != "BUHBYE":
                self.record_error("Missing BUHBYE after WAZZUP", self.current())
            # if 'BUHBYE' is found
            else:
                self.eat("BUHBYE")
            self.in_wazzup = False

        # Parse main program statements until KTHXBYE or EOF
        while self.current().type != "KTHXBYE" and self.current().type != "EOF":
            stmt = self.statement()
            if stmt:
                nodes.append(stmt)

        if self.current().type != "KTHXBYE":
            self.record_error("Program must end with KTHXBYE", self.current())
        else:
            self.eat("KTHXBYE")
        
        return {"node_type": "program", "body": nodes}

    # parses a single LOLCODE statement
    def statement(self):
        self.skip_comments()
        # get the type of the current token
        tok = self.current().type
        if tok == "I_HAS_A":
            return self.var_declaration()
        elif tok == "IDENTIFIER":
            if self.peek().type == "R":
                return self.assignment()
            elif self.peek().type == "IS_NOW_A":
                return self.type_cast()
            else:
                # Bare identifier should assign to IT
                expr = self.parse_expression()
                return {"node_type": "assignment", "target": "IT", "expr": expr, "line": expr.get('line')} # Expression as statement (e.g. IT = expr)
        elif tok == "VISIBLE":
            return self.output_statement()
        elif tok == "GIMMEH":
            return self.input_statement()
        elif tok == "ORLY":
            return self.if_statement()
        elif tok == "IM_IN_YR":
            return self.loop_statement()
        elif tok == "HOW_IZ_I":
            return self.function_def()
        elif tok == "WTF":
            return self.switch_statement()
        elif tok == "GTFO":
            line = self.current().line
            self.eat("GTFO")
            return {"node_type": "break", "line": line}
        elif tok == "FOUND_YR":
            return self.return_statement()
        elif tok == "I_IZ":
            return self.function_call()
        elif tok in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", 
                     "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", 
                     "NOT", "ALL_OF", "ANY_OF", "BOTH_SAEM", "DIFFRINT", "SMOOSH", "MAEK",
                     "INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL", "IT"):
            # Standalone expression, implicitly assigns to IT
            expr = self.parse_expression()
            return {"node_type": "assignment", "target": "IT", "expr": expr, "line": expr.get('line')}
        # if the token doesn't match any known statement type
        else:
            # self.record_error(f"Unexpected token {tok} in statement", self.current())
            self.position += 1
            return None

    # parses a var declaration
    def var_declaration(self):
        line = self.current().line
        self.eat("I_HAS_A")
        name = None
        if self.current().type != "IDENTIFIER":
            self.record_error("Invalid variable name in declaration", self.current())
        # If it is an identifier
        else:
            if not VAR_NAME_REGEX.match(self.current().value):
                 self.record_error(f"Invalid variable name format '{self.current().value}'", self.current())
            name = self.current().value
            self.variables_declared.add(name)
            self.eat("IDENTIFIER")
        
        init_val = None
        # check for optional initialization (ITZ expression)
        if self.current().type == "ITZ":
            self.eat("ITZ")
            init_val = self.parse_expression()
            
        return {"node_type": "var_decl", "name": name, "value": init_val, "line": line}

    # Parses an assignment statement
    def assignment(self):
        line = self.current().line
        target = self.current().value
        self.eat("IDENTIFIER")
        self.eat("R")
        expr = self.parse_expression()
        return {"node_type": "assignment", "target": target, "expr": expr, "line": line}

    # Parses an explicit type cast
    def type_cast(self):
        line = self.current().line
        target = self.current().value
        self.eat("IDENTIFIER")
        self.eat("IS_NOW_A")
        target_type = self.current().value
        self.eat("TYPE") 
        return {"node_type": "type_cast", "target": target, "type": target_type, "line": line}

    # Parses an input statement
    def input_statement(self):
        line = self.current().line
        self.eat("GIMMEH")
        var_name = None
        if self.current().type != "IDENTIFIER":
            self.record_error("GIMMEH must be followed by variable", self.current())
        else:
            var_name = self.current().value
            self.eat("IDENTIFIER")
        return {"node_type": "input", "variable": var_name, "line": line}

    # Parses an output statement
    def output_statement(self):
        line = self.current().line
        self.eat("VISIBLE")
        args = []

        # Expect at least one expression
        first_arg = self.parse_expression()
        args.append(first_arg)
        
        # Track the line of the last argument to detect implicit newlines
        last_arg_line = first_arg.get('line', line)

        while self.current().type in ("AN", "PLUS") or self.is_expression_start(self.current().type):
            # Check for implicit concatenation across lines
            if self.current().type not in ("AN", "PLUS"):
                if self.current().line > last_arg_line:
                    break

            # Only eat AN if it is NOT inside SMOOSH
            if self.current().type in ("AN", "PLUS"):
                # Peek previous node
                if args[-1]['node_type'] != 'n_ary_op' or args[-1].get('op') != 'SMOOSH':
                    self.eat(self.current().type)
                else:
                    break  # Stop eating ANs for SMOOSH
            
            args.append(self.parse_expression())
            last_arg_line = args[-1].get('line', last_arg_line)

        return {"node_type": "visible", "args": args, "line": line}

    # Parses an if statement
    def if_statement(self):
        line = self.current().line
        self.eat("ORLY")
        if self.current().type != "YA_RLY":
            self.record_error("Missing YA_RLY after ORLY", self.current())
        # If 'YA_RLY' is present
        else:
            self.eat("YA_RLY")
        
        true_block = []
        # Parse statements in the 'YA RLY' block
        while self.current().type not in ("NO_WAI", "OIC", "MEBBE", "EOF"):
            stmt = self.statement()
            if stmt: true_block.append(stmt)
            
        else_if_blocks = []
        # Loop for optional ELSE IF blocks
        while self.current().type == "MEBBE":
            self.eat("MEBBE")
            cond = self.parse_expression()
            block = []
            while self.current().type not in ("NO_WAI", "OIC", "MEBBE", "EOF"):
                stmt = self.statement()
                if stmt: block.append(stmt)
            else_if_blocks.append({"condition": cond, "body": block})

        else_block = []
        # Check for optional ELSE block
        if self.current().type == "NO_WAI":
            self.eat("NO_WAI")
            while self.current().type not in ("OIC", "EOF"):
                stmt = self.statement()
                if stmt: else_block.append(stmt)
        
        # Check for the mandatory IF block end
        if self.current().type != "OIC":
            self.record_error("Missing OIC at end of IF block", self.current())
        else:
            self.eat("OIC")
            
        return {
            "node_type": "if_stmt",
            "true_block": true_block,
            "else_if_blocks": else_if_blocks,
            "else_block": else_block,
            "line": line
        }

    # Parses a switch statement
    def switch_statement(self):
        line = self.current().line
        self.eat("WTF")
        if self.current().type != "OMG":
             self.record_error("Expected OMG after WTF", self.current())
        
        cases = []
        # Loop for one or more case blocks
        while self.current().type == "OMG":
            self.eat("OMG")
            val = self.parse_literal()
            body = []
            while self.current().type not in ("OMG", "OMGWTF", "OIC", "EOF"):
                stmt = self.statement()
                if stmt: body.append(stmt)
            cases.append({"value": val, "body": body})
        
        default_case = []
        # Check for optional default case
        if self.current().type == "OMGWTF":
            self.eat("OMGWTF")
            while self.current().type not in ("OIC", "EOF"):
                stmt = self.statement()
                if stmt: default_case.append(stmt)
        
        self.eat("OIC")
        return {"node_type": "switch_stmt", "cases": cases, "default": default_case, "line": line}

    # Parses a loop
    def loop_statement(self):
        line = self.current().line
        self.eat("IM_IN_YR")
        label = None
        if self.current().type == "IDENTIFIER":
            label = self.current().value
            self.eat("IDENTIFIER")
        
        operation = None
        var = None
        # Check for optional loop counter operation
        if self.current().type in ("UPPIN", "NERFIN"):
            op_type = self.current().type
            self.eat(op_type)
            if self.current().type == "YR":
                self.eat("YR")
                var = self.current().value
                self.eat("IDENTIFIER")
                operation = {"type": op_type, "variable": var}
        
        condition = None
        # Check for optional loop termination/continuation condition
        if self.current().type in ("TIL", "WILE"):
            cond_type = self.current().type
            self.eat(cond_type)
            expr = self.parse_expression()
            condition = {"type": cond_type, "expr": expr}
            
        body = []
         # Parse statements inside the loop body
        while self.current().type not in ("IM_OUTTA_YR", "EOF"):
            stmt = self.statement()
            if stmt: body.append(stmt)
            
        # Check for the mandatory loop end
        if self.current().type != "IM_OUTTA_YR":
            self.record_error("Missing IM_OUTTA_YR at end of loop", self.current())
        else:
            self.eat("IM_OUTTA_YR")
            if self.current().type == "IDENTIFIER":
                self.eat("IDENTIFIER") # consume label
                
        return {
            "node_type": "loop",
            "label": label,
            "operation": operation,
            "condition": condition,
            "body": body,
            "line": line
        }

    # Parses a function definition
    def function_def(self):
        line = self.current().line
        self.eat("HOW_IZ_I")
        name = None
        if self.current().type != "IDENTIFIER":
            self.record_error("Invalid function name", self.current())
        else:
            name = self.current().value
            self.eat("IDENTIFIER")
        
        params = []
        # Loop for function parameters
        while self.current().type == "YR":
            self.eat("YR")
            pname = self.current().value
            self.eat("IDENTIFIER")
            params.append(pname)
            if self.current().type == "AN":
                self.eat("AN")
        
        body = []
        # Parse statements in the function body
        while self.current().type not in ("IF_U_SAY_SO", "EOF"):
            stmt = self.statement()
            if stmt: body.append(stmt)
            
        # Check for mandatory function end
        if self.current().type == "IF_U_SAY_SO":
            self.eat("IF_U_SAY_SO")
        else:
            self.record_error("Missing IF U SAY SO at end of function", self.current())
            
        return {"node_type": "func_def", "name": name, "params": params, "body": body, "line": line}

    # Parses a function call
    def function_call(self):
        line = self.current().line
        self.eat("I_IZ")
        name = None
        if self.current().type != "IDENTIFIER":
            self.record_error("Invalid function name in call", self.current())
        else:
            name = self.current().value
            self.eat("IDENTIFIER")
        
        args = []
        # Arguments? YR x AN YR y ...
        while self.current().type == "YR":
            self.eat("YR")
            args.append(self.parse_expression())
            if self.current().type == "AN":
                self.eat("AN")
        
        # MKAY?
        if self.current().type == "MKAY":
            self.eat("MKAY")
            
        return {"node_type": "func_call", "name": name, "args": args, "line": line}

    # Parses a return statement
    def return_statement(self):
        line = self.current().line
        self.eat("FOUND_YR")
        expr = self.parse_expression()
        return {"node_type": "return", "value": expr, "line": line}

    # Parses a generic LOLCODE expression
    def parse_expression(self):
        line = self.current().line
        tok = self.current().type
        
        if tok in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", 
                   "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", 
                   "BOTH_SAEM", "DIFFRINT"):
            self.eat(tok)
            left = self.parse_expression()
            if self.current().type == "AN":
                self.eat("AN")
            right = self.parse_expression()
            return {"node_type": "binary_op", "op": tok, "left": left, "right": right, "line": line}
            
        elif tok in ("ALL_OF", "ANY_OF"):
            self.eat(tok)
            operands = []
            operands.append(self.parse_expression())
            while self.current().type == "AN":
                self.eat("AN")
                operands.append(self.parse_expression())
            if self.current().type == "MKAY":
                self.eat("MKAY")
            return {"node_type": "n_ary_op", "op": tok, "operands": operands, "line": line}
            
        elif tok == "NOT":
            self.eat("NOT")
            operand = self.parse_expression()
            return {"node_type": "unary_op", "op": "NOT", "operand": operand, "line": line}
            
        elif tok == "SMOOSH":
            self.eat("SMOOSH")
            operands = []
            operands.append(self.parse_expression())
            while self.current().type == "AN":
                self.eat("AN")
                operands.append(self.parse_expression())
            return {"node_type": "n_ary_op", "op": "SMOOSH", "operands": operands, "line": line}
            
        elif tok == "MAEK":
            self.eat("MAEK")
            expr = self.parse_expression()
            if self.current().type == "A":
                self.eat("A")
            target_type = self.current().value
            self.eat("TYPE") 
            return {"node_type": "type_cast", "expr": expr, "type": target_type, "line": line}
            
        elif tok == "IDENTIFIER":
            val = self.current().value
            self.eat("IDENTIFIER")
            return {"node_type": "operand", "value": val, "kind": "IDENTIFIER", "line": line}
            
        elif tok == "IT":
            self.eat("IT")
            return {"node_type": "operand", "value": "IT", "kind": "IT", "line": line}
            
        elif tok in ("INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL"):
            val = self.current().value
            if tok == "INTEGER_LITERAL":
                val = int(val)
            elif tok == "FLOAT_LITERAL":
                val = float(val)
            elif tok == "STRING":
                val = val.strip('"')
            elif tok == "TROOF_LITERAL":
                pass # keep as WIN/FAIL string for now, or convert to bool
            
            self.eat(tok)
            return {"node_type": "operand", "value": val, "kind": tok, "line": line}
            
        else:
            self.record_error(f"Unexpected token in expression: {tok}", self.current())
            self.position += 1
            return None

    # Parses a literal value (used in switch case OMG blocks)
    def parse_literal(self):
        line = self.current().line
        if self.current().type in ("INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL"):
            val = self.current().value
            if self.current().type == "INTEGER_LITERAL":
                val = int(val)
            elif self.current().type == "FLOAT_LITERAL":
                val = float(val)
            elif self.current().type == "STRING":
                val = val.strip('"')
            self.eat(self.current().type)
            return val
        else:
            self.record_error("Expected literal", self.current())
            return None

    # Helper function to check if a token type can start an expression
    def is_expression_start(self, type):
        return type in ("IDENTIFIER", "IT", "INTEGER_LITERAL", "FLOAT_LITERAL", "STRING", "TROOF_LITERAL",
                        "SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF", 
                        "BIGGR_OF", "SMALLR_OF", "BOTH_OF", "EITHER_OF", "WON_OF", 
                        "NOT", "ALL_OF", "ANY_OF", "BOTH_SAEM", "DIFFRINT", "SMOOSH", "MAEK")

# main function execution
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python syntax2.py <lolcode_file.lol>", file=sys.stderr)
        sys.exit(2)

    # Get the file path 
    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)

    # tokenize the source code
    tokens = get_tokens(code)
    # parsing process
    parser = Parser(tokens)
    ast = parser.parse()

    # Check if any syntax errors were recorded
    if parser.errors:
        print("\n--- ERRORS DETECTED ---")
        for err in parser.errors:
            print(err)
        print(f"Total errors: {len(parser.errors)}")
        sys.exit(1)
    else:
        # print("No errors found.")
        # print(ast) # Debug: print AST
        pass
