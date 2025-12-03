HAI
	WAZZUP
		I HAS A choice
		I HAS A input
	BUHBYE
	
	BTW if w/o MEBBE, 1 only, everything else is invalid
	VISIBLE "1. Compute age"
	VISIBLE "2. Compute tip"
	VISIBLE "3. Compute square area"
	VISIBLE "0. Exit"

	VISIBLE "Choice: "
	GIMMEH choice

	choice			BTW idk if this should be error (commented out) or included [i believe error dapat since WTF? should use value in IT]
	WTF?
		OMG 1
			VISIBLE "Enter birth year: "
			GIMMEH input
			VISIBLE DIFF OF 2025 AN input
			GTFO
		OMG 2
			VISIBLE "Enter bill cost: "
			GIMMEH input
			BTW originally <VISIBLE "Tip: " + PRODUCKT OF input AN 0.1>  i just corrected PRODUCKT to run code and added '+'
			VISIBLE "Tip: " + PRODUKT OF input AN 0.1		
			GTFO
		OMG 3
			VISIBLE "Enter width: "
			GIMMEH input
			BTW originally <VISIBLE "Square Area: " PRODUKT OF input AN input>, i just added '+' to run code
			VISIBLE "Square Area: " + PRODUKT OF input AN input
			GTFO
		OMG 0
			VISIBLE "Goodbye"
			GTFO				BTW added GTFO since there wasn't -> SYNTAX ERROR missing GTFO on OMG block
		OMGWTF
			VISIBLE "Invalid Input!"	BTW OMGWTF does not need GTFO
	OIC

KTHXBYE