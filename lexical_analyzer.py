keywords = {
            "HAI":          "Code Delimiter HAI",
            "KTHXBYE":      "Code Delimiter KTHXBYE",
            "WAZZUP":       "Variable List Delimiter WAZZUP",
            "BUHBYE":       "Variable List Delimiter BUHBYE",
            "I HAS A":      "Variable Declaration I HAS A",
            "ITZ":          "Variable Assignment (following I HAS A) ITZ",
            "R":            "Variable Assignment (following variable name) R",
            "SUM OF":       "Arithmetic Operation SUM OF",
            "DIFF OF":      "Arithmetic Operation DIFF OF",
            "PRODUKT OF":   "Arithmetic Operation PRODUKT OF",
            "QUOSHUNT OF":  "Arithmetic Operation QUOSHUNT OF",
            "MOD OF":       "Arithmetic Operation MOD OF",
            "BIGGR OF":     "Comparison Operator BIGGR OF",
            "SMALLR OF":    "Comparison Operator SMALLR OF",
            "BOTH OF":      "Logical Operator BOTH OF",
            "EITHER OF":    "Logical Operator EITHER OF",
            "WON OF":       "Comparison Operator WON OF",
            "NOT":          "Logical Operator NOT",
            "ANY OF":       "Logical Operator ANY OF",
            "ALL OF":       "Logical Operator ALL OF",
            "BOTH SAEM":    "Comparison Operator BOTH SAEM",
            "DIFFRINT":     "Comparison Operator DIFFRINT",
            "SMOOSH":       "String Operator SMOOSH",
            "MAEK":         "Type Conversion Operator MAEK",
            "A":            "Operator Connection (following an operator) A",
            "IS NOW A":     "Type Casting Operator IS NOW A",
            "VISIBLE":      "Output Identifier VISIBLE",
            "GIMMEH":       "Input Identifier GIMMEH",
            "O RLY?":       "Conditional Delimiter O RLY?",
            "YA RLY":       "Conditional True Block YA RLY",
            "MEBBE":        "Conditional Else-If MEBBE",
            "NO WAI":       "Conditional False Block NO WAI",
            "OIC":          "Conditional Delimiter Block OIC",
            "WTF?":         "Switch Statement Delimiter WTF?",
            "OMG":          "Switch Case OMG",
            "OMGWTF":       "Switch Default OMGWTF",
            "IM IN YR":     "Loop Delimiter IM IN YR",
            "UPPIN":        "Loop Increment UPPIN",
            "NERFIN":       "Loop Decrement NERFIN",
            "YR":           "Loop Variable Reference YR",
            "TIL":          "Loop Condition TIL",
            "WILE":         "Loop Condition WILE",
            "IM OUTTA YR":  "Loop Delimiter IM OUTTA YR",
            "HOW IZ I":     "Function Definition HOW IZ I",
            "IF U SAY SO":  "Function Delimiter IF U SAY SO",
            "GTFO":         "Loop Break Identifier GTFO",
            "FOUND YR":     "Variable Reference (following VISIBLE) FOUND YR",
            "I IZ":         "Variable Assignment I IZ",
            "MKAY":         "Statement Delimiter MKAY",
            "AN":           "Separator (following operators and between operands) AN",
            "IT":           "Implicit Variable Identifier (following VISIBLE) IT",
            }

def non_keyword(token):
    if isinstance(token, int): # if token is integer
        print(f"Integer Literal {token}")
    elif isinstance(token, float): # if token is float
        print(f"Float Literal {token}")
    elif token.startswith('"') and token.endswith('"'): # if token is string
        print(f'String Literal {token}')
    else:
        print(f'Variable Identifier {token}')

variable = input("Enter one line of code: ")
tokens = variable.split()
for token in tokens:
    if token in keywords:
        print(f"{keywords[token]}")
    else:
        non_keyword(token)