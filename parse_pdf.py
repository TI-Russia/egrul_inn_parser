import pandas as pd
import os
import re
from tqdm import tqdm
from pdfcom import get_n_key, getse, get_info


argparser = argparse.ArgumentParser(description='Парсер ЕГРЮЛ')
requiredNamed = argparser.add_argument_group('required arguments')
requiredNamed.add_argument('--pdf_path', type=str, default="./dwnldpdf", help="путь к pdf-выпискам", required=True)

args = argparser.parse_args()

pdf_path = args.pdf_path

h = []

pdfs = os.listdir(pdf_path)

with tqdm(total=len(pdfs)) as pbar:
    for pdf_name in pdfs:
        
        pdf_id = re.sub(r"\.\w+$", "", pdf_name)
        
        try:
            h.append(get_info(os.path.join(pdf_path, pdf_name), pdf_id))
            pbar.update()
        except Exception as E:
            print(E, pdf_id, sep="\n")
                 
inn_pers = []

for inf in h:
    if inf["pers"]:
        for p in inf["pers"]:
            r = (
                inf["id"], 
                get_n_key(
                    p["lastname"],
                    p["firstname"],
                    p["patronymic"]
                ),
                p["firstname"].capitalize(),
                p["patronymic"].capitalize(),
                p["inn"], 
                p["date"]
            )
            inn_pers.append(r)
            
df_inn = pd.DataFrame(inn_pers, columns=[
    "legal_entity_id", 
    "name_key", 
    "name_egrul", 
    "patronymic_egrul", 
    "inn",
    "date"])

df_inn = df_inn.astype(str)
df_inn.to_csv("persons_egrul.csv", index=False)

legal_entities = pd.DataFrame(h).drop(columns=["pers"])
legal_entities.to_csv("legal_entities.csv", index=False)