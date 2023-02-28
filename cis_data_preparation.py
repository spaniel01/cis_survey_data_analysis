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
allCatVarMerge = {'No tiene criterio':np.nan, 'N.C.':np.nan, 'N.S.':np.nan, 'nan':np.nan}
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
                           '10 Derecha':10},
    "claseSocial":{'No cree en las clases' : np.nan, 'Otras':np.nan,  'No sabe, duda':np.nan,
    'Clase pobre' : 'Clase baja', 'A los/as de abajo' : 'Clase baja', 'Excluidos/as' : 'Clase baja', 
    'Clase trabajadora/obrera' : 'Clase media-baja', 'A la gente común' : 'Clase media-baja', 'Proletariado' : 'Clase media-baja'},
    "religion":{'Católico/a no practicante' : "Catholic", 
                'Creyente de otra religión' : "Other religion",
                'Católico/a practicante' : "Pract. Catholic",
                'Agnóstico/a (no niegan la existencia de Dios pero tampoco la descartan)' : "Agnostic",
                'Ateo/a (niegan la existencia de Dios)' : "Atheist",
                'Indiferente, no creyente' : "Indifferent"},
    "tamanoMunicipo" : {'10.001 a 50.000 habitantes': "10t to 50t", '100.001 a 400.000 habitantes':"100t to 400t",
                        '2.001 a 10.000 habitantes': "2t to 10t", 'Menos o igual a 2.000 habitantes':"< 2t",
                        '50.001 a 100.000 habitantes':"50t to 100t" , '400.001 a 1.000.000 habitantes':"400t to 1M",
                        'Más de 1.000.000 habitantes': "> 1M"},
    "ccaa" : {'Asturias (Principado de)':'Asturias',
       'Balears (Illes)' : 'Balears', 'Comunitat Valenciana' : 'Valencia',
       'Madrid (Comunidad de)' : 'Madrid',
       'Murcia (Región de)': 'Murcia', 'Navarra (Comunidad Foral de)':'Navarra', 
       'Rioja (La)': 'La Rioja', 'Ceuta (Ciudad Autónoma de)':'Ceuta',
       'Melilla (Ciudad Autónoma de)':'Melilla'},
    "preocupRusiaUcrania" : {'Nada preocupado/a': 'Nada', 'Poco preocupado/a':'Poco', 'Algo preocupado/a':'Algo', 'Bastante preocupado/a':'Bastante', 'Muy preocupado/a':'Muy'},
    "preocupCambioClimatico" : {'No cree que haya cambio climático':'No existe'},
}
for key, value in varsAndValuesToReplace.items():
    df[key].replace(value, inplace = True)

df.ingresosHogar = df.ingresosHogar.str[0:-3]

### Replacing string values for repeating name vars
liderValoracion = {'1 Muy mal':1, '10 Muy bien':10}
for var in df.columns:
    if "liderValoracion" in var:
        df[var].replace({'1 Muy mal':1, '10 Muy bien':10}, inplace = True)

df_gastar = [col for col in df if col.startswith('gastar')]
for var in df_gastar:
        df[var] = df[var].str.replace("Gastar ", "")
        df[var] = df[var].str.replace(" que ahora", "")

preocupVals = {'mal comportamiento de los/as políticos/as' : "comport. político",
       'Papel de los medios de comunicación y redes: desinformación, manipulación informativa, difusión de bulos' : "medios de comunic.",
       'problemas políticos en general': "política", 
       'corrupción y el fraude' : "corrupción",
       'crisis económica, los problemas de índole económica': "económica" ,
       'Gobierno y partidos o políticos/as concretos/as' : "actores polít. partic.", 
       'Aumento de la crispación social, revueltas sociales': "crispación social",
       'falta de acuerdos, unidad y capacidad de colaboración. Situación e inestabilidad política' : "colab. política",
       'funcionamiento de la democracia' : "democracia", 
       'problemas de índole social': "prob. sociales",
       'subida de tarifas energéticas' : "costes energéticos", 
       'ocupación de viviendas' : "ocupa. viviendas",
       'funcionamiento de los servicios públicos' : "servicios públicos", 
       'Lo que hacen los partidos políticos' : "partidos políticos", 
       'problemas de la agricultura, ganadería y pesca' : "agricul. etc.",
       'desigualdades, incluida la de género, las diferencias de clases, la pobreza' : "desigual. y pobreza",
       'crisis de valores' : "valores",
       'incertidumbres ante el futuro, la inseguridad y el miedo al futuro' : "el futuro",
       'Administración de Justicia' : 'admin. de Justicia',
       'inseguridad ciudadana' : "inseg. ciudadana", 
       'problemas relacionados con la juventud. Falta de apoyo y oportunidades a los/as jóvenes' : "probl. de los jovenes",
       'problemas relacionados con la calidad del empleo' : "calidad empleo",
       'violencia de género' : "viol. de género",
       'falta de confianza en los/las políticos/as y las instituciones' : "confianza sist. pol.",
       'peligros para la salud: COVID-19. coronavirus. Falta de recursos suficientes para hacer frente a la pandemia' : "COVID-19",
       'Guerra de Ucrania y Rusia' : "Ucrania y Rusia",
       'falta de servicios públicos. recortes' : "servicios públicos", 
       'subida de impuestos' : 'subida impuestos',
       'modelo productivo español. falta de inversión en industrias e I+D' : "invers. indust. + I+D",
       'Poca conciencia ciudadana (falta de civismo, de sentido espíritu cívico)' : "civismo",
       'Política exterior y relaciones internacionales. Papel de España en el marco internacional': "política exterior",
       'problemas relacionados con los/as autónomos/as' : "autónomos",
       'Falta claridad en las informaciones y medidas relacionadas con la COVID-19' : 'info. + medidas COVID-19',
       'España vaciada, la despoblación' : "España vaciada", 
       'independencia de Cataluña' : "indep. Cataluña",
       'Problemas psicológicos (preocupaciones, soledad, tristeza, desamparo, etc.)' : "Prob. psico.",
       "Desabastecimiento, falta de materias primas y suministros" : "desabastecimiento",
       "problemas relacionados con la mujer": "probl. de mujeres",
       "guerras en general" : "guerras",
       "terrorismo internacional": "terrorismo inter.",
       "Crisis con Marruecos. Fronteras de Ceuta y Melilla" : "Marruecos, C. y M.",
       "bajada de impuestos a los/as más ricos/as" : "bajar impuestos a ricos",
       "Aumento de odio, violencia y agresiones homófobas" : "homófobia",
       "Catástrofes naturales: el volcán de La Palma" : "volcán de La Palma",
       "preocupaciones y situaciones personales": "problemas personales", 
       "Los cambios de hábitos en mi vida cotidiana (no hacer vida normal, etc.)" : "cambios en vida cotidiana" }

for var in df.columns:
    if "probEsp" in var:  #"probPersonal"
        for word in ["La ", "El ", "Las ", "Los "]:
            df[var] = df[var].str.replace(word,"")
            df[var] = df[var].replace(preocupVals)

### Replacing different regional names of Podemos to Podemos 
podemos = ['Podemos', 'Unidas Podemos','En Comú Podem','En Común-Unidas Podemos']
df.replace(dict.fromkeys(podemos, "Podemos"), inplace = True)

### Ordering cats of ordinal vars

# Unqiue name vars
ordinalVarsUnique = {
    "culpaNoRenovarConsejoGeneral" : ['Ninguno de los dos', 'El PSOE', 'El PP', 'Los dos por igual'],
    "preocupCorona" : ['Nada', 'Poco', 'Regular', 'Bastante', 'Mucho'],
    "preocupCambioClimatico" : ['No existe', 'Nada', 'Regular', 'Bastante', 'Mucho'],
    "preocupRusiaUcrania" : ['Nada', 'Poco', 'Algo', 'Bastante', 'Muy'],
    "ingresosHogar" : df.ingresosHogar.unique()[[0, 5, 1, 4, 3, 2]],
    "escuela" : ['No, es analfabeto/a', 'No, pero sabe leer y escribir', 'Sí, ha ido a la escuela'],
    "practicaRelig" : ['Varias veces a la semana', 'Todos los domingos o festivos', 'Dos o tres veces al mes', 'Varias veces al año', 'Casi nunca', 'Nunca'],
    "tamanoMunicipo": df.tamanoMunicipo.unique()[[3,2,0,4,1, 5, 6]],
    "claseSocial" : df.claseSocial.unique()[[4,2,1,3,5]],
    "autodefIdeolo1": ['Comunista', 'Socialista', 'Ecologista', 'Progresista', 'Feminista', 'Socialdemócrata', 'Liberal', 'Demócrata cristiano/a', 'Nacionalista', 'Conservador/a', 'Otra respuesta', 'Apolítico/a'],
    "autodefIdeolo2": ['Comunista', 'Socialista', 'Ecologista', 'Progresista', 'Feminista', 'Socialdemócrata', 'Liberal', 'Demócrata cristiano/a', 'Nacionalista', 'Conservador/a', 'Otra respuesta', 'Apolítico/a']
    }
df.columns
for key, values in ordinalVarsUnique.items():
    df[key] = pd.Categorical(df[key], categories = values, ordered = True)

# Repeating vars
ordinalVarsRep = {
    "valor" : ['Muy mala','Mala', 'Regular', 'Buena',  'Muy buena'],
    "gastar" : ['mucho menos', 'menos','lo mismo', 'más', 'mucho más'],
    "liderConoce"  : ['No nonoce', 'Conoce'],
    "confianza"  : ['Ninguna confianza', 'Poca confianza', 'Bastante confianza', 'Mucha confianza'],
    "preperacion"  : ['Poco preparado', 'Muy mal preparado', 'Regular', 'Bastante bien preparado', 'Muy bien preparado'],
    "religion" : ['Pract. Catholic', 'Catholic', 'Other religion', 'Atheist' , 'Agnostic', 'Indifferent']
    }

df.religion.unique()

for varKeyword, categoryOrder in ordinalVarsRep.items():
    for varName in df.columns:
        if varKeyword in varName: 
            df[varName] = pd.Categorical(df[varName], 
                                         categories = ordinalVarsRep[varKeyword], 
                                         ordered=True)
            
### Var type conversion to integer, float and cat
df = df.astype({"edad":"Int64", 
           "probVoto":"Int64", 
           "posicionIdeolPropia":"Int64"})
for varName in df.columns:
    if "liderValoracion" in varName:
        df = df.astype({varName:"float"})
        df = df.astype({varName:"Int64"})

### Save changes    
df.to_pickle("cis_survey_data_revised.pkl")    

