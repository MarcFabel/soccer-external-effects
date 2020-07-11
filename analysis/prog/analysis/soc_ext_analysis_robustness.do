// ***************************** PREAMBLE***************************************
*	Created: 03.04.2020
*	Author: Marc Fabel
*	
*	Description:
*		Robustness ß Regression analysis of impact of soccer matches on assaults
*
*	Input:
*		data_prepared.csv
*
*	Output:
*		tables in $tables
*
	
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
*	Poisson with number of assaults
********************************************************************************

	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 
	
	
	// Total Assault **********************************************************	
	preg_fe a1 ass $gd "" 		"$region_fe $time_fe"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"-"
	qui estadd local holiday	"-"
	qui estadd local interact	"-"
		
	preg_fe a2 ass $gd "$weather" "$region_fe $time_fe"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"-"
	qui estadd local interact	"-"
	
	preg_fe a3 ass $gd "$weather" "$region_fe $time_fe $holiday"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"-"
	
	preg_fe a4 ass $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		scalars("mean Effect size [\%]" "Nn Observations" 				///
		"region Region FE" "time Time Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 
		
	
	esttab a* using "$tables/assaults_poisson_fixed_effects.tex",	///
		se star(* 0.10 ** 0.05 *** 0.01)				 				///
		keep(d_gameday) coeflabels(d_gameday "Game day")				///
		scalars("mean \midrule Effect size [\%]" "Nn Observations"		///
		"region Region FE" "time Time Fe" "weather Weather Controls"	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 						///
		replace booktabs fragment label 								///
		nomtitles nonumbers noobs nonote nogaps noline
	
	
********************************************************************************
*	Drop delayed games & unweighted results
********************************************************************************	
		
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 	
		
	
	* baseline
	eststo clear
	reg_fe a4 assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"	
	
	* drop delayed games
	preserve
		drop if d_delayed == 1
		reg_fe x assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
		qui estadd local region 	"yes"
		qui estadd local time 		"yes" 
		qui estadd local weather 	"yes"
		qui estadd local holiday	"yes"
		qui estadd local interact	"yes"
	restore
	
	* unweighted 
	reg_fe_unweighted y assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"		
		
		
	esttab a4 x y, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		scalars("mean Effect size [\%]" "Nn Observations" 				///
		"region Region FE" "time Time Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 	
		
	esttab a4 x y using "$tables/assrate_fixed_effects_robust_delayed_unweighted.tex", 				///
		se star(* 0.10 ** 0.05 *** 0.01)				 				///
		keep(d_gameday) coeflabels(d_gameday "Game day")				///
		scalars("mean \midrule Effect size [\%]" "Nn Observations"		///
		"region Region FE" "time Time Fe" "weather Weather Controls"	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 						///
		replace booktabs fragment label 								///
		nomtitles nonumbers noobs nonote nogaps noline	
		
		
		
		
		