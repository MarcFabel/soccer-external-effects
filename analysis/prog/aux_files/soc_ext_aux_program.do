	// define regression variables *************************************************
	global gd 				"d_gameday"
	global region_fe 		"i.ags"
	global time_fe 			"i.dow_num i.month i.year" // i.woy 
	global weather 			"tmk txk tnk tgk vpm nm pm upm rs sdk sh fm"
	global holiday 			"i.sch_hday i.pub_hday i.special_day"
	global interaction 		"i.ags##i.dow_num i.ags##i.month i.ags##i.year" // alternative way: i.ags##i.(dow_num month year)
	
	
// Programm for regression *****************************************************
capture program drop reg_fe
	program define reg_fe
		qui eststo `1': reghdfe `2' `3' `4' [pw=p_wght], absorb(`5') vce(cluster ags#year year#month)  
		qui estadd scalar Nn = e(N)
		qui summ `2' if e(sample) & d_gameday == 0
		qui estadd scalar mean = abs(round(_b[`3']/`r(mean)'*100,.01))
	end
