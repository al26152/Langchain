Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

BMC Health Services Research

https://doi.org/10.1186/s12913-024-11832-0

**RESEARCH**

**Open Access**

Improving equitable healthcare resource use: 

developing a neighbourhood district nurse 

needs index for staffing allocation

Luís Filipe1\*, Roberta Piroddi2, Wes Baker3, Joe Rafferty3, Iain Buchan2 and Ben Barr2

**Abstract**

**Background** Allocating healthcare resources to local areas in proportion to need is an important element of many universal health care systems, aiming to provide equal access for equal need. The UK National Health Service allocates resources to relatively large areas in proportion to need, using needs-weighted capitation formulae. However, within those planning areas, local providers and commissioners also require robust methods for allocating resources to neighbourhoods in proportion to need to ensure equitable access. We therefore developed a local resource allocation formula for NHS district nursing services for a City in the North West of England, demonstrating a novel application of the national formulae principles for equitable resource allocation to small areas. 

**Methods** Using linked data from community health services, primary care, secondary care and social care, we used a zero-inflated Poisson regression to model the number of district nursing services contacts for each individual based on predictors of need, while including the supply of district nurses per head to account for historical supply induced patterns. Individual need was estimated based on the predictions from this model, keeping supply fixed at the average. We then compared the distribution of district nurses between neighbourhoods, based on our formula, to the current service staffing distribution. 

**Results** Key predictors of need for district nursing services were age, deprivation, chronic diseases such as, cardiovascular disease, chronic liver disease, neurological disease, mental ill health, learning disability living in a nursing home, living alone, and receiving palliative care. Need for district nursing services was highly weighted towards older and more deprived populations. The current distribution of staff was, however, more correlated with age than deprivation. Moving to a needs-based staffing distribution would shift staff from less deprived areas to more deprived areas potentially reducing inequalities. 

**Conclusion** A neighbourhood-level model for needs for district nursing is a useful tool that can potentially improve the allocation of resources, addressing unmet need and inequalities. 

**Keywords** Resource allocation, Community health services, District nursing, Utilization formula, Neighbourhood-level model, Unmet needs, Inequalities

\*Correspondence:

Luís Filipe

l.filipe@lancaster.ac.uk

1Department of Health Research, Lancaster University, Lancaster, UK

2Department of Public Health, Policy, and Systems, Institute of Population Health, University of Liverpool, Liverpool, UK

3Mersey Care NHS Foundation Trust, Prescot, UK

© The Author\(s\) 2024. **Open Access** This article is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 

International License, which permits any non-commercial use, sharing, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author\(s\) and the source, provide a link to the Creative Commons licence, and indicate if you modified the licensed material. You do not have permission under this licence to share adapted material derived from this article or parts of it. The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit h t t p :/ / c r e a t i

v e c o m m o n s .o r g / li c e n s e s / b y - n c - n d / 4 .0 / .  

Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

Page 2 of 10

**Introduction**

with 16 neighbourhood teams. The staffing levels of these 

District nurses provide key community services to help teams have not previously been set based on any formal people with health care needs live independently \[1\]. assessment of need. We used newly available linked data These services are commonly delivered through col-across primary, secondary care and community services 

laborations between health care and social care teams, to develop a needs-weighted capitation measure for including General Practitioners \(GPs\), other community district nursing across Liverpool and assess how staff-and mental health nurses, therapists, other health profes-

ing levels would need to change to better reflect pat-

sionals and social care workers \[1\]. These teams are usu-terns of need. Our model offers three key contributions 

ally organised around neighbourhoods or groups of GP compared to the national formula for community ser-practices. To ensure equitable access to these services vices. First, it incorporated a broader set of local needs differences in staffing levels need to match differences variables, enhancing the precision of our estimates and in need across neighbourhoods. Whilst there have been their relevance to the region under analysis. Second, some previous studies developing tools to support the we applied a Zero Inflated Poisson Model, which better management of community nursing workloads, enabling accommodates both the count-based nature of the data safe staffing levels \[2\], and a study defining allocation of and the excess of zero values for district nursing contacts. 

community services resources across NHS Integrated Third, instead of using Kent as an external benchmark Care Boards \[3\], there have been no previous models, to for supply, we used a measure of district nursing density our knowledge, developed to inform the needs based-that was sterilized, ensuring that our predictions of need 

distribution of district nurse staffing levels between geo-

were based on an equal supply of district nursing services 

graphical neighbourhoods. 

*within* the target population. 

In the UK, as in many other countries, the NHS uses 

weighted capitation formulae to distribute health care **Method**

funding to health care planning regions called Integrated **Data**

Care Boards \(ICB\). These are relatively large areas with We used anonymised linked data for all adults \(age18\+\) an average population of 1.5 million people \[4\]. The for-living in Liverpool and registered with a GP in 2021. This 

mulae are applied to separate service areas \(e.g., general included primary care data, extracted from GP practice and acute, mental health, prescribing and primary care clinical systems, linked to data on use of community ser-services\) that along with adjustment for differences in vices from the community services dataset \(CSDS\) \[11\], 

the cost of providing services in each area are used to information on secondary care usage \(hospital admis-compute need-based shares for each ICB. The general sions and A&E attendances\) from the secondary users approach is to use a regression model with utilisation as dataset \[12\]. All data was linked at the individual level the outcome and a large set of need \(e.g., age, sex, long-by the NHS Data Services for Commissioners Regional 

term conditions, deprivation\) and supply \(e.g., distance Office and made available as an anonymised extract to to hospitals, waiting times\) related factors as indepen-the regional relevant authority, NHS Cheshire and Mer-

dent variables \[5, 6\]. Need is then estimated as predicted seyside Integrated Care Board. We further linked these utilisation whilst holding the supply variables constant, two datasets with the index of multiple deprivation therefore estimating patterns of utilisation that are driven \(IMD\) \[13\], which categorizes small areas of England by need and not differences in supply \[7–9\]. In 2019 a according to their level of deprivation. The variables used national formula was developed for community ser-in the analysis included age, gender, ethnicity, Index of 

vices \(including district nursing\) \[3\]. This formula only Multiple Deprivation \(IMD\) overall scores at the Lower included a limited number of needs variables \(age, sex Layer Super Output Areas \(LSOA\) \[13\], whether died and area deprivation\) and was modelled using data from during the year, days alive during the year \(logged\), being one region in the South East of England, as national data in a care home, living alone, receiving palliative care, hav-was not available. 

ing a learning disability, dementia, cancer, cardiovascular 

The methods used for national allocation of resources disease, chronic liver disease, chronic obstructive pulmo-between regions, can also be applied within regions to nary disease, neurological disease, mental health prob-inform allocation of resources, such as staffing levels, lems, number of visits to accident and emergency in the between neighbourhoods. Increasingly regional linked year, elective and emergency admissions to hospital in data resources \[10\] are becoming available for health care the year, number of general practitioners \(GP\) consulta-planning and these can be used to provide rich informa-

tions, and number of district nurses in the team serving 

tion on patterns of need, enabling needs-based workforce the individual as a proportion of the catchment popula-allocation. 

tion of the team. The codes used to extract these diagnos-

In this study, we examined the district nursing ser-

tic variables were based on nationally agreed algorithms 

vices in Liverpool, a city in the North West of England that are used to provide financial compensation to GPs 





Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

Page 3 of 10

through the national Quality and Outcomes Framework of district nurses in a neighbourhood, were sterilized, by 

\[14\]. Our outcome measure was the number of contacts setting the levels in the variable to be equal to the mean with district nurses within the year as recorded within level of the entire city \[17, 18\]. Following the procedure the CSDS data. 

used on national NHS resource allocation formula \[19\], 

where we found that being from a minority ethnic group 

**Analysis**

was associated with lower utilisation \(conditional on 

We used the following model to generate the coefficients other measures of need\), we assumed that this was due associated with each predicting variable:

to lower service access and also sterilised this from the 

prediction of need \(set al.l values to non-Black, Asian 

*Contactsi *= *α *\+ *β * 1 *Agei *\+ *β * 2 *Sexi *\+ *β * 3 *IMDi* or Minority Ethnicity\), so that need was not under esti-

\+ *β * 4 *Agei × Gender *\+ *β*

*i*

5 *Agei × IM Di*

mated due to poor access in this group. 



\+ *γ Xi *\+ *δ Hi *\+ *ρ Ui *\+ *θ DNi *\+ * i* We then derived the needs index for two types of sub-populations, \(1\) the catchment populations for the 16 

Where *Contactsi * was the number of times individual *i * current district nursing teams and \(2\) small neighbour-used a district nursing service, in the year in analysis. 

hoods called Lower Layer Super Output Areas \(LSOA\). 

*Agei * were the standardized values of age LSOA are standardised small geographical areas cover-



*− *

ing the whole of England, each containing a population 

*Z*

*Age*

*Age *= *Agei−*

. 

of around 1500 people. To derive the local needs index 

*i*

*SDAge*

for sub populations we standardised the predicted utili-

*Sexi * was a variable taking value 1 if the individual’s sation levels by dividing the mean of individual predic-phenotypical sex was male and 0 if female. 

tions for each sub population by the mean predictions for 

*IMDi * were the standardized values of IMD score all individuals in Liverpool. Results were also displayed comparing the needs index by age group gender and 



*− *

*Z*

*IMD*

*IMD *= *IMDi−*

. 

IMD quintiles \(computed from the overall IMD scores\). 

*i*

*SDIMD*

We then estimated the needs-based staffing levels by dis-

*Xi * was a vector containing other sociodemographic tributing the total number of full-time equivalent district variables \(e.g., ethnicity, living in a nursing home\). 

nurses in the city to each of the 16 district nursing teams 

*Hi * was a vector containing flags for chronic health in proportion to the estimated need and compared that conditions \(e.g., dementia, use of palliative care, learning to the actual distribution of district nurses between these disabilities, dead\). 

teams in 2021. 

*Ui * included variables of utilization of health care ser-

vices \(e.g., emergency care, GP consultations\)

**Results**

*DN i * corresponds to the proportion of district nurses The total number of contacts in 2021 that patients made to the population in the neighbourhood where individual with district nursing services was 307,783 contacts from *i * lives. Note that was is a key variable is aimed at captur-19,648 individuals, meaning an average of 15.7 contacts 

ing supply side effects on district nursing services utiliza-

per person who had some contact with district nursing. 

tion. Our model assumed that by including this variable, Table 1 displays the summary statistics for all variables most supply-side effects will be accounted for. As a result, used in the analysis, for the full sample, and the sub-sam-other variables that may have been influenced by supply-

ple of people who have used community services at least 

side factors \(such as access to care\) will be less biased and once in 2021. 

will more accurately reflect demand. 

People using district nursing services tended to be 

We used a zero inflated Poisson model \[15\], to account older and slightly more likely to be female \(53.3%\), com-for the count nature of the activity data with a high pro-

pared to the general population. Regarding ethnicity, dis-

portion of people with zero utilisation \[16\]. This model trict nursing users were more likely to be “White” when was composed by two parts: \(1\) The first stage accounted compared to the overall sample \(84% vs. 93%\). All health-for the probability of using district nursing, \(2\) The sec-

related variables \(chronic conditions and use of second-

ond stage accounted for the number of times the individ-

ary care services\) were more prevalent in the subgroup 

ual used district nursing conditional on being predicted using district nursing services. This group also used more to use it at least once. 

accident and emergency, and GP consultations and were 

After estimating the utilisation model, we computed more likely to have died during the year \(9% vs. 1%\). They our estimate of need for each individual in the popula-were also more likely to be served by teams with higher 

tion as the predictions from this model using the esti-

district nursing staff levels. 

mated model coefficients. Supply side effects, proportion 

Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

Page 4 of 10

**Table 1** Descriptive statistics

**Variable**

**Full Cohort**

**District Nursing Users**

Number of observations

359,774

19,648

Number of contacts

307,567

307,567

Mean contacts per person \(Mean \(SD\)\)

0.85 \(10.81\)

15.65 \(43.68\)

**Age**

Age \(Mean \(SD\)\)

47.11 \(18.61\)

66.44 \(18.64\)

18–29 years interval

84,631 \(23.5%\)

1163 \(5.9%\)

30–49 years interval

122,776 \(34.1%\)

2611 \(13.3%\)

50–69 years interval

105,359 \(29.3%\)

6195 \(31.5%\)

70–89 years interval

44,764 \(12.4%\)

8624 \(43.9%\)

90 \+ years

2244 \(0.6%\)

1055 \(5.4%\)

**Gender**

Female

183,207 \(50.9%\)

10,471 \(53.3%\)

Male

176,567 \(49.1%\)

9177 \(46.7%\)

**Index of multiple deprivation**

Index of multiple deprivation score \(Mean \(SD\)\)

43.02 \(20.62\)

43.28 \(20.64\)

1st Quintile score - Most deprived \(Mean \(SD\)\)

70.1 \(5.10\)

69.7 \(4.95\)

2nd Quintile score \(Mean \(SD\)\)

57.7 \(2.99\)

57.5 \(2.96\)

3rd Quintile score \(Mean \(SD\)\)

43.6 \(4.57\)

43.5 \(4.57\)

4th Quintile score \(Mean \(SD\)\)

27.7 \(4.20\)

28.2 \(4.10\)

5th Quintile score - Least deprived \(Mean \(SD\)\)

13.8 \(4.17\)

13.4 \(4.02\)

**Other characteristics**

Black, Asian or Minority Ethnicity

57,073 \(16%\)

1336 \(7%\)

Died within year

3875 \(1%\)

1837 \(9%\)

Days alive during the year \(logged\) \(Mean \(SD\)\)

5.9 \(0.09\)

5.87 \(0.22\)

Nursing home

3858 \(1%\)

1895 \(1%\)

Living alone

54,703 \(15%\)

4905 \(25%\)

Palliative care

2381 \(1%\)

1425 \(7%\)

Learning disability

4181 \(1%\)

516 \(3%\)

Dementia

4165 \(1%\)

1830 \(9%\)

Cancer

7496 \(2%\)

2247 \(11%\)

Cardiovascular disease

30,921 \(9%\)

6020 \(31%\)

Chronic liver disease

10,287 \(3%\)

1059 \(5%\)

Chronic obstructive pulmonary disease

12,187 \(3%\)

1850 \(9%\)

Neurological condition

1511 \(0.4%\)

430 \(2%\)

Any mental health problem

106,564 \(30%\)

9894 \(50%\)

Accident and emergency attendances \(Mean \(SD\)\)

0.36 \(1.06\)

1.03 \(1.94\)

Elective admissions \(Mean \(SD\)\)

0.02 \(0.19\)

0.1 \(0.39\)

Emergency admissions \(Mean \(SD\)\)

0.14 \(0.56\)

0.71 \(1.3\)

General practitioner consultations \(Mean \(SD\)\)

21.41 \(19.85\)

43.40 \(28.48\)

District nurses per 10,000 \(Mean \(SD\)\)

4.17 \(1.58\)

4.5 \(1.46\)

The table displays means and standard deviations, for continuous variables, or number of occurrences and percentages, for factor variables. The first column describes the full cohort, while the second column describes only the individuals who have had at least one contact with district nursing services. All variables except index of multiple deprivation score and district nurses per 10.000 are recorded at the individual level. A higher score in the index of multiple deprivation means the individual lives in a more deprived area. Diagnostic variables are identified through flags in the Quality and Outcomes Framework. This table describes 359,774 unique individuals in the year 2021

**Regression results**

Age, having died during the year, receiving pallia-

Table 2 shows the results of the first stage zero inflation tive care, living in nursing home or living alone, having model of the zero inflated Poisson regression. The first been admitted to hospital, were all associated with an stage regression indicates the association between each increased chance of having some contact with district variable with *not* having contact with district nursing. Or nurses. Most of the diseases included were associated to put it another way, having an odds ratio under 1 indi-with an increased chance of having some contact with 

cates that characteristics were associated with an increased district nurses, except for chronic liver disease which chance of having some contact with district nurses. 

was associated with a lower chance. Being female, having 

Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

Page 5 of 10

**Table 2** Zero-inflation model. Odds ratios showing factors 

**Table 3** Count model. Rate ratios showing factors associated associated with **not** having any contact with district nursing increased number of district nursing contacts amongst people 

**Variable**

**Odds 95% CI**

***p*****-**

who have had some contact with district nursing

**Ratio**

**value**

**Variable**

**Rate **

**95% CI**

***p*****-**

Age \(z-score\)

0.44

0.46

0.43

< 0.001

**Ratio**

**value**

Index of multiple deprivation score 

0.98

1.00

0.96

0.114

Age \(z-score\)

2.81

3.10

2.54

< 0.001

\(z-score\)

Index of multiple deprivation score 

1.19

1.20

1.19

< 0.001

Female gender

1.15

1.21

1.10

< 0.001

\(z-score\)

Age\*Female

0.99

1.02

0.95

0.547

Female gender

1.03

1.04

1.03

< 0.001

Age\*Index of multiple deprivation

1.01

1.02

0.99

0.541

Age\*Female

0.92

0.93

0.91

< 0.001

Died during year

0.49

0.53

0.44

< 0.001

Age\* Index of multiple deprivation

1.02

1.03

1.01

< 0.001

Black, Asian or other Minority ethnic 

1.36

1.45

1.28

< 0.001

Died during year

1.01

1.01

1.01

< 0.001

groups

Black, Asian or other Minority ethnic 

1.45

1.46

1.43

< 0.001

Days alive during the year \(logged\)

1.19

1.31

1.08

< 0.001

groups

Nursing care home

0.45

0.49

0.42

< 0.001

Days alive during the year \(logged\)

1.08

1.10

1.07

< 0.001

Living alone

0.94

0.98

0.90

0.001

Nursing care home

1.08

1.10

1.06

< 0.001

Palliative care

0.46

0.51

0.41

< 0.001

Living alone

1.19

1.20

1.17

< 0.001

Learning disability

0.36

0.40

0.32

< 0.001

Palliative care

1.29

1.30

1.28

< 0.001

Dementia

0.65

0.71

0.60

< 0.001

Learning disability

1.54

1.56

1.52

< 0.001

Cancer

0.49

0.53

0.46

< 0.001

Dementia

2.21

2.25

2.17

< 0.001

Cardiovascular disease

0.88

0.91

0.84

< 0.001

Cancer

0.96

0.97

0.95

< 0.001

Chronic liver disease

1.13

1.22

1.05

0.001

Cardiovascular disease

0.87

0.88

0.86

< 0.001

Chronic obstructive pulmonary 

1.02

1.09

0.96

0.438

Chronic liver disease

1.28

1.29

1.27

< 0.001

disease

Chronic obstructive pulmonary 

1.11

1.13

1.10

< 0.001

Neurological condition

0.44

0.51

0.39

< 0.001

disease

Any mental health problem

0.85

0.88

0.82

< 0.001

Neurological condition

0.78

0.79

0.77

< 0.001

Accident and emergency 

1.00

1.02

0.99

0.721

Any mental health problem

1.45

1.48

1.43

< 0.001

attendances

Accident and emergency attendances 1.36

1.38

1.35

< 0.001

Elective admissions

0.53

0.56

0.50

< 0.001

Elective admissions

0.97

0.97

0.97

< 0.001

Emergency admissions

0.72

0.74

0.71

< 0.001

Emergency admissions

0.98

0.99

0.97

< 0.001

General practitioner consultations

0.98

0.98

0.98

< 0.001

GP consultations

1.11

1.11

1.11

< 0.001

District nurses per 10,000 population

0.95

0.96

0.94

< 0.001

District nurses per 10,000 population

1.01

1.01

1.01

< 0.001

This table displays the results of the first stage of the Zero Inflated Poisson This table displays the results of the second stage of the Zero Inflated Poisson model \(described in the methods section\), estimating the probability of model \(described in the methods section\), estimating the number of contacts individuals not having any contact with district nursing services in the period with district nursing services, conditional on the probability of having at least in analysis. The Odds Ratios in this regression are fully adjusted. A difference of one contact, in the period in analysis. The Odds Ratios in this regression are fully 0.01 in the odds ratio means that for a 1-unit increase \(decrease\) in the variable adjusted. A difference of 0.01 in the odds ratio means that for a 1-unit increase of interest, the likelihood of a district nursing contact becomes more \(less\) likely \(decrease\) in the variable of interest, the expected number of district nursing by a factor of 0.01. This regression uses 359,774 observations \(359,774 unique contacts increases \(decreases\) by a factor of 0.01. This regression uses 359,774 

individuals\) in the year 2021

observations \(359,774 unique individuals\) in the year 2021

been alive for a greater proportion of the year and being 

increased number of contacts with the district nursing 

from a Black or ethnic minority group, was associated services. There were important interactions between age, with a lower probability of having received some contact gender and deprivation. Age has a greater effect on num-with district nursing services. Greater availability of dis-

ber of contacts in more deprived groups and amongst 

trict nurses per capita increased the probability of having men. Living in a nursing home, living alone, and having at least one contact. 

used palliative care increased the number of contacts 

Table 3 shows the results of the second stage regres-with district nursing services. Long-term conditions such 

sion, indicating the relative association of each factor as learning disability, cardiovascular disease, chronic with the number of contacts with district nursing, condi-liver disease, neurological disease and mental ill health 

tional on having at least 1 contact. 

increased the number of contacts. Conversely demen-

The second stage shows that age, deprivation, having tia, cancer and chronic obstructive pulmonary disease died during the year, receiving palliative care, number of decreased the number of contacts. Visits to accident and days alive during the year, living in a nursing home or liv-emergency and elective admissions predicted a lower 

ing alone, being from Black, Asian, and Minority Ethnics number of contacts. The number of district nurses as a group, having had an emergency admission and GP con-proportion of the population was associated with more 

sultations were associated with an. 

contacts. 



Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

Page 6 of 10



**Fig. 1** Estimated district nursing \(DN\) needs index by Age intervals, IMD \(Quintile 1 = most deprived, Quintile 5 = least deprived\) and gender. This graph displays the district nursing needs index by age and index of multiple deprivation quintiles for the city of Liverpool. The predictions result from the Zero Inflated Poisson model described in the methods section

As we find that in the first stage \(zero inflation\) regres-

full-time equivalent district nurses per 10,000 inhabitants 

sion, being from a minority ethnic group is associated in the regions with higher variation. On average, needs with reduced service uptake, we sterilise this from the based staff allocation, in Liverpool, would shift staff from prediction of need in the first stage, so that need is not teams that serve populations with relatively lower needs underestimated due to poor access in this group. Fig-for district nursing services to teams that serve popula-

ure 1 displays the needs index categorized by age groups tions with relatively higher needs for those services. But and IMD quintiles. These figures represent the extent this is not consistent across teams. The team that cur-to which each group’s requirement exceeds the overall rently serves the population with the highest needs, mean. Essentially, a score of 5 indicates that the need is would gain an additional 4.5 staff per 10,000 population, five times greater than the norm. Age seems is the pre-if needs-based allocation was applied, whilst the team 

dominant factor driving need, as older age groups had with the 2nd highest level of need would lose 6.5 WTE 

indexes as high as 11 \(eleven times more need than the per 10,000 population. 

average population\). While needs index was relatively 

less sensitive to IMD, there was still a positive gradient **Discussion** with people living in more deprived areas having greater We show how population linked health care data can be needs. The IMD gradient became stronger with age. Our used to estimate neighbourhood need for district nursing formula resulted in similar predictions between men and services, highlighting those factors that objectively con-women. Yet, it predicted slightly higher needs weights tribute to increased service need. Whilst this shows that for men in the third deprivation quintile of the 90 \+ age the current allocation of staff to neighbourhood district group. 

nursing team in Liverpool does broadly reflect need, it 

Figure 2 shows the comparison between current alloca-identifies some mismatch between resources and need 

tion of district nursing staff \(on the right\) and the needs at a more granular level and some substantive realloca-index based on our formula \(on the left\). Whilst the cur-

tion of staff between teams would be needed, to ensure 

rent allocation of staffing levels broadly matches patterns a more equitable distribution of resources. On average of need, there are some neighbourhoods that are under-this would shift staff to teams with higher overall levels 

served relative to need. 

of need. 

In Fig. 3, we show how number of full-time equivalent Our approach has a number of advantages. The avail-staff would need to vary to better reflect the needs of the ability of rich data enables the creation of a utilisation population for district nursing services. We can see that formula that accounts for a broader range of factors variations ranged from approximately minus 6.5 to plus 5 that contribute to need. Factors not accounted for in the 



Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

Page 7 of 10



**Fig. 2** District nursing estimated needs index and current staffing levels by LSOA. This graph displays the district nursing needs index by Lower Layer Super Output Area in the city of Liverpool. The predictions result from the Zero Inflated Poisson model described in the methods section national model, such as ethnicity, long-term conditions, of supply, our measure would not adequately reflect pat-and household circumstances are particularly useful in terns of total needs. Furthermore, if the observables used predicting need and likely to enhance models \[20\]. This is in the model are associated with unmet needs \[7\], then an advance on and a more statistically complete approach our predictions may underestimate need. For example, if than the national model \[20\]. Furthermore, by sterilizing individuals with physical disabilities are receiving more variables that may contain supply effects, we can generate district nursing services than the average person but still predictions based on a more equitable hypothesis where not enough to meet al.l their needs, their coefficients will every individual has equal opportunities to access health-be lower than what they should have been, and their pre-

care \[7–9\]. Ultimately, this approach can help ensure that dicted needs will be underestimated. This highlights the community services are allocated fairly and efficiently importance of considering the limitations of observable based on local needs. 

data when making predictions and the need to develop 

Despite its benefits, there are potential drawbacks to complementary approaches to identify and address our approach relying on observable data \[21, 22\]. While unmet needs \[23\]. Additionally, the approach to alloca-our predictions make an important effort to incorporate tion we outline aims to allocate resources in proportion available information regarding socio-economic char-to need, where need is defined simply as the amount of 

acteristics and health conditions, it’s important to rec-

district nurse contacts a population would expect to use 

ognize that utilisation approaches can only predict what if the supply was set to the mean, i.e. aiming to achieve is observable. This means that individuals who are not equal access for equal need. This principle of proportion-registered with a GP or who have undiagnosed condi-

ality is not the only objective of resource allocation. As 

tions may be excluded from the analysis or not properly we are not taking account of or estimating the benefit accounted for. The Quality and Outcomes Framework accrued to these population from the allocation of dis-register is expected to capture health data for most indi-

trict nursing resources, we cannot say that this propor-

viduals in the region, though it may occasionally miss tional distribution would necessarily be more efficient some cases, which may be seen as a limitation of our data. \(i.e. lead to more benefit per unit of cost\) or decrease the Intensity of care is also absent from the model, as we only gap in outcomes between more and less socially disad-have the number of contacts, but not the amount of time vantaged groups. In other words, if groups identified as of each contact. This may be particularly worrisome if having higher needs have lower ability to benefit from some groups of patients may require longer visits than additional district nursing services than groups identified others. If there are systematic differences in unmet needs as having lower needs, then re-allocation of resources that are not sufficiently accounted for in our measures may not result in higher efficiency \[24–28\]. Additionally, 



Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

Page 8 of 10



**Fig. 3** Change in the number of district nurses per 10,000 in each district nursing \(DN\) team that would result from redistributing staff based on estimated numbers off staff in each team. This graph displays the district nursing needs index by district nursing teams in Liverpool. The predictions result from the Zero Inflated Poisson \(model described in the methods section\) evidence suggests that since 2010, the national fund-It could however be the case that this does reflect lower 

ing formula has become less effective at reflecting actual need for “any contact” in this population. Using a binary needs in its allocations to ICB \[29\]. As a result, even if value is not ideal, as the various ethnic groups catego-ICB improve their ability to allocate resources propor-

rized under Black, Asian, or other Minority Ethnic labels 

tionally within their local areas, the overall distribution may have distinct needs and encounter different chal-may remain inequitable. 

lenges in accessing district nursing services. Due to the 

Ethnicity’s inclusion is particularly important given the limited quality of ethnicity data and the predominance documented disparities in health outcomes and access of white ethnicity in the dataset, pooling other ethnici-to healthcare services among different ethnic groups. ties together was necessary for the analysis. While this However alternative interpretations of the coefficients, to should not affect our predictions \(as ethnicity would still those we present, are plausible. We found that being from be sterilized\), we lose some information on which ethnic-a Black, Asian, or other Minority Ethnic group reduced ities face the biggest barriers in accessing district nursing the chances of having any contact with district nurses services. 

\(conditional of other indicators of need\) but increased 

the numbers of contacts when people did have con-

**Implications for policy**

tact. We interpret this as indicating lower initial service With the increasing availability of linked regional health access in these groups, potentially due to either service or and social care datasets, for example through the cur-patient related factors \(e.g. help seeking behaviour\), but rent NHS programme of establishing regional Secure that when they do have access, they then actually have Data Environments \[30\], there is the opportunity to higher needs. As we think the coefficient on this variable apply the methods outlined here for developing effec-in the initial regression, reflects unequal access, rather tive local formula for estimating service needs. Local lower need, we sterilise this from the prediction of need. approaches for neighbourhood level resource allocation 



Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

Page 9 of 10

have been underutilised as an approach for addressing these services by neighbourhood. Our research presents unmet needs and health care inequalities. The NHS in a novel district nurse staffing allocation model designed England has made addressing inequalities and reducing to distribute healthcare resources more accurately and unmet need a priority \[31\]. The approach we outline pro-equitably at the neighbourhood level. By prioritising 

vides a powerful tool for local health and care systems areas of higher need and ensuring that resource alloca-to meet these obligations and redistribute district nurs-

tion is closely aligned with local demographic and health 

ing staff according to localised need profiles, which can profiles, we offer a path towards more equitable health-significantly improve the match between healthcare ser-

care service delivery. 

vices and patient requirements. This approach not only 

aims to ensure that resources are used where they are **Acknowledgements** The authors wish to thank NHS Cheshire & Merseyside Integrated Care Board most needed but also contributes to a more sustainable for supporting this study, and Laura Anselmi \(University of Manchester\), for healthcare system by optimising the use of limited staff-providing methodological advice. 

ing resources \[32\]. 

**Data sharing**

The methods and findings we report may be used in Data are currently available under license from NHS England. Statistical code is two ways. First, they may inform district nursing alloca-available at https:/ /github .com/ci pha- uk/dis trict-n ursing- allo cation.git. 

tion across teams. This would mean that teams serving **Authors’ contributions** relatively understaffed regions, in proportion to need, L.F. and B.B. designed the work, analysed the data, prepared figures and could see their resources increased, while teams serv-tables and wrote the manuscript.R.P. linked and cleaned datasets, provided ing relatively overstaffed regions, in proportion to need, contextual information for the interpretation of the results and reviewed drafts of the manuscript.W.B. provided important contributions for work design, could see their resources reduced. Second, they may contextual information for the interpretation of the results and reviewed inform reallocation of resources within each team. Since drafts of the manuscript J.R., and I.B. provided contextual information for the we provide information on LSOA level, district nursing interpretation of the results and reviewed drafts of the manuscript. 

teams may work to identify the needs of the LSOA with **Funding**

higher needs scores in our results and adjust resources to This research was funded by the NIHR Policy Research Programme \(RESTORE; better face those needs. It is important to note that while Award ID, NIHR202484\), the NIHR Applied Research Collaboration Northwest Coast \(NWC ARC\), the Health Foundation, United Kingdom - The Network Data we identified where needs are greatest, there may be bar-Lab, the NIHR Three Research Schools Fellowship in Mental Health Research riers to the direct reallocation of staff or other resources. - n. MHF106 and the NIHR senior investigator award NIHR205131. The views Therefore, we recommend that decision-makers first expressed in this publication are those of the authors and not necessarily those of the National Institute for Health Research or the Department of assess why certain areas are not receiving the resources Health and Social Care. 

suggested by our model. If access issues are identified, 

these should be addressed before reallocating staff or **Data availability** Data are currently available under license from NHS England. Statistical code is other district nursing resources. We recognize that dis-available on request from the authors. 

trict nursing resources can be “sticky”, meaning realloca-

tions may take time. For example, instead of immediately **Declarations** transferring staff, decision-makers may need to wait for 

natural opportunities, such as not replacing retirees in **Ethics approval and consent to participate** The results in this manuscript are informed by the analysis of anonymised areas with a relative oversupply of staff and direct new secondary data held by NHS Cheshire & Merseyside and approved by their hires to areas with relative undersupply of staff. Decision Data Access and Asset Group. Only anonymised secondary data were used. 

makers need to work around these constraints, such that No personal data was used in this study and as such, there is no requirement for research ethics committee review. 

the costs of reallocations do not surpass their benefits. 

Since this approach relies on the availability of linked, **Competing interests** cross-sectoral and rich data of health and care indica-The authors declared the following potential conflicts of interest with respect to the research, authorship, and/or publication of this article: Wes tors, it is paramount to develop a culture of better, civi-Baker and Joe Rafferty are employed by Mersey Care NHS foundation Trust, cally oriented and trustworthy sharing of data and robust the provider of district nursing services in Liverpool. They were involved methods to ensure rigorous curation and quality assur-in providing information about the nature of district nursing services and staffing in Liverpool, facilitating access to data, as well as providing contextual ance of data resources, especially enhancing the pro-information for the interpretation of the results, reviewing drafts of the cesses available in the recording of routinely collected manuscript. They had no role in the analysis or presentation of the results. 

data. 

The views expressed in this article are those of the authors and do not represent the views of Mersey Care NHS foundation Trust. There are no other relationships or activities that could appear to have influenced the submitted **Conclusion**

work. 

Community services are a core part of England’s Inte-

grated Care Systems \(ICSs\), which need tools for allocat-

Received: 16 May 2024 / Accepted: 23 October 2024

ing resources proportionate to their residents’ needs for 

Filipe *et al. BMC Health Services Research* \(2024\) 24:1362 

Page 10 of 10

**References**

17. Penno E, Gauld R, Audas R. How are population-based funding formulae for 1. N.H.S England. NHS England » Community health services. 2022. h t t p s :/ / w w 

healthcare composed? A comparative analysis of seven models. BMC Health 

w . e n g la n d .n h s .u k / c o m m u n it y - h e a lt h - s e r v ic e s / . Accessed 4 Aug 2022. 

Serv Res. 2013;13:470. 

2. Willis E, Henderson J, Toffoli L, Walter B. Calculating nurse staffing in commu-18. Rice N, Smith PC. Ethics and geographical equity in health care. J Med Ethics. 

nity mental health and community health settings in South Australia. Nurs 2001;27:256–61. 

Forum \(Auckl\). 2012;47:52–64. 

19. NHS England, Analytical Services \(Finance\). Technical Guide to Allocation 3. NHS England – Analysis and Insight for Finance. Community Services alloca-Formulae and Pace of Change for 2016-17 to 2020-21 revenue allocations to tions formula: for 2019/20 to 2023/24 revenue allocations. 2019. h t t p s :/ / w w w 

clinical commissioning and commissioning areas. 2016. h t t p s :/ / w w w . e n g l a n 

. e n g l a n d . n h s . u k / p u b li c a t io n / c o m m u n it y - s e r v ic e s - a l o c a t io n s - fo r m u la / . 

d . n h s . u k / p u b l i c a t i o n / t e c h n ic a l - g u i d e - t o - a l o c a t io n - f o r m u la e - a n d - p a c e - o f - c 

4. Office for National Statistics. Annual mid-year population estimates for Clini-

h a n g e - fo r - 2 0 1 6 - 1 7 - t o - 2 0 2 0 - 2 1 - r e v e n u e - a l o c a t io n s - t o - c li n ic a l- c o m m is s io n in 

cal Commissioning Groups. 2022. h t t p s :/ / w w w . o n s . g o v . u k / p e o p l e p o p u l a t i o n 

g - g r o u p s - a n d - c o m m is s io n in g - a r e a s / . 

a n d c o m m u n i t y / p o p u la t i o n a n d m ig r a t io n / p o p u la t io n e s t im a t e s / b u l e t in s / a n n 

20. Radinmanesh M, Ebadifard Azar F, aghaei Hashjin A, Najafi B, Majdzadeh R. A 

u a ls m a l a r e a p o p u la t io n e s t im a t e s / 2 0 1 3 - 0 8 - 1 5 . Accessed 4 Aug 2022. 

review of appropriate indicators for need-based financial resource allocation 5. NHS England, Analytical Services \(Finance\). Refreshing the Formulae for CCG 

in health systems. BMC Health Serv Res. 2021;21:674. 

Allocations for allocations to Clinical Commissioning Groups from 2016-17 - 

21. Asthana S, Gibson A. Health care equity, health equity and resource alloca-Report on the methods and modelling. 2016. h t t p s :/ / w w w . e n g l a n d . n h s . u k / p 

tion: towards a normative approach to achieving the core principles of the 

u b l i c a t i o n / r e f r e s h i n g - t h e - f o r m u l a e - f o r - c c g - a l o c a t i o n s - f o r - a l o c a t io n s - t o - c li n i

NHS. Radic Stat. 2008;96:6. 

c a l- c o m m is s io n in g - g r o u p s - f r o m - 2 0 1 6 - 1 7 - r e p o r t - o n - t h e - m e t h o d s - a n d - m o d e 

22. Smith PC, Rice N, Carr-Hill R. Capitation funding in the public sector. J R Stat 

l i n g - n h s - e n g la n d - a n a ly t ic a l- s e r v ic e s - fi n a n c e / . 

Soc Ser Stat Soc. 2001;164:217–57. 

6. Dixon J, Smith P, Gravelle H, et al. A person based formula for allocating com-23. Vallejo-Torres L, Morris S, Carr-Hill R, et al. Can regional resource shares be missioning funds to general practices in England: development of a statistical based only on prevalence data? An empirical investigation of the proportion-model. BMJ. 2011;343:d6608. 

ality assumption. Soc Sci Med. 2009;69:1634–42. 

7. Aragon MJA, Chalkley M, Goddard M. Defining and measuring unmet need 24. Gustavsson E. From needs to Health Care needs. Health Care Anal. 

to guide healthcare funding. Identifying and filling the gaps, Centre for 2014;22:22–35. 

Health Economics. York: University of York; 2017. 

25. Watt IS, Sheldon TA. Rurality and resource allocation in the UK. Health Policy. 

8. Cookson R, Doran T, Asaria M, Gupta I, Mujica FP. The inverse care law re-1993;26:19–27. 

examined: a global perspective. Lancet. 2021;397:828–38. 

26. Culyer A. Efficiency, equity and equality in health and 

9. Gravelle H, Sutton M, Morris S, et al. Modelling supply and demand influences healthcare. F1000Research. 2019;8\(800\):800. 

on the use of health care: implications for deriving a needs-based capitation 27. Love-Koh J, Griffin S, Kataika E, Revill P, Sibandze S, Walker S. Methods to formula. Health Econ. 2003;12:985–1004. 

promote equity in health resource allocation in low- and middle-income 10. NHS England. » Investing in the future of health research: secure, accessible countries: an overview. Glob Health. 2020;16:6. 

and life saving. h t t p s :/ / w w w . e n g l a n d . n h s . u k / b lo g / in v e s t in g - in - t h e - f u t u r e - o 

28. O’Sullivan L, Aldasoro E, O’Brien Á, Nolan M, McGovern C, Carroll Á. Ethical 

f - h e a lt h - r e s e a r c h - s e c u r e - a c c e s s ib le - a n d - li fe - s a v in g / . Accessed 12 Feb 2024. 

values and principles to guide the fair allocation of resources in response to a 11. NHS Digital. Community Services Data Set. NHS Digit. 2022. h t t p s :/ / d i g i t a l . n h 

pandemic: a rapid systematic review. BMC Med Ethics. 2022;23:70. 

s . u k / d a t a - a n d - in f o r m a t io n / d a t a - c o l e c t io n s - a n d - d a t a - s e t s / d a t a - s e t s / c o m m u 

29. Barr B, Taylor-Robinson D. Poor areas lose out most in new NHS budget 

n it y - s e r v ic e s - d a t a - s e t . Accessed 4 Aug 2022. 

allocation. BMJ. 2014;348:g160. 

12. Secondary Uses Service. h t t p s :/ / w w w . d a t a d ic t io n a r y .n h s .u k / s u p p o r t in g \_ in fo r 

30. HDRUK Innovation Gateway | The NHS Research Secure Data Environment 

m a t io n / s e c o n d a r y \_ u s e s \_ s e r v ic e .h t m l . Accessed 12 Feb 2024. 

Network. h t t p s :/ / w w w . h e a l t h d a t a g a t e w a y .o r g / a b o u t / t h e - n h s - r e s e a r c h - s e c u r 

13. National Statistics. English indices of deprivation 2019. GOV.UK. 2019. h t t p s 

e - d a t a - e n v ir o n m e n t - n e t w o r k . Accessed 15 May 2024. 

: / / w w w . g o v . u k / g o v e r n m e n t / s t a t is t ic s / e n g li s h - in d ic e s - o f - d e p r iv a t io n - 2 0 1 9 . 

31. England NHS. NHS England » The Equality and Health Inequalities Hub. 2022. 

Accessed 4 Aug 2022. 

https:/ /www.en gland.n hs.u k/about/equality/equality-hub/. Accessed 4 Aug 14. NHS Digital. Quality and Outcomes Framework \(QOF\). NHS Digit. 2021. h t t p s :/ 

2022. 

/ d i g i t a l . n h s . u k / d a t a - a n d - in f o r m a t io n / d a t a - t o o ls - a n d - s e r v ic e s / d a t a - s e r v ic e s / g 

32. Barr B, Bambra C, Whitehead M. The impact of NHS resource allocation policy 

e n e r a l- p r a c t ic e - d a t a - h u b / q u a li t y - o u t c o m e s - f r a m e w o r k - q o f . Accessed 4 Aug on health inequalities in England 2001-11: longitudinal ecological study. BMJ. 

2022. 

2014;348:g3231–3231. 

15. Lambert D. Zero-inflated Poisson Regression, with an application to defects in Manufacturing. Technometrics. 1992;34\(1\). h t t p s :/ / d o i . o r g / 1 0 .1 0 8 0 / 0 0 4 0 1 7 

0 6 .1 9 9 2 .1 0 4 8 5 2 2 8 . Accessed 4 Aug 2022. 

**Publisher’s note**

16. Cameron AC, Trivedi PK. Regression Analysis of Count Data. Cambridge Springer Nature remains neutral with regard to jurisdictional claims in University Press; 2013. 

published maps and institutional affiliations. 


# Document Outline

+ ﻿Improving equitable healthcare resource use: developing a neighbourhood district nurse needs index for staffing allocation  
	+ ﻿Abstract 
	+ ﻿Introduction 
	+ ﻿Method  
		+ ﻿Data 
		+ ﻿Analysis 

	+ ﻿Results  
		+ ﻿Regression results 

	+ ﻿Discussion  
		+ ﻿Implications for policy 

	+ ﻿Conclusion 
	+ ﻿References



