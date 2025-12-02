import re
import sys
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
    "GTFO": "Break Statement",

    #functions
    "HOW_IZ_I": "Function Definition Start",
    "IF_U_SAY_SO": "Function Definition End",
    "I_IZ": "Function Call",
    "FOUND_YR": "Return Statement",
    "MKAY": "Infinite Arity End",

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
    "PLUS": "Concatenation Operator",
    "VERSION": "Version Marker",
    "IT": "Temporary Variable",
    "TYPE": "Type Literal",
    "TROOF_TRUE": "Boolean Value (True)",
    "TROOF_FALSE": "Boolean Value (False)",
}

#this dictionary provides the regex for the tokens, whether it expects spaces etc or another arguments
#ordered dictionary is essential since the order in which regular expressions are defined directly 
#determines the priority of token matching

#we follow the maximal munch principle where tokens that are substrings of longer tokens must be 
#defined before the longer token

#also, reserved keywords must always be checked before the generic identifier pattern
TOKEN_REGEX = OrderedDict([
    #comments
    ("BTW", r"BTW[^\n]*"),           #single Comment
    ("OBTW", r"\bOBTW\b"),           #multiline comment start
    ("TLDR", r"\bTLDR\b"),           #multiline comment end

    #spaces or newlines
    ("WHITESPACE", r"[ \t]+"),
    ("NEWLINE", r"\n"),
    ("LINEBREAK", r"newline"),

    #delimiters
    ("HAI", r"\bHAI\b(?:\s+VERSION)?"), #optional version after hai
    ("KTHXBYE", r"\bKTHXBYE\b"),
    ("WAZZUP", r"\bWAZZUP\b"),
    ("BUHBYE", r"\bBUHBYE\b"),

    #keywords
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
    ("DIFFRINT", r"\bDIFFRINT\b"),
    ("BOTH_OF", r"\bBOTH\s+OF\b"),
    ("EITHER_OF", r"\bEITHER\s+OF\b"),
    ("WON_OF", r"\bWON\s+OF\b"),
    ("ALL_OF", r"\bALL\s+OF\b"),
    ("ANY_OF", r"\bANY\s+OF\b"),

    ("ITZ", r"\bITZ\b"),
    ("R", r"\bR\b"),
    ("NOT", r"\bNOT\b"),
    ("SMOOSH", r"\bSMOOSH\b"),
    ("MAEK", r"\bMAEK\b"),
    ("A", r"\bA\b"),
    ("VISIBLE", r"\bVISIBLE\b"),
    ("GIMMEH", r"\bGIMMEH\b"),
    ("AN", r"\bAN\b"),
    ("PLUS", r"\+"),
    ("IT", r"\bIT\b"),
    ("VERSION", r"\bVERSION\b"),

    #control flow
    ("ORLY", r"\b(O\s+RLY|ORLY)\??"),
    ("YA_RLY", r"\bYA\s+RLY\b"),
    ("MEBBE", r"\bMEBBE\b"),
    ("NO_WAI", r"\bNO\s+WAI\b"),
    ("OIC", r"\bOIC\b"),
    ("WTF", r"\bWTF\??"),
    ("OMG", r"\bOMG\b"),
    ("OMGWTF", r"\bOMGWTF\b"),
    ("GTFO", r"\bGTFO\b"),

    #functions
    ("HOW_IZ_I", r"\bHOW\s+IZ\s+I\b"),
    ("IF_U_SAY_SO", r"\bIF\s+U\s+SAY\s+SO\b"),
    ("I_IZ", r"\bI\s+IZ\b"),
    ("FOUND_YR", r"\bFOUND\s+YR\b"),
    ("MKAY", r"\bMKAY\b"),

    #loops
    ("IM_IN_YR", r"\bIM\s+IN\s+YR\b"),
    ("UPPIN", r"\bUPPIN\b"),
    ("NERFIN", r"\bNERFIN\b"),
    ("YR", r"\bYR\b"),
    ("TIL", r"\bTIL\b"),
    ("WILE", r"\bWILE\b"),
    ("IM_OUTTA_YR", r"\bIM\s+OUTTA\s+YR\b"),

    #literals
    ("TROOF_LITERAL", r"\b(WIN|FAIL|true|false)\b"),
    ("STRING", r'"([^"\\]|\\.)*"'),
    ("FLOAT_LITERAL", r"[+-]?\d+\.\d+"),
    ("INTEGER_LITERAL", r"[+-]?\d+"),
    ("TYPE", r"\b(NUMBR|NUMBAR|YARN|TROOF|NOOB)\b"),
    
    #identifiers
    ("IDENTIFIER", r"[a-zA-Z][a-zA-Z0-9_]*"),
    
    #catch all
    ("UNKNOWN", r"."),
])

#join all patterns into one big regex with named groups

#1. loops through every token name and its corresponding regex
#2. for each token, it wraps the pattern in a named capturing group
#3. when the scanner finds "WAZZUP", it doesn't just know what was found;
#   it knows what kind of token it is.
#4. it allows the scanner to check for all possible tokens simultaneously at every position in the source code
tok_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_REGEX.items())

#1. pre-processes the regular expression string into a regex object
#2. correctly recognize the beginning and end of lines
#contains all tokens in a specific order, arranged how they were defined in the dict
token_re = re.compile(tok_regex, re.MULTILINE)

def print_token(type, value):

    if type == "TROOF_LITERAL":
        if value in ("WIN", "true"):
            print(f"{TOKEN_LABELS['TROOF_TRUE']} {value} {value}")
        else:
            print(f"{TOKEN_LABELS['TROOF_FALSE']} {value} {value}")

    elif type == "FLOAT_LITERAL":
        print(f"Float Literal {value} {value}")

    elif type == "INTEGER_LITERAL":
        print(f"Integer Literal {value} {value}")

    elif type == "STRING":
        content = value.strip('"')
        print('String Delimiter "')
        print(f"String Literal {content} {content}") 
        print('String Delimiter "')

    elif type == "IDENTIFIER":
        print(f"Variable Identifier {value}")

    elif type in TOKEN_LABELS:
        #manually check for the multi-word op used in the test case
        if type in ("BIGGR_OF", "SMALLR_OF", "BOTH_SAEM", "DIFFRINT"):
            print(f"Comparison Operator {value}")
        elif type in ("SUM_OF", "DIFF_OF", "PRODUKT_OF", "QUOSHUNT_OF", "MOD_OF"):
            print(f"Arithmetic Operator {value}")
        else:
            print(f"{TOKEN_LABELS[type]} {value}")

    elif type in ("BTW", "WHITESPACE", "NEWLINE", "LINEBREAK"):
        pass

    else:
        print(f"Unknown token: {value}")
    return

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        
        if type == "IDENTIFIER":
            self.label = "Variable Identifier"
        elif type == "INTEGER_LITERAL":
            self.label = "Integer Literal"
        elif type == "FLOAT_LITERAL":
            self.label = "Float Literal"
        elif type == "STRING":
            self.label = "String Literal"
        elif type == "TROOF_LITERAL":
            if value in ("WIN", "true"):
                self.label = "Boolean Value (True)"
            else:
                self.label = "Boolean Value (False)"
        else:
            self.label = TOKEN_LABELS.get(type, "Unknown")

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.column})"

def get_tokens(code):
    tokens = []
    in_comment = False
    position = 0
    line_num = 1
    line_start = 0

    while position < len(code):
        match = token_re.match(code, position)
        
        if match:
            type = match.lastgroup
            value = match.group()
            
            # Calculate column
            column = position - line_start + 1

            if type == "NEWLINE":
                line_num += 1
                line_start = match.end()
                position = match.end()
                continue
            
            if type == "BTW":
                newline_pos = code.find('\n', position)
                position = newline_pos + 1 if newline_pos != -1 else len(code)
                line_num += 1
                line_start = position
                continue
            elif type == "OBTW":
                in_comment = True
                position = match.end()
                continue
            elif type == "TLDR":
                in_comment = False
                position = match.end()
                continue
                
            if in_comment:
                if '\n' in value:
                     line_num += value.count('\n')
                     last_newline = value.rfind('\n')
                     line_start = position + last_newline + 1
                position = match.end()
                continue
            
            if type in ("WHITESPACE", "LINEBREAK"):
                position = match.end()
                continue

            tokens.append(Token(type, value, line_num, column))
            position = match.end()
            
        else:
            # Handle unknown character
            unknown_char = code[position]
            if unknown_char == '\n':
                line_num += 1
                line_start = position + 1
            else:
                print(f"Unknown token: {unknown_char}")
            position += 1
            
    return tokens

def tokenize(code):
    tokens = get_tokens(code)
    for token in tokens:
        print_token(token.type, token.value)

def main():
    #use argv to only provide input during runtime
    if len(sys.argv) != 2:
        print("Wrong format", file=sys.stderr)
        sys.exit(2)
    
    path = sys.argv[1] 

    if path == "-":
        code = sys.stdin.read()
    else:
        if not path.lower().endswith(".lol"):
            print("Error: Input file is not a LOLCODE file (.lol)", file=sys.stderr)
            sys.exit(2)
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception:
            print(f"Error reading {path}", file=sys.stderr)
            sys.exit(1)
    
    tokenize(code)

if __name__ == "__main__":
    main()

#REFERENCES

#Maximal Munch:                 https://cs.uwaterloo.ca/~cbruni/CS241Resources/lectures/2019_Winter/CS241L09_cfg_post.pdf
#Python RegEx operations:       https://docs.python.org/3/library/re.html
#sys.argv:                      https://www.geeksforgeeks.org/python/how-to-use-sys-argv-in-python/
#python for lexical analysis:   https://github.com/SixSen/lexical-analysis/blob/master/%E8%AF%8D%E6%B3%95.py
#                               https://github.com/Abduallah-Elmaraghy/Analysis_Part_Compiler_Course_Project/blob/main/Lexical%20Analyzer/lexical_analyzer.py
#discussions on re.compile():   http://stackoverflow.com/questions/452104/is-it-worth-using-pythons-re-compile
