from tabula import read_pdf
import pandas as pd
import re
import json
from collections import Counter


class InfIter:
    def __iter__(self):
        self.num = 1
        return self

    def __next__(self):
        num = self.num
        self.num += 1
        return num


def get_n_key(l, n, p):

    N = ""
    if n:
        N = f"{n[0]}."

    P = ""
    if p:
        P = f"{p[0]}."

    return f"{N}{P}{l}".lower()


def getse(df, a, b):
    for i, r in df.iterrows():
        if a in str(r[0]):
            start = i
        if b in str(r[0]):
            end = i
            break
    return a, b


n = iter(InfIter())


def get_pers_inf(DF):

    persons = []

    head_data_str = "Сведения о лице, имеющем право без доверенности действовать от имени юридического лица" 
    person_date_str = "ГРН и дата внесения в ЕГРЮЛ сведений о данном лице"
    position_str = "Должность"
    grbg = [
    "ГРН и дата внесения в ЕГРЮЛ записи, содержащей указанные сведения", 
    "ГРН и дата внесения в ЕГРЮЛ записи об исправлении технической ошибки в указанных сведениях"
    ]

    if head_data_str in DF[0].values:
        a = DF.set_index(0).loc[head_data_str, "f"]
        pers_info = DF.set_index("f")[a:a+1].set_index(1, drop=False).dropna()
        pers_info[0] = pers_info[0].astype(float)
        Counter(pers_info.index)
        d = Counter(pers_info.index)
        
        if d.get(person_date_str, None) == d.get(position_str, None):
            if d[position_str] == 1:
                det_a = pers_info.loc[person_date_str, 0]
                det_b = pers_info.loc[position_str, 0]
                boundaries = [(det_a, det_b)]
            else:
                det_a = pers_info.loc[person_date_str, 0].values
                det_b = pers_info.loc[position_str, 0].values
                boundaries = list(zip(det_a, det_b))
            for pers_det in boundaries:
                start, end = pers_det
                actual_one = pers_info.set_index(0)[start:end].set_index(1)[2].str.lower()
                actual_one_clean = actual_one.loc[~actual_one.index.isin(grbg)].to_json(force_ascii=False)
                person_json = json.loads(actual_one_clean)
                
                # person_json["grn"] = re.search(r"\d{3,}", person_json[person_date_str]).group()
                person_json["date"] = re.search(r"\d\d\.\d\d\.\d{4}", person_json[person_date_str]).group()

                pj = {

                "lastname" : person_json.get("Фамилия", "").strip(),
                "firstname" : person_json.get("Имя", "").strip(),
                "patronymic" : person_json.get("Отчество", "").strip(),
                "inn" : person_json.get("ИНН", ""),
                "date" : person_json["date"]

                }
                
                
                persons.append(pj)

    return persons


def flag(x):

    if re.search(r"^[А-ЯЁа-яё\s\(\),\.]+$", str(x)):
        return next(n)


def get_block(DF, sss):

    if sss in DF[0].values:

        m = DF.set_index(0).loc[sss, "f"]
        main_info = DF.set_index("f")[m:m+1].set_index(1, drop=True).dropna()
        main_info_j = main_info.loc[main_info.index.drop_duplicates(keep=False)][2].to_json(force_ascii=False)
        main_info_j = json.loads(main_info_j)

        return main_info_j
    return {}


def get_info(pdfpath, k):

    df = read_pdf(
        pdfpath,
        # encoding='windows-1251',
        encoding='utf-8',
        lattice=True,
        pandas_options={'header' : None, 'dtype' : str},
        pages='all',
        multiple_tables=True
    )

    DF = df[1].append([df[2], df[3], df[4]])
    DF.reset_index(drop=True, inplace=True)
    DF = DF.replace({r'\r|\n': ' '}, regex=True)#.set_index(0)

    DF["f"] = DF[0].apply(flag)
    
    info = {
        "id":k,
        "ogrn" : get_block(DF, "Сведения о регистрации").get("ОГРН", ""),
        "inn"  : get_block(DF, "Сведения об учете в налоговом органе").get("ИНН", ""),
        "full_name_egrul" : get_block(DF, "Наименование").get("Полное наименование", ""),
        "pers" : get_pers_inf(DF)
    }

    return info