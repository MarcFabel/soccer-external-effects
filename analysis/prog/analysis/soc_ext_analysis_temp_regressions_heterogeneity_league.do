	
	
* rumspielerei mit League: 

	qui gen league2 = league
	qui replace league2 = -99 if league2 == .
	qui gen TxL = d_gameday * league2	
	
	
	reg_fe a1 assrate $gd "$weather if league == 1" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	reg_fe a2 assrate $gd "$weather if league == 2" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	reg_fe a3 assrate $gd "$weather if league == 3" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	
	
	reghdfe assrate i.TxL $weather [pw=p_wght], absorb($region_fe $time_fe $holiday $interaction) vce(cluster ags#year year#month)  
	
	
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		scalars("mean Effect size [\%]" "Nn Observations" 				///
		"region Region FE" "time Time Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 