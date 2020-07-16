// ***************************** PREAMBLE***************************************
*	Created: 28.10.2019
*	Author: Marc Fabel
*	
*	Description:
*		Regression analysis of impact of soccer matches on assaults
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
*	First regressions
********************************************************************************
	
	
// import and prepare data *****************************************************
	do "$prog/aux_files/soc_ext_aux_prepare.do" 
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 
	
	
// Total Assault rate **********************************************************	
	reg_fe a1 assrate $gd "" 		"$region_fe $time_fe"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"-"
	qui estadd local holiday	"-"
	qui estadd local interact	"-"
		
	reg_fe a2 assrate $gd "$weather" "$region_fe $time_fe"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"-"
	qui estadd local interact	"-"
	
	reg_fe a3 assrate $gd "$weather" "$region_fe $time_fe $holiday"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"-"
	
	reg_fe a4 assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		scalars("mean Effect size [\%]" "Nn Observations" 				///
		"region Region FE" "time Date Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 	
	
	esttab a* using "$tables/assrate_fixed_effects.tex", 				///
		se star(* 0.10 ** 0.05 *** 0.01)				 				///
		keep(d_gameday) coeflabels(d_gameday "Game day")				///
		scalars("mean \midrule Effect size [\%]" "Nn Observations"		///
		"region Region FE" "time Date Fe" "weather Weather Controls"	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 						///
		replace booktabs fragment label 								///
		nomtitles nonumbers noobs nonote nogaps noline
	
	

		
// Total Assault rate (WIHT LEADS & LAGS) **************************************
	eststo clear
	sort ags date2
	reg_fe a1 assrate $gd "L.$gd F.$gd" 			"$region_fe $time_fe"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"-"
	qui estadd local holiday	"-"
	qui estadd local interact	"-"
	
	reg_fe a2 assrate $gd "L.$gd F.$gd $weather" "$region_fe $time_fe"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"-"
	qui estadd local interact	"-"
	
	reg_fe a3 assrate $gd "L.$gd F.$gd $weather" "$region_fe $time_fe $holiday"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"-"
	
	reg_fe a4 assrate $gd "L.$gd F.$gd $weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"

	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) 								///
		keep(d_gameday F.d_gameday L.d_gameday) coeflabels(				///
		$gd "Game day" L.$gd "Day after game" F.$gd "Day before game")	///
		scalars("mean Effect size [\%]" "Nn Observations" 				///
		"region Region FE" "time Date Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 	
	
	esttab a* using "$tables/assrate_fixed_effects_leads_lags.tex", 	///
		se star(* 0.10 ** 0.05 *** 0.01)				 				///
		keep(d_gameday F.d_gameday L.d_gameday) coeflabels(				///
		$gd "Game day" L.$gd "Day after game" F.$gd "Day before game")	///
		scalars("mean \midrule Effect size [\%]" "Nn Observations"		///
		"region Region FE" "time Date Fe" "weather Weather Controls"	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 						///
		replace booktabs fragment label 								///
		nomtitles nonumbers noobs nonote nogaps noline
	
	
	
// Total Assault rate (SUBCATEGORIES: VICTIM CHARACTERISTICS) ******************
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do"
	
	eststo clear
	*baseline
	reg_fe a1 assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*female
	reg_fe a2 assrate_f $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*male
	reg_fe a3 assrate_m $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*strangers
	reg_fe a4 assrate_vs_strangers $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*prior relationship
	reg_fe a5 assrate_vs_rel $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*domestic
	reg_fe a6 assrate_domestic $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		scalars("mean Effect size" "Nn Observations" 				///
		"region Region FE" "time Date Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f)
	
	esttab a* using "$tables/assrate_fixed_effects_subcat_victim_chars.tex",	///
		se star(* 0.10 ** 0.05 *** 0.01)				 				///
		keep(d_gameday) coeflabels(d_gameday "Game day")				///
		scalars("mean \midrule Effect size [\%]" "Nn Observations"		///
		"region Region FE" "time Date Fe" "weather Weather Controls"	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 						///
		replace booktabs fragment label 								///
		nomtitles nonumbers noobs nonote nogaps noline
	
	
	
	
	
// Total Assault rate (SUBCATEGORIES: CRIME CHARACTERISTICS) *******************
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do"
	
	* define summer and winter season
	qui gen d_summer_months = cond(month >= 4 & month <=9, 1, 0)
	qui gen d_winter_months = cond(d_summer_months!=1 , 1, 0)
	qui gen d_spring = cond(month==3 | month==4 | month==5, 1, 0)
	qui gen d_summer = cond(month==6 | month==7 | month==8, 1, 0)
	qui gen d_fall = cond(month==9 | month==10 | month==11, 1, 0)
	qui gen d_winter = cond(month==12 | month==1 | month==2, 1, 0)
	
	eststo clear
	*baseline
	reg_fe a1 assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"	
	
	*spring
	reg_fe a2 assrate $gd "$weather if d_spring == 1" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"	
	
	*summer
	reg_fe a3 assrate $gd "$weather if d_summer == 1" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"	
	
	*fall
	reg_fe a4 assrate $gd "$weather if d_fall == 1" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*winter
	reg_fe a5 assrate $gd "$weather if d_winter == 1" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*attempt
	reg_fe a6 assrate_attempt $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*success
	reg_fe a7 assrate_success $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		scalars("mean Effect size" "Nn Observations" 				///
		"region Region FE" "time Date Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f)
	
	esttab a* using "$tables/assrate_fixed_effects_subcat_crime_chars.tex",	///
		se star(* 0.10 ** 0.05 *** 0.01)				 				///
		keep(d_gameday) coeflabels(d_gameday "Game day")				///
		scalars("mean \midrule Effect size [\%]" "Nn Observations"		///
		"region Region FE" "time Date Fe" "weather Weather Controls"	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 						///
		replace booktabs fragment label 								///
		nomtitles nonumbers noobs nonote nogaps noline
	
	

	
	
	

// Total Assault rate (SUBCATEGORIES: MATCH CHARACTERISTICS) *******************
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do"
	
	eststo clear
	* baseline
	reg_fe a1 assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	* home team loses (28% of matches)
	reg_fe a2 assrate d_gd_ht_loses  "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	* home team wins (45% of matches)
	reg_fe a3 assrate d_gd_ht_wins  "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	* home team was not behind at break, but lost in the end (12 % of matches)
	reg_fe a4 assrate d_gd_ht_loses_2nd_half  "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*league 
	
	*schiri
	qui gen d_gd_ref = d_gameday * grade_ref
	reg_fe a5 assrate d_gd_ref  "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	qui gen d_gd_ref_good = cond(grade_ref >= 1 & grade_ref<=3, 1, 0)
	reg_fe a6 assrate d_gameday  "$weather if grade_ref <= 3" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	reg_fe a7 assrate d_gameday  "$weather if grade_ref <= 3" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_g*) 					///
		scalars("mean Effect size" "Nn Observations" 					///
		"region Region FE" "time Date Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 						///
		rename(d_gd_ht_loses d_gameday d_gd_ht_wins d_gameday d_gd_ht_loses_2nd_half d_gameday)
	
	
	
	
* mit absolute numbers and poisson, also available for multiple hierarchy fixed effects
	
	

	
