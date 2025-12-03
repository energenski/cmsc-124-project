HAI
    WAZZUP
        BTW variable dec
        I HAS A x
        I HAS A y
    BUHBYE

    VISIBLE "x: " + WIN + ", y: " + WIN     BTW changed x: to WIN from FAIL (must be typo)
    x R WIN
    y R WIN

    VISIBLE BOTH OF x AN y                  BTW should be WIN
    VISIBLE EITHER OF x AN y                BTW should be WIN
    VISIBLE WON OF x AN y                   BTW should be FAIL (WIN XOR WIN)
    VISIBLE NOT x                           BTW should be FAIL (!FAIL)
    VISIBLE ALL OF x AN x AN x AN y MKAY    BTW should be WIN (since x and y are both WIN)
    VISIBLE ANY OF y AN y AN y AN 0 MKAY    BTW should be WIN (infinite arity OR == (WIN U WIN U WIN U FAIL [0]))
    VISIBLE ANY OF BOTH OF x AN EITHER OF NOT x AN y AN y AN NOT y MKAY BTW should be WIN ((WIN ^ (!WIN U WIN)) U WIN U (!WIN))
    VISIBLE BOTH OF x AN EITHER OF NOT x AN y BTW should be WIN (WIN ^ (!WIN U WIN))

    VISIBLE "x: " + FAIL + ", y: " + WIN
    x R FAIL

    VISIBLE BOTH OF x AN y                  BTW should be FAIL
    VISIBLE EITHER OF x AN y                BTW should be WIN                
    VISIBLE WON OF x AN y                   BTW should be WIN (FAIL XOR WIN)
    VISIBLE NOT x                           BTW should be WIN (!FAIL)
    VISIBLE ALL OF x AN x AN x AN y MKAY    BTW should be FAIL (since x is FAIL, y is WIN, inf arity AND, there is >=1 FAIL == FAIL)
    VISIBLE ANY OF y AN y AN y AN 0 MKAY    BTW should be WIN (infinite arity OR == (WIN U WIN U WIN U FAIL [0]))
    VISIBLE ANY OF BOTH OF x AN EITHER OF NOT x AN y AN y AN NOT y MKAY BTW should be WIN ((FAIL ^ (!FAIL U WIN)) U WIN U (!WIN))
    VISIBLE BOTH OF x AN EITHER OF NOT x AN y BTW should be FAIL (FAIL ^ (!FAIL U WIN))

    VISIBLE "x: " + FAIL + ", y: " + FAIL
    y R FAIL

    VISIBLE BOTH OF x AN y                  BTW should be FAIL
    VISIBLE EITHER OF x AN y                BTW should be FAIL (FAIL U FAIL)   
    VISIBLE WON OF x AN y                   BTW should be FAIL (FAIL XOR FAIL)
    VISIBLE NOT x                           BTW should be WIN (!FAIL)
    VISIBLE ALL OF x AN x AN x AN y MKAY    BTW should be FAIL (FAIL ^ FAIL ^ FAIL ^ FAIL)
    VISIBLE ANY OF y AN y AN y AN 0 MKAY    BTW should be FAIL (infinite arity OR == (FAIL U FAIL U FAIL U FAIL [0]))
    VISIBLE ANY OF BOTH OF x AN EITHER OF NOT x AN y AN y AN NOT y MKAY BTW should be WIN ((FAIL ^ (!FAIL U FAIL)) U FAIL U (!FAIL))
    VISIBLE BOTH OF x AN EITHER OF NOT x AN y BTW should be FAIL (FAIL ^ (!FAIL U FAIL))
KTHXBYE