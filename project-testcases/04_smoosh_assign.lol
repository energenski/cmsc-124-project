HAI
    WAZZUP
        BTW variable dec
        I HAS A x
        I HAS A y
    BUHBYE

    OBTW
    input "hello" (w/o quotes) for x, " world" (yes with space at start, w/o quotes) for y to 
    follow inline expected output comments. 
    otherwise, feel free to check urself with different inputs
    TLDR

    VISIBLE "Hello! Please enter two strings:"
    VISIBLE "String 1: "
    GIMMEH x
    VISIBLE "String 2: "
    GIMMEH y

    VISIBLE SMOOSH x AN y       BTW shold print: hello world

    VISIBLE SMOOSH x AN x AN x AN y AN y    BTW should print: hellohellohello world world

    x R SMOOSH x AN y           BTW now x is 'hello world'
    VISIBLE x                   BTW must print 'hello world'

    y R 100                     BTW y will now be 100 (int)
    VISIBLE y                   BTW should print 100

    BTW VISIBLE x AN 52615 AN y AN MOD OF 10 AN 6 AN "End!"      BTW must error cuz of no SMOOSH (commented out to continue)

    BTW correct and working ver of above, should print out: hello world526151004End!
    VISIBLE SMOOSH x AN 52615 AN y AN MOD OF 10 AN 6 AN "End!" 

    VISIBLE SMOOSH 10 AN y     BTW error cuz no SMOOSH (comment out if want to test w/ no error)
    BTW (if w/ SMOOSH, should print: 10100)

    y IS NOW A NUMBAR
    VISIBLE y               BTW should print out 100.0 since its now NUMBAR

    VISIBLE SMOOSH 10 AN y     BTW error cuz no SMOOSH (comment out if want to test w/ no error)
    BTW (if w/ SMOOSH, should print: 10100.0)

    y R 0
    VISIBLE y                   BTW should print: 0.0

    BTW y R MAEK A y TROOF      BTW this is INVALID syntax so it should be SYNTAX ERROR

    y R MAEK y A TROOF          BTW MAEK y A TROOF would return TROOF equivalent of y (0.0) to IT (FAIL) and then its going to be y R IT
    VISIBLE y                   BTW should print: FAIL

    y IS NOW A NUMBR            BTW now y will be a NUMBR from FAIL
    VISIBLE y                   BTW should print 0 (without decimal since its NUMBR/int)
KTHXBYE