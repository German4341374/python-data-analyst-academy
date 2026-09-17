"""Authoring source for the small, reviewed v0.1 curriculum. Output is versioned JSON."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
lessons = []
questions = []
challenges = []


def lesson(
    identity, title, module, topic, level, minutes, summary, objectives, sections, challenge_ids
):
    lessons.append(
        dict(
            id=identity,
            version=1,
            title=title,
            module=module,
            topic=topic,
            level=level,
            minutes=minutes,
            summary=summary,
            objectives=objectives,
            sections=[dict(title=t, text=b, code=c) for t, b, c in sections],
            challengeIds=challenge_ids,
        )
    )


def quiz(lesson_id, rows):
    topic = next(x["topic"] for x in lessons if x["id"] == lesson_id)
    for i, (prompt, options, correct, explanations, example) in enumerate(rows, 1):
        questions.append(
            dict(
                id=f"{lesson_id}-q{i}",
                version=1,
                lessonId=lesson_id,
                topic=topic,
                prompt=prompt,
                options=options,
                correct=correct,
                explanations=explanations,
                example=example,
            )
        )


def challenge(
    identity,
    title,
    lesson_id,
    library,
    kind,
    function,
    description,
    schema,
    output,
    starter,
    solution,
    hints,
    rows,
    hidden=None,
    ordering="Порядок строк входа сохраняется; индекс не проверяется.",
    difficulty="Easy",
):
    parent = next(x for x in lessons if x["id"] == lesson_id)
    challenges.append(
        dict(
            id=identity,
            version=1,
            title=title,
            lessonId=lesson_id,
            topic=parent["topic"],
            library=library,
            kind=kind,
            difficulty=difficulty,
            function=function,
            functionSignature=f"def {function}(df: pd.DataFrame)"
            if kind != "sql"
            else "SELECT ... FROM orders",
            description=description,
            inputSchema=schema,
            outputSchema=output,
            ordering=ordering,
            immutable=True,
            starterCode=starter,
            visibleDataset=rows,
            visibleTests=[
                "Тип, значения, колонки и порядок согласно контракту",
                "Входная таблица не изменена",
            ],
            hiddenDatasetGenerators=hidden
            or ["unseen-categories", "shuffled", "one-group", "decimals", "duplicates", "larger"],
            hints=hints,
            solution=solution,
            explanation=hints[-1],
            timeLimit=12,
            memoryLimit=256,
            rtol=1e-6,
            atol=1e-8,
        )
    )


lesson(
    "python-start",
    "Первая строка Python",
    "01 · Основы Python",
    "Python Basics",
    0,
    15,
    "От первого print() к выручке магазина. Никакого опыта программирования не нужно.",
    [
        "Запустить Python-код в редакторе",
        "Сохранить значение в переменной",
        "Различать число и текст",
    ],
    [
        (
            "Код — это последовательность инструкций",
            "Python выполняет строки сверху вниз. Команда print() показывает значение в панели вывода. Текст заключают в кавычки. Нажмите «Практика», чтобы запустить пример; устанавливать Python для этого урока не нужно.",
            'print("Привет, аналитик!")\nprint(3 * 250)',
        ),
        (
            "Назовём данные",
            "Переменная связывает понятное имя со значением. Знак = присваивает значение, а не сравнивает. price — цена одной единицы в евро; quantity — количество. Выручка до возвратов — их произведение. Комментарий после # не выполняется.",
            "price = 250\nquantity = 3\nrevenue = price * quantity\nprint(revenue)  # 750",
        ),
        (
            "Число или строка?",
            'int — целое число; float — число с дробной частью; str — текст; bool — True или False. Строка "250" не равна числу 250. type() помогает проверить тип; float() превращает корректную числовую строку в число. None означает отсутствие значения, а не ноль.',
            'raw_price = "19.90"\nprice = float(raw_price)\nprint(type(price))\nprint(f"Цена: {price:.2f} EUR")',
        ),
        (
            "Проверь понимание",
            "Измените quantity на 5 и предскажите выручку до запуска. Для имён используйте revenue_total, а не непонятное x. Python чувствителен к регистру: Revenue и revenue — разные имена.",
            "quantity = 5\nprice = 12.5\nprint(quantity * price)",
        ),
    ],
    ["conversion"],
)
quiz(
    "python-start",
    [
        (
            "Что напечатает print(3 * 250)?",
            ["3250", "750", "3 * 250"],
            1,
            [
                "Умножение чисел не склеивает их запись.",
                "Оператор * умножает два числа: 3 × 250 = 750.",
                "Кавычек нет: Python вычисляет выражение.",
            ],
            "print(3 * 250)  # 750",
        ),
        (
            "Что делает revenue = 100?",
            ["Сравнивает значения", "Печатает 100", "Сохраняет 100 под именем revenue"],
            2,
            [
                "Для сравнения используют ==.",
                "Для вывода нужен print().",
                "Один знак = присваивает значение имени.",
            ],
            "revenue = 100\nprint(revenue)",
        ),
        (
            "Как преобразовать строку '19.90' в число?",
            ["float('19.90')", "int('19.90')", "str('19.90')"],
            0,
            [
                "float понимает строковую запись дробного числа.",
                "int не разбирает строку с десятичной точкой: возникнет ValueError.",
                "str оставляет значение текстом.",
            ],
            "price = float('19.90')",
        ),
        (
            "Какой тип у True?",
            ["str", "bool", "None"],
            1,
            [
                "Строка 'True' требует кавычек.",
                "True и False — два булевых значения.",
                "None — отдельное значение отсутствия.",
            ],
            "print(type(True))  # bool",
        ),
        (
            "Что означает # в начале строки?",
            ["Комментарий", "Ошибка", "Команду вывода"],
            0,
            [
                "Комментарий объясняет код и не исполняется.",
                "Комментарии допустимы в Python.",
                "Для вывода вызывают print().",
            ],
            "# Revenue before returns\nrevenue = 3 * 250",
        ),
    ],
)

lesson(
    "functions",
    "Функции и надёжные расчёты",
    "01 · Основы Python",
    "Functions",
    1,
    25,
    "Пишем расчёт конверсии, который работает с новыми числами и не падает на нуле.",
    [
        "Передавать аргументы и возвращать результат",
        "Понимать if, циклы и отступы",
        "Обрабатывать ошибки данных",
    ],
    [
        (
            "Функция как повторяемый расчёт",
            "def объявляет функцию. Параметры получают значения при вызове. return возвращает результат вызывающему коду; print лишь показывает его. Четыре пробела отделяют тело функции.",
            "def conversion(purchases, visits):\n    if visits == 0:\n        return 0.0\n    return purchases / visits\n\nprint(conversion(12, 200))",
        ),
        (
            "Условия и коллекции",
            "if выполняет ветку только при истинном условии. Список хранит последовательность значений; словарь связывает ключ со значением. Цикл for повторяет действие. == сравнивает значения, is проверяет идентичность объекта: для чисел используйте ==, для None — is None.",
            'orders = [100, 200, 50]\ntotal = 0\nfor amount in orders:\n    total += amount\nprices = {"coffee": 4.5}\nprint(total, prices["coffee"])',
        ),
        (
            "Ошибки полезны",
            "ValueError означает, что значение не удалось преобразовать; TypeError — что операция не подходит для типа. Перехватывайте ожидаемую ошибку, а не скрывайте все ошибки через except без типа. Проверьте границы: ноль посещений, одна покупка, дробный результат.",
            'try:\n    price = float("unknown")\nexcept ValueError:\n    price = None\n\nif price is None:\n    print("Проверьте исходную цену")',
        ),
        (
            "Взвешенная конверсия",
            "Общая конверсия — сумма покупок / сумма посещений. Среднее дневных конверсий может быть неверным, если трафик по дням различается. В задаче df.visits.sum() возвращает сумму столбца visits. Мы изучим DataFrame подробнее в следующем разделе.",
            "visits = [10, 1000]\npurchases = [5, 50]\nprint(sum(purchases) / sum(visits))",
        ),
    ],
    ["conversion"],
)
quiz(
    "functions",
    [
        (
            "Что возвращает функция без return?",
            ["Последний результат", "None", "0"],
            1,
            [
                "Python не возвращает последнее выражение автоматически.",
                "Без return функция возвращает None.",
                "Ноль нужно вернуть явно.",
            ],
            "def f():\n    print(5)\nprint(f())  # 5, затем None",
        ),
        (
            "Как сравнить переменную value с None?",
            ["value is None", "value = None", "value > None"],
            0,
            [
                "None — одиночный объект, здесь уместно is.",
                "Присваивание не проверяет условие.",
                "У None нет такого порядка сравнения с числами.",
            ],
            "if value is None:\n    print('missing')",
        ),
        (
            "Что произойдёт при 10 / 0?",
            ["Получится 0", "Получится None", "ZeroDivisionError"],
            2,
            [
                "Деление на ноль не даёт ноль.",
                "Python не заменяет арифметические ошибки на None.",
                "Проверьте знаменатель перед делением.",
            ],
            "rate = purchases / visits if visits else 0.0",
        ),
        (
            "В первый день 1/2, во второй 9/98 покупок. Общая конверсия?",
            ["Среднее 50% и 9.18%", "10 / 100 = 10%", "50%"],
            1,
            [
                "Дни имеют разный трафик: простое среднее искажает общий результат.",
                "Сначала суммируем покупки и посещения, затем делим.",
                "Первый день не представляет весь период.",
            ],
            "rate = (1 + 9) / (2 + 98)",
        ),
        (
            "Какую ошибку ожидаем от float('unknown')?",
            ["KeyError", "ValueError", "IndexError"],
            1,
            [
                "KeyError связан с отсутствующим ключом.",
                "Тип str допустим, но значение не является числовой записью.",
                "IndexError связан с выходом за границы последовательности.",
            ],
            "try:\n    float('unknown')\nexcept ValueError:\n    print('invalid price')",
        ),
    ],
)

lesson(
    "pandas-intro",
    "Знакомство с DataFrame",
    "02 · pandas",
    "Pandas",
    4,
    20,
    "Читаем таблицу как аналитик: строки, колонки, типы и первые проверки.",
    ["Различать Series и DataFrame", "Выбирать колонки", "Проверять форму и типы данных"],
    [
        (
            "Таблица в Python",
            "DataFrame — таблица с именованными колонками. Series — одна колонка с индексом. Одна строка наших данных — позиция заказа; price измеряется в EUR за единицу, quantity — количество единиц. Это важно: выручка не равна сумме цен.",
            'import pandas as pd\n\ndf = pd.DataFrame({"city": ["Riga", "Tallinn"], "price": [20, 50], "quantity": [2, 1]})\nprint(df.head())',
        ),
        (
            "Начните с вопросов к данным",
            "shape сообщает (строки, колонки); dtypes — тип каждой колонки. head() показывает первые пять строк, но не доказывает качество всей таблицы. info() печатает краткое описание, describe() считает сводные числовые характеристики.",
            "print(df.shape)\nprint(df.dtypes)\ndf.info()\nprint(df.describe())",
        ),
        (
            "Одна колонка или таблица",
            "df['price'] — Series. df[['city', 'price']] — DataFrame, потому что передан список имён колонок. Имена чувствительны к пробелам и регистру. KeyError часто означает опечатку: посмотрите df.columns.",
            'prices = df["price"]\npreview = df[["city", "price"]].copy()\nprint(preview)',
        ),
        (
            "Загрузка и воспроизводимость",
            "В локальном Python read_csv читает CSV, read_excel — Excel с openpyxl. Указывайте разделитель и нужные колонки. В учебном runner таблица уже передана как df; файлы с вашего компьютера недоступны. В notebook выполните Restart & Run All: результат не должен зависеть от старых ячеек.",
            'df = pd.read_csv("orders.csv", usecols=["city", "price", "quantity"])\n# Excel: pd.read_excel("orders.xlsx", sheet_name="Orders")',
        ),
    ],
    ["select-columns"],
)
quiz(
    "pandas-intro",
    [
        (
            "Что возвращает df['price']?",
            ["DataFrame", "Series", "Список"],
            1,
            [
                "Для DataFrame передайте список имён: df[['price']].",
                "Выбор одной колонки строкой возвращает Series.",
                "Series хранит индекс и отличается от списка.",
            ],
            "series = df['price']\ntable = df[['price']]",
        ),
        (
            "У таблицы shape == (30, 4). Что это значит?",
            ["30 колонок, 4 строки", "30 строк, 4 колонки", "120 строк"],
            1,
            [
                "Порядок shape: сначала строки.",
                "Первое число — строки, второе — колонки.",
                "Произведение — число ячеек, не строк.",
            ],
            "rows, columns = df.shape",
        ),
        (
            "Как получить таблицу только city и price?",
            ["df['city', 'price']", "df[['city', 'price']]", "df['city'] + df['price']"],
            1,
            [
                "Кортеж внутри [] обычно ищет один составной ключ.",
                "Список имён выбирает несколько колонок.",
                "Это сложение Series, не выбор колонок.",
            ],
            "result = df[['city', 'price']].copy()",
        ),
        (
            "head() выглядит правильно. Все данные проверены?",
            ["Да", "Нет, это лишь первые строки"],
            1,
            [
                "Ошибки могут находиться за пределами preview.",
                "Проверьте dtypes, пропуски, диапазоны и дубликаты на всей таблице.",
            ],
            "print(df.isna().sum())\nprint(df.dtypes)",
        ),
        (
            "Возник KeyError: 'Price'. Что проверить сначала?",
            ["df.columns", "Перезапустить компьютер", "Умножить таблицу на 2"],
            0,
            [
                "Проверьте точное имя, регистр и пробелы в названии колонки.",
                "Перезапуск не исправит имя колонки.",
                "Арифметика не исправляет отсутствующий ключ.",
            ],
            "print(df.columns.tolist())",
        ),
    ],
)

lesson(
    "pandas-filtering",
    "Фильтрация данных",
    "02 · pandas",
    "Pandas",
    4,
    25,
    "От булевой маски к точному ответу на бизнес-вопрос. Объединяем условия без ошибок.",
    ["Построить булеву маску", "Объединить условия через & и |", "Сохранить исходные данные"],
    [
        (
            "Бизнес-вопрос прежде кода",
            "Найдём позиции заказов с ценой выше 100 EUR и количеством не меньше двух. Одна строка — позиция заказа, а не клиент. Сначала сформулируйте строгие границы: цена 100 не подходит, количество 2 подходит.",
            "price_limit = 100\nminimum_quantity = 2",
        ),
        (
            "Маска — ещё не таблица",
            "df['price'] > 100 возвращает Series из True и False, по одному значению на строку. Чтобы получить сами строки, передайте эту маску обратно в df. Внутри маски нет копии исходных данных.",
            'mask = df["price"] > 100\nresult = df.loc[mask]\nprint(result)',
        ),
        (
            "Два условия вместе",
            "Для Series используйте & (и), | (или), ~ (не). and и or предназначены для отдельных булевых значений. Каждое сравнение берите в скобки: без них Python иначе расставит приоритет операций.",
            'mask = (df["price"] > 100) & (df["quantity"] >= 2)\nresult = df.loc[mask].copy()',
        ),
        (
            "Честная проверка",
            "Хорошее решение выдерживает новый порядок строк, другой город и больше заказов. Не выбирайте строки по их номерам из примера. Если планируете менять результат, сделайте copy(); исходный DataFrame задачи должен сохраниться.",
            'def filter_orders(df):\n    mask = (df["price"] > 100) & (df["quantity"] >= 2)\n    return df.loc[mask].copy()',
        ),
    ],
    ["filter-orders", "sort-orders"],
)
quiz(
    "pandas-filtering",
    [
        (
            "Как получить строки df, где price > 100?",
            ["df['price'] > 100", "df[df['price'] > 100]", "df['price' > 100]"],
            1,
            [
                "Это булева Series, а не отфильтрованный DataFrame. Передайте маску внутрь df[...].",
                "Сравнение создаёт маску, а внешние [] выбирают строки, где она True.",
                "Здесь Python пытается сравнить текст 'price' с числом, а не значения колонки.",
            ],
            "mask = df['price'] > 100\nresult = df[mask]",
        ),
        (
            "Как объединить две маски условием И?",
            ["and", "& со скобками", "+"],
            1,
            [
                "and пытается получить одно булево значение всей Series и вызывает ошибку.",
                "& выполняет поэлементное И; скобки защищают приоритет сравнений.",
                "Сложение не выражает контракт фильтрации.",
            ],
            "df[(df['price'] > 100) & (df['quantity'] >= 2)]",
        ),
        (
            "Цена равна 100. Пройдёт ли строка условие price > 100?",
            ["Да", "Нет"],
            1,
            ["Строгое > не включает равенство.", "Для включения границы нужен >=."],
            "print(100 > 100)  # False",
        ),
        (
            "Как выбрать строки по позициям 0 и 2?",
            ["df.iloc[[0, 2]]", "df.loc[0:2]", "df[0, 2]"],
            0,
            [
                "iloc выбирает по целочисленным позициям, передаём список.",
                "loc работает с метками и срез включает границы; это другое условие.",
                "Так pandas ищет ключ колонки, а не две позиции строк.",
            ],
            "result = df.iloc[[0, 2]]",
        ),
        (
            "Почему df.iloc[[1, 3]] — плохое решение задачи о дорогих заказах?",
            [
                "iloc запрещён",
                "На другой таблице дорогие заказы будут в других строках",
                "Он всегда сортирует",
            ],
            1,
            [
                "iloc допустим, если задача именно о позициях.",
                "Решение должно зависеть от значений price, а не запомненных номеров.",
                "iloc сохраняет указанный порядок и не сортирует по цене.",
            ],
            "result = df.loc[df['price'] > 100]",
        ),
    ],
)

lesson(
    "groupby",
    "Выручка по городам",
    "02 · pandas",
    "Data Transformation",
    4,
    30,
    "Считаем revenue, группируем заказы и собираем воспроизводимый отчёт.",
    ["Создать вычисляемую колонку", "Использовать groupby и sum", "Задать однозначную сортировку"],
    [
        (
            "Что именно суммируем",
            "price — цена единицы, quantity — число единиц. Сначала вычисляем выручку каждой позиции: quantity × price. Сумма цен сама по себе не является выручкой. Данные примера синтетические, суммы — в EUR, налоги и возвраты не включены.",
            'orders = df.assign(revenue=df["quantity"] * df["price"])',
        ),
        (
            "Split → apply → combine",
            "groupby разбивает строки на группы, sum агрегирует значения, pandas соединяет результаты. as_index=False оставляет city обычной колонкой. Не перечисляйте города вручную: набор городов определяется входом.",
            'summary = orders.groupby("city", as_index=False)["revenue"].sum()',
        ),
        (
            "Контракт результата",
            "Верните ровно city и revenue. Сортировка: revenue по убыванию, при равенстве city по алфавиту. Индекс не важен. Небольшая погрешность float допустима, но округлять каждую позицию до целого нельзя. Повторяющиеся строки — отдельные позиции и учитываются.",
            'summary = summary.sort_values(\n    ["revenue", "city"], ascending=[False, True]\n).reset_index(drop=True)',
        ),
        (
            "Несколько метрик",
            "Именованная агрегация задаёт читаемые имена результата. size считает строки, count — непустые значения, nunique — разные значения. Для числа заказов используйте уникальный order_id, если заказ состоит из нескольких позиций.",
            'report = orders.groupby("city", as_index=False).agg(\n    revenue=("revenue", "sum"),\n    line_items=("revenue", "size"),\n)',
        ),
    ],
    ["revenue-city", "aov", "customer-summary"],
)
quiz(
    "groupby",
    [
        (
            "Как вычислить выручку строки?",
            ["price + quantity", "price * quantity", "price / quantity"],
            1,
            [
                "Цена и количество имеют разные единицы, складывать их бессмысленно.",
                "EUR/ед. × ед. = EUR.",
                "Деление не даёт выручку.",
            ],
            "df.assign(revenue=df.quantity * df.price)",
        ),
        (
            "Зачем as_index=False в groupby?",
            ["Чтобы city остался колонкой", "Чтобы убрать пропуски", "Чтобы запретить сортировку"],
            0,
            [
                "Ключ группировки будет обычной колонкой результата.",
                "Правила пропусков задаются отдельно.",
                "as_index не запрещает sort_values.",
            ],
            "df.groupby('city', as_index=False).revenue.sum()",
        ),
        (
            "Что делает count() в группе?",
            ["Считает все строки, включая NaN", "Считает непустые значения", "Суммирует числа"],
            1,
            [
                "Для всех строк используют size().",
                "count исключает пропуски в выбранной колонке.",
                "Сумму считает sum().",
            ],
            "df.groupby('city').price.count()",
        ),
        (
            "Как сортировать revenue вниз, city вверх?",
            ["ascending=True", "ascending=[False, True]", "ascending=[True, False]"],
            1,
            [
                "Один True сортирует обе колонки вверх.",
                "Флаги соответствуют порядку ['revenue', 'city'].",
                "Это противоположные направления.",
            ],
            "df.sort_values(['revenue', 'city'], ascending=[False, True])",
        ),
        (
            "Почему assign() удобен в функции задачи?",
            ["Возвращает новую таблицу", "Меняет df всегда", "Запрещает арифметику"],
            0,
            [
                "assign создаёт результат, сохраняя исходную таблицу.",
                "Прямое df['x'] = ... меняет вход; assign возвращает новый DataFrame.",
                "assign принимает вычисленные Series.",
            ],
            "result = df.assign(revenue=df.quantity * df.price)",
        ),
    ],
)

sales = [
    dict(city="Riga", quantity=2, price=120.0),
    dict(city="Tallinn", quantity=1, price=240.0),
    dict(city="Riga", quantity=3, price=80.0),
    dict(city="Vilnius", quantity=2, price=150.0),
    dict(city="Tallinn", quantity=4, price=25.0),
]
sales_schema = {
    "city": "string · город, без пропусков",
    "quantity": "integer > 0 · количество единиц",
    "price": "float >= 0 · цена единицы, EUR",
}
challenge(
    "filter-orders",
    "Отберите крупные покупки",
    "pandas-filtering",
    "pandas",
    "dataframe",
    "filter_orders",
    "Верните все строки, где price > 100 и quantity >= 2. Сохраните колонки и исходный порядок подходящих строк. Не изменяйте df. Повторяющиеся позиции учитываются отдельно.",
    sales_schema,
    "DataFrame: city, quantity, price",
    "def filter_orders(df):\n    # Постройте маску и верните подходящие строки\n    return df\n",
    "def filter_orders(df):\n    return df.loc[(df.price > 100) & (df.quantity >= 2)].copy()\n",
    [
        "Условие проверяется для каждой строки.",
        "Объедините сравнения оператором &; каждое заключите в скобки.",
        "Передайте маску в df.loc[mask] и верните копию выбранных строк.",
    ],
    sales,
)
challenge(
    "revenue-city",
    "Calculate revenue by city",
    "groupby",
    "pandas",
    "dataframe",
    "revenue_by_city",
    "Рассчитайте revenue = quantity × price для каждой позиции, затем общую выручку каждого города. Верните city, revenue. Сортируйте по revenue убывающе, при равенстве по city возрастающе. Повторяющиеся строки — отдельные позиции. Пропусков нет; df не изменяйте.",
    sales_schema,
    "DataFrame: city (string), revenue (numeric, EUR)",
    "def revenue_by_city(df):\n    # 1. Вычислите revenue\n    # 2. Сгруппируйте по city\n    # 3. Отсортируйте результат\n    return df\n",
    "def revenue_by_city(df):\n    return (df.assign(revenue=df.quantity * df.price)\n        .groupby('city', as_index=False).revenue.sum()\n        .sort_values(['revenue', 'city'], ascending=[False, True])\n        .reset_index(drop=True))\n",
    [
        "Сначала получите выручку каждой позиции, затем суммируйте внутри городов.",
        "Используйте assign(), groupby(..., as_index=False) и sum().",
        "groupby('city') использует все города входа. Затем sort_values(['revenue', 'city'], ascending=[False, True]).",
    ],
    sales,
    ordering="revenue ↓, при равенстве city ↑; индекс игнорируется.",
)
challenge(
    "select-columns",
    "Соберите preview каталога",
    "pandas-intro",
    "pandas",
    "dataframe",
    "select_columns",
    "Верните только колонки city и price, именно в таком порядке. Строки и значения сохраняются. Исходный df не изменяйте.",
    sales_schema,
    "DataFrame: city, price",
    "def select_columns(df):\n    return df\n",
    "def select_columns(df):\n    return df[['city', 'price']].copy()\n",
    [
        "Передайте имена нужных колонок списком.",
        "Для нескольких колонок нужны двойные квадратные скобки.",
        "df[['city', 'price']].copy() сохраняет порядок и отделяет результат.",
    ],
    sales,
    difficulty="Beginner",
)
challenge(
    "sort-orders",
    "Самые дорогие позиции",
    "pandas-filtering",
    "pandas",
    "dataframe",
    "sort_orders",
    "Отсортируйте все строки по price убывающе, при одинаковой цене — city по алфавиту. Сохраните все колонки. Не изменяйте вход.",
    sales_schema,
    "DataFrame: city, quantity, price",
    "def sort_orders(df):\n    return df\n",
    "def sort_orders(df):\n    return df.sort_values(['price', 'city'], ascending=[False, True])\n",
    [
        "Нужна сортировка, а не фильтрация.",
        "sort_values принимает список колонок и список направлений.",
        "Используйте ['price', 'city'] и ascending=[False, True].",
    ],
    sales,
    ordering="price ↓, city ↑; индекс игнорируется.",
)
challenge(
    "aov",
    "Средний чек без округления",
    "groupby",
    "pandas",
    "scalar",
    "average_order_value",
    "Здесь каждая строка — отдельный заказ из одного товара. Посчитайте общую выручку quantity × price, затем разделите на число заказов. Таблица непустая. Не округляйте результат и не изменяйте df.",
    sales_schema,
    "float · средний чек, EUR",
    "def average_order_value(df):\n    return 0.0\n",
    "def average_order_value(df):\n    return float((df.quantity * df.price).sum() / len(df))\n",
    [
        "Сумма цен не учитывает количество.",
        "Посчитайте sum(quantity * price).",
        "Разделите общую выручку на len(df). Это AOV только при одной строке на заказ.",
    ],
    sales,
)
challenge(
    "conversion",
    "Конверсия магазина",
    "functions",
    "Python",
    "scalar",
    "conversion_rate",
    "Верните общую конверсию как долю от 0 до 1: сумма purchases / сумма visits. Если сумма visits равна 0, верните 0.0. Одна строка — день; целые значения неотрицательные, purchases <= visits. df не изменяйте.",
    {"visits": "integer >= 0 · посещения за день", "purchases": "integer >= 0 · покупки за день"},
    "float · доля покупателей",
    "def conversion_rate(df):\n    visits = df['visits'].sum()\n    purchases = df['purchases'].sum()\n    # Обработайте нулевой знаменатель\n    return 0.0\n",
    "def conversion_rate(df):\n    visits = df.visits.sum()\n    return float(df.purchases.sum() / visits) if visits else 0.0\n",
    [
        "Нужна общая доля, а не среднее дневных долей.",
        "Сначала суммируйте visits и purchases.",
        "Если visits == 0, верните 0.0; иначе purchases / visits.",
    ],
    [dict(visits=10, purchases=5), dict(visits=1000, purchases=50), dict(visits=0, purchases=0)],
    hidden=["shuffled", "one-group", "larger", "duplicates"],
)


challenge(
    "customer-summary",
    "Покупатели и повторные заказы",
    "groupby",
    "pandas",
    "dataframe",
    "customer_summary",
    "Одна строка — позиция заказа. Для каждого customer_id верните количество уникальных order_id в orders и сумму quantity × price в revenue. Сортируйте customer_id по возрастанию. Строки не удаляйте, df не изменяйте.",
    {
        "order_id": "integer · заказ; может встречаться в нескольких позициях",
        "customer_id": "integer · покупатель",
        "quantity": "integer > 0 · количество",
        "price": "float >= 0 · EUR за единицу",
    },
    "DataFrame: customer_id, orders, revenue",
    "def customer_summary(df):\n    return df\n",
    "def customer_summary(df):\n    return (df.assign(revenue=df.quantity * df.price)\n        .groupby('customer_id', as_index=False)\n        .agg(orders=('order_id', 'nunique'), revenue=('revenue', 'sum'))\n        .sort_values('customer_id'))\n",
    [
        "У одного заказа может быть несколько позиций.",
        "Для заказов нужен nunique, для выручки sum.",
        "Создайте revenue через assign и используйте именованную агрегацию по customer_id.",
    ],
    [
        {"order_id": 1, "customer_id": 10, "quantity": 2, "price": 20.0},
        {"order_id": 1, "customer_id": 10, "quantity": 1, "price": 15.0},
        {"order_id": 2, "customer_id": 20, "quantity": 3, "price": 12.0},
        {"order_id": 3, "customer_id": 10, "quantity": 2, "price": 10.0},
    ],
    hidden=["shuffled", "one-group", "decimals", "duplicates", "larger"],
    ordering="customer_id ↑; индекс игнорируется.",
)


def write():
    from curriculum import extend

    projects = extend(lesson, quiz, challenge, sales, sales_schema)
    challenge(
        "python-revenue",
        "Первая выручка на Python",
        "python-start",
        "Python",
        "scalar",
        "",
        "В редактор уже переданы две переменные: price — цена единицы, quantity — количество. Сохраните их произведение в переменную result. Выведите результат через print(result). Не задавайте price и quantity вручную: при проверке они изменятся.",
        {"price": "float >= 0 · цена единицы, EUR", "quantity": "integer > 0 · количество"},
        "result: число · price × quantity",
        "# price и quantity уже доступны\nresult = 0\nprint(result)\n",
        "result = price * quantity\nprint(result)\n",
        [
            "Выручка равна цене одной единицы, умноженной на количество.",
            "Умножение в Python записывается символом *.",
            "Напишите result = price * quantity, затем print(result).",
        ],
        [{"price": 12.5, "quantity": 4}],
        hidden=["different-numbers", "zero-price", "decimals"],
        difficulty="Beginner",
    )
    challenges[-1]["functionSignature"] = "result = ..."
    lessons[0]["challengeIds"] = ["python-revenue"]
    for current in lessons:
        current["module"] = (
            current["module"]
            .replace("02 · pandas", "03 · pandas")
            .replace("03 · NumPy", "02 · NumPy")
        )
    lessons.sort(key=lambda current: current["module"])
    next(c for c in challenges if c["id"] == "conversion")["hiddenDatasetGenerators"] += [
        "zero-visits",
        "different-funnel",
    ]
    exams = [
        {
            "id": identity,
            "title": title,
            "questionIds": [q["id"] for q in questions if q["lessonId"] in lesson_ids],
            "challengeIds": task_ids,
        }
        for identity, title, lesson_ids, task_ids in [
            ("python-check", "Python", ["python-start", "functions"], ["conversion"]),
            ("numpy-check", "NumPy", ["numpy"], ["numpy-mask"]),
            (
                "pandas-check",
                "pandas",
                ["pandas-intro", "pandas-filtering", "groupby"],
                ["filter-orders", "revenue-city"],
            ),
            (
                "cleaning-check",
                "Очистка",
                ["cleaning", "joins-dates"],
                ["clean-cities", "fill-missing"],
            ),
            ("plot-check", "Графики", ["visualization"], ["monthly-plot"]),
            ("stats-check", "Статистика", ["eda", "statistics"], ["median"]),
            ("sql-check", "SQL", ["sql"], ["sql-revenue"]),
        ]
    ]
    path = ROOT / "content" / "catalog.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        json.dumps(
            dict(
                version="0.1.0",
                lessons=lessons,
                questions=questions,
                challenges=challenges,
                projects=projects,
                exams=exams,
            ),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    write()
