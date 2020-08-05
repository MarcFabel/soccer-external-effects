	set seed 123
	set processors 4
	

	global path   	   	"F:\econ\soc_ext\analysis"	
	global data			"$path\data\final"
	global temp			"$path/output/temp"
	global prog			"$path\prog"

	
	
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 
	eststo clear
	
	
	
	capture drop temp d_gameday_random
	summ d_gameday
	scalar number_games = r(mean)
	drop if d_gameday == 1
	qui gen temp = runiform() 
	qui gen d_gameday_random = cond(temp < number_games, 1,0)
	
	reg_fe a assrate d_gameday_random "$weather" "$region_fe $time_fe $holiday $interaction"
	
	esttab a using "$temp/placebo_10000.csv", replace noobs 	wide		///
		se nostar keep(d_gameday_random) 				///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) ///
		nomtitles nonumbers  nonote nogaps noline nopar
	
	
	
	
	
	forval j=1/9999 {
		disp `j'
		capture drop temp d_gameday_random
		qui gen temp = runiform() 
		qui gen d_gameday_random = cond(temp < number_games, 1,0)
		
		reg_fe a assrate d_gameday_random "$weather" "$region_fe $time_fe $holiday $interaction"
		
		esttab a using "$temp/placebo_10000.csv", append noobs wide			///
			se nostar keep(d_gameday_random) 				///
			sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) ///
			nomtitles nonumbers  nonote nogaps noline nopar
		
	}
	
	
// open file: 
	import delimited "$temp/placebo_10000.csv", delimiter("") stripquote(yes) colrange(2) clear 
	
	capture drop beta
	qui gen beta = substr(v1,2,.)
	qui gen se = substr(v2,2,.)
	drop v1 v2
	destring * , replace
	qui gen t = (beta/se)
	qui gen n = _n
	qui gen d_significant = cond(t<-1.96 | t>1.96,1,0)
	qui gen number_significant = [0]
	replace number_significant = d_significant[_n] + number_significant[_n-1] if n>1
	qui gen fraction_significant = (number_significant/n)*100
	
	summ d_significant    // 6.57% of all estimates are statistically significant with alpha = 0.05
	
	* alpha = 0.01 : z=2.325
	qui gen d_significant_99 = cond(t<-2.325 | t>2.325,1,0)
	summ d_significant_99 //  3.06 of all estimates are statistically significant with alpha = 0.01
	
	
	
	// Figures
	kdensity beta, generate(beta_vals beta_den_vals)
	
	* histogram beta 
	hist beta  , normal normopt(lcolor(navy) lw(thick) ) ///
		fcol(gs8%50) ///
		scheme(s1mono) plotregion(color(white)) ///
		xlabel(-.5 0 .5) ///
		xtitle(Beta) /// 
		title("Panel A: Distribution of Coefficients", pos(11) span size(vlarge)) ///
		addplot(line beta_den_vals beta_vals, lc(none) ) ///
		legend(label(2 " normal density") order(2) pos(2) ring(0) region(ls(none))) ///
		saving($temp/placebo_beta.gph, replace)
	
	
	*density t
	kdensity t, generate(t_vals den_vals)
	
	twoway 	area den_vals t_vals, color(gs8) || ///
		area den_vals t_vals if t_vals<-1.96, color(gs2%80) || ///
		area den_vals t_vals if t_vals>1.96, color(gs2%80) || ///
		line den_vals t_vals, color(gs2)   ///
		scheme(s1mono) plotregion(color(white)) ///
		legend(off) ///
		xtitle("t") ytitle("Density") /// 
		title("Panel B: Distribution of t-statistics", pos(11) span size(vlarge)) ///
		saving($temp/placebo_t.gph, replace)
		
		
	* histogram t
	preserve
		drop if t<-4 | t>4					// just for visualization purposes * drops 3/10,000 observations
		capture drop t_vals den_vals
		kdensity t, generate(t_vals den_vals)
		
		hist t, kden  kdenopts(lcolor(maroon) lw(thick)) 	///
			fcol(gs8%50) ///
			scheme(s1mono) plotregion(color(white)) ///
			xtitle("t") ///
			addplot(area den_vals t_vals if t_vals<-1.96, color(maroon%100) || ///
			area den_vals t_vals if t_vals>1.96, color(maroon%100) below) ///
			legend(label(2 "kernel density") label(3 "significant" "coefficients") ///
			order(2 3)  pos(2) ring(0) region(ls(none))) ///
			title("Panel B: Distribution of t-statistics", pos(11) span size(vlarge)) ///
			saving($temp/placebo_t.gph, replace)
	restore
		

	
	* fraction of significant estimates
	line fraction_significant n if n>40, lc(gs2) ///
		scheme(s1mono) plotregion(color(white)) ///
		xtitle("Iteration") ytitle("Percent") ///
		title("Panel C: Fraction significant estimates", pos(11) span size(vlarge)) ///
		saving($temp/placebo_fraction_significant.gph, replace)
	
	*graph combine
	cd $temp	
	graph combine "placebo_beta" "placebo_t.gph" "placebo_fraction_significant.gph", ///
		altshrink scheme(s1mono) plotregion(color(white)) col(2)
		
	graph export "$graphs/robustness_placebo_games.pdf", as(pdf) replace
	
