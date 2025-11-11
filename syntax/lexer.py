import re
from collections import OrderedDict

#this dictionary is for properly identifying the token types to see if it's being properly captured
TOKEN_LABELS = {
    #program structure
    "HAI": "Code Delimiter",
    "KTHXBYE": "Code Delimiter",
    "WAZZUP": "Variable List Delimiter",
    "BUHBYE": "Variable List Delimiter",

    #Comments
    "BTW": "Single-Line Comment Delimiter",
    "OBTW": "Multi-Line Comment Delimiter (Start)",
    "TLDR": "Multi-Line Comment Delimiter (End)",

    #variable declaration / assignment
    "I_HAS_A": "Variable Declaration",
    "ITZ": "Variable Assignment (following I HAS A)",
    "R": "Assignment Operator",

    #operators
    "SUM_OF": "Arithmetic Operator",
    "DIFF_OF": "Arithmetic Operator",
    "PRODUKT_OF": "Arithmetic Operator",
    "QUOSHUNT_OF": "Arithmetic Operator",
    "MOD_OF": "Arithmetic Operator",
    "BIGGR_OF": "Comparison Operator",
    "SMALLR_OF": "Comparison Operator",

    #logic operators
    "BOTH_OF": "Logic Operator",
    "EITHER_OF": "Logic Operator",
    "WON_OF": "Logic Operator",
    "NOT": "Logic Operator",
    "ANY_OF": "Logic Operator",
    "ALL_OF": "Logic Operator",

    #comparison operators
    "BOTH_SAEM": "Comparison Operator",
    "DIFFRINT": "Comparison Operator",

    #concatenation
    "SMOOSH": "String Concat Keyword",

    #type casting
    "MAEK": "Type Cast Keyword",
    "A": "Type Cast Separator",
    "IS_NOW_A": "Type Cast Keyword",

    #I/O
    "VISIBLE": "Output Keyword",
    "GIMMEH": "Input Keyword",

    #control flow
    "ORLY": "If-Then Start",
    "YA_RLY": "If-Then (True Block)",
    "MEBBE": "If-Then (Else If)",
    "NO_WAI": "If-Then (Else Block)",
    "OIC": "Control Flow End",
    "WTF": "Switch Start",
    "OMG": "Switch Case",
    "OMGWTF": "Switch Default Case",

    #loop
    "IM_IN_YR": "Loop Start",
    "UPPIN": "Loop Operation (Increment)",
    "NERFIN": "Loop Operation (Decrement)",
    "YR": "Parameter/Variable Designator",
    "TIL": "Loop Condition (Until)",
    "WILE": "Loop Condition (While)",
    "IM_OUTTA_YR": "Loop End",

    #miscellaneous lexemes
    "AN": "Multiple Parameter Separator",
    "VERSION": "Version Marker",
    "IT": "Temporary Variable",
    "TYPE_LITERAL": "Type Literal", # Renamed from TYPE for clarity
    "TROOF_TRUE": "Boolean Value (True)",
    "TROOF_FALSE": "Boolean Value (False)",
}

#ordered dictionary is essential for priority of token matching (Maximal Munch)
TOKEN_REGEX = OrderedDict([
    #comments
    ("BTW", r"BTW[^\n]*"), 
    ("OBTW", r"\bOBTW\b"), 
    ("TLDR", r"\bTLDR\b"), 

    #spaces or newlines (consumed but not returned to parser)
    ("WHITESPACE", r"[ \t]+"),
    ("NEWLINE", r"\n"),

    #keywords (multi-word must come before single-word components)
    ("I_HAS_A", r"\bI\s+HAS\s+A\b"),
    ("IS_NOW_A", r"\bIS\s+NOW\s+A\b"),
    ("SUM_OF", r"\bSUM\s+OF\b"),
    ("DIFF_OF", r"\bDIFF\s+OF\b"),
    ("PRODUKT_OF", r"\bPRODUKT\s+OF\b"),
    ("QUOSHUNT_OF", r"\bQUOSHUNT\s+OF\b"),
    ("MOD_OF", r"\bMOD\s+OF\b"),
    ("BIGGR_OF", r"\bBIGGR\s+OF\b"),
    ("SMALLR_OF", r"\bSMALLR\s+OF\b"),
    ("BOTH_SAEM", r"\bBOTH\s+SAEM\b"),
    ("EITHER_OF", r"\bEITHER\s+OF\b"),
    ("BOTH_OF", r"\bBOTH\s+OF\b"),
    ("WON_OF", r"\bWON\s+OF\b"),

    #keywords (single-word)
    ("HAI", r"\bHAI\b(?:\s+VERSION)?"), # optional version after hai
    ("KTHXBYE", r"\bKTHXBYE\b"),
    ("WAZZUP", r"\bWAZZUP\b"),
    ("BUHBYE", r"\bBUHBYE\b"),
    ("DIFFRINT", r"\bDIFFRINT\b"),
    ("ITZ", r"\bITZ\b"),
    ("R", r"\bR\b"),
    ("NOT", r"\bNOT\b"),
    ("SMOOSH", r"\bSMOOSH\b"),
    ("MAEK", r"\bMAEK\b"),
    ("A", r"\bA\b"),
    ("VISIBLE", r"\bVISIBLE\b"),
    ("GIMMEH", r"\bGIMMEH\b"),
    ("AN", r"\bAN\b"),
    ("IT", r"\bIT\b"),
    ("VERSION", r"\bVERSION\b"),
    ("ORLY", r"\bORLY\b"),
    ("YA_RLY", r"\bYA_RLY\b"),
    ("MEBBE", r"\bMEBBE\b"),
    ("NO_WAI", r"\bNO_WAI\b"),
    ("OIC", r"\bOIC\b"),
    ("WTF", r"\bWTF\b"),
    ("OMG", r"\bOMG\b"),
    ("OMGWTF", r"\bOMGWTF\b"),


    #literals
    ("TROOF_LITERAL", r"\b(WIN|FAIL)\b"), 
    ("STRING", r'"([^"\\]|\\.)*"'),
    ("FLOAT_LITERAL", r"[+-]?\d+\.\d+"),
    ("INTEGER_LITERAL", r"[+-]?\d+"),
    ("TYPE_LITERAL", r"\b(NUMBR|NUMBAR|YARN|TROOF|NOOB)\b"), 
    
    #identifiers
    ("IDENTIFIER", r"[a-zA-Z][a-zA-Z0-9_]*"),
    
    #catch all
    ("UNKNOWN", r"."),
])

tok_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_REGEX.items())
token_re = re.compile(tok_regex, re.MULTILINE)

class Token:
    """Represents a token with its type, value, and location."""
    def __init__(self, type, value, line=1, column=1):
        self.type = type
        self.value = value
        # Add the full label for better error reporting in the parser
        self.label = TOKEN_LABELS.get(type, type) 
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Line {self.line}, Col {self.column})"

def lexer(code):
    """
    Performs lexical analysis (tokenization) on the LOLCODE source code.
    Returns a list of Token objects, filtering out comments and whitespace.
    """
    tokens = []
    in_comment = False
    position = 0
    line_num = 1
    col_num = 1

    while position < len(code):
        match = token_re.match(code, position)
        
        if match:
            type = match.lastgroup
            value = match.group()
            match_len = len(value)
            
            # Line/Column Tracking
            if type == "NEWLINE":
                line_num += 1
                col_num = 1
            else:
                col_num += match_len
            
            # Comment Handling
            if type == "BTW":
                # Skip to next line
                newline_pos = code.find('\n', position)
                position = newline_pos if newline_pos != -1 else len(code)
                continue
            elif type == "OBTW":
                in_comment = True
            elif type == "TLDR":
                in_comment = False
            
            # Skip consumed tokens
            if in_comment or type in ("WHITESPACE", "NEWLINE"):
                position = match.end()
                continue
            
            # Store the token
            tokens.append(Token(type, value, line_num, col_num - match_len))
            position = match.end()
            
        else:
            # Handle unknown characters (single character match)
            unknown_char = code[position]
            tokens.append(Token("UNKNOWN", unknown_char, line_num, col_num))
            position += 1
            col_num += 1

    # Add an End-of-File marker for the parser
    tokens.append(Token("EOF", "", line_num, col_num))
    return tokens

if __name__ == "__main__":
    import sys
    # This block allows lexer.py to be run independently for testing the tokenizer
    if len(sys.argv) != 2:
        print("Usage: python lexer.py <lolcode_file.lol>", file=sys.stderr)
        sys.exit(2)
    
    path = sys.argv[1]
    code = ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("--- Tokens Generated ---")
    generated_tokens = lexer(code)
    for token in generated_tokens:
        print(token)