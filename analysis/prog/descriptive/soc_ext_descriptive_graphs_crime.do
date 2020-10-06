// ***************************** PREAMBLE********************************
	clear all 
	set more off
	
	*paths
	global path   	   	"F:\econ\soc_ext\analysis"	
	global data			"$path\output/temp/"
	global graphs		"$path\output\graphs\descriptive"
	global graphs_temp	"$path\output\graphs\temp"
	global prefix 		"soc_ext_"
	global prog			"$path\prog"


	
// ***********************************************************************







// 1.A) Assaults across day ****************************************************
use "$data/ass_h.dta", clear
label define HOUR ///
	0  "06" ///
	1  "07" ///
	2  "08" ///
	3  "09" ///
	4  "10" ///
	5  "11" ///
	6  "12" ///
	7  "13" ///
	8  "14" ///
	9  "15" ///
	10 "16" ///
	11 "17" ///
	12 "18" ///
	13 "19" ///
	14 "20" ///
	15 "21" ///
	16 "22" ///
	17 "23" ///
	18 "00" ///
	19 "01" ///
	20 "02" ///
	21 "03" ///
	22 "04" ///
	23 "05" 
	
label val hour_num HOUR	

graph bar freq, over(hour_num)  stack ///
	title("Panel A: Assaults across the course of a day",pos(11) span  size(vlarge)) ///
		plotregion(color(white)) scheme(s1mono) ///
		ytitle("Relative frequency") ///
		saving($graphs_temp/soc_ext_desc_crime_h, replace)
		
		
		

// 1.B) Assaults across DOW ****************************************************
use "$data/ass_dow.dta", clear
label define DOW ///
	1  "Mon" ///
	2  "Tue" ///
	3  "Wed" ///
	4  "Thu" ///
	5  "Fri" ///
	6  "Sat" ///
	7  "Sun" 
	
	
label val dow_num DOW	

graph bar freq, over(dow_num)  stack ///
	title("Panel B: Assaults across days of the week",pos(11) span  size(vlarge)) ///
		plotregion(color(white)) scheme(s1mono) ///
		ytitle("Relative frequency") ///
		saving($graphs_temp/soc_ext_desc_crime_dow, replace)
		
		
// 1.C) Assaults across months ****************************************************
use "$data/ass_month.dta", clear
label define MONTH ///
	1  "Jan" ///
	2  "Feb" ///
	3  "Mar" ///
	4  "Apr" ///
	5  "May" ///
	6  "Jun" ///
	7  "Jul" ///
	8  "Aug" ///
	9  "Sep" ///
	10 "Oct" ///
	11 "Nov" ///
	12 "Dec" ///
	
	
label val month_num MONTH	

graph bar freq_norm, over(month_num)  stack ///
	title("Panel C: Assaults across months of the year{superscript:1}",pos(11) span  size(vlarge)) ///
		plotregion(color(white)) scheme(s1mono) ///
		ytitle("Relative frequency") ///
		saving($graphs_temp/soc_ext_desc_crime_month, replace)	
		
		
		
// 1.D) Assaults across months ****************************************************
use "$data/ass_day.dta", clear		
		
	
line freq date_d_mod, ///
	title("Panel D: Assaults across days of the year{superscript:1}",pos(11) span  size(vlarge)) ///
		plotregion(color(white)) scheme(s1mono) ///
		ytitle("Relative frequency") xtitle("") ///
		ylabel(,grid) tlabel(01jan2014 01mar2014 01may2014 01jul2014 01sep2014 01nov2014,format(%tdm)) ///
		tmtick(01feb2014 01apr2014 01jun2014 01aug2014 01oct2014 01dec2014) ///
		saving($graphs_temp/soc_ext_desc_crime_days, replace)	
		

		
// 1.E) Combine the single graphs **********************************************	
	graph combine "$graphs_temp/soc_ext_desc_crime_h.gph" ///
		"$graphs_temp/soc_ext_desc_crime_dow.gph" ///
		"$graphs_temp/soc_ext_desc_crime_month.gph" ///
		"$graphs_temp/soc_ext_desc_crime_days.gph" , ///
		altshrink scheme(s1mono) plotregion(color(white)) col(2)	
		
	graph export "$graphs/soc_ect_desc_crime_ass_time.pdf", as(pdf) replace		
		