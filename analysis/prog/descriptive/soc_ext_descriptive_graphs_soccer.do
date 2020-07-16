// ***************************** PREAMBLE********************************
	clear all 
	set more off
	
	*paths
	global path   	   	"F:\econ\soc_ext\analysis"	
	global data			"$path\data\final"
	global graphs		"$path\output\graphs\descriptive"
	global graphs_temp	"$path\output\graphs\temp"
	global prefix 		"soc_ext_"
	global prog			"$path\prog"


	
// ***********************************************************************





********************************************************************************
*	Descriptives for Soccer Games
********************************************************************************
use "$data/data_prepared.dta", clear
do "$prog/aux_files/soc_ext_aux_program.do" 
keep if d_gameday == 1

// 1.A) Games per weekday ******************************************************
	bys dow_num: egen temp = count(dow_num)
	qui gen dow_freq = temp / _N
	drop temp 
	
	twoway bar  dow_freq dow_num, ///
		barw(0.95) color(gs2%85) ///
		xlabel(1 2 3 4 5 6 7 , valuelabel) ///
		ytitle("Relative frequency") ///
		xtitle("") ///
		plotregion(color(white)) scheme(s1mono) 

		
	* by league:
	bys dow_num league: egen temp = count(dow_num)
	qui gen l1 = temp if league == 1
	qui gen l2 = temp if league == 2
	qui gen l3 = temp if league == 3
	
	graph bar l1 l2 l3, over(dow_num) stack ///
		legend(label(1 "1st league") label(2 "2nd league") label(3 "3rd league") ///
		pos(11) ring(0) col(1) ) ///
		bar(1, color(gs4)) bar(2, color(gs7)) bar(3, color(gs10)) ///
		ytitle("Number of matches") ///
		title("Panel A: Matches by day of the week",pos(11) span  size(vlarge)) ///
		plotregion(color(white)) scheme(s1mono) ///
		ylabel(0 (500) 2000) ///
		saving($graphs_temp/soc_ext_desc_soccer_matches_dow, replace)
	*graph export "$graphs/soc_ext_desc_soccer_matches_dow.pdf", as(pdf) replace
		
		
		
// 1.B) Time of the matches ****************************************************
	capture drop weekend
	qui gen weekend = cond(dow_num>5,1,0)
	
	*encode the time
	capture drop time_enc
	qui gen time_enc = clock(time, "hm")
	format time_enc %tcDDmonCCYY_HH:MM
	
	hist time_enc if weekend == 0 , color(gs8%60) w(1800000) ///
		addplot(hist time_enc if weekend == 1, color(gs2%60) w(1800000) freq) ///
		tlabel(46800000 (3600000) 75600000,  format(%tcHH:MM)) /// 
		tmtick(48600000 (3600000) 73800000) ///
		legend(label(2 "weekend") label(1 "weekday") pos(2) ring(0) col(1)) ///
		xtitle("") ///
		plotregion(color(white)) scheme(s1mono) freq /// 
		ytitle(Number of matches) ylabel(0 500 1000) ///
		title("Panel B: Matches by time of the day",pos(11) span  size(vlarge)) ///
		ylabel(,grid) ///
		saving($graphs_temp/soc_ext_desc_soccer_matches_hour, replace)
	*graph export "$graphs/soc_ext_desc_soccer_matches_hour.pdf", as(pdf) replace

		
	
// 1.C) Number of spectators ***************************************************
	replace attendance = attendance / 1000

	twoway kdensity attendance if league == 1, color(gs4) || ///
		kdensity attendance if league == 2, lp(longdash) color(gs4) || ///
		kdensity attendance if league == 3, lp(shortdash_dot ) color(gs4) ///
		legend(label(1 "1st league") label(2 "2nd league") label(3 "3rd league") ///
		pos(2) ring(0) col(1) ) ///
		xtitle("Attendance [in thousand]") ytitle("Density") ///
		ylabel(0 .05 .1,grid) plotregion(color(white)) scheme(s1mono) ///
		title("Panel C: Attendance across leagues",pos(11) span  size(vlarge)) ///
		saving($graphs_temp/soc_ext_desc_soccer_attendance_league, replace)
	*graph export "$graphs/soc_ext_desc_soccer_attendance_league.pdf", as(pdf) replace

	
	
// 1.D) Combine the single graphs **********************************************	
	graph combine "$graphs_temp/soc_ext_desc_soccer_matches_dow.gph" ///
		"$graphs_temp/soc_ext_desc_soccer_matches_hour.gph" ///
		"$graphs_temp/soc_ext_desc_soccer_attendance_league.gph" , ///
		altshrink scheme(s1mono) plotregion(color(white)) col(2)
	graph export "$graphs/soc_ect_desc_soccer_macthes_attendance.pdf", as(pdf) replace
		
		
		
********************************************************************************
*	2 Average number of assaults on gameday / non-gameday
********************************************************************************	

// 2.a) distribution of gamedays ***********************************************	 	
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do"
	keep if d_gameday == 1
	qui gen temp = 1
	
	collapse (count) temp, by(dow_num)
	qui egen temp2 = total(temp)
	qui gen freq = temp / temp2
	
	twoway bar freq  dow_num, horizontal ///
		xscale(rev) yscale(alt rev lc(white))  ///
		ytitle("") xlabel(0 0.25 0.5,grid ) ///
		plotregion(color(white)) scheme(s1mono) ///		
		ylabel(none) xtitle("Frequency of games") ///
		plotregion(margin(right)) ///
		fxsize(25) ///
		saving($graphs_temp/distr_gamedays_hor,replace)

		
// 2.b) assrate on gameday and non-gamday **************************************	 	
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 
	
	collapse (mean) ass assrate assrate_f assrate_m [fw=pop_t], by(d_gameday dow_num)
	reshape wide ass assrate assrate_f assrate_m, i(dow_num) j(d_gameday)

	graph bar assrate0 assrate1, over(dow_num) horizontal ///
		legend(label(1 "w/o game") label(2 "with game") order(2 1) ///
		pos(2) ring(0) col(1) ) ///
		bar(1, color(gs4)) bar(2, color(forest_green)) ///
		ytitle("Average assault rate") ///
		plotregion(color(white)) scheme(s1mono) ///
		saving($graphs_temp/assrate_gd_nongd_hor,replace)
		
	
// 2.c) combine the graphsw ****************************************************
	graph combine "$graphs_temp/distr_gamedays_hor" "$graphs_temp/assrate_gd_nongd_hor", ///
		row(1) imargin(zero) plotregion(color(white)) scheme(s1mono)
	
	graph export "$graphs/soc_ext_descr_assaultrate_gd_nongd_hor.pdf", as(pdf) replace

	
	
	
	
// 2.X) Same figure with just the NUMBER of assaults	 ***********************
// 
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 
	
	collapse (mean) ass  [fw=pop_t], by(d_gameday dow_num)
	reshape wide ass , i(dow_num) j(d_gameday)

	graph bar ass0 ass1, over(dow_num) horizontal ///
		legend(label(1 "w/o game") label(2 "with game") order(2 1) ///
		pos(2) ring(0) col(1) ) ///
		bar(1, color(gs4)) bar(2, color(forest_green)) ///
		ytitle("Average number of assaults") ///
		plotregion(color(white)) scheme(s1mono) ///
		saving($graphs_temp/ass_gd_nongd_hor,replace)	
	
	graph combine "$graphs_temp/distr_gamedays_hor" "$graphs_temp/ass_gd_nongd_hor", ///
		row(1) imargin(zero) plotregion(color(white)) scheme(s1mono)
	
	graph export "$graphs/soc_ext_descr_assaults_gd_nongd_hor.pdf", as(pdf) replace
	
	

	
// 2.c) Significance of the difference	 ***************************************
	
	
	
	
	
	
	
	/* old
	
	
	
// AVERAGE ASSAULT RATE ON GAMEDAY AND NON GAMEDAY - but VERTICALLY	
		use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 
	
	collapse (mean) ass assrate assrate_f assrate_m [fw=pop_t], by(d_gameday dow_num)
	reshape wide ass assrate assrate_f assrate_m, i(dow_num) j(d_gameday)

	graph bar assrate0 assrate1, over(dow_num) ///
		legend(label(1 "Nongame weeks") label(2 "Game weeks") order(2 1) ///
		pos(11) ring(0) col(1) ) ///
		bar(1, color(gs4)) bar(2, color(forest_green)) ///
		ytitle("Average assault rate") ///
		plotregion(color(white)) scheme(s1mono) ///
		ylabel(0 (200) 800) ///
		saving($graphs_temp/assrate_gd_nongd,replace)
		
	* distribution of gamedays	
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do"
	keep if d_gameday == 1
	qui gen temp = 1
	
	collapse (count) temp, by(dow_num)
	qui egen temp2 = total(temp)
	qui gen freq = temp / temp2
	
	twoway bar freq  dow_num, ///
		xscale(alt lc(white)) yscale(rev) ///
		plotregion(color(white)) scheme(s1mono) ///		
		xlabel(none) ///
		plotregion(margin(top)) ///
		xtitle("") ytitle("Frequency") ///
		fysize(25) ///
		saving($graphs_temp/distr_gamedays,replace)
		
		
	graph combine "$graphs_temp/assrate_gd_nongd" "$graphs_temp/distr_gamedays", ///
		col(1) imargin(zero) plotregion(color(white)) scheme(s1mono) 
	graph export "$graphs/soc_ext_descr_assaultrate_gd_nongd.pdf", as(pdf) replace
	