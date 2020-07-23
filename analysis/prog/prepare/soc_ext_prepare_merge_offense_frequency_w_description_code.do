// generate overview of offense distribution and their description & paragraph in the law code


	global path   	   	"F:\econ\soc_ext\analysis"	
	global temp			"$path/output/temp"


* frequency of 2014 offenses
	import delimited "F:\econ\soc_ext\analysis\data\intermediate\crime\offenses_frequency_2014.csv", stringcols(1) clear 
	
	* add leading zeros 
	replace offense_key = "010079" if offense_key == "10079"
	replace offense_key = "011000" if offense_key == "11000"
	replace offense_key = "012000" if offense_key == "12000"
	replace offense_key = "020010" if offense_key == "20010"
	replace offense_key = "020020" if offense_key == "20020"
	replace offense_key = "020030" if offense_key == "20030"
	replace offense_key = "030000" if offense_key == "30000"

	save "$temp/offenses_frequency_2014.dta", replace
	
	
* open sheet of BKA DATEN w/ description of the key
 import excel "F:\econ\soc_ext\analysis\data\source\BKA\Kataloge-Datenblatt_EDS_Opfer_2014\01-0_Strft-Kat_Plausi_SumBez_gesamt_14.xlsx", ///
	sheet("1_PKS_Strft-Kat-2014-DB") cellrange(N11:T1047) allstring clear
	rename N offense_key
	rename O description
	rename Q code
	rename R paragraph
	rename S v_from
	rename T v_until
	drop P
	drop if offense_key == "" | offense_key == "------"
	
	merge 1:1 offense_key using "$temp/offenses_frequency_2014.dta"
	keep if _merge == 3
	gsort - counts
	qui gen rank = _n
	drop _merge
	
	
	qui gen key_2 = substr(offense_key,1,2)
	order key_2
	
	order rank offense_key counts freq description paragraph code
	
	