HAI
    WAZZUP
        I HAS A outerCond ITZ 10
        I HAS A innerCond ITZ 5
    BUHBYE

    DIFFRINT outerCond AN 5 BTW Outer condition: 10 != 5 (WIN). Stored in IT.

    O RLY? BTW Outer IF (IT is WIN)
        YA RLY
            VISIBLE "Outer IF: WIN"

            BOTH SAEM innerCond AN 5 BTW Inner condition: 5 == 5 (WIN). Stored in IT.

            O RLY? BTW Inner IF (IT is WIN)
                YA RLY
                    VISIBLE "Inner IF: WIN"
                NO WAI
                    VISIBLE "Inner ELSE: FAIL"
            OIC

            innerCond R 0
            DIFFRINT innerCond AN 5 BTW Inner condition: 0 != 5 (WIN). Stored in IT.

            O RLY? BTW Inner IF (IT is WIN)
                YA RLY
                    VISIBLE "Inner IF 2: WIN"
                NO WAI
                    VISIBLE "Inner ELSE 2: FAIL"
            OIC
            
        NO WAI
            VISIBLE "Outer ELSE: FAIL"
    OIC

    outerCond R 5
    DIFFRINT outerCond AN 5 BTW Outer condition: 5 != 5 (FAIL). Stored in IT.

    O RLY? BTW Outer IF (IT is FAIL)
        YA RLY
            VISIBLE "Outer IF 2: WIN (SHOULD NOT PRINT)"
        NO WAI
            VISIBLE "Outer ELSE 2: FAIL"
    OIC

KTHXBYE