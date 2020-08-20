
	use "$data/data_prepared.dta", clear
	order pop_t
	keep if year == 2015
	keep if date2 == td(01jan2015)
	collapse (sum) pop_t

	* population in 2014:  20,933,382
	
	use "$data/data_prepared.dta", clear
	keep if season == "2014-15"
	count if d_gameday == 1
	
	
	
	* wieviel assaults hat es in dem Jahr gegeben? 
	use "$data/data_prepared.dta", clear
	collapse (sum) ass, by(season)
	/*season	ass
	2014-15	105,364
	18% sind 19,000 assaults durch Fussball
	*/

