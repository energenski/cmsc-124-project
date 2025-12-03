HAI
    WAZZUP
        I HAS A testValue ITZ 5
    BUHBYE

    testValue R 5
    BOTH SAEM testValue AN 10 BTW First condition: 5 == 10 (FAIL). Stored in IT.

    O RLY?
        YA RLY
            VISIBLE "O RLY? (If) executed (SHOULD NOT PRINT)"
        MEBBE BOTH SAEM testValue AN 5 BTW Else-if 1: 5 == 5 (WIN). New expression evaluated.
            VISIBLE "MEBBE (Else-If) 1 executed"
        MEBBE BOTH SAEM testValue AN 5 BTW Else-if 2: This should be skipped because MEBBE 1 was WIN.
            VISIBLE "MEBBE (Else-If) 2 executed (SHOULD NOT PRINT)"
        NO WAI
            VISIBLE "NO WAI (Else) executed (SHOULD NOT PRINT)"
    OIC

    testValue R 1
    BOTH SAEM testValue AN 10 BTW First condition: 1 == 10 (FAIL). Stored in IT.

    O RLY?
        YA RLY
            VISIBLE "O RLY? (If) executed (SHOULD NOT PRINT)"
        MEBBE BOTH SAEM testValue AN 5 BTW Else-if 1: 1 == 5 (FAIL).
            VISIBLE "MEBBE (Else-If) 1 executed (SHOULD NOT PRINT)"
        MEBBE BOTH SAEM testValue AN 1 BTW Else-if 2: 1 == 1 (WIN). New expression evaluated.
            VISIBLE "MEBBE (Else-If) 2 executed"
        NO WAI
            VISIBLE "NO WAI (Else) executed (SHOULD NOT PRINT)"
    OIC

    testValue R 0
    BOTH SAEM testValue AN 10 BTW First condition: 0 == 10 (FAIL). Stored in IT.

    O RLY?
        YA RLY
            VISIBLE "O RLY? (If) executed (SHOULD NOT PRINT)"
        MEBBE BOTH SAEM testValue AN 5 BTW Else-if 1: 0 == 5 (FAIL).
            VISIBLE "MEBBE (Else-If) 1 executed (SHOULD NOT PRINT)"
        MEBBE DIFFRINT testValue AN 0 BTW Else-if 2: 0 != 0 (FAIL).
            VISIBLE "MEBBE (Else-If) 2 executed (SHOULD NOT PRINT)"
        NO WAI
            VISIBLE "NO WAI (Else) executed"
    OIC

KTHXBYE