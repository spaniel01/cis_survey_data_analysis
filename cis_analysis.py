# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import math
import matplotlib as mplt
import matplotlib.pyplot as plt
import seaborn as sns
mplt.interactive(True)
sns.set_theme(style = "darkgrid")

df = pd.read_pickle("cis_survey_data_revised.pkl")
dfTypes = pd.DataFrame(df.dtypes)

# Party groups
partyGroups = {"partidoNacionalTodos" : ['Podemos', 'PP', 'Ciudadanos', 'Ninguno', np.nan, 'PSOE', 'Otro partido', 'VOX', 'Más País', 'IU', 'Más Madrid', 'SUMAR'],
               "partidoNacionalVIP" : ['Podemos','PP', 'Ciudadanos', 'Ninguno', np.nan, 'PSOE', 'Otro partido', 'VOX'],
               "catalan" : ['CUP', 'ERC', 'JxCat', 'PdeCat'],
               "regionalVipSocios" : ['ERC', 'PRC', 'PNV', 'EH Bildu'],
               "regionalTodos" : ['Compromís', 'Andalucía Por Sí', 'Teruel Existe', 'CUP', 'MÉS (PSM-Entesa)', 'ERC', 'Nueva Canarias','CC-PNC', 'BNG', 'PRC', 'JxCat', 'EH Bildu', 'PdeCat', 'EAJ-PNV', 'Geroa Bai', 'UPN']
               } # Sumar, Yolanda, Más País, Errejon
partidoNacionalTodos = pd.CategoricalDtype(categories = ['Podemos', 'Más Madrid', 'Más País', 'SUMAR', 'IU', 'PSOE', 'Ciudadanos', 'PP','VOX', 'Otro partido', 'Ninguno'],
                                           ordered = True)

# Variable groups
df_pol = list(df.iloc[:,list(range(8,59))].columns)
df_social = list(df.iloc[:,list(np.r_[0:3, 5:8, 59:69])].columns)
df_survey = list(df.iloc[:,list(np.r_[0:5, 79:-1])].columns)
df_ideol = ["masCercanoPartido", "autodefIdeol1", "autodefIdeal2", "simpatiaHaciaPartido", "intencionVotoPartido1", "intencionVotoPartido2", "posicionIdeolPropia"]
df_gastar = [col for col in df if col.startswith('gastar')]
df_preocup = [col for col in df if col.startswith('preocup')]
df_liderCononce = [col for col in df if col.startswith('liderConoce')]
df_liderValoracion = [col for col in df if col.startswith('liderValoracion')]
df_probEsp = [col for col in df if col.startswith('probEsp')]
df_probPersonal = [col for col in df if col.startswith('probPersonal')]
df_situaction_eco = ['valorSitEcoPersonal', 'valorSitEcoEspana']
df_confianza = [col for col in df if col.startswith('confianza')]
df_preperacion = [col for col in df if col.startswith('preperacion')]
df_mod = [col for col in df if col.startswith('mod')]

# Variable type groups
catVars = list(df.select_dtypes("category").columns) 
objVars = list(df.select_dtypes("object").columns)
contVars = list(df.select_dtypes("int64").columns) + list(df.select_dtypes("float64").columns)


############################################################################################################################################################  
df.columns
### NA values
df_na = df.drop(columns = df_mod).isna().sum()
df_na = df_na[df_na.iloc[:,] != 0].sort_values()
df_na.plot(kind = "barh")
plt.show();

### Social

# AC and gender
pd.crosstab(df['ccaa'], df['sexo']).plot(kind='barh', stacked=True)
plt.tight_layout()
plt.show();

# Pop of place of origin
(pd.crosstab(df['ccaa'], df['tamanoMunicipo'], normalize = "index",)*100).plot(kind='barh', stacked=True)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, title="Bla")
plt.tight_layout()
plt.show();

# Age
sns.displot(data=df, x="edad")
plt.tight_layout()
plt.show();

# Social class
catOrder = list(df.claseSocial.cat.categories)
catOrder.reverse()
(df.claseSocial.value_counts(normalize = True)*100)[catOrder].plot(kind = "barh")
plt.tight_layout()
plt.show();

# Religion
(df.religion.value_counts(normalize = True)*100)[df.religion.cat.categories].plot(kind="barh")
plt.tight_layout()
plt.show();

# Religion and practicing
df2=df.loc[df["religion"].isin(["Catholic", "Other religion", "Pract. Catholic"])].copy()
df2["religion"] = df2.religion.cat.remove_unused_categories()
g1 =sns.jointplot(data=df2, x="religion", y="practicaRelig", kind="hist")
g1.ax_joint.set_xticklabels(list(df2.religion.cat.categories), rotation = 45)
plt.tight_layout()
plt.show();

# Add these graphically
df.columns
df.escuela.unique()
df.maxEstudios.unique()
df.situacionLaboral
df.situacionProfesional
df.ocupacion
df.ingresosHogar
df.claseSocial

### Political
if len(df_preocup)/3 > 1:
      fig, axs = plt.subplots(ncols=3, nrows = math.ceil(len(df_preocup)/3), sharey = True)
      horizontal = 0
      vertical = 0
      for var in df_preocup:
            sns.countplot(x = var, data=df, ax=axs[vertical, horizontal])
            ax.tick_params(axis = "x", rotation = 90)
            horizontal += 1
            if horizontal > 2:
                  horizontal = 0
                  vertical += 1 
else : 
      fig, axs = plt.subplots(ncols=3, nrows = 1, sharey = True)
      horizontal = 0
      for var in df_preocup:
            sns.countplot(x = var, data=df, ax=axs[horizontal])
            horizontal += 1
for ax in axs.flatten():
      ax.tick_params(axis = "x", rotation = 90)
plt.tight_layout()
plt.show();

def countPlots(varNameList, df, shareXBool = False, figSize=(15, 15), Pad = 1.08, RectTupleLBRT = (0,0,1,1), title = None, Rotation = 90):
      if len(varNameList)/3 > 1:
            fig, axs = plt.subplots(ncols=3, nrows = math.ceil(len(varNameList)/3), sharey = True, sharex = shareXBool, figsize=figSize)
            horizontal = 0
            vertical = 0
            for var in varNameList:
                  sns.countplot(x = var, data=df, ax=axs[vertical, horizontal])
                  horizontal += 1
                  if horizontal > 2:
                        horizontal = 0
                        vertical += 1 
      else : 
            fig, axs = plt.subplots(ncols=len(varNameList), nrows = 1, sharey = True, figsize=figSize)
            horizontal = 0
            for var in varNameList:
                  sns.countplot(x = var, data=df, ax=axs[horizontal])
                  horizontal += 1
      axCount = 0
      for ax in axs.flatten():
            ax.tick_params(axis = "x", rotation = Rotation)
            if title is not None:
                  ax.set_title(varNameList[axCount])
                  axCount += 1
      plt.tight_layout(pad = Pad, rect = RectTupleLBRT)
      plt.show();

def countPlotsNum(varNameList, df, shareXBool = False, figSize=(15, 15), Pad = 1.08, RectTupleLBRT = (0,0,1,1), title = None, Rotation = 90, Binwidth = 1):
      if len(varNameList)/3 > 1:
            fig, axs = plt.subplots(ncols=3, nrows = math.ceil(len(varNameList)/3), sharey = True, sharex = shareXBool, figsize=figSize)
            horizontal = 0
            vertical = 0
            for var in varNameList:
                  sns.histplot(x = var, data=df, discrete = True, ax=axs[vertical, horizontal])
                  horizontal += 1
                  if horizontal > 2:
                        horizontal = 0
                        vertical += 1 
      else : 
            fig, axs = plt.subplots(ncols=len(varNameList), nrows = 1, sharey = True, figsize=figSize)
            horizontal = 0
            for var in varNameList:
                  sns.histplot(x = var, data=df, discrete = True, ax=axs[horizontal])
                  horizontal += 1
      axCount = 0
      for ax in axs.flatten():
            ax.tick_params(axis = "x", rotation = Rotation)
            if title is not None:
                  ax.set_title(varNameList[axCount])
                  axCount += 1
      plt.tight_layout(pad = Pad, rect = RectTupleLBRT)
      plt.show();

# Worries and spending
countPlots(df_preocup, df)
countPlots(df_gastar, df, shareXBool = True, Pad = 1.3, RectTupleLBRT = (0,.255,1,1))

# Leadership
countPlots(df_liderCononce, df, Rotation = 0)
countPlotsNum(df_liderValoracion, df, Rotation = 0)

# Valorar situacion economica
countPlots(df_situaction_eco, df, title = True)
sns.jointplot(data=df, x = df_situaction_eco[0], y = df_situaction_eco[1], kind = "hist")
plt.show();

# Problems in Spain
df_probEsp_melted = df[df_probEsp].melt()
df_probEsp_melted.variable = pd.Categorical(df_probEsp_melted.variable, ordered = True, categories = reversed(df_probEsp))
df_probEsp_melted.value = pd.Categorical(df_probEsp_melted.value, ordered = True, categories = df_probEsp_melted.value.value_counts().index.values)
sns.displot(data = df_probEsp_melted, y = "value", hue = "variable", discrete = True, kind="hist", multiple = "stack")
plt.show();

# Personal problems
df_probPersonal_melted = df[df_probPersonal].melt()
df_probPersonal_melted.variable = pd.Categorical(df_probPersonal_melted.variable, ordered = True, categories = reversed(df_probPersonal))
df_probPersonal_melted.value = pd.Categorical(df_probPersonal_melted.value, ordered = True, categories = df_probPersonal_melted.value.value_counts().index.values)
sns.displot(data = df_probPersonal_melted, y = "value", hue = "variable", discrete = True, kind="hist", multiple = "stack")
plt.show();

# Confianza
df_confianza_melted = df[df_confianza].melt()
df_confianza_melted.value = pd.Categorical(df_confianza_melted.value, ordered = True, categories = df.confianzaEnLiderOposic.cat.categories)
ax = sns.countplot(data = df_confianza_melted, x = "value",  hue = "variable")
total = len(df_confianza_melted) - df_confianza_melted.value.isna().sum()
for p in ax.patches:
    percentage = f'{100 * p.get_height() / total:.1f}%\n'
    x = p.get_x() + p.get_width() / 2
    y = p.get_height()
    ax.annotate(percentage, (x, y), ha='center', va='center')
plt.show();

# Preperacion
df_preperacion_melted = df[df_preperacion].melt()
df_preperacion_melted.value = pd.Categorical(df_preperacion_melted.value, ordered = True, categories = df.preperacionOposicion.cat.categories)
ax = sns.countplot(data = df_preperacion_melted, x = "value",  hue = "variable")
total = len(df_preperacion_melted) - df_preperacion_melted.value.isna().sum()
for p in ax.patches:
    percentage = f'{100 * p.get_height() / total:.1f}%\n'
    x = p.get_x() + p.get_width() / 2
    y = p.get_height()
    ax.annotate(percentage, (x, y), ha='center', va='center')
plt.show();

# Culpa consejo general
ax = sns.countplot(data = df, x = "culpaNoRenovarConsejoGeneral")
total = len(df)-df.culpaNoRenovarConsejoGeneral.isna().sum()
for p in ax.patches:
    percentage = f'{100 * p.get_height() / total:.1f}%\n'
    x = p.get_x() + p.get_width()/2
    y = p.get_height()
    ax.annotate(percentage, (x, y), ha='center', va='center')
plt.show();

ax = sns.countplot(data = df, x = "participGenerales19")
total = len(df)-df.participGenerales19.isna().sum()
for p in ax.patches:
    percentage = f'{100 * (p.get_height() / total):.1f}%\n'
    x = p.get_x() + p.get_width() / 2
    y = p.get_height()
    ax.annotate(percentage, (x, y), ha='center', va='center')
plt.show();

ax = sns.countplot(data = df, x = "recuerdoVotoPartido19")
total = len(df)-df.recuerdoVotoPartido19.isna().sum()
for p in ax.patches:
    print(p)
    percentage = f'{100 * p.get_height() / total:.1f}%\n'
    x = p.get_x() + p.get_width()/2 
    y = p.get_height()
    ax.annotate(percentage, (x, y), ha='center', va='center')
plt.show();

### Ideological
# masCercanoPartido, autodefIdeol1, autodefIdeal2, simpatiaHaciaPartido,
# intencionVotoPartido1, intencionVotoPartido2, posicionIdeolPropia

#Ideological position
sns.displot(x=df.posicionIdeolPropia, kind = "hist", discrete = True)
plt.tight_layout()
plt.show();

#Closest party
sns.countplot(x=df[df.masCercanoPartido.isin(partyGroups["partidoNacionalTodos"])].masCercanoPartido, 
              order = df[df.masCercanoPartido.isin(partyGroups["partidoNacionalTodos"])].masCercanoPartido.value_counts().index)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show();

#Simpatia hacia partido
sns.countplot(x=df[df.simpatiaHaciaPartido.isin(partyGroups["partidoNacionalTodos"])].simpatiaHaciaPartido, 
              order = df[df.simpatiaHaciaPartido.isin(partyGroups["partidoNacionalTodos"])].simpatiaHaciaPartido.value_counts().index)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show();

#Closest and simpatia
df2 = df[df.simpatiaHaciaPartido.isin(partyGroups["partidoNacionalTodos"])]
df2.simpatiaHaciaPartido = df2.simpatiaHaciaPartido.astype(partidoNacionalTodos)
df2.masCercanoPartido = df.masCercanoPartido.astype(partidoNacionalTodos)
g1 = sns.jointplot(data = df2, 
                   x = df2.simpatiaHaciaPartido,
                   y = df2.masCercanoPartido, 
                   kind = "hist")
g1.ax_joint.tick_params(axis='x', rotation=90)
plt.tight_layout()
plt.show();

#Self-definition
g1 =sns.jointplot(data=df, x="autodefIdeolo1", y="autodefIdeolo2", kind="hist")
g1.ax_joint.set_xticklabels(list(df.autodefIdeolo1.cat.categories), rotation = 90)
plt.tight_layout()
plt.show();

# Intencion voto...?


################################################################################################################################################################ 
### Relaitionships
df[contVars].corr(method = "spearman")


for var in df[catVars].columns:
      df[var] = df[var].cat.codes
corrMatrix = df[catVars].corr(method = "kendall")
sns.heatmap(matrix, annot = True)
plt.show();

corrMatrix.replace({1.0:np.nan}, inplace = True)
for col in corrMatrix.columns:
      for row in corrMatrix.index:
            if (corrMatrix.loc[row, col] < 0.2) & (corrMatrix.loc[row, col] > -0.2):
                  corrMatrix.loc[row, col] = np.nan
corrMatrix.dropna(how = "all")
corrMatrix = corrMatrix.reset_index().melt(id_vars = "index").dropna(subset="value").sort_values("value", ascending = False)
corrMatrix[corrMatrix.value.duplicated()]

#

