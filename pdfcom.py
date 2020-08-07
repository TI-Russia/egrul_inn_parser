from tabula import read_pdf
import pandas as pd


def get_n_key(l, n, p):
    return f"{l.lower().strip()}.{n.lower().strip()[0]}.{p.lower().strip()[0]}"


def getse(df, a, b):
    for i, r in df.iterrows():
        if a in str(r[0]):
            start = i
        if b in str(r[0]):
            end = i
            break
    return a, b


def get_info(pdfpath, k):

    df = read_pdf(
        pdfpath,
        # encoding='windows-1251',
        encoding='utf-8',
        lattice=True,
        pandas_options={'header': None},
        pages='all',
        multiple_tables=True
    )

    ogrn = "".join(df[0].values[0].astype(str))

    DF = df[1].append([df[2], df[3]])
    DF.reset_index(drop=True, inplace=True)
    DF = DF.replace({r'\r|\n': ' '}, regex=True).set_index(0)

    a = "Сведения о лице, имеющем право без доверенности действовать от имени юридического лица"

    b = "Сведения об учредителях (участниках) юридического лица"
    b2 = "Сведения об основном виде деятельности"
    b3 = "Сведения о записях, внесенных в Единый государственный реестр юридических лиц"

    if not b in DF.index:
        if b2 in DF.index:
            b = b2
        else:
            b = b3

    c = "Наименование"
    d = "Сведения о регистрации в качестве страхователя в территориальном органе Пенсионного фонда Российской Федерации"
    
    DF.fillna("", inplace=True)
    main_info = DF[c:d].set_index(1)

    pers_info = DF[a:b].set_index(1)
    
    info = {
        "id":k,
        "ogrn" : ogrn,
        "inn"  : main_info.loc["ИНН", 2],
        "full_name_egrul" : main_info.loc["Полное наименование", 2],
        "pers" : []
    }
    
    hms = ["Фамилия", "Имя", "Отчество", "ИНН", "ГРН и дата внесения в ЕГРЮЛ сведений о данном лице"]
    for hm in hms:
        if not hm in pers_info.index or len(pers_info.loc[hm]) != len(pers_info.loc["ИНН"]):
            print(pers_info)
            return info

    ppp = pers_info.loc[hms].drop_duplicates()

    lns = ppp.loc["Фамилия", 2]
    fns = ppp.loc["Имя", 2]
    pcs = ppp.loc["Отчество", 2]
    pinns = ppp.loc["ИНН", 2]
    grn_date = ppp.loc["ГРН и дата внесения в ЕГРЮЛ сведений о данном лице", 2]
    
    if ppp.shape[0]>5:
        prsns = list(zip(lns, fns, pcs, pinns, grn_date))
        
        info["pers"] = [
            {
                "lastname" : p[0].lower(),
                "firstname" : p[1].lower(),
                "patronymic" : p[2].lower(),
                "inn" : p[3].lower(),
                "grn" : re.search(r"\d{3,}", p[4]).group(),
                "date" : re.search(r"\d\d\.\d\d\.\d{4}", p[4]).group()
            } for p in prsns]

    else:
        
        info["pers"] = [
            {"lastname" : lns.lower(),
             "firstname" : fns.lower(),
             "patronymic" : pcs.lower(),
             "inn" : pinns.lower(),
             "grn" : re.search(r"\d{3,}", grn_date).group(),
             "date" : re.search(r"\d\d\.\d\d\.\d{4}", grn_date).group()
            }
        ]

    return info