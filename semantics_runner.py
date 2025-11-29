import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from semantics.semantics1 import SemanticAnalyzer, Types
from syntax.syntax2 import Parser
from lexer1 import get_tokens

# --- Monkey-patching infer_expr_type ---
def infer_expr_type(self, node):
    if not node:
        return Types.NOOB
        
    ntype = node.get('node_type')
    
    if ntype == 'operand':
        val = node.get('value')
        # Check if it's a variable usage
        if isinstance(val, str) and not (val.startswith('"') and val.endswith('"')) and val not in ('WIN', 'FAIL'):
             # It's a variable identifier
             # We need to look it up to know its type
             # But we can't easily do that without running the analysis.
             # However, analyze_node calls check_variable_usage which returns the type.
             # So if we are here, we might be inferring type of a literal OR a variable.
             
             # If it is a variable, we should look it up.
             info = self.lookup_var_info(val)
             if info:
                 return info['current_type']
             return Types.WTF # Should have been caught by check_variable_usage
        
        # It's a literal
        if isinstance(val, int): return Types.NUMBR
        if isinstance(val, float): return Types.NUMBAR
        if isinstance(val, str):
            if val.startswith('"') and val.endswith('"'): return Types.YARN
            if val in ('WIN', 'FAIL', 'true', 'false'): return Types.TROOF
            # If it's just a string but not quoted and not bool, it might be an identifier that slipped through?
            # Or it's a raw string from lexer?
            # Lexer gives STRING with quotes.
            return Types.YARN 
        return Types.ANY

    elif ntype == 'binary_op':
        # For now, simplify: Math -> NUMBAR (or NUMBR), Logic/Comparison -> TROOF
        op = node.get('op')
        if op in ['SUM_OF', 'DIFF_OF', 'PRODUKT_OF', 'QUOSHUNT_OF', 'MOD_OF', 'BIGGR_OF', 'SMALLR_OF']:
             # Simplified inference: if we knew operands we could be specific
             return Types.NUMBAR 
        if op in ['BOTH_OF', 'EITHER_OF', 'WON_OF', 'BOTH_SAEM', 'DIFFRINT']:
            return Types.TROOF
            
    elif ntype == 'unary_op':
        if node.get('op') == 'NOT':
            return Types.TROOF
            
    elif ntype == 'n_ary_op':
        if node.get('op') == 'SMOOSH':
            return Types.YARN
        return Types.TROOF # ALL OF / ANY OF
        
    elif ntype == 'type_cast':
        return node.get('type')
        
    return Types.NOOB

# Inject the method into the class
SemanticAnalyzer.infer_expr_type = infer_expr_type
# ---------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python semantics_runner.py <file.lol>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # 1. Tokenize
    tokens = get_tokens(code)
    
    # 2. Parse
    parser = Parser(tokens)
    ast = parser.parse()
    
    if parser.errors:
        print("Syntax Errors:")
        for err in parser.errors:
            print(err)
        sys.exit(1)

    # 3. Analyze
    analyzer = SemanticAnalyzer()
    analyzer.analyze_node(ast)
    
    if analyzer.errors:
        print("Semantic Errors:")
        for err in analyzer.errors:
            print(err)
    else:
        print("Semantic Analysis Passed! No errors found.")
        # Optionally print symbol table or other info if desired
        # print("Final Scope:", analyzer.scopes[0])

if __name__ == "__main__":
    main()
