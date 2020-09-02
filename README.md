# egrul_inn_parser

Работа парсера состоит из двух этапов и нескольких шагов, включающих обновление базы при помощи команд в Django.

### Этап 1

**Получение таблицы с наименованиями юридических лиц**

1. Необходимо запустить скрипт `new_old_legal_entity.py`, который находит юридические лица в графе `positions`. Для работы необходимо наличие в папке со скриптом налицие файлов `params.json` (параметры для запросов в базу) и `forms.csv` (допустимые организационные формы по которым будет производиться поиск). Как результат создается таблица `new_old_legal_entity.csv` с полями `"id"` (id секции),`"position"`, `"clean_position"`. ВАЖНО! Таблица вида "один ко многим": разным `id` может соответствовать одинаковые `clean_position`. 

2. Обновить в базе таблицу с юридическими лицами командой `legal_entities_search` с таблицей `new_old_legal_entity.csv`.


### Этап 2

**Парсим егрюл**

1. Выгружаем из базы табицу с юридическими лицами, которые необходимо спарсить с ЕГРЮЛ. Обязательные поля: `id`, `name`.

2. Запускаем скрипт `egrul_parser.py`, в качестве аргумента передаём таблицу с юрлицами. В результате получаем папку с pdf-выписками, названия формата %id%.pdf

3. Парсим скачанные выписки скриптом `parse_pdf.py`. Получаем  две таблицы: `persons_egrul.csv`, содержащую данные о _"Сведения о лицах, имеющих право без доверенности действовать от имени юридического лица"_, и `legal_entities.csv` с подробной информацией о самих юридических лицах.

4. С помощью скрипта `clean_person_info.py` ищем соответствие между персонами, которые уже есть в базе и которые найдены в выписках. Результат — таблица `persons_egul_done.csv`. Для работы необходимо наличие в папке со скриптом файлов `params.json` (параметры для запросов в базу).

5. Обновляем информацию о персонах, юридических лицах и в модели `PersonLegalPosition` командой `load_egrul` с аргументами `persons_egul_done.csv` и `legal_entities.csv`.
