import pandas as pd
import sqlalchemy
import json
import argparse
from pdfcom import get_n_key


argparser = argparse.ArgumentParser(description='Поиск персон из выписок ЕГРЮЛ в базе')
requiredNamed = argparser.add_argument_group('required arguments')
requiredNamed.add_argument('--persons_egrul', type=str, help="таблица с данными о персонах из ЕГРЮЛ", required=True)

args = argparser.parse_args()

params = json.loads(open("params.json").read())

engine = sqlalchemy.create_engine(params["engine"])

query_persons = params["query_persons"]
df = pd.read_sql_query(query_persons, engine)

df["name_key"] = df.apply(lambda x: get_n_key(
    x["family_name"], 
    x["name"], 
    x["patronymic"]
), axis=1)

            
df = df.astype(str).drop_duplicates()
df = df.astype(str).drop_duplicates(["legal_entity_id", "name_key"])

pers_inn = pd.read_csv(args.persons_egrul, dtype=str)
pers_inn = pd.merge(pers_inn, df, how="inner", on=["legal_entity_id", "name_key"])#.drop_duplicates()

pers_inn.date = pd.to_datetime(pers_inn.date, format="%d.%m.%Y")

for i, g in pers_inn.groupby("legal_entity_id"):
    G = g.sort_values("date")
    if G.shape[0]>1:
        G.reset_index(inplace=True)
        for I, R in G[:-1].iterrows():
            pers_inn.loc[R["index"], "end_date"] = G.iloc[I+1].date
            
pers_inn.drop(columns=["name_key"], inplace=True)

pers_inn = pers_inn.astype(str).replace("NaT", "")
pers_inn.to_csv("persons_egrul_clean_done.csv", index=False)