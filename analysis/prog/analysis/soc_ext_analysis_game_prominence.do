// ***************************** PREAMBLE***************************************
*	Created: 08.04.2020
*	Author: Marc Fabel
*	
*	Description:
*		ßßßßßßß
*
*	Input:
*		xxx
*
*	Output:
*		xxx
*
*
*	Update: 
*		29.07.2020	added games to violent_games list (increased effect of derbies)	
	
	clear all 
	set more off
	set matsize 11000
	
	*paths
	global path   	   	"F:\econ\soc_ext\analysis"	
	global data			"$path\data\final"
	global tables 		"$path\output\tables\reg_fe"
	global temp			"$path/output/temp"
	global prog			"$path\prog"
	global source		"$path/data/source/soccer"
	
	cd "$prog\analysis"
	

	
	
	do "$prog/aux_files/soc_ext_aux_program.do" 
	
	
********************************************************************************
*	merge data to working sample
********************************************************************************
	
	
	import delimited "$source/violent_games.csv", delimiter(";") varnames(nonames) encoding(UTF-8) clear 
	rename v1 home_team
	rename v2 away_team
	
	merge 1:m home_team away_team using "$data/data_prepared.dta"
	drop if _merge == 1
	qui gen d_derby = cond(_merge == 3, 1, 0)
	drop _merge

********************************************************************************
*	 Lindo approach - Game Prominence
********************************************************************************

	qui gen d_game_nonderby = cond(d_gameday == 1 & d_derby==0, 1, 0)
	qui gen d_game_derby = cond(d_gameday == 1 & d_derby==1, 1, 0)
		 
			 
	eststo clear
	reg_fe a1 assrate d_game_derby    "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	reg_fe a2 assrate d_game_nonderby "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"

				
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		rename(d_game_nonderby d_gameday d_game_derby d_gameday) 		///
		coeflabels(d_gameday "Game day") 								///
		scalars("mean Effect size [\%]" "Nn Observations" 				///
		"region Region FE" "time Date Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f)			
		
/*
--------------------------------------------
                      (1)             (2)   
                  assrate         assrate   
--------------------------------------------
d_game_derby        7.976***                
                  (1.779)                   

d_game_non~y                        2.430***
                                  (0.282)   
--------------------------------------------

* with more derbies: v2 of violent games

*/				






********************************************************************************
/// Liga - Team Prominence
********************************************************************************


* interactions league w/ gameday indicator
	qui gen d_game_l1 = cond(d_gameday == 1 & league == 1, 1, 0)
	qui gen d_game_l2 = cond(d_gameday == 1 & league == 2, 1, 0)
	qui gen d_game_l3 = cond(d_gameday == 1 & league == 3, 1, 0)

	reg_fe b1 assrate d_game_l1 "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	reg_fe b2 assrate d_game_l2 "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"

	reg_fe b3 assrate d_game_l3 "$weather" "$region_fe $time_fe $holiday $interaction"
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
		
/*		
------------------------------------------------------------
d_game_l1           3.530***                                
                  (0.460)                                   

d_game_l2                           1.878***                
                                  (0.318)                   

d_game_l3                                           1.569***
                                                  (0.350)   
------------------------------------------------------------
*/	
	
	
	
	
	esttab a* b*, noobs													///
		se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 				///
		rename(d_game_nonderby d_gameday d_game_derby d_gameday			///
		d_game_l1 d_gameday d_game_l2 d_gameday d_game_l3 d_gameday)	/// 
		coeflabels(d_gameday "Game day") 								///
		scalars("mean Effect size [\%]" "Nn Observations" 				///
		"region Region FE" "time Date Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f)	


	
		
		
		
	esttab a* b* using "$tables/assrate_fixed_effects_prominent_games.tex", 				///
		se star(* 0.10 ** 0.05 *** 0.01)				 				///
		keep(d_gameday) coeflabels(d_gameday "Game day")				///
		rename(d_game_nonderby d_gameday d_game_derby d_gameday			///
		d_game_l1 d_gameday d_game_l2 d_gameday d_game_l3 d_gameday)	/// 
		scalars("mean \midrule Effect size [\%]" "Nn Observations"		///
		"region Region FE" "time Date Fe" "weather Weather Controls"	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt(%3.2f %12.0fc)	b(%12.3f) se(%12.3f) 						///
		replace booktabs fragment label 								///
		nomtitles nonumbers noobs nonote nogaps noline		
		
		
		
		
		
		
/*


	reghdfe assrate i.TxL $weather [pw=p_wght], absorb($region_fe $time_fe $holiday $interaction) vce(cluster ags#year year#month)  
	
/*
------------------------------------------------------------------------------
             |               Robust
     assrate |      Coef.   Std. Err.      t    P>|t|     [95% Conf. Interval]
-------------+----------------------------------------------------------------
         TxL |
          1  |   3.745923   .4643874     8.07   0.000      2.81221    4.679637
          2  |   2.136899   .3229615     6.62   0.000     1.487541    2.786257
          3  |   1.824483   .3629552     5.03   0.000     1.094713    2.554253
*/






	reghdfe assrate i.d_gameday#i.d_derby $weather [pw=p_wght], absorb($region_fe $time_fe $holiday $interaction) vce(cluster ags#year year#month)  
	
/*	
d_gameday#d_derby |
             0 1  |          0  (empty)
             1 0  |    2.50149   .2834135     8.83   0.000     1.931648    3.071331
             1 1  |   8.524272   1.791706     4.76   0.000     4.921805    12.12674

*/
			
			

	
	reghdfe assrate d_game_* $weather [pw=p_wght], absorb($region_fe $time_fe $holiday $interaction) vce(cluster ags#year year#month)  
	
	* same as with  i.d_gameday#i.d_derby
	
	
	// what with ##

	reghdfe assrate i.d_gameday##i.d_derby $weather [pw=p_wght], absorb($region_fe $time_fe $holiday $interaction) vce(cluster ags#year year#month)  
	
	
/*	
      1.d_gameday |    2.50149   .2834135     8.83   0.000     1.931648    3.071331
        1.d_derby |   6.022782   1.797708     3.35   0.002     2.408249    9.637315
                  |
d_gameday#d_derby |
             0 1  |          0  (empty)
             1 1  |          0  (omitted)
			 
			 */




*/
	sum pop_density, d
	qui gen city = cond(pop_density >= r(p50),1,0)

	eststo clear
	reg_fe b1 assrate d_gameday "$weather if city == 1" "$region_fe $time_fe $holiday $interaction"
	reg_fe b2 assrate d_gameday "$weather if city == 0" "$region_fe $time_fe $holiday $interaction"
	esttab b*, se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 

	
	/*	
	--------------------------------------------
						(1)             (2)   
				       assrate         assrate   
	--------------------------------------------
	d_gameday           2.479***        4.033***
					   (0.297)         (0.495)   
	--------------------------------------------
	N                   44089           43939   
	--------------------------------------------
	*/
	
		
	
	sum ue_rate, d
	qui gen ueregion = cond(ue_rate >= r(p50),1,0)
	eststo clear
	reg_fe b1 assrate d_gameday "$weather if ueregion == 1" "$region_fe $time_fe $holiday $interaction"
	reg_fe b2 assrate d_gameday "$weather if ueregion == 0" "$region_fe $time_fe $holiday $interaction"
	esttab b*, se star(* 0.10 ** 0.05 *** 0.01) keep(d_gameday) 


