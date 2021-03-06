from selenium.webdriver import Chrome
import os
import pandas as pd
import re
import time
from selenium.webdriver.chrome.options import Options
import random
from tqdm import tqdm
import argparse


# добавить логгер
# единый формат входной таблицы
# закрытие браузера при ошибке


def t_o():
    time.sleep(random.uniform(12.5,17.5))


argparser = argparse.ArgumentParser(description='Парсер ЕГРЮЛ')
argparser.add_argument('--pdf_path', type=str, default="./dwnldpdf", help="путь для сохранения pdf-выписок", required=False)
requiredNamed = argparser.add_argument_group('required arguments')
requiredNamed.add_argument('--data_path', type=str, help="таблица с данными о legalentity (название для поиска, id в базе)", required=True)
requiredNamed.add_argument('--driver', type=str, help="путь к chromedriver", required=True)

args = argparser.parse_args()

dwdirname = args.pdf_path

if not os.path.exists(dwdirname):
    os.mkdir(dwdirname)

absdwdirname = os.path.abspath(dwdirname)

chromeOptions = Options()
prefs = {"download.default_directory" : absdwdirname}
chromeOptions.add_experimental_option("prefs",prefs)

df = pd.read_csv(args.data_path, dtype=str)

driver = Chrome(executable_path=args.driver, options=chromeOptions)
driver.get("https://egrul.nalog.ru/index.html")
DATA = os.listdir(absdwdirname)

dfcl = df.drop_duplicates("name")

doneid = [re.sub("\.\w+$", "", name) for name in DATA]
dfcl = dfcl[~dfcl.id.isin(doneid)]


with tqdm(total=dfcl.shape[0]) as pbar:
    for i, r in dfcl.iterrows():
        
        name = r["name"]
        did = r["id"]
        
        search = driver.find_element_by_id('query')

        search.clear()
        search.send_keys(name)

        S = driver.find_element_by_id('btnSearch')

        S.click()

        t_o()

        ress = driver.find_elements_by_class_name("res-row")

        if ress:
            try:
                b = ress[0].find_element_by_tag_name("button")
                b.click()
                
                t_o()
                
                new_pdf = set(os.listdir(absdwdirname)) - set(DATA)
                
#                 print(new_pdf)
                new_one = list(new_pdf)[0]
                ext = re.search(r"\.\w+$", new_one).group()
                os.rename(
                    os.path.join(absdwdirname, new_one),
                    os.path.join(absdwdirname, did+ext)
                )
                
                DATA.append(str(did)+ext)
                
            except Exception as E:
                print(i, did, name, "CODE 1", E, sep = " | ")
                t_o()
                
        else:
            print(i, did, name, "CODE 0", sep = " | ")
            t_o()
        
        pbar.update()