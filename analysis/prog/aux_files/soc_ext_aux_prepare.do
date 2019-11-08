// ***************************** PREAMBLE***************************************
*	Created: 29.10.2019
*	Author: Marc Fabel
*
* 	Description:
*		The program executes some small preparation task - outside of Python,
*		e.g. generate variables that are used by all do-files
*
// *****************************************************************************


	import delimited "$data/data_prepared.csv", delimiter(";") encoding(utf8) clear

	* declare as panel
	gen date2 = date(date, "YMD")
	format date2 %td
	order date*
	xtset ags date2
	
	*encode dow
	qui gen dow_num = 1 if dow == "Mon"
	qui replace dow_num = 2 if dow == "Tue"
	qui replace dow_num = 3 if dow == "Wed"
	qui replace dow_num = 4 if dow == "Thu"
	qui replace dow_num = 5 if dow == "Fri"
	qui replace dow_num = 6 if dow == "Sat"
	qui replace dow_num = 7 if dow == "Sun"
	label define DOW 1 "Mon" 2 "Tue" 3 "Wed" 4 "Thu" 5 "Fri" 6 "Sat" 7 "Sun"
	label val dow_num DOW
	
	*define probability weigts (population weighted) - sum of weights sum to one
	qui gen temp = 1
	bys temp: egen temp2 = sum(pop_t)
	qui gen p_wght = pop_t / temp2
	drop temp*
	
	
	save "$data/data_prepared.dta", replace
	
	

