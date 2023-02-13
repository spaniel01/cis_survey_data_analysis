# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


df = pd.read_spss("3384.sav")
#print(df.dtypes)

# Eliminate irrelevant cols
filter_col = [col for col in df if not col.startswith('IA')]
df = df[filter_col]
df.drop(["ESTUDIO", "REGISTRO", "CUES", "TIPO_TEL", "ENTREV"],
        axis = "columns", 
        inplace = True)

# Create loopUpTable for meaning of varNames
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
for i in renameDictUnqiueVars.keys():
    if i in lookUpTable["varName"]:
        lookUpTable.loc[i, "edited"] = True

renameDictRepeatNameVars = {"P6":"gastar", 
        "PESPANNA":"probEsp", 
        "PPERSONAL":"probPersonal",
        "LIDERESCONOCE":"liderConoce",
        "VALORALIDERES":"liderValoracion"}
for key in renameDictRepeatNameVars.keys():
    for var in lookUpTable["varName"]:
        if key in var:
            lookUpTable.loc[var, "edited"] = True

# Rename cols with "unique" names
df.rename(renameDictUnqiueVars,
    axis = "columns",
    inplace = True)

# Rename cols which repeatedly start with same val
for key, value in renameDictRepeatNameVars.items():
    for colName in df.columns.values:
        if key in colName:
            df.rename({colName:value + lookUpTable.loc[colName, "varContent"].title().replace(" ", "")},
                      axis = "columns",
                      inplace = True)

# Remove cap on single word vars (which have not been changed so far)
for var in lookUpTable.loc[lookUpTable["edited"] == False, "varName"].values:
    df.rename({var: 
               var.lower()},
              axis = "columns",
              inplace = True)

### Convert all to string and remove "No leer"
dfTypes = df.dtypes
for var in dfTypes.index.values:
    if dfTypes[var] == "category" and type(df[var][0]) == str:
        df = df.astype({var:"str"})
        counter = 0
        for value in df[var]:
            if "(NO LEER) " in value:
                df.iloc[counter, df.columns.get_loc(var)] = df.iloc[counter, df.columns.get_loc(var)].replace("(NO LEER) ", "")  
            counter += 1

### Replacing NA type categories with NA FOR ALL VARS!!!
allCatVarMerge = {'No tiene criterio':np.nan, 'N.C.':np.nan, 'N.S.':np.nan}
df.replace(allCatVarMerge, inplace = True)

### Replacing values for unique vars
varsAndValuesToReplace = {"probVoto":{'0 Con toda seguridad no iría a votar':0,
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

### Replacing values for repeating name vars
liderValoracion = {'1 Muy mal':1, '10 Muy bien':10}
for var in df.columns:
    if "liderValoracion" in var:
        df[var].replace({'1 Muy mal':1, '10 Muy bien':10}, inplace = True)


### Ordering cats of ordinal vars

# Unqiue name vars
df.culpaNoRenovarConsejoGeneral = pd.Categorical(df.culpaNoRenovarConsejoGeneral, categories = ['Ninguno de los dos', 'El PSOE', 'El PP',
        'Los dos por igual'], ordered=True)
df.preocupCorona = pd.Categorical(df.preocupCorona, categories = ['Nada', 'Poco', 'Regular', 'Bastante', 'Mucho'], ordered=True)
df.preocupCambioClimatico = pd.Categorical(df.preocupCambioClimatico, categories = ['No cree que haya cambio climático', 'Nada', 'Regular', 'Bastante', 'Mucho'], ordered=True)
df.preocupRusiaUcrania = pd.Categorical(df.preocupRusiaUcrania, categories = ['Nada preocupado/a', 'Poco preocupado/a', 'Algo preocupado/a', 
                 'Bastante preocupado/a', 'Muy preocupado/a'], ordered=True)

#Sort party names
#NATIONAL: 'PP', 'Ciudadanos', 'Ninguno', nan, 'PSOE', 'Otro partido', 'VOX', 
#        'Más País', # Errejon
#        'IU', 'Más Madrid'
#        'SUMAR', # Yolanda
#PODEMOS: 'Podemos', 'Unidas Podemos', 'En Comú Podem','En Común-Unidas Podemos'
#REGIONAL: 'Compromís', 'Andalucía Por Sí', 'Teruel Existe', 'CUP', 'MÉS (PSM-Entesa)', 'ERC',
#           'Nueva Canarias','CC-PNC', 'BNG', 'PRC', 'JxCat', 'EH Bildu', 'PdeCat', 'EAJ-PNV', 'Geroa Bai', 'UPN'
# OTHER: 'PACMA', 'Partido Libertario','Los Verdes', 'PCPE','Partido Feminista de España', 'Por un Mundo más Justo (M+J)'

# Rename
podemos = ['Podemos', 'Unidas Podemos','En Comú Podem','En Común-Unidas Podemos']
partidoNacionalTodos = ['Podemos', 'PP', 'Ciudadanos', 'Ninguno', np.nan, 'PSOE', 'Otro partido', 'VOX', 'Más País', 'IU', 'Más Madrid', 'SUMAR']
partidoNacionalVIP = ['Podemos','PP', 'Ciudadanos', 'Ninguno', np.nan, 'PSOE', 'Otro partido', 'VOX']
catalan = ['CUP', 'ERC', 'JxCat', 'PdeCat']
regionalVipSocios = ['ERC', 'PRC', 'PNV', 'EH Bildu']
regionalTodos = ['Compromís', 'Andalucía Por Sí', 'Teruel Existe', 'CUP', 'MÉS (PSM-Entesa)', 'ERC', 'Nueva Canarias','CC-PNC', 'BNG', 'PRC', 'JxCat', 'EH Bildu', 'PdeCat', 'EAJ-PNV', 'Geroa Bai', 'UPN']


  
lookUp2 = pd.DataFrame(df.dtypes)   
df.to_pickle("cis_survey_data_revised.pkl")    
