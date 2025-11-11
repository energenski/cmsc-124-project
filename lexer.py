import re
import sys

# Ordered dictionary-like list 
token_regex = {
    "Variable Declaration": [r"^I HAS A$"],
    "Variable Assignment (following I HAS A)": [r"^ITZ$"],

    "Arithmetic Operator": [
        r"^SUM OF$", r"^DIFF OF$", r"^PRODUKT OF$",
        r"^QUOSHUNT OF$", r"^MOD OF$"
    ],

    "Comparison Operator": [
        r"^BIGGR OF$", r"^BIGGER OF$", r"^SMALL OF$",
        r"^BOTH SAEM$", r"^DIFFRINT$"
    ],

    "Multiple Parameter Separator": [r"^AN$"],

    "Output Keyword": [r"^VISIBLE$"],

    "Code Delimiter": [r"^HAI$", r"^KTHXBYE$"],
    "Variable List Delimiter": [r"^WAZZUP$", r"^BUHBYE$"],

    "Boolean Value (True)": [r"^WIN$"],
    "Boolean Value (False)": [r"^FAIL$"],

    "Float Literal": [r"^[0-9]+\.[0-9]+$"],
    "Integer Literal": [r"^[0-9]+$"],

    "Variable Identifier": [r"^[A-Za-z_][A-Za-z0-9_]*$"],
}

# multi-word tokens first
multiword = [
    "I HAS A", "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF",
    "MOD OF", "BIGGR OF", "BIGGER OF", "SMALLR OF",
    "BOTH SAEM", "DIFFRINT"
]

def classify(tok):
    for token_type, patterns in token_regex.items():
        for p in patterns:
            if re.match(p, tok):
                if "Literal" in token_type or "Boolean" in token_type:
                    return f"{token_type} {tok} {tok}"
                return f"{token_type} {tok}"
    return None

def tokenize(text):
    text = re.sub(r"BTW.*", "", text)  

    # detect multiword tokens first
    for m in multiword:
        text = text.replace(m, m.replace(" ", "_MULTI_"))

    raw = re.findall(r'"|[^\s"]+|\"', text)

    inside_str = False
    buffer = ""

    for tok in raw:
        # string mode
        if tok == '"':
            if not inside_str:
                inside_str = True
                print('String Delimiter "')
            else:
                inside_str = False
                print(f"String Literal {buffer} {buffer}")
                print('String Delimiter "')
                buffer = ""
            continue

        if inside_str:
            buffer += tok
            continue

        # restore multiwords
        tok = tok.replace("_MULTI_", " ")

        if not tok.strip():
            continue

        # match against dictionary
        result = classify(tok)
        if result:
            print(result)

def main():
    tokenize(sys.stdin.read())

if __name__ == "__main__":
    main()
