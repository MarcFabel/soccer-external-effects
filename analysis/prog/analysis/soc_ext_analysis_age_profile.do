// ***************************** PREAMBLE***************************************
*	Created: 04.11.2019
*	Author: Marc Fabel
*	
*	Description:
*		Investigates the age profile of the effects
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
	global graphs		"$path\output\graphs\regression"

	
	cd "$prog\analysis"
	
	
	
********************************************************************************
*	Regressionmodels - output will be read in to generate graphs
********************************************************************************

	
// Total Assault rate (AGE-PROFILE) ********************************************
	eststo clear
	*baseline
	reg_fe a1 $y $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*0_17
	reg_fe a2 assrate_0_17 $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*18_29
	reg_fe a3 assrate_18_29 $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*30_39
	reg_fe a4 assrate_30_39 $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*40_49
	reg_fe a5 assrate_40_49 $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*50_59
	reg_fe a6 assrate_50_59 $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*60+
	reg_fe a7 assrate_60 $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		scalars("mean Effect size" "Nn Observations" 				///
		"region Region FE" "time Time Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 	
	
	*read out for graph:
	esttab a* using "$temp/age_profiles.csv" , replace noobs se nostar keep(d_gameday) nopar nonotes nonumbers plain
	
	
// Total Assault rate (AGE-PROFILE - FEMALE) ***********************************
	
	eststo clear
	*baseline
	reg_fe a1 assrate_f $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*0_17
	reg_fe a2 assrate_0_17_f $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*18_29
	reg_fe a3 assrate_18_29_f $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*30_39
	reg_fe a4 assrate_30_39_f $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*40_49
	reg_fe a5 assrate_40_49_f $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*50_59
	reg_fe a6 assrate_50_59_f $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*60+
	reg_fe a7 assrate_60_f $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		scalars("mean Effect size" "Nn Observations" 				///
		"region Region FE" "time Time Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 	

	*read out for graph:
	esttab a* using "$temp/age_profiles_f.csv" , replace noobs se nostar keep(d_gameday) nopar nonotes nonumbers plain	
	
	
	
	
// Total Assault rate (AGE-PROFILE - MALE) *************************************
	eststo clear
	*baseline
	reg_fe a1 assrate_m $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*0_17
	reg_fe a2 assrate_0_17_m $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*18_29
	reg_fe a3 assrate_18_29_m $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*30_39
	reg_fe a4 assrate_30_39_m $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*40_49
	reg_fe a5 assrate_40_49_m $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*50_59
	reg_fe a6 assrate_50_59_m $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	*60+
	reg_fe a7 assrate_60_m $gd "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		scalars("mean Effect size" "Nn Observations" 				///
		"region Region FE" "time Time Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 	
	
	*read out for graph:
	esttab a* using "$temp/age_profiles_m.csv" , replace noobs se nostar keep(d_gameday) nopar nonotes nonumbers plain	
	
	
	
	
	
	
********************************************************************************
*	GENERATE GRAPHS OF THE MODELS
********************************************************************************	

// MAKE GRAPH OF AGEPROFILE (TOTAL) ********************************************
import delimited F:\econ\soc_ext\analysis\output\temp\age_profiles.csv, varnames(1) clear
qui gen temp = _n
drop if temp == 1
drop v1
qui gen element = "b" if temp == 2
qui replace element = "se"  if temp == 3
qui destring *, replace
drop temp

reshape long a, i(element) j(model) 
reshape wide a,  i(model) j(element) string

rename ab beta
rename ase ste

qui gen CIL = (beta - $t_95 * ste)
qui gen CIR = (beta + $t_95 * ste)

label define MODEL 1 "baseline" 2 "0 - 17" 3 "18 - 29" 4 "30 - 39" 5 "40 - 49" 6 "50 - 59" 7 "60+"
label values model MODEL

drop if model == 1

twoway scatter beta model , sort color(gs4)  || ///
	rcap CIR CIL model, color(gs4%75) sort ///
	yline(0, lw(thin) lpattern(dash) lcolor(black))   ///
	scheme(s1mono) plotregion(color(white)) ///
	legend(off) ///
	xlabel(,val) ///
	xtitle("Age brackets") ///
	ytitle("") ///
	xscale(r(1.5 7.5)) yscale(r(0 65)) ylabel(0 20 40 60) ///
	saving($temp/fe_agebrackets_t.gph, replace)
graph export "$graphs/fe_agebrackets_t.pdf", as(pdf) replace


// MAKE GRAPH OF AGEPROFILE (FEMALE) ******************************************
import delimited F:\econ\soc_ext\analysis\output\temp\age_profiles_f.csv, varnames(1) clear
qui gen temp = _n
drop if temp == 1
drop v1
qui gen element = "b" if temp == 2
qui replace element = "se"  if temp == 3
qui destring *, replace
drop temp

reshape long a, i(element) j(model) 
reshape wide a,  i(model) j(element) string

rename ab beta
rename ase ste

qui gen CIL = (beta - $t_95 * ste)
qui gen CIR = (beta + $t_95 * ste)

label define MODEL 1 "baseline" 2 "0 - 17" 3 "18 - 29" 4 "30 - 39" 5 "40 - 49" 6 "50 - 59" 7 "60+"
label values model MODEL

drop if model == 1

twoway scatter beta model , sort color(cranberry)  || ///
	rcap CIR CIL model, color(cranberry%75) sort ///
	yline(0, lw(thin) lpattern(dash) lcolor(black))   ///
	scheme(s1mono) plotregion(color(white)) ///
	legend(off) ///
	xlabel(,val) ///
	xtitle("Age brackets") ///
	ytitle("") ///
	xscale(r(1.5 7.5)) yscale(r(0 65)) ylabel(0 20 40 60) ///
	saving($temp/fe_agebrackets_f.gph, replace)
graph export "$graphs/fe_agebrackets_f.pdf", as(pdf) replace

	
	
// MAKE GRAPH OF AGEPROFILE (MALE) *********************************************
import delimited F:\econ\soc_ext\analysis\output\temp\age_profiles_m.csv, varnames(1) clear
qui gen temp = _n
drop if temp == 1
drop v1
qui gen element = "b" if temp == 2
qui replace element = "se"  if temp == 3
qui destring *, replace
drop temp

reshape long a, i(element) j(model) 
reshape wide a,  i(model) j(element) string

rename ab beta
rename ase ste

qui gen CIL = (beta - $t_95 * ste)
qui gen CIR = (beta + $t_95 * ste)

label define MODEL 1 "baseline" 2 "0 - 17" 3 "18 - 29" 4 "30 - 39" 5 "40 - 49" 6 "50 - 59" 7 "60+"
label values model MODEL

drop if model == 1

twoway scatter beta model , sort color(navy)  || ///
	rcap CIR CIL model, color(navy%75) sort ///
	yline(0, lw(thin) lpattern(dash) lcolor(black))   ///
	scheme(s1mono) plotregion(color(white)) ///
	legend(off) ///
	xlabel(,val) ///
	xtitle("Age brackets") ///
	ytitle("") ///
	xscale(r(1.5 7.5)) yscale(r(0 65)) ylabel(0 20 40 60) ///
	saving($temp/fe_agebrackets_m.gph, replace)	
graph export "$graphs/fe_agebrackets_m.pdf", as(pdf) replace
	
/*
cd $temp	
graph combine "fe_agebrackets_t" "fe_agebrackets_f" "fe_agebrackets_m", col(3)	altshrink iscale(1) ycommon
	
	
	