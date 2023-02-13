# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib as mplt
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_pickle("cis_survey_data_revised.pkl")
dataRef = pd.DataFrame(df.dtypes).reset_index()



df.masCercanoPartido.unique()[0]
df_pol = df.iloc[:, 8:9]
df_socio = df.iloc[:, np.r_[5:8, 59:69]]
sns.catplot()

### ideological affinities
# masCercanoPartido, autodefIdeol1, autodefIdeal2, simpatiaHaciaPartido,
# intencionVotoPartido1, intencionVotoPartido2, posicionIdeolPropia

sns.displot(x=df.posicionIdeolPropia, kind = "hist", discrete = True)

sns.displot(x=df.masCercanoPartido, kind = "hist", discrete = True)
