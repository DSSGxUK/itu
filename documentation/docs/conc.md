# Discussion

Throughout the project, the team has gained a variety of insights that can be used in future research and for extending the completed model for the pilot countries. The model is intended as a generic tool and is replicable across countries, while allowing for further customization for every additional country.
The tool developed is capable of providing multiple outcomes: 

•	First of all, the size of offline populations is estimated around schools and at the community level, across the country.

•	Then, based on the model application, a rank of priority can be given to schools, which can serve to inform a national connectivity roadmap. The prioritization of schools to be connected can be sorted by the absolute number of the offline population that can potentially be served by a new connection, or by the relative share of online population. In addition, it is possible to introduce additional criteria or indicators to adapt the ranking depending on higher-level policy priorities, e.g., by excluding densely populated or metropolitan areas. This focus could be placed if schools in less populated or rural areas experience specific challenges and would benefit most from Internet connectivity.

•	Moreover, the level of geographic aggregation of connectivity ratios can be readily modified up to the federal state or to the country level. The scripts and relevant documentation developed for this project can inform national connectivity initiatives and support institutions throughout their implementation. Development partners and initiatives, such as Giga, can likewise leverage the tool to enhance resource allocation for connecting schools, accelerate connectivity and maximize social impact. The analysis can be done for a country, across multiple countries as well as on the province, region or city level. 

•	Last but not least, to support the work of institutions and partners, the team has developed a straightforward tool for data gathering and Exploratory Data Analysis (EDA). Creating quick map graphics or correlation plots might already indicate the presence of clear trends and inform policy and implementation discussions. 


# Limitations

During the project, we have faced certain limitations, in particular in the area of model evaluation. The model performs accurately within the original pilot country, however its level of applicability to countries from other global regions with differences in economic and social indicators is yet to be determined. Future applications and extension of the models can help to further refine and enhance the project outcome. 

In the case of Thailand in particular, the team encountered additional challenges with data quality. It was not possible to separate the different sources of error within the dataset from each other. In this specific case, for instance, we could not find out to which degree the geographic aggregation of the target variable or the fact that we used Open Street Maps (OSM) schools impacted model performance and error.
In addition to the limitations faced, there are more uncertainties that might have affected the findings of our work and its future extensions. Those deserve further scrutiny and discussion.

•	As explained above, we cannot evaluate yet how OSM school data performs compared to official school location data. If this data source is to be used as an alternative to UNICEF school data, its representativity should be carefully reviewed. 

•	Furthermore, while Facebook data could contribute to producing reliable near real-time estimates of Internet population in some countries or regions, in some cases it could prove insufficiently representative. Since the popularity of Facebook varies over time, between countries or according to demographics, estimating Internet use solely based on it might lead to misinterpretation. For instance, if a large metropolitan area shows a low percentage of Facebook users, this is not yet an indication of low overall Internet penetration, but could be due to the fact that another social media platform (such as Instagram) has overtaken it in popularity. An analysis of the distribution of Facebook users among social groups could improve data interpretation.

•	Another potential source of bias could be the fact that, in our original approach, survey data is used as ground truth. Survey data are typically prone to bias due to, for instance, misreporting or systematic non-response (e.g., survey respondents have previously stated that they are not using the Internet but in the same survey declared themselves as Facebook users). Importantly, non-response could be problematic since the offline population is less likely to respond to the survey. A potential corroborating measure here could be comparing the distribution of demographic data within the survey (e.g., income, gender) with other open data sources. 

•	Ultimately, if the analysis is extended to more countries, the availability of microdata could introduce bias in the selection of countries to be targeted. It would be fair to assume that countries where no microdata on telecommunications use exists are likely to display lower connectivity levels. Therefore, further research should attempt to provide sound estimates of the offline population in the absence of national microdata, i.e. a global model that can be reliably applied to most countries. Applying a robust model that can accommodate various countries’ circumstances without requiring microdata would then also be fully open-source. 


# Next Steps

## Additional Methods

Multiple additional methods could be applied to our existing models and analyses. This can either lead to both, a further corroboration of results and the extension/improvement of the existing work.  

• Full scoring on Brazil 

Given our existing champion model, all schools outside the featured enumeration areas can now be scored with an estimated level of connectivity. This could be done for a sample of schools as a sanity check or for the entire country, which would yield a similar map to the Giga connectivity map. 


• Statistical robustness checks 

In particular, two steps could be reasonable additions that take the geographic nature of the data even more into account: 

1.	Estimating a Geographically Weighted Regression (GWR) 

2.	Performing spatial cross-validation of the models


•	Experiment with featured data

The way some of the model features are configured could be further fine-tuned. 

1. First, it is worth experimenting with Facebook data to explore whether it can be used as a standalone proxy variable for online population. This would provide a quick and efficient tool to estimate connectivity and allow for the extension of the project to a greater number of countries. 

2. Separately, pulling OSM school locations for Brazil and applying the model to this new sample of schools could yield insights on the representativity of OSM data. 

3. Finally, buffer zones around schools are currently constant in diameter, but could be varied according to specific variables (e.g., population data). 


## Extension to other countries

The existing model can be applied to every country with OSM school location data available. However, model evaluation or model training requires two more components: 

•	Microdata (on household, individual or enumeration area level)

•	The respective shapefiles/geolocation of the enumeration area

Our current experience indicates that analyzing larger geographical aggregates such as provinces diminishes model performance and interpretability. An enumeration area is assumed to be a homogeneous area, whereas the variation of localized connectivity levels within a federal state for instance is expected to be much higher. 
Further model training
With more countries being included in the connectivity analysis, more options of model combinations open up. As long as the requirements (microdata and shapefiles) are met, an individual model can and should be trained for each country and evaluated separately. In addition, joint models with multiple countries could result in a high predictive power on a global level and increase model robustness. Comparing the performance of combined and single-country models can give insights on the impact of country specific differences. Furthermore, the idea of training regional models (e.g., a model for South-East Asian countries) appears worth exploring. National stakeholders that are not able to share enumeration area level microdata (e.g., for legal reasons due to anonymity restrictions) can obtain the scripts and additional content developed through this project and run a custom model training locally. 

## Additional data sources

Introducing additional data sources in the modelling can improve its predictive power and replicability.

• Country-level data

When extending the models to multiple countries, including country level variables might allow for boosting the original model. Possible additions could be urbanization rate, GDP, public spending on telecommunications or other indices of human/infrastructural development. In doing so, country-specific intercepts are featured in the estimation and will assist accounting for differences in overall connectivity between countries.

• Additional content from survey/school data

The original models have so far only been using the necessarily required features of survey and school location data. To keep our approach as generic and replicable to other countries as possible, additional information from these data sources has not been built in the models. However, in order to enhance national models, additional data series from surveys can be usefully integrated (e.g., connectivity-related variables, reasons for (non-)connectivity, demographic information such as age or gender or information on household size or income). Similarly, additional information contained in school location datasets such as pupil count or computer availability could also be used in further analysis (e.g., for estimating the propensity or ease of connection for a specific school). 

• Further data 

Arguably, existing models could be improved by adding more features to the training datasets. Possible additions could stem from official data provided by national stakeholders such as Ministries, regulatory authorities, telecom operators and service providers (e.g., coverage and characteristics of existing infrastructure), or digital platforms and monitoring services (such as Google, Facebook or Cisco Analytics). As a minimum requirement, a hypothetical logical connection between feature and target variable should always exist. 
