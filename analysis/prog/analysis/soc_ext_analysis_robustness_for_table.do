use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 	
		
	eststo clear

********************************************************************************		
// baseline

	reg_fe a1 assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	
********************************************************************************		
// Econometric specification		

	* drop delayed games
	preserve
		drop if d_delayed == 1
		reg_fe a2 assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	restore
	
	* unweighted 
	reg_fe_unweighted a3 assrate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	
	*poisson	
	preg_fe a4 ass $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	
********************************************************************************		
	// Other forms of violence	
	
	* broadly defined assault 
	capture drop numerator assrate_broad
	qui egen numerator = rowtotal(ass negligent_bh dangerous_bh grievous_bh brawls_bh )
	qui gen assrate_broad = numerator *1000000 /pop_t
	reg_fe a5 assrate_broad $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	
	*threats
	qui gen threat_rate = threats *1000000 / pop_t
	reg_fe a6 threat_rate $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	
	* resistence
	qui gen resistence_rate = resistence_enforcenebt *1000000/pop_t
	reg_fe a7 resistence_rate $gd "$weather" "$region_fe $time_fe $holiday $interaction"

********************************************************************************		
// Placebo Tests
	
	* placebo games
	set seed 123
	capture drop temp d_gameday_random
	qui gen temp = runiform() 
	summ d_gameday
	qui gen d_gameday_random = cond(temp < r(mean), 1,0)
	
	reg_fe a8 assrate d_gameday_random "$weather" "$region_fe $time_fe $holiday $interaction"
	
********************************************************************************		
	
		
		
	esttab a*, noobs 												///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday*) 				///
		scalars("mean Effect size [\%]" "Nn Observations") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 	