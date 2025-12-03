HAI

    WAZZUP
        I HAS A name
        I HAS A num1
        I HAS A num2
        I HAS A x      BTW initialize to global scope (to test for func call), otherwise error
    BUHBYE
    
    HOW IZ I addNum YR x AN YR y
        FOUND YR SUM OF x AN y
        BTW originally <FOUND YR SUM OF x an y>, made an -> AN
    IF U SAY SO

    HOW IZ I printName YR person
        VISIBLE "Hello, " + person
        GTFO
    IF U SAY SO

    HOW IZ I printNum YR x
        FOUND YR x
    IF U SAY SO

    VISIBLE "Enter num1:"
    GIMMEH num1
    VISIBLE "Enter num2:"
    GIMMEH num2

    I IZ addNum YR num1 AN YR num2 MKAY     BTW should be error, just add MKAY at end
    VISIBLE IT

    VISIBLE "Enter your name:"
    GIMMEH name
    I IZ printName YR name MKAY             BTW should be error, just add MKAY at end
    VISIBLE IT

    VISIBLE "Will print SUM OF x (if initialized) AN 2:"
    I IZ printNum YR SUM OF x AN 2 MKAY        BTW should be error, just add MKAY and make sure x is declared & initialized in global scope
    VISIBLE IT

KTHXBYE