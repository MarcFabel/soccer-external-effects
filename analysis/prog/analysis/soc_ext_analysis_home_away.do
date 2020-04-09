// ***************************** PREAMBLE***************************************
*	Created: 08.04.2020
*	Author: Marc Fabel
*	
*	Description:
*		Regression analysis of impact of soccer matches on assaults
*		allowing for the distinction between home and away games
*
*	Input:
*		data_prepared_neighbor_regions.csv
*
*	Output:
*		tables in $tables
*
*	comment: only league 1 & 2, additionally 178 games were deleted because there
*		were doublings in region and date - if this was not done, the treatment 
*		status of the region on that day would be unclear - see prepare files
	
	clear all 
	set more off
	set matsize 11000
	
	*paths
	global path   	   	"F:\econ\soc_ext\analysis"	
	global data			"$path\data\final"
	global tables 		"$path\output\tables\reg_fe"
	global temp			"$path/output/temp"
	global prog			"$path\prog"
	
	cd "$prog\analysis"
	


********************************************************************************
*	import and prepare data
********************************************************************************

	import delimited "$data/data_prepared_home_away.csv", delimiter(";") encoding(utf8) clear

	
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
	


********************************************************************************
*	Define the program
********************************************************************************

	// define regression variables *********************************************
	global gd 				"d_away_game d_home_game"
	global region_fe 		"i.ags"
	global time_fe 			"i.dow_num i.month i.year" // i.woy 
	global weather 			"tmk txk tnk tgk vpm nm pm upm rs sdk sh fm"
	global holiday 			"i.sch_hday i.pub_hday i.special_day"
	global interaction 		"i.ags##i.dow_num i.ags##i.month i.ags##i.year" // alternative way: i.ags##i.(dow_num month year)
	
	
	// Programm for regression *************************************************
	capture program drop reg_fe
		program define reg_fe
			qui eststo `1': reghdfe `2' `3' `4' `5' [pw=p_wght], absorb(`6') vce(cluster ags#year year#month)  
			qui estadd scalar Nn = e(N)
			qui summ `2' if e(sample) & d_away_game == 0 & d_home_game == 0
			qui estadd scalar mean = abs(round(_b[`3']/`r(mean)'*100,.01))
		end
	
	
********************************************************************************
*	Analysis
********************************************************************************

	// Total Assault rate ******************************************************
	reg_fe a4 assrate d_home_game d_away_game  "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_home_game d_away_game) 	///
		scalars("mean Effect size [\%]" "Nn Observations" 				///
		"region Region FE" "time Time Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 	
		
		
		
		
	// generate sample in normal data set that is comparable with the home/away sample

	keep ags
	duplicates drop
	qui save "$temp/list_ags_used_for_home_away.dta", replace

	* open normal file & delete unused regions
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 
	
	qui merge m:1 ags using  "$temp/list_ags_used_for_home_away.dta"
	keep if _merge == 3
	
	reg_fe b4 assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	esttab b4 a4, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday d_home_game d_away_game) 				///
		coeflabels(d_gameday "Game day" d_home_game "Home game day" d_away_game "Away game day")	///
		scalars("mean Effect size [\%]" "Nn Observations" 				///
		"region Region FE" "time Time Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 

	esttab  b4 a4 using "$tables/assrate_fixed_effects_home_away.tex",  ///
		se star(* 0.10 ** 0.05 *** 0.01)				 				///
		keep(d_gameday d_home_game d_away_game)							///
		coeflabels(d_gameday "Game day" d_home_game "Home game day" d_away_game "Away game day")	///			
		scalars("mean \midrule Effect size [\%]" "Nn Observations"		///
		"region Region FE" "time Time Fe" "weather Weather Controls"	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 						///
		replace booktabs fragment label 								///
		nomtitles nonumbers noobs nonote nogaps noline

