// ***************************** PREAMBLE***************************************
*	Created: 06.05.2020
*	Author: Marc Fabel
*	
*	Description:
*		Regression analysis: impact of emotional cues on violent behavior
*
*	Input:
*		data_prepared.csv
*
*	Output:
*		tables in $tables
*		figures in $graphs
*		itnermed figures in $graphs_temp
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
	global graphs		"$path\output\graphs\descriptive"
	global prefix 		"soc_ext_"
	global graphs_temp	"$path\output\graphs\temp"

	
	cd "$prog\analysis"
	
********************************************************************************
*	descriptives about pregame probability spread
********************************************************************************
	
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 	
	
	// how well is the pre-game point spread (expectation vs reality)	
	keep if d_gameday == 1
	
	foreach x in "_win" "_tie" "_loss" {
		qui gen p`x' = 1/odd`x'
	}
	
	qui gen p_diff = p_win - p_loss
	
	
	 _pctile p_diff , p(25, 33.333, 50, 66.667, 75)
	return list
	
	* 25 50 25
	*global thresh_pgpd_l =  `r(r1)'
	*global thresh_pgpd_h =  `r(r5)'

	* 1/3 each
	*global thresh_pgpd_l =  `r(r2)'
	*global thresh_pgpd_h =  `r(r4)'
	
	global thresh_pgpd_l = -0.2
	global thresh_pgpd_h = 0.2
	
	
	qui gen goal_diff = home_result_end - away_result_end	
	
	* scatter PGPS vs REALIZED SCORE DIFFERENTIAL
	scatter goal_diff p_diff, color(navy%10)  || ///
		lfit goal_diff p_diff, color(gs4) lw(medthick) ///
		xtitle("Pregame probability spread") ytitle("Realized score differential") ///
		scheme(s1mono) plotregion(color(white)) ///
		legend(off) ///
		xline($thresh_pgpd_l $thresh_pgpd_h, lp(dash)) ///
		text(-10 -0.6 "predicted loss",place(c) size(small)) ///
		text(-10 0.6  "predicted win",place(c) size(small)) ///
		text(-10 0  "predicted close",place(c) size(small)) ///
		title("Panel A: Final score versus pregame probability spread",pos(11) span  ) ///
		xmtick( -0.9 (.1) 0.9) ///
		saving($graphs_temp/soc_ext_desc_final_score_pgps, replace)
		
	*graph export "$graphs/soc_ext_desc_final_score_pgps.pdf", as(pdf) replace	
		
		* 45 % of the games are in predicted close and win category, and roughly 10 %  in 
		* predicted win (home advantage)
		
		reg goal_diff p_diff
		* the plotted regression line has an intercept of -.0199237   (.0291977) , and a slope of 2.328273   (.0952187)

	
//////////////////
	
	* gen categorical variable containing game outcomes
	capture drop pred_outc
	qui gen pred_outc = 1 if p_diff < $thresh_pgpd_l
	qui replace pred_outc = 3 if p_diff > $thresh_pgpd_h & p_diff != .
	qui replace pred_outc = 2 if pred_outc == . & p_diff !=.
	label define PRED_OUT 1 "predicted loss" 2 "predicted close" 3 "predicted win"
	label val pred_outc PRED_OUT
	
	capture drop dwin dtie dloss
	bys pred_outc: egen dwin = mean(cond(goal_diff>0,1,0))
	by pred_outc: egen dtie = mean(cond(goal_diff==0,1,0))
	by pred_outc: egen dloss = mean(cond(goal_diff<0,1,0))
	
	graph bar dwin dtie dloss, over(pred_outc) stack bar(1,color(forest_green)) ///
		bar(2,color(gs6)) bar(3,color(maroon)) ytitle("Fraction") ///
		scheme(s1mono) plotregion(color(white)) ylabel(,nogrid) ///
		title("Panel B: Outcomes versus predicted outcome",pos(11) span  ) ///
		legend(label(3 "loss") label(2 "tie") label(1 "win") pos(6) ring(1) col(3)) ///
		saving($graphs_temp/soc_ext_desc_share_outcomes_per_pred_outcome, replace)
	*graph export "$graphs/soc_ext_desc_share_outcomes_per_pred_outcome.pdf", as(pdf) replace	
		
		
	// probability of victory
	qui gen dvictory = cond(goal_diff>0,1,0)
	
	
	capture drop d_victory_pred
	reg dvictory c.p_diff##C.p_diff##C.p_diff 
	predict d_victory_pred
	
	line d_victory_pred p_diff, sort lw(medthick) lc(gs4) ///
		xtitle("Pregame probability spread") ytitle("Probability of victory") ///
		scheme(s1mono) plotregion(color(white)) ///
		legend(off) ylabel(0 (0.25) 1) ///
		xline($thresh_pgpd_l $thresh_pgpd_h, lp(dash)) ///
		text(0 -0.6 "predicted loss",place(c) size(small)) ///
		text(0 0.6  "predicted win",place(c) size(small)) ///
		text(0 0  "predicted close",place(c) size(small)) ///		
		xmtick( -0.9 (.1) 0.9) ///
		title("Panel C: Probability of victory as function of spread",pos(11) span  ) ///
		saving($graphs_temp/soc_ext_desc_prob_victory, replace)
			
			
	graph combine ///
		"$graphs_temp/soc_ext_desc_final_score_pgps.gph" ///
		"$graphs_temp/soc_ext_desc_share_outcomes_per_pred_outcome.gph" ///
		"$graphs_temp/soc_ext_desc_prob_victory.gph" , ///
		altshrink scheme(s1mono) plotregion(color(white)) col(2)
		
	graph export "$graphs/soc_ext_pregame_probability_spread_outcomes.pdf", ///
		as(pdf) replace
		
		
********************************************************************************
*	2 Regression
********************************************************************************
	use "$data/data_prepared.dta", clear
	do "$prog/aux_files/soc_ext_aux_program.do" 
	
	
	
	foreach x in "_win" "_tie" "_loss" {
		qui gen p`x' = 1/odd`x'
	}
	qui gen p_diff = p_win - p_loss

	
	* generate variables
	qui gen goal_diff = home_result_end - away_result_end	
	qui gen dwin = cond(goal_diff>0 & goal_diff!=.,1,0)
	qui gen dloss = cond(goal_diff<0,1,0)
	qui gen dtie = cond(goal_diff==0,1,0)
	

	
	qui gen pred_loss = cond(p_diff < $thresh_pgpd_l ,1,0)
	qui gen pred_win = cond(p_diff > $thresh_pgpd_h & p_diff!=.,1,0)
	qui gen pred_close =cond(p_diff >= $thresh_pgpd_l & p_diff<=$thresh_pgpd_h ,1,0)
	
	qui gen pred_loss_win = cond(dwin == 1 & pred_loss == 1,1,0)
	qui gen pred_close_loss = cond(dloss == 1 & pred_close == 1,1,0)
	qui gen pred_close_win = cond(dwin == 1& pred_close == 1,1,0)
	qui gen pred_win_loss = cond(dloss == 1 & pred_win == 1,1,0)
	

	
	
	global expect_outcome "pred_loss pred_win pred_close"
	global expect_outcomeXactual_outcomes "pred_loss_win pred_close_loss pred_win_loss"
	*global expect_outcomeXactual_outcomes "pred_loss_win pred_close_win pred_win_loss" 
	
* w/o interaction expectation and actual outcome
	eststo b1: reghdfe assrate $expect_outcome $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)  
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"

	
* w/ interaction: expectation and 	
	eststo b2: reghdfe assrate $expect_outcome $expect_outcomeXactual_outcomes $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)  
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"


	esttab b*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01)  								///
		keep(pred_*) 													///
		scalars( "N Observations" 										///
		"region Region FE" "time Date Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt( %12.0fc)	b(%12.3f) se(%12.3f) 		///
		coeflabels(pred_loss "Gameday, expected to lose"				///
			pred_win "Gameday, expected to win"							///
			pred_close "Gameday, expected to be close"					///
			pred_loss_win "Gameday, expected to lose and won"			///
			pred_win_loss "Gameday, expected to win and lost"			///
			pred_close_loss "Gameday, expected to be close and lost")

	
	
	
	// no difference when I make it not symmetric to th eorigin.

	
	
	
********************************************************************************
*	3 Regression with other dimensions of emotional cues
********************************************************************************	
	* stärker aufs Geschen eingehen
	
	* game outcomes 
	global outcome "dwin dtie dloss"
	eststo a1: reghdfe assrate $outcome $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)  
		
	* refereee quality
	capture drop d_ref*
	qui gen d_ref_notbad = cond(grade_ref <= 4,1,0)
	qui gen d_ref_bad = cond(grade_ref >4 & grade_ref!=.,1,0)
	local ref_vars "d_ref_bad d_ref_notbad"
	eststo a2: reghdfe assrate `ref_vars' $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)
		
		
	* league
	qui gen d_l1 = cond(league == 1, 1,0)
	qui gen d_l2 = cond(league == 2, 1,0)
	qui gen d_l3 = cond(league == 3, 1,0)
	local league_vars "d_l1 d_l2 d_l3"
	eststo a3: reghdfe assrate `league_vars' $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)
		
		
	* penalties
	qui gen d_penalty = cond(penalties > 0 & penalties!=.,1,0)
	qui gen d_penalty_null = cond(penalties == 0,1,0)
	local penalty_vars "d_penalty d_penalty_null"
	eststo a4: reghdfe assrate `penalty_vars' $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)
		
		
	* red cards
	qui gen red_cards = home_red + away_red
	qui gen d_red = cond(red_cards>0 & red_cards!=.,1,0)
	qui gen d_red_no = cond(red_cards==0,1,0)
	local red_vars "d_red d_red_no"
	eststo a5: reghdfe assrate `red_vars' $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)
	
	
	*index (20% have penalty, 15% bad ref, 10% red card) : 35% of games have upsetting event
	qui gen d_upset = cond(d_red==1 | d_penalty==1 | d_ref_bad==1,1,0)
	qui gen d_upset_no = cond(d_upset == 0 & d_gameday==1,1,0)
	local index_vars "d_upset d_upset_no"
	eststo a6: reghdfe assrate `index_vars' $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
		
	
	*index in two columns not in one regression
	eststo a7: reghdfe assrate d_upset $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)	
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"
	
	eststo a8: reghdfe assrate d_upset_no $weather [pw=p_wght], ///
		absorb($region_fe $time_fe $holiday $interaction ) ///
		vce(cluster ags#year year#month)	
	qui estadd local region 	"yes"
	qui estadd local time 		"yes" 
	qui estadd local weather 	"yes"
	qui estadd local holiday	"yes"
	qui estadd local interact	"yes"	
	
	
	 * won/lost in last minutes, place of table X Spieltag 
		
	* derbys
	
	* interaction vars mit win/loss
	
		
	esttab a*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01)  								///
		keep(dwin dtie dloss d_ref* d_l* d_penal* d_red* d_upset*) 		///
		scalars( "N Observations" 										///
		"region Region FE" "time Date Fe" "weather Weather Controls" 	///
		"holiday Holiday FE" "interact Interact FE") 					///
		sfmt( %12.0fc)	b(%12.3f) se(%12.3f)	
		
		
		
	
	
	
// COMBINE EMOTIONAL CUES SPECIFICATIONS for outreg ****************************	
		
		
	esttab a6 b*, noobs 													///
		se star(* 0.10 ** 0.05 *** 0.01)  									///
		keep(d_upset* pred_*) 												///
		scalars( "N Observations" 											///
		"region Region FE" "time Date Fe" "weather Weather Controls" 		///
		"holiday Holiday FE" "interact Interact FE") 						///
		sfmt( %12.0fc)	b(%12.3f) se(%12.3f) 								///
		coeflabels(															///
			d_upset "Upset event (Index)"									///
			d_upset_no "No upset event (Index)"								///
			pred_loss "Expected to lose"									///
			pred_win "Expected to win"										///
			pred_close "Expected to be close"								///
			pred_loss_win "Expected to lose and won (upset win)"			///
			pred_win_loss "Expected to win and lost (upset loss)"			///
			pred_close_loss "Expected to be close and lost (upset loss)")
		
	
	
	esttab a6 b* using "$tables/assrate_fixed_effects_emotional_cues.tex", 	///
		se star(* 0.10 ** 0.05 *** 0.01)				 					///
		keep(d_upset* pred_*) 												///
		scalars("N \midrule Observations"									///
		"region Region FE" "time Date Fe" "weather Weather Controls"		///
		"holiday Holiday FE" "interact Interact FE") 						///
		sfmt(%12.0fc)	b(%12.3f) se(%12.3f) 								///
		replace booktabs fragment label 									///
		nomtitles nonumbers noobs nonote nogaps noline						///
		coeflabels(															///
			d_upset "Upset event (Index)"									///
			d_upset_no "No upset event (Index)"								///
			pred_loss "Expected to lose"									///
			pred_win "Expected to win"										///
			pred_close "Expected to be close"								///
			pred_loss_win "Expected to lose and won (upset win)"			///
			pred_win_loss "Expected to win and lost (upset loss)"			///
			pred_close_loss "Expected to be close and lost (upset loss)")
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
		