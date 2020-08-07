import pandas as pd
import sqlalchemy
import numpy as np
import re
import json


# Поиск новых юридических лиц в существующих position.

# В папке с кодом обязательно долны находиться файлы:
# - params.json для доступа к базе
# - forms.csv для поиска релевантных организационных форм


def get_relivant(s):
#     s = s.lower()
    res = re.search(fr"({forms})\s.+$", s)
    if res:
        RES = res.group()
        
        if res.group(1) in no_abr.keys():
            RES = re.sub(fr"^{res.group(1)}", no_abr[res.group(1)], RES)
            
        RES = re.sub("'", "\"", RES)
        RES = re.sub("\"\"", "\"", RES)
        RES = re.sub("\s\"", " «", RES)
        RES = re.sub("\"", "»", RES)
        
        if "»" in RES and not "«" in RES:
            RES = RES.replace("»", "")
            
        RES = re.sub("(»)", r"\1†", RES).split("†")[0]
        
        RES = re.sub("\s+", r" ", RES)
            
        return RES


params = json.loads(open("params.json").read())

engine = sqlalchemy.create_engine(params["engine"])

query_sections = params["query_sections"]
df = pd.read_sql_query(query_sections, engine)

query_legalentities = params["query_legalentities"]
df_le = pd.read_sql_query(query_legalentities, engine)

df_forms = pd.read_csv("forms.csv")

a1 = df_forms[["Полное наименование", "Аббревиатура вар 1"]]
a1.set_index("Аббревиатура вар 1", inplace=True)
no_abr = json.loads(a1.to_json(force_ascii=False))["Полное наименование"]

a2 = df_forms[["Полное наименование", "Аббревиатура вар 2"]]
a2 = a2.dropna()
a2.set_index("Аббревиатура вар 2", inplace=True)

a3 = df_forms[["Полное наименование", "Полное наименование РП"]]
a3.set_index("Полное наименование РП", inplace=True)

no_abr.update(json.loads(a2.to_json(force_ascii=False))["Полное наименование"])
no_abr.update(json.loads(a3.to_json(force_ascii=False))["Полное наименование"])

forms = "|".join(pd.Series(np.concatenate(df_forms.values)).dropna().values)#.lower()
KKK = '|'.join(df_forms['Полное наименование РП'].values)
    
df["clean_position"] = df.position.apply(get_relivant)
df_fin = df[~df.clean_position.isna()]

df_fin.to_csv("new_old_legal_entity.csv", index=False)