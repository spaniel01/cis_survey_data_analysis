# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

df = pd.read_spss("3384.sav")

### Eliminate irrelevant cols
filter_col = [col for col in df if not col.startswith('IA')]
df = df[filter_col]
df.drop(["ESTUDIO", "REGISTRO", "CUES", "TIPO_TEL", "ENTREV"],
        axis = "columns", 
        inplace = True)

### Create lookUpTable for meaning of varNames from separate file
varName = []
varContent = []
with open("varNameDesc") as f:
    lines = f.readlines()
varNames = [varName for varName in lines if "/IA" not in varName]
for line in varNames:
    line = line.strip().replace("/", "").split(" ", 1)
    varName.append(line[0])
    varContent.append(line[1][1:-1])
lookUpTable = pd.DataFrame(zip(varName, varContent), columns = ["varName", "varContent"])
lookUpTable["edited"] = False
lookUpTable.set_index("varName", inplace = True, drop = False)

### Rename unique name vars

# Dict of vars to rename
renameDictUnqiueVars = {
    "TAMUNI":"tamanoMunicipo",
    "P0":"nacionalidad",
    "P1":"preocupCorona",
    "P2":"preocupRusiaUcrania",
    "P3":"preocupCambioClimatico",
    "ECOPER":"valorSitEcoPersonal",
    "ECOESP":"valorSitEcoEspana",
    "PREFPTE":"presidentePreferido",
    "PROBVOTO":"probVoto",
    "P11":"actuacRepresentPoliticos",
    "P12":"paQueElecciones",
    "INTENCIONG":"intencionVotoPartido",
    "INTENCIONGALTER":"intencionVotoPartido2",
    "SIMPATIA":"simpatiaHaciaPartido",
    "ESCIDEOL":"posicionIdeolPropia",
    "CONFIANZAPTE":"confianzaEnPresidente",
    "CONFIANZAOPOSIC":"confianzaEnLiderOposic",
    "P20": "preperacionPresidente",
    "P21": "preperacionOposicion",
    "P22": "culpaNoRenovarConsejoGeneral",
    "PARTICIPACIONG":"participGenerales19",
    "RECUVOTOG":"recuerdoVotoPartido19",
    "CERCANIA":"masCercanoPartido",
    "P25":"autodefIdeolo1",
    "P25_A":"autodefIdeolo2",
    "NIVELESTENTREV":"maxEstudios",
    "PRACTICARELIG6":"practicaRelig",
    "ECIVIL":"estadoCivil",
    "SITLAB":"situacionLaboral",
    "RELALAB":"situacionProfesional",
    "CNO11":"ocupacion",
    "INGRESHOG": "ingresosHogar",
    "CLASESOCIAL":"claseSocial",
    "INTENCIONGR":"mod_intencionVotoPartido",
    "INTENCIONGALTERR":"mod_intencionVotoPartido2",
    "SIMPATIAR":"mod_simpatiaHaciaPartido",
    "VOTOSIMG":"mod_votoPlusSimpatia",
    "RECUVOTOGR":"mod_recuerdoVotoPartido",
    "RECUERDO" : "mod_recuerdoVotoPartido19",
    "CERCANIAR":"mod_masCercanoPartido"}

# Rename cols with "unique" names
df.rename(renameDictUnqiueVars,
    axis = "columns",
    inplace = True)

# Register change in lookUpTable
for i in renameDictUnqiueVars.keys():
    if i in lookUpTable["varName"]:
        lookUpTable.loc[i, "edited"] = True

### Rename vars which start with the same letters 

# Dict of first parts of var names starting with same letters to be renamed
renameDictRepeatNameVars = {
    "P6":"gastar", 
    "PESPANNA":"probEsp", 
    "PPERSONAL":"probPersonal",
    "LIDERESCONOCE":"liderConoce",
    "VALORALIDERES":"liderValoracion"
    }

# Rename cols which repeatedly start with same val
for key, value in renameDictRepeatNameVars.items():
    for colName in df.columns.values:
        if key in colName:
            df.rename({colName:value + lookUpTable.loc[colName, "varContent"].title().replace(" ", "")},
                      axis = "columns",
                      inplace = True)

# Register change in lookUpTable
for key in renameDictRepeatNameVars.keys():
    for var in lookUpTable["varName"]:
        if key in var:
            lookUpTable.loc[var, "edited"] = True
     
### Remove cap on single word vars (which have not been changed so far)
for var in lookUpTable.loc[lookUpTable["edited"] == False, "varName"].values:
    df.rename({var: 
               var.lower()},
              axis = "columns",
              inplace = True)

# Register change
lookUpTable.loc[lookUpTable["edited"] == False, "edited"] = True
    
### Convert categorical vars containing strings to string type and remove "(No leer) " from strings
dfTypes = df.dtypes
for var in dfTypes.index.values:
    if dfTypes[var] == "category" and type(df[var][0]) == str:
        df = df.astype({var:"str"})
        counter = 0
        for value in df[var]:
            if "(NO LEER) " in value:
                df.iloc[counter, df.columns.get_loc(var)] = df.iloc[counter, df.columns.get_loc(var)].replace("(NO LEER) ", "")  
            counter += 1

### Replacing NAN type categories with np.nan for all vars
allCatVarMerge = {'No tiene criterio':np.nan, 'N.C.':np.nan, 'N.S.':np.nan}
df.replace(allCatVarMerge, inplace = True)

### Replacing string values for unique vars
varsAndValuesToReplace = {
    "probVoto":{'0 Con toda seguridad no iría a votar':0,
                '10 Con toda seguridad, iría a votar':10},
    "actuacRepresentPoliticos":{'Que los representantes políticos reflejen al máximo los deseos y preferencias de la ciudadanía':'que hagan lo que quiere la gente',
                                'Que los representantes políticos se mantengan fieles y defiendan las propuestas políticas de su partido y que busquen qu':'que actuen fiel a sus partidos'},
    "paQueElecciones":{'Que los candidatos presenten a los electores sus programas y propuestas para la siguiente legislatura':'que presenten sus programas electorales',
                       'Que los candidatos respondan o rindan cuentas por sus acciones y decisiones en la legislatura que termina':'que rinden cuentas por sus acciones'},
    "posicionIdeolPropia":{'1 Izquierda':1,
                           '10 Derecha':10}
}
for key, value in varsAndValuesToReplace.items():
    df[key].replace(value, inplace = True)

### Replacing string values for repeating name vars
liderValoracion = {'1 Muy mal':1, '10 Muy bien':10}
for var in df.columns:
    if "liderValoracion" in var:
        df[var].replace({'1 Muy mal':1, '10 Muy bien':10}, inplace = True)

### Replacing different regional names of Podemos to Podemos 
podemos = ['Podemos', 'Unidas Podemos','En Comú Podem','En Común-Unidas Podemos']
df.replace(dict.fromkeys(podemos, "Podemos"), inplace = True)

### Ordering cats of ordinal vars

# Unqiue name vars
ordinalVarsUnique = {
    "culpaNoRenovarConsejoGeneral" : ['Ninguno de los dos', 'El PSOE', 'El PP', 'Los dos por igual'],
    "preocupCorona" : ['Nada', 'Poco', 'Regular', 'Bastante', 'Mucho'],
    "preocupCambioClimatico" : ['No cree que haya cambio climático', 'Nada', 'Regular', 'Bastante', 'Mucho'],
    "preocupRusiaUcrania" : ['Nada preocupado/a', 'Poco preocupado/a', 'Algo preocupado/a', 'Bastante preocupado/a', 'Muy preocupado/a']
    }

for key, values in ordinalVarsUnique.items():
    df[key] = pd.Categorical(df[key], categories = values, ordered = True)
    

# Repeating vars
ordinalVarsRep = {
    "valor" : ['Muy mala','Mala', 'Regular', 'Buena',  'Muy buena'],
    "gastar" : ['Gastar mucho menos que ahora', 'Gastar menos','Gastar lo mismo que ahora', 'Gastar más', 'Gastar mucho más que ahora'],
    "liderConoce"  : ['No nonoce', 'Conoce'],
    "confianza"  : ['Ninguna confianza', 'Poca confianza', 'Bastante confianza', 'Mucha confianza'],
    "preperacion"  : ['Poco preparado', 'Muy mal preparado', 'Regular', 'Bastante bien preparado', 'Muy bien preparado']}

for varKeyword, categoryOrder in ordinalVarsRep.items():
    for varName in df.columns:
        if varKeyword in varName: 
            df[varName] = pd.Categorical(df[varName], 
                                         categories = ordinalVarsRep[varKeyword], 
                                         ordered=True)
            
### Var type conversion to integer and float
df = df.astype({"edad":"Int64", 
           "probVoto":"Int64", 
           "posicionIdeolPropia":"Int64"})
for varName in df.columns:
    if "liderValoracion" in varName:
        df = df.astype({varName:"float"})
        df = df.astype({varName:"Int64"})

### Save changes    
df.to_pickle("cis_survey_data_revised.pkl")    


print(pd.DataFrame(df["maxEstudios"].unique() ))
    


"escuela" : ['No, es analfabeto/a', 'No, pero sabe leer y escribir', 'Sí, ha ido a la escuela']
