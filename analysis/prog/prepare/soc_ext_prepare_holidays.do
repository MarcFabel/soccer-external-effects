********************************************************************************
*******************************SCHULFERIEN**************************************
********************************************************************************
*Aufbauend auf do-File von Costanza Gai

clear all
set processor 4
set maxvar 120000
*** Makros
global data "F:\econ\soc_ext\analysis\data\source\holidays\" 
global outputdata "F:\econ\soc_ext\analysis\data\final\holidays\"
 


********************************************************************************
*************************LOOP OVER SINGLE FILES*********************************
********************************************************************************

forvalues i=94/119 {
	local j = `i' + 1
	import excel "${data}Excel_Tabellen\Schulferien_`i'_`j'.xlsx",clear 
	
	*1.Year variable: year1 before Christmas, year2 after Christmas 
	gen n=_n
	gen year=B if n==2
	destring year, replace force 
	egen year1=max(year)
	drop year
	gen year=E if n==2
	destring year, replace force
	egen year2=max(year)
	drop year 
	
	*2.Rename Variables according to Holiday type:
	*Files with Sommer at the beginning of the new school year
	if  `i'<=101 {
		rename A Bundesland 
		rename B Sommer 
		rename C Herbst 
		rename D Weinachten 
		rename E Winter 
		rename F Ostern  
		rename G Himmelf_Pfingsten 
		drop if _n==1 |_n==2
	}
	*Files with Sommer at the end of the past school year
	else if `i'>101 {
		rename A Bundesland 
		rename B Herbst 
		rename C Weinachten 
		rename D Winter 
		rename E Ostern  
		rename F Himmelf_Pfingsten 
		rename G Sommer
		drop if _n==1 |_n==2
	}
	*3.Remove parentheses from Bundeländer:
	gen bew_Ferien=substr(Bundesland, strpos(Bundesland, "(")+1,strpos(Bundesland, ")")-strpos(Bundesland, "(")-1)
	gen bew_Ferien2=substr(Bundesland, strpos(Bundesland, "("),strpos(Bundesland, ")")-strpos(Bundesland, "("))
	replace Bundesland=substr(Bundesland, 1, strpos(Bundesland, "(") - 1) if bew_Ferien2!="" 
	replace Bundesland= subinstr(Bundesland," ","",.)
	replace bew_Ferien="." if (bew_Ferien=="" | bew_Ferien=="-") 
	gen bew_Ferien_1=substr(bew_Ferien,1,strpos(bew_Ferien, "-")-1) if strlen(bew_Ferien)>=3
	gen bew_Ferien_2=substr(bew_Ferien,strpos(bew_Ferien, "-")+1,.) if strlen(bew_Ferien)>=3
	destring bew_Ferien_1 bew_Ferien_2, replace
	replace bew_Ferien="(bew_Ferien_1+bew_Ferien_2)/2" if bew_Ferien_1!=. & bew_Ferien_2!=.
	destring bew_Ferien, replace
	drop bew_Ferien_1 bew_Ferien_2 
	
	
	*4.Generate empty variables for each type of holiday to be filled in later: 
	foreach var of varlist Sommer Herbst Weinachten Winter Ostern Himmelf_Pfingsten {
		replace `var'= usubinstr(`var'," ","",.) 
		gen `var'_ft_d=""
		gen `var'_ft_m=""
		gen `var'_ft1_d=""
		gen `var'_ft1_m=""
		gen `var'_ft2_d=""
		gen `var'_ft2_m=""
		gen `var'_ft3_d=""
		gen `var'_ft3_m=""
	}
	
	*5.Generate variables that allow to identify all possible separation cases: "-", "u.", "und", "+", "/": 
	foreach var of varlist Sommer Herbst Weinachten Winter Ostern Himmelf_Pfingsten {
		replace `var'=subinstr(`var',"–","-",3)                                          // convert extended ASCII into plain ASCII so that split always recognises "-" 
		gen test_`var'=strpos(`var', "-")  
		
		gen testu_`var'=strpos(`var', "u.")
		egen testu_`var'_tot=total(testu_`var')
		
		gen testund_`var'=strpos(`var', "und")
		egen testund_`var'_tot=total(testund_`var')
		
		gen testp_`var'=strpos(`var', "+")
		egen testp_`var'_tot=total(testp_`var')
		
		gen tests_`var'=strpos(`var', "/")
		egen tests_`var'_tot=total(tests_`var')
		
		gen testsl_`var'=strrpos(`var', "/")                                             // gives the last obs. of /, for cases in which there are two "/" separators 
		egen testsl_`var'_tot=total(testsl_`var')
	}
	
	********************STRING SEPARATION AND FORMATTING****************************
	
	*CASE 1: holidays separated by "-" and in some cases also by "/", "und" or "u." 
	* or a combination of both: 
	foreach var of varlist Sommer Herbst Weinachten Winter Ostern Himmelf_Pfingsten {
		split `var' if test_`var'>0,p(-) 
		gen `var'1_length=  strlen(`var'1)                                                
		gen `var'_beg_d=substr(`var'1,1,2) if testu_`var'==0&testund_`var'==0&tests_`var'==0
		gen `var'_beg_m=substr(`var'1,4,2) if testu_`var'==0&testund_`var'==0&tests_`var'==0
		gen `var'_end_d=substr(`var'2,1,2) if testu_`var'==0&testund_`var'==0&tests_`var'==0
		gen `var'_end_m=substr(`var'2,4,2) if testu_`var'==0&testund_`var'==0&tests_`var'==0
		replace `var'_beg_m=`var'_end_m if testu_`var'==0&testund_`var'==0&tests_`var'==0&`var'1_length==3
		
		replace `var'1= subinstr(`var'1," ","",.)                                        // eliminate all blank spaces of string variables 
		replace `var'2= subinstr(`var'2," ","",.)
		
		gen tests_`var'1=strpos(`var'1, "/")                                             // Generate indicators for each SPLITTED variable for indicators "/", "und" and "u."
		egen tests_`var'1_tot=total(tests_`var'1)
		gen tests_`var'2=strpos(`var'2, "/")                                             
		egen tests_`var'2_tot=total(tests_`var'2)
		
		gen testund1_`var'1=strpos(`var'1, "und")                                      
		egen testund1_`var'1_tot=total(testund1_`var'1)
		gen testund2_`var'2=strpos(`var'2, "und")                                       
		egen testund2_`var'2_tot=total(testund2_`var'2)
		
		gen testu1_`var'1=strpos(`var'1, "u.")                                         
		egen testu1_`var'1_tot=total(testu1_`var'1)
		gen testu2_`var'2=strpos(`var'2, "u.")                                           
		egen testu2_`var'2_tot=total(testu2_`var'2)
		
		if tests_`var'1_tot>0 {                                                          // if splitted VARIABLE1 contains "/", then  
			split `var'1,p(/)  
			replace `var'11=ustrtrim(`var'11)   
			replace `var'12=ustrtrim(`var'12) 
			gen `var'12_length=  strlen(`var'12)
			gen `var'11_length=  strlen(`var'11)                                                                                        
			replace `var'_ft_d=substr(`var'11,1,2) if tests_`var'1!=0
			replace `var'_ft_m=substr(`var'11,4,2) if tests_`var'1!=0
			replace `var'_beg_d=substr(`var'12,1,2) if tests_`var'1!=0
			replace `var'_beg_m=substr(`var'12,4,2) if tests_`var'1!=0
			replace `var'_end_d=substr(`var'2,1,2) if tests_`var'2==0
			replace `var'_end_m=substr(`var'2,4,2) if tests_`var'2==0
			replace `var'_beg_m=`var'_end_m  if tests_`var'2==0&`var'12_length==3
			replace `var'_ft_m=`var'_beg_m  if tests_`var'2==0&`var'11_length==3
			if testund1_`var'1_tot>0 {                                                       // if splitted VARIABLE1 also contains "und", then 
				replace `var'_ft1_d=substr(`var'11,1,2) if tests_`var'1!=0 &testund1_`var'1!=0
				replace `var'_ft1_m=substr(`var'11,4,2) if tests_`var'1!=0 &testund1_`var'1!=0
				replace `var'_ft2_d=substr(`var'12,1,2) if tests_`var'1!=0 &testund1_`var'1!=0
				replace `var'_ft2_m=substr(`var'12,4,2) if tests_`var'1!=0 &testund1_`var'1!=0
				split `var'12,p(und)
				replace `var'_beg_d=substr(`var'122,1,2) if tests_`var'1!=0&testund1_`var'1!=0
				replace `var'_beg_m=substr(`var'122,4,2) if tests_`var'1!=0&testund1_`var'1!=0
				drop `var'121 `var'122 `var'12_length `var'11_length
			}
			drop `var'11 `var'12 
		}
		if tests_`var'2_tot>0 {                                                          // if splitted VARIABLE2 contains "/", then 
		split `var'2, p(/)  
		replace `var'21=ustrtrim(`var'21)   
		replace `var'22=ustrtrim(`var'22)                                                                                               
		replace `var'_ft_d=substr(`var'22,1,2) if tests_`var'2!=0
		replace `var'_ft_m=substr(`var'22,4,2) if tests_`var'2!=0
		replace `var'_end_d=substr(`var'21,1,2) if tests_`var'2!=0
		replace `var'_end_m=substr(`var'21,4,2) if tests_`var'2!=0
		replace `var'_beg_d=substr(`var'1,1,2) if tests_`var'1==0
		replace `var'_beg_m=substr(`var'1,4,2) if tests_`var'1==0
		drop `var'22 `var'21
		}
		
		if testund1_`var'1_tot>0 {                                                      // if splitted VARIABLE1 contains "und", then                                                   
			split `var'1,p(und) 
			replace `var'11=ustrtrim(`var'11)   
			replace `var'12=ustrtrim(`var'12)                                                                                                   
			replace `var'_ft_d=substr(`var'11,1,2) if testund1_`var'1!=0
			replace `var'_ft_m=substr(`var'11,4,2) if testund1_`var'1!=0
			replace `var'_beg_d=substr(`var'12,1,2) if testund1_`var'1!=0
			replace `var'_beg_m=substr(`var'12,4,2) if testund1_`var'1!=0
			replace `var'_end_d=substr(`var'2,1,2) if testund2_`var'2==0
			replace `var'_end_m=substr(`var'2,4,2) if testund2_`var'2==0
			drop `var'11 `var'12 
		}
		if testund2_`var'2_tot>0 {                                                       // if splitted VARIABLE2 contains "und", then                                                 
			split `var'2, p(und)  
			replace `var'21=ustrtrim(`var'21)   
			replace `var'22=ustrtrim(`var'22)                                                                                                  
			replace `var'_ft_d=substr(`var'22,1,2) if testund2_`var'2!=0
			replace `var'_ft_m=substr(`var'22,4,2) if testund2_`var'2!=0
			replace `var'_end_d=substr(`var'21,1,2) if testund2_`var'2!=0
			replace `var'_end_m=substr(`var'21,4,2) if testund2_`var'2!=0
			replace `var'_beg_d=substr(`var'1,1,2) if testund1_`var'1==0
			replace `var'_beg_m=substr(`var'1,4,2) if testund1_`var'1==0
			drop `var'22 `var'21
		}
		
		if testu1_`var'1_tot>0 {                                                         // if splitted VARIABLE1 contains "u.",then                                               
			split `var'1,p(u.)
			replace `var'11=ustrtrim(`var'11)   
			replace `var'12=ustrtrim(`var'12)                                                                                                   
			replace `var'_ft_d=substr(`var'11,1,2) if testu1_`var'1!=0
			replace `var'_ft_m=substr(`var'11,4,2) if testu1_`var'1!=0
			replace `var'_beg_d=substr(`var'12,1,2) if testu1_`var'1!=0
			replace `var'_beg_m=substr(`var'12,4,2) if testu1_`var'1!=0
			replace `var'_end_d=substr(`var'2,1,2) if testu2_`var'2==0
			replace `var'_end_m=substr(`var'2,4,2) if testu2_`var'2==0
			drop `var'11 `var'12 
		}
		if testu2_`var'2_tot>0 {                                                         // if splitted VARIABLE2 contain "u.", then                                               
			split `var'2, p(u.)  
			replace `var'21=ustrtrim(`var'21)   
			replace `var'22=ustrtrim(`var'22)                                                                                               
			replace `var'_ft_d=substr(`var'22,1,2) if testu2_`var'2!=0
			replace `var'_ft_m=substr(`var'22,4,2) if testu2_`var'2!=0
			replace `var'_end_d=substr(`var'21,1,2) if testu2_`var'2!=0
			replace `var'_end_m=substr(`var'21,4,2) if testu2_`var'2!=0
			replace `var'_beg_d=substr(`var'1,1,2) if testu1_`var'1==0
			replace `var'_beg_m=substr(`var'1,4,2) if testu1_`var'1==0
			drop `var'22 `var'21
		}                                                                                                                                                         
		drop `var'1 `var'2 `var'1_length
		destring `var'_beg_d, replace force
		destring `var'_beg_m, replace force 
		destring `var'_end_d,replace force 
		destring `var'_end_m, replace force 
	}
	
	*DATE FORMATTING:
	*Weinachten: 
	gen  mdy_Weinachten_beg=mdy(Weinachten_beg_m,Weinachten_beg_d,year1) 
	format mdy_Weinachten_beg %td
	gen mdy_Weinachten_end=mdy(Weinachten_end_m,Weinachten_end_d,year1) if Weinachten_end_m==12
	replace mdy_Weinachten_end=mdy(Weinachten_end_m,Weinachten_end_d,year2) if Weinachten_end_m<12
	format mdy_Weinachten_end %td
	
	*Files mit Sommer am Anfang: 
	if  `i'<=101 {
		foreach var of varlist Sommer Herbst {
			gen mdy_`var'_beg = mdy( `var'_beg_m, `var'_beg_d, year1) 
			format mdy_`var'_beg %td 
			gen mdy_`var'_end = mdy( `var'_end_m, `var'_end_d, year1) 
			format mdy_`var'_end %td                                        
		}
		
		foreach var of varlist Winter Ostern Himmelf_Pfingsten {
			gen mdy_`var'_beg = mdy( `var'_beg_m, `var'_beg_d, year2)
			format  mdy_`var'_beg %td
			gen mdy_`var'_end = mdy( `var'_end_m, `var'_end_d, year2) 
			format mdy_`var'_end %td 
		} 
	}
	*Files mit Sommer am Ende: 
	else if `i'>101 {
		gen  mdy_Herbst_beg=mdy(Herbst_beg_m,Herbst_beg_d,year1) 
		format mdy_Herbst_beg %td
		gen mdy_Herbst_end=mdy(Herbst_end_m,Herbst_end_d,year1) 
		format mdy_Herbst_end %td
		
		foreach var of varlist Winter Ostern Himmelf_Pfingsten Sommer {
			gen mdy_`var'_beg = mdy( `var'_beg_m, `var'_beg_d, year2)
			format  mdy_`var'_beg %td
			gen mdy_`var'_end = mdy( `var'_end_m, `var'_end_d, year2) 
			format mdy_`var'_end %td 
		} 
	} 
	
	
	*CASE 2: holidays separated only by "u." , therefore composed of two ft: 
	foreach var of varlist Sommer Herbst Weinachten Winter Ostern Himmelf_Pfingsten {
		if testu_`var'_tot>0 {                                                           // split only if variable contains "u."
			split `var',p(u.) 
			replace `var'1="" if `var'2==""    
			replace `var'_ft1_d=substr(`var'1,1,2) if `var'_ft1_d==""&testu1_`var'1==0&testu2_`var'2==0
			replace `var'_ft1_m=substr(`var'1,4,2) if `var'_ft1_m==""&testu1_`var'1==0&testu2_`var'2==0
			replace `var'_ft2_d=substr(`var'2,1,2) if `var'_ft2_d==""&testu1_`var'1==0&testu2_`var'2==0
			replace `var'_ft2_m=substr(`var'2,4,2) if `var'_ft2_m==""&testu1_`var'1==0&testu2_`var'2==0
			drop `var'1 `var'2
		}
	}
	
	*CASE 3: holidays separated only by "und", therefore composed of two ft: 
	foreach var of varlist Sommer Herbst Weinachten Winter Ostern Himmelf_Pfingsten {
		if testund_`var'_tot>0 {                                                         // split only if variable  contains "und" 
			split `var',p(und) 
			replace `var'1="" if `var'2==""
			replace `var'_ft1_d=substr(`var'1,1,2) if `var'_ft1_d==""&testund1_`var'1==0&testund2_`var'2==0
			replace `var'_ft1_m=substr(`var'1,4,2) if `var'_ft1_m==""&testund1_`var'1==0&testund2_`var'2==0
			replace `var'_ft2_d=substr(`var'2,1,2) if `var'_ft2_d==""&testund1_`var'1==0&testund2_`var'2==0
			replace `var'_ft2_m=substr(`var'2,4,2) if `var'_ft2_m=="" &testund1_`var'1==0&testund2_`var'2==0
			drop `var'1 `var'2
		}
	}
	
	*CASE 4: holidays separated only by "+", therefore composed of two ft: 
	foreach var of varlist Sommer Herbst Weinachten Winter Ostern Himmelf_Pfingsten {
		if testp_`var'_tot>0 {                                                           // split only if variable contains "+"
			split `var',p(+) 
			replace `var'1="" if `var'2==""
			replace `var'_ft1_d=substr(`var'1,1,2) if `var'_ft1_d==""
			replace `var'_ft1_m=substr(`var'1,4,2) if `var'_ft1_m==""
			replace `var'_ft2_d=substr(`var'2,1,2) if `var'_ft2_d=="" 
			replace `var'_ft2_m=substr(`var'2,4,2) if `var'_ft2_m=="" 
			drop `var'1 `var'2
		}
	}
	
	*CASE 5: holidays separated only by "/", therefore composed of two ft: 
	foreach var of varlist Sommer Herbst Weinachten Winter Ostern Himmelf_Pfingsten {
		if  tests_`var'_tot>0 {                                                    
			split `var',p(/) 
			replace `var'1="" if `var'2==""
			replace `var'_ft1_d=substr(`var'1,1,2) if `var'_ft1_d=="" &tests_`var'1==0&tests_`var'2==0 
			replace `var'_ft1_m=substr(`var'1,4,2) if `var'_ft1_m=="" &tests_`var'1==0&tests_`var'2==0
			replace `var'_ft2_d=substr(`var'2,1,2) if `var'_ft2_d=="" &tests_`var'1==0&tests_`var'2==0
			replace `var'_ft2_m=substr(`var'2,4,2) if `var'_ft2_m=="" &tests_`var'1==0&tests_`var'2==0
			if tests_`var'_tot!=testsl_`var'_tot {
				replace `var'_ft3_d=substr(`var'3,1,2) if `var'_ft3_d=="" &tests_`var'1==0&tests_`var'2==0
				replace `var'_ft3_m=substr(`var'3,4,2) if `var'_ft3_m=="" &tests_`var'1==0&tests_`var'2==0
				drop `var'1 `var'2 
			}
		}
		*FORMATTING OF FT: 
		destring `var'_ft1_d, replace force
		destring `var'_ft1_m, replace force 
		destring `var'_ft2_d,replace force 
		destring `var'_ft2_m, replace force 
		destring `var'_ft3_d,replace force 
		destring `var'_ft3_m, replace force 
	}
	*Weinachten: 
	gen mdy_Weinachten_ft1 = mdy( Weinachten_ft1_m, Weinachten_ft1_d, year1)   if   Weinachten_ft1_m==12
	replace  mdy_Weinachten_ft1 = mdy( Weinachten_ft1_m, Weinachten_ft1_d, year2) if   Weinachten_ft1_m<=12
	format mdy_Weinachten_ft1 %td
	gen mdy_Weinachten_ft2 = mdy( Weinachten_ft2_m, Weinachten_ft2_d, year1) if   Weinachten_ft2_m==12
	replace  mdy_Weinachten_ft2 = mdy( Weinachten_ft2_m, Weinachten_ft2_d, year2) if   Weinachten_ft2_m<12
	format mdy_Weinachten_ft2 %td 
	gen mdy_Weinachten_ft3=mdy(Weinachten_ft3_m, Weinachten_ft3_d, year1) if   Weinachten_ft3_m==12
	replace mdy_Weinachten_ft3=mdy(Weinachten_ft3_m, Weinachten_ft3_d, year2) if   Weinachten_ft3_m<12
	format mdy_Weinachten_ft3 %td 
	
	*Files mit Sommer am Anfang: 
	if  `i'<=101 {
		foreach var of varlist Sommer Herbst {
			gen mdy_`var'_ft1 = mdy( `var'_ft1_m, `var'_ft1_d, year1)     
			format mdy_`var'_ft1 %td
			gen mdy_`var'_ft2 = mdy( `var'_ft2_m, `var'_ft2_d, year1) 
			format mdy_`var'_ft2 %td 
			gen mdy_`var'_ft3=mdy(`var'_ft3_m, `var'_ft3_d, year1) 
			format mdy_`var'_ft3 %td 
		}
		
		foreach var of varlist Winter Ostern Himmelf_Pfingsten {
			gen mdy_`var'_ft1 = mdy( `var'_ft1_m, `var'_ft1_d, year2)     
			format mdy_`var'_ft1 %td
			gen mdy_`var'_ft2 = mdy( `var'_ft2_m, `var'_ft2_d, year2) 
			format mdy_`var'_ft2 %td 
			gen mdy_`var'_ft3=mdy(`var'_ft3_m, `var'_ft3_d, year2) 
			format mdy_`var'_ft3 %td 
		}
	}
	
	*Files mit Sommer am Ende: 
	else if `i'>101 {
		gen mdy_Herbst_ft1=mdy( Herbst_ft1_m, Herbst_ft1_d, year1)
		format mdy_Herbst_ft1 %td
		gen mdy_Herbst_ft2=mdy(Herbst_ft2_m,Herbst_ft2_d,year1)
		format mdy_Herbst_ft2 %td
		gen mdy_Herbst_ft3=mdy(Herbst_ft3_m,Herbst_ft3_d,year1)
		format mdy_Herbst_ft3 %td
		
		foreach var of varlist Winter Ostern Himmelf_Pfingsten Sommer {
			gen mdy_`var'_ft1 = mdy( `var'_ft1_m, `var'_ft1_d, year2)     
			format mdy_`var'_ft1 %td
			gen mdy_`var'_ft2 = mdy( `var'_ft2_m, `var'_ft2_d, year2) 
			format mdy_`var'_ft2 %td 
			gen mdy_`var'_ft3=mdy(`var'_ft3_m, `var'_ft3_d, year2) 
			format mdy_`var'_ft3 %td 
		}
	}
	
	*CASE 6: SINGLE day holidays(one day holiday): 
	foreach var of varlist Sommer Herbst Weinachten Winter Ostern Himmelf_Pfingsten {
		gen `var'_length= strlen(`var') 
		replace `var' = substr(`var', 1, strpos(`var', ")") - 2) if `var'_length==8
		drop `var'_length
		gen `var'_length= strlen(`var')
		replace `var'_ft_d=substr(`var',1,2) if `var'_length==6
		replace `var'_ft_m=substr(`var',4,2) if `var'_length==6 
		destring `var'_ft_d, replace force
		destring `var'_ft_m, replace force
	}
	
	gen mdy_Weinachten_ft = mdy( Weinachten_ft_m, Weinachten_ft_d, year1)   if   Weinachten_ft_m==12
	replace  mdy_Weinachten_ft = mdy( Weinachten_ft_m, Weinachten_ft_d, year2) if   Weinachten_ft_m<=12
	format mdy_Weinachten_ft %td
	
	if  `i'<=101 {
		foreach var of varlist Sommer Herbst {
			gen mdy_`var'_ft = mdy( `var'_ft_m, `var'_ft_d, year1)     
			format mdy_`var'_ft %td
		}
		
		foreach var of varlist Winter Ostern Himmelf_Pfingsten {
			gen mdy_`var'_ft = mdy( `var'_ft_m, `var'_ft_d, year2)     
			format mdy_`var'_ft %td
		}
	}
	else if `i'>101 {
		gen mdy_Herbst_ft = mdy( Herbst_ft_m, Herbst_ft_d, year1)     
		format mdy_Herbst_ft %td
		
		foreach var of varlist Winter Ostern Himmelf_Pfingsten Sommer {
			gen mdy_`var'_ft = mdy( `var'_ft_m, `var'_ft_d, year2)     
			format mdy_`var'_ft %td
		}
	}
	
	drop test*
	
	*********************Prepare Dataset for merge**********************************
	*Generate BULA ID variable: 
	gen bula=. 
	replace bula=1 if Bundesland=="Schleswig-Holstein"
	replace bula=2 if Bundesland=="Hamburg"
	replace bula=3 if Bundesland=="Niedersachsen"
	replace bula=4 if Bundesland=="Bremen"
	replace bula=5 if Bundesland=="Nordrhein-Westfalen"
	replace bula=6 if Bundesland=="Hessen"
	replace bula=7 if Bundesland=="Rheinland-Pfalz"
	replace bula=8 if Bundesland=="Baden-Württemberg"
	replace bula=9 if Bundesland=="Bayern"
	replace bula=10 if Bundesland=="Saarland"
	replace bula=11 if Bundesland=="Berlin"
	replace bula=12 if Bundesland=="Brandenburg"
	replace bula=13 if Bundesland=="Mecklenburg-Vorpommern"
	replace bula=14 if Bundesland=="Sachsen"
	replace bula=15 if Bundesland=="Sachsen-Anhalt"
	replace bula=16 if Bundesland=="Thüringen"
	
	*Rename variables in order to reshape dataset:
	foreach var of varlist Sommer Herbst Weinachten Winter Ostern Himmelf_Pfingsten {
		rename mdy_`var'_beg mdy_beg_`var'
		rename mdy_`var'_end mdy_end_`var'
		rename mdy_`var'_ft mdy_ft_`var'
		rename mdy_`var'_ft1 mdy_ft1_`var'
		rename mdy_`var'_ft2 mdy_ft2_`var'
		rename mdy_`var'_ft3 mdy_ft3_`var'
		rename mdy_ft3_`var' mdy_ft4_`var'
		rename mdy_ft2_`var' mdy_ft3_`var'
		rename mdy_ft1_`var' mdy_ft2_`var'
		rename mdy_ft_`var' mdy_ft1_`var'
		
		replace mdy_ft1_`var'=. if mdy_ft1_`var'==mdy_ft2_`var' &mdy_ft1_`var'!=.&mdy_ft2_`var'!=.
		replace mdy_ft1_`var'=mdy_ft2_`var' if mdy_ft1_`var'==.&mdy_ft2_`var'!=.
		replace mdy_ft2_`var'=mdy_ft3_`var' if mdy_ft3_`var'!=.
		replace mdy_ft2_`var'=. if mdy_ft3_`var'==.
		replace mdy_ft3_`var'=mdy_ft4_`var' if mdy_ft4_`var'!=.
		replace mdy_ft3_`var'=. if mdy_ft4_`var'==.
		replace mdy_ft4_`var'=. if mdy_ft3_`var'==mdy_ft4_`var'
	}
	save "${data}temp\Schulferien_`i'_`j'.dta",replace
	clear
}


********************************************************************************
*************************CREATION OF FINAL DATASET******************************
********************************************************************************

************************SEPARATE DATASETS FOR MERGE*****************************

******************DATASET 1: only Beg-End holidays, no single Ferientage******** 
forvalues i=94/119 {
	local j = `i' + 1
	use "${data}temp\Schulferien_`i'_`j'.dta",clear 
	preserve 
	keep bula bew_Ferien
	save "${data}temp\Schulferien_bew_`i'_`j'.dta",replace
	restore
	keep bula Sommer Herbst Winter Weinachten Himmelf_Pfingsten Ostern  mdy_beg_Sommer mdy_beg_Herbst mdy_beg_Winter mdy_beg_Weinachten mdy_beg_Ostern mdy_beg_Himmelf_Pfingsten mdy_end_Sommer mdy_end_Herbst mdy_end_Winter mdy_end_Weinachten mdy_end_Ostern mdy_end_Himmelf_Pfingsten
	
	*Append all holidays for the same Bundesland:
	reshape long mdy_beg mdy_end,i(bula) j(Ferien) string
	
	*Compute holiday duration: 
	gen ferien_dauer=mdy_end-mdy_beg
	keep bula Ferien mdy_beg mdy_end ferien_dauer 
	
	merge m:1 bula using "${data}temp\Schulferien_bew_`i'_`j'.dta"
	drop _merge
	save "${data}temp\Schulferien_begend_`i'_`j'.dta",replace 
	clear 
}
*Append all datasets 1:
use "${data}temp\Schulferien_begend_94_95.dta",clear 
forvalues i=95/119 {
	local j = `i' + 1
	append using "${data}temp\Schulferien_begend_`i'_`j'.dta", force  
}
*Generate variable identical to mdy_beg for merge: 
gen mdy=mdy_beg  
save "${data}temp\Schulferien_begend.dta",replace
clear


**********************DATASET 2: only single Ferientage*************************
*Adjust for Unterrichtsfreie Tagen that were written in the notes: 

*Rosenmontag und Faschingsdienstag im Saarland und Reformationstag und Gruendonnerstag in Baden-Württemberg: 
input bula str20 Ferien mdy 
	10 "Rosenmontag" 12841
	10 "Faschingsdienstag" 12842
	10 "Rosenmontag" 13198
	10 "Faschingsdienstag" 13199
	10 "Rosenmontag" 13555
	10 "Faschingsdienstag" 13556
	10 "Rosenmontag" 13933
	10 "Faschingsdienstag" 13934
	10 "Rosenmontag" 14290
	10 "Faschingsdienstag" 14291
	10 "Rosenmontag" 14675
	10 "Faschingsdienstag" 14676
	10 "Rosenmontag" 15032
	10 "Faschingsdienstag" 15033
	10 "Rosenmontag" 15382
	10 "Faschingsdienstag" 15383
	8 "Reformationstag" 17836
	8 "Reformationstag" 18201
	8 "Reformationstag" 18566
	8 "Reformationstag" 18931
	8 "Gruendonnerstag" 17996
	8 "Gruendonnerstag" 18353
	8 "Gruendonnerstag" 18738
end

save "${data}temp\Schulferien_notes.dta", replace

forvalues i=94/119 {
	local j = `i' + 1
	use "${data}temp\Schulferien_`i'_`j'.dta",clear 
	keep bula  Sommer Herbst Winter Weinachten Ostern Himmelf_Pfingsten mdy_ft1_Sommer mdy_ft2_Sommer mdy_ft3_Sommer mdy_ft4_Sommer mdy_ft1_Herbst mdy_ft2_Herbst mdy_ft3_Herbst mdy_ft4_Herbst mdy_ft1_Winter mdy_ft2_Winter mdy_ft3_Winter mdy_ft4_Winter mdy_ft1_Weinachten mdy_ft2_Weinachten mdy_ft3_Weinachten mdy_ft4_Weinachten mdy_ft1_Ostern mdy_ft2_Ostern mdy_ft3_Ostern mdy_ft4_Ostern mdy_ft1_Himmelf_Pfingsten mdy_ft2_Himmelf_Pfingsten mdy_ft3_Himmelf_Pfingsten mdy_ft4_Himmelf_Pfingsten
	
	*Append all ferientage for the same Bundesland 
	reshape long mdy, i(bula) j(Ferien) string  
	replace Ferien=substr(Ferien,6,strlen(Ferien))
	keep bula Ferien mdy 
	merge m:1 bula using "${data}temp\Schulferien_bew_`i'_`j'.dta"
	drop _merge
	save "${data}temp\Schulferien_ft_`i'_`j'.dta",replace 
	clear
}

*Append all datasets 2: 
use "${data}temp\Schulferien_ft_94_95.dta",clear
forvalues i=95/119 {
	local j = `i' + 1
	append using "${data}temp\Schulferien_ft_`i'_`j'.dta" 
}

append using "${data}temp\Schulferien_notes.dta"
sort bula mdy 
gen year=year(mdy) 
replace bew_Ferien=bew_Ferien[_n-1] if bew_Ferien==. & bew_Ferien[_n-1]!=. & bula==bula[_n-1] & year==year[_n-1] & mdy!=.
replace bew_Ferien=bew_Ferien[_n-2] if bew_Ferien==. & bew_Ferien[_n-2]!=. & bula==bula[_n-2] & year==year[_n-2] & mdy!=.
drop year

*Generate variable identical to mdy for merge: 
gen mdy_ft=mdy 
save "${data}temp\Schulferien_ft.dta",replace
clear

/*
**********************DATASET 3: only bew_Ferien********************************
forvalues i=94/116 {
local j = `i' + 1
use "temp\Schulferien_`i'_`j'.dta",clear 
keep bula bew_Ferien year1 year2

save "temp\Schulferien_bew_`i'_`j'.dta",replace 
clear
}

*Append all datasets 3: 
use "temp\Schulferien_ft_94_95.dta",clear
forvalues i=95/116 {
local j = `i' + 1
append using "temp\Schulferien_bew_`i'_`j'.dta" 
}
stop
*/
***************Creation of new dataset with daily time variable**************

*Generate daily date variable from 1. January 1994 to 31. December 2016: 
di mdy(1,1,1994)
di mdy(12,31,2017)
di mdy(12,31,2020) - mdy(1,1,1994)
set obs 9862
gen mdy = mdy(12,31,1993) + _n
format mdy %td

*Exapand the sequence 16 times for the 16 Bundesländer:
expand 16
sort mdy

*Generate Bundesländer id number sequence: 
egen bula=fill(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16) 

save "${data}temp\Schulferien_final.dta",replace

*Merge with DATASET 1 (Urlaubstage "long holidays"): 
*NB: 1:m merge as because of the missings, bula mdy is not identifying in the using file

merge 1:m bula mdy using "${data}temp\Schulferien_begend.dta"
drop if _merge==2 // NB: _megre==2 only when missing or 2017 
drop _merge 

merge 1:m bula mdy using "${data}temp\Schulferien_ft.dta"
drop if _merge==2 // NB: _megre==2 only when missing or 2017 
drop _merge

format mdy_ft %td

*Fill ferien_dauer with -1 series so to vertically identify holiday days after the first: 
bysort bula: replace ferien_dauer=ferien_dauer[_n-1]-1 if ferien_dauer[_n-1]>0&ferien_dauer[_n]==.
gen ferientag=0
replace ferientag=1 if mdy==mdy_ft
replace ferientag=1 if ferien_dauer!=.

replace Ferien=substr(Ferien,2,strlen(Ferien))
keep mdy bula Ferien ferientag bew_Ferien
save "${data}temp\Schulferien_final.dta",replace 


***************ADD FEIERTAGE COMING FROM WEBSITE SCHULFERIEN.DE****************
clear 


*Generate first file with only Feiertage in ALL Bundesländer
import excel "${data}Excel_Tabellen\Feiertagen.xlsx", firstrow 

*Drop all observations where Feiertag is not a Feiertag  IN ALL Bundesländer: 
replace Bula1= subinstr(Bula1," ","",.)                                          // eliminate all blank spaces 
drop if Bula1!="alle"
drop Bula1 Bula2 Bula3 Bula4 Bula5 Bula6

*Expand dataset 16 times so that each Bula has all the Feiertage: 
expand 16

*Generate Bundesländer id number sequence:
sort Feiertage mdy
egen bula=fill(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16)
 
*Eliminate blank space at the end of "Zweiter Weinachtsfeiertag": 
replace Feiertage=strrtrim(Feiertage)

*Date formatting:
replace mdy= usubinstr(mdy," ","",.)
gen mdy_length= strlen(mdy)  
gen type=substr(mdy,-5,1) 

gen day=substr(mdy,1,1) if mdy_length==9 & type!="/"
replace day=substr(mdy,1,2) if mdy_length==10 & type!="/"
gen month=substr(mdy,3,2) if mdy_length==9 & type!="/"
replace month=substr(mdy,4,2) if mdy_length==10 & type!="/"
gen year=substr(mdy,6,4) if mdy_length==9 & type!="/"
replace year=substr(mdy,7,4) if mdy_length==10 & type!="/"

gen type2=substr(mdy,-8,1) 

replace month=substr(mdy,1,1) if month=="" & mdy_length==8 & type=="/"
replace month=substr(mdy,1,1) if month=="" & mdy_length==9 & type=="/" & type2=="/"
replace month=substr(mdy,1,2) if month=="" & mdy_length==9 & type=="/" & type2!="/"
replace month=substr(mdy,1,2) if month=="" & mdy_length==10 & type=="/" & type2=="/"
replace day=substr(mdy,3,1) if day=="" & mdy_length==8 & type=="/" 
replace day=substr(mdy,3,2) if day=="" & mdy_length==9 & type=="/" & type2=="/"
replace day=substr(mdy,4,1) if day=="" & mdy_length==9 & type=="/" & type2!="/"
replace day=substr(mdy,4,2) if day=="" & mdy_length==10 & type=="/" & type2=="/"
replace year=substr(mdy,-4,4) if type=="/"

drop type type2

destring day, replace force 
destring month, replace force
destring year, replace force 

gen mdy_neu=mdy(month,day,year)
format mdy_neu %td 
gen mdy_feiertag=mdy_neu
format mdy_feiertag %td
drop mdy
rename mdy_neu mdy 
drop day month year mdy_length

save "${data}temp\Feiertage_alle.dta",replace 
clear
 
*Generate second file with only Feiertage in SOME Bundesländer:
import excel "${data}Excel_Tabellen\Feiertagen.xlsx", firstrow 

*Drop all observations where Feiertagis Feiertag for all Bundesländer: 
replace Bula1= subinstr(Bula1," ","",.)                                          // eliminate all blank spaces 
drop if Bula1=="alle" 
destring Bula1, replace force 

*Reshape from wide to long: 
reshape long Bula, i(Feiertag mdy) j(bula) 
drop bula 
rename Bula bula 
drop if bula==. 

*Eliminate blank space at the end of "Zweiter Weinachtsfeiertag": 
replace Feiertage=strrtrim(Feiertage)

*Date formatting:
replace mdy= usubinstr(mdy," ","",.) 
gen mdy_length= strlen(mdy)  

gen type=substr(mdy,-5,1) 

gen day=substr(mdy,1,1) if mdy_length==9 & type!="/"
replace day=substr(mdy,1,2) if mdy_length==10 & type!="/"
gen month=substr(mdy,3,2) if mdy_length==9 & type!="/"
replace month=substr(mdy,4,2) if mdy_length==10 & type!="/"
gen year=substr(mdy,6,4) if mdy_length==9 & type!="/"
replace year=substr(mdy,7,4) if mdy_length==10 & type!="/"

gen type2=substr(mdy,-8,1) 

replace month=substr(mdy,1,1) if month=="" & mdy_length==8 & type=="/"
replace month=substr(mdy,1,1) if month=="" & mdy_length==9 & type=="/" & type2=="/"
replace month=substr(mdy,1,2) if month=="" & mdy_length==9 & type=="/" & type2!="/"
replace month=substr(mdy,1,2) if month=="" & mdy_length==10 & type=="/" & type2=="/"
replace day=substr(mdy,3,1) if day=="" & mdy_length==8 & type=="/" 
replace day=substr(mdy,3,2) if day=="" & mdy_length==9 & type=="/" & type2=="/"
replace day=substr(mdy,4,1) if day=="" & mdy_length==9 & type=="/" & type2!="/"
replace day=substr(mdy,4,2) if day=="" & mdy_length==10 & type=="/" & type2=="/"
replace year=substr(mdy,-4,4) if type=="/"

destring day, replace force 
destring month, replace force
destring year, replace force 

gen mdy_neu=mdy(month,day,year)
format mdy_neu %td 
gen mdy_feiertag=mdy_neu
format mdy_feiertag %td
drop mdy
rename mdy_neu mdy 
drop day month year mdy_length



save "${data}temp\Feiertage_einzeln.dta",replace 

clear 

************************Merge with Final Dataset********************************
use "${data}temp\Schulferien_final.dta"

*Merge mit Ferientagen die in alle Bundesländer als Ferientage gelten: 
merge 1:m bula mdy using "${data}temp\Feiertage_alle.dta"                        // NB: here one to many as in 2008 Christi Himmelfahrt was on the same day as Tag der Arbeit.
drop _merge 																	// Therefore in 2008 there are duplicates in terms of bula mdy. 

*Merge mit Ferientagen die in nur in einzelne Bundesländer als Ferientage gelten: 
merge m:m bula mdy using "${data}temp\Feiertage_einzeln.dta", update replace      //NB: many to many merge for the same reason mentioned above.
drop _merge 	

*Generate Feiertag Variable: 
gen feiertag=0
replace feiertag=1 if mdy_feiertag!=.

drop mdy_feiertag 

rename ferientag sch_hday
rename feiertag pub_hday
rename Feiertage feiertag
rename Ferien ferien


label var mdy "Datum (Monat, Tag, Jahr)"
label var ferien "Art der Schulferien" 
label var sch_hday "Indikator für Ferientag (school holiday)" 
label var bula "Bundesland" 
label var feiertag "Name des Feiertags" 
label var pub_hday "Indikator für Feiertag (public holiday)" 
label var bew_Ferien "bewegliche Ferientage"

replace ferien="Weihnachten" if ferien=="Weinachten" 
replace feiertag="Erster Weihnachtsfeiertag" if feiertag=="Erster Weinachtsfeiertag" 
replace feiertag="Zweiter Weihnachtsfeiertag" if feiertag=="Zweiter Weinachtsfeiertag" 
replace feiertag="Heilige Drei Koenige" if feiertag=="Heilige Drei Könige" 

sort bula mdy 

replace ferien=ferien[_n-1] if ferien=="" & sch_hday==1 & sch_hday[_n-1]==1
replace bew_Ferien=bew_Ferien[_n-1] if bew_Ferien==. & sch_hday==1 
replace bew_Ferien=bew_Ferien[_n-1] if bew_Ferien==. & ferien[_n-1]!="Sommer" 
gsort bula -mdy 
replace bew_Ferien=bew_Ferien[_n-1] if bew_Ferien==. 
sort bula mdy

*Adjust for Unterrichtsfreie Tagen that were written in the notes: 

*1.Rosenmontag und Faschingsdienstag im Saarland: 
*Display all the Rosenmontage: 
di mdy(02,27,1995) // 12841 
di mdy(02,19,1996) // 13198
di mdy(02,10,1997) // 13555
di mdy(02,23,1998) // 13933
di mdy(02,15,1999) // 14290
di mdy(03,06,2000) // 14675
di mdy(02,26,2001) // 15032
di mdy(02,11,2002) // 15382
di mdy(03,03,2003) // 15767
di mdy(02,23,2004) // 16124

*1995
replace sch_hday=1 if mdy==12841&bula==10
replace ferien="Rosenmontag" if mdy==12841&bula==10
replace sch_hday=1 if mdy==12842&bula==10
replace ferien="Faschingsdienstag" if mdy==12842&bula==10
*1996
replace sch_hday=1 if mdy==13198&bula==10
replace ferien="Rosenmontag" if mdy==13198&bula==10
replace sch_hday=1 if mdy==13199&bula==10
replace ferien="Faschingsdienstag" if mdy==13199&bula==10
*1997
replace sch_hday=1 if mdy==13555&bula==10
replace ferien="Rosenmontag" if mdy==13555&bula==10
replace sch_hday=1 if mdy==13556&bula==10
replace ferien="Faschingsdienstag" if mdy==13556&bula==10
*1998
replace sch_hday=1 if mdy==13933&bula==10
replace ferien="Rosenmontag" if mdy==13933&bula==10
replace sch_hday=1 if mdy==13934&bula==10
replace ferien="Faschingsdienstag" if mdy==13934&bula==10
*1999
replace sch_hday=1 if mdy==14290&bula==10
replace ferien="Rosenmontag" if mdy==14290&bula==10
replace sch_hday=1 if mdy==14291&bula==10
replace ferien="Faschingsdienstag" if mdy==14291&bula==10
*2000
replace sch_hday=1 if mdy==14675&bula==10
replace ferien="Rosenmontag" if mdy==14675&bula==1
replace sch_hday=1 if mdy==14676&bula==10
replace ferien="Faschingsdienstag" if mdy==14676&bula==10
*2001
replace sch_hday=1 if mdy==15032&bula==10
replace ferien="Rosenmontag" if mdy==15032&bula==10
replace sch_hday=1 if mdy==15033&bula==10
replace ferien="Faschingsdienstag" if mdy==15033&bula==10
*2002
replace sch_hday=1 if mdy==15382&bula==10
replace ferien="Rosenmontag" if mdy==15382&bula==10
replace sch_hday=1 if mdy==15383&bula==10
replace ferien="Faschingsdienstag" if mdy==15383&bula==10
*2003
replace sch_hday=1 if mdy==15767&bula==10
replace ferien="Rosenmontag" if mdy==15767&bula==10
replace sch_hday=1 if mdy==15768&bula==10
replace ferien="Faschingsdienstag" if mdy==15768&bula==10
*2004
replace sch_hday=1 if mdy==16124&bula==10
replace ferien="Rosenmontag" if mdy==16124&bula==10
replace sch_hday=1 if mdy==16125&bula==10
replace ferien="Faschingsdienstag" if mdy==16125&bula==10

*2.Reformationstag und Gründonnerstag im Baden-Wüttenberg: 
gen year=year(mdy) 
gen month=month(mdy)
gen day=day(mdy)

*Reformationstag: 
replace sch_hday=1 if bula==8&day==31&month==10&year>=2008&year<=2011
replace ferien="Reformationstag" if bula==8&day==31&month==10&year>=2008&year<=2011

drop year day month 

*Gründonnerstag:
di mdy(04,09,2009) //17996
di mdy(04,01,2010) //18353
di mdy(04,21,2011) //18738

*2009
replace sch_hday=1 if bula==8&mdy==17996
replace ferien="Gruendonnerstag" if bula==8&mdy==17996&ferien!="Ostern"
*2010
replace sch_hday=1 if bula==8&mdy==18353
replace ferien="Gruendonnerstag" if bula==8&mdy==18353&ferien!="Ostern"
*2011
replace sch_hday=1 if bula==8&mdy==18738
replace ferien="Gruendonnerstag" if bula==8&mdy==18738&ferien!="Ostern"

save  "${data}temp\Schulferien_final.dta",replace 

preserve 

	drop if mdy<mdy(01,01,2010) | mdy>mdy(12,31,2015) 
	
	format mdy %td 
	
	drop bew_Ferien type*
	
	
	
	* generate fasching dummy
		xtset bula mdy
		qui gen ft10 = 1 if feiertag == "Ostermontag"
		qui gen fasching = 0 
		qui replace fasching = 1 if F47.ft10==1 |  F48.ft10==1 |  F49.ft10==1 |  F50.ft10==1 |  F51.ft10==1 |  F52.ft10==1 |  F53.ft10==1
		drop ft10
	
	
	save  "${outputdata}\Schulferien_1015.dta",replace 

restore




preserve
	drop if mdy<mdy(01,01,2020) | mdy>mdy(30,04,2020) 
	
	format mdy %td 
	
	drop bew_Ferien type*
	
	
	
	* generate fasching dummy
		xtset bula mdy
		qui gen ft10 = 1 if feiertag == "Ostermontag"
		qui gen fasching = 0 
		qui replace fasching = 1 if F47.ft10==1 |  F48.ft10==1 |  F49.ft10==1 |  F50.ft10==1 |  F51.ft10==1 |  F52.ft10==1 |  F53.ft10==1
		drop ft10
		rename mdy refdatum
	
	
	save  "${outputdata}\Schulferien_2020_Jan_Apr.dta",replace 
restore






// export 2019 for the greta_cons project
preserve
	qui gen year = year(mdy)
	keep if year == 2019
	drop year
	
	*corrections school_holiday dummy
	replace sch_hday = 1 if bula == 2  & mdy == td(01nov2019)
	replace sch_hday = 1 if bula == 8  & mdy == td(31oct2019)
	replace sch_hday = 1 if bula == 13 & mdy == td(01nov2019)
	replace sch_hday = 1 if bula == 15 & mdy == td(01nov2019)
	
	* correction of pub_hday
	replace pub_hday = 1 if bula == 1  & mdy == td(31oct2019)
	replace pub_hday = 1 if bula == 3  & mdy == td(31oct2019)
	replace pub_hday = 1 if bula == 4  & mdy == td(31oct2019)
	
	
	format mdy %td 
	drop bew_Ferien type*
	
	
	* generate fasching dummy
		xtset bula mdy
		qui gen ft10 = 1 if feiertag == "Ostermontag"
		qui gen fasching = 0 
		qui replace fasching = 1 if F47.ft10==1 |  F48.ft10==1 |  F49.ft10==1 |  F50.ft10==1 |  F51.ft10==1 |  F52.ft10==1 |  F53.ft10==1
		drop ft10
		rename mdy date
	
	
	save  "${outputdata}\Schulferien_2019.dta",replace 
restore




*drop if mdy<mdy(01,01,1995) | mdy>mdy(12,31,2014) 

*format mdy %td 

*replace ferien="Weihnachten" if sch_hday==1 & mdy==mdy(01,01,1995) 

*save  "${data}temp\Schulferien_export.dta",replace 
*save  "${outputdata}\Schulferien_export.dta",replace
 

*end 

/*

********** Creation of csv data to put in hospital data do-file *************

use "temp\Schulferien_begend.dta", clear

append using "temp\Schulferien_ft.dta"
rename mdy beg
gen end = mdy_end
keep bula beg end bew_Ferien 
drop if beg==. 

export delimited using "csv_files\Schulferien.csv", replace

drop if (end<mdy(01,01,1995) | beg>mdy(12,31,2014))

format beg %td
format end %td 

save  "temp\Schulferien_compressed.dta",replace 

*Generate first file with only Feiertage in ALL Bundesländer
import excel "Excel_Tabellen\Feiertagen.xlsx", firstrow clear

*Drop all observations where Feiertag is not a Feiertag  IN ALL Bundesländer: 
replace Bula1= subinstr(Bula1," ","",.)                                          // eliminate all blank spaces 
replace Bula1="99" if Bula1=="alle" 
destring Bula1, replace 

*Date formatting:
replace mdy= usubinstr(mdy," ","",.) 
gen mdy_length= strlen(mdy)  
gen day=substr(mdy,1,1) if mdy_length==9
replace day=substr(mdy,1,2) if mdy_length==10
gen month=substr(mdy,3,2) if mdy_length==9
replace month=substr(mdy,4,2) if mdy_length==10
gen year=substr(mdy,6,4) if mdy_length==9
replace year=substr(mdy,7,4) if mdy_length==10
 
destring day, replace force 
destring month, replace force
destring year, replace force 

gen mdy_neu=mdy(month,day,year)
format mdy_neu %td 
gen mdy_feiertag=mdy_neu
format mdy_feiertag %td
drop mdy mdy_neu
*rename mdy_neu mdy 
drop day month year mdy_length
*gen feiertag=mdy_feiertag 
*keep feiertag Bula1 Bula2 Bula3 Bula4 Bula5 Bula6

export delimited using "csv_files\Feiertage.csv", replace

preserve

drop if (mdy_feiertag<mdy(01,01,2013) | mdy_feiertag>mdy(12,31,2017))


drop if (mdy_feiertag<mdy(01,01,1995) | mdy_feiertag>mdy(12,31,2014))

save  "temp\Feiertage_compressed.dta",replace 


********************************************************************************

*/








