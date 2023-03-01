# Centro de Investigaciones Sociológicas (CIS) survey exploratory data analysis

*In progress!*

In this project, one of the latest CIS' survey data is explored and analysed. The CIS is a public Spanish government institute which regularly conducts fairly large scale surveys and makes the generated data available to the general public. 

The project (currently) consists of two major files:
- The **cis_data_preparation.py** file, where the data is cleaned, variables dropped, renamed, variables' values (esp. text) are edited and variables are converted to their optimal data type. In order to avoid coding redudancy, a large part of this process is automated via the use of loops and dictionaries. 
- The **cis_analysis.py** file, where the data is analysed. In order to proceed systematically, the variables where divided into three groups (social, political, ideological), which are first analyzed separately in terms of their distributions. In a second step, the relationship between these three groups of variables will be analyzed. 
Once the data analysis has been largely completed in terms of coding, a Jupyter Lab report will be provided, which discusses the major findings and insights. 
