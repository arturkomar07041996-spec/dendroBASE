import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import pandas as pd
import folium
import threading
import tempfile
import webbrowser
from datetime import datetime

# ==================== НАЛАДЫ БАЗЫ ДАДЗЕНЫХ ====================
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '12345678',
    'host': 'localhost',
    'port': '5433'
}

# ==================== СПІСЫ ДЛЯ ВЫПАДАЮЧЫХ МЕНЮ ====================
PORODA_LIST = [
    "А", "АЖ", "АРЧ", "АЙВ", "БР", "ББР", "Б", "ББ", "БП", "БК",
    "БКР", "БКК", "БЯР", "БРК", "БУК", "БХТ", "БХ", "БЗН", "В", "ВШ",
    "ЧШ", "Г", "ГШ", "Д", "ДЛ", "ДН", "ДЧ", "ДК", "ДС", "ДР", "Е",
    "ЕЕ", "ЕК", "ЕЖ", "Ж", "ИВЛ", "ИВБ", "ИВД", "ИВО", "ИВШ", "ИВК",
    "ИЛ", "ИР", "КЗ", "КЛ", "КЛП", "КЛО", "КЛБ", "КЛЯ", "КШ", "КЛН",
    "К", "КС", "КРС", "КРЛ", "Л", "ЛСБ", "ЛЖ", "ЛП", "ЛПК", "ЛПМ",
    "ЛЩ", "МЛ", "МЖX", "МЖ", "ОБЛ", "ОЛX", "ОЛС", "ОЛЧ", "ОС", "ОРХ",
    "ОРГ", "ОРМ", "П", "ПБ", "ПП", "Р", "РК", "С", "СБ", "СВ", "СВД",
    "СИР", "СЛ", "АЛ", "СМР", "СПР", "Т", "ТБ", "ТК", "ТЧ", "ТД",
    "ТУЗ", "ЧР", "ЧРМ", "Ш", "ШП", "Я", "ЯБ"
]

PORODA_DICT = {
    "А": "Акация белая", "АЖ": "Акация желтая", "АРЧ": "Арония чернопл.",
    "АЙВ": "Айва", "БР": "Берест", "ББР": "Барбарис", "Б": "Береза",
    "ББ": "Береза бородав.", "БП": "Береза пушистая", "БК": "Береза каменная",
    "БКР": "Береза карел.", "БКК": "Береза карлик.", "БЯР": "Боярышник",
    "БРК": "Бересклет", "БУК": "Бук", "БХТ": "Бархат", "БХ": "Бархат амур.",
    "БЗН": "Бузина", "В": "Вяз", "ВШ": "Вишня", "ЧШ": "Черешня", "Г": "Граб",
    "ГШ": "Груша", "Д": "Дуб", "ДЛ": "Дуб летний", "ДН": "Дуб низкоств.",
    "ДЧ": "Дуб черешч.", "ДК": "Дуб красный", "ДС": "Дуб скальный", "ДР": "Дерен",
    "Е": "Ель", "ЕЕ": "Ель европ.", "ЕК": "Ель колючая", "ЕЖ": "Ежевика",
    "Ж": "Жимолость", "ИВЛ": "Ива ломкая", "ИВБ": "Ива белая", "ИВД": "Ива древовид.",
    "ИВО": "Ива остролист.", "ИВШ": "Ива шаровидн.", "ИВК": "Ива кустарник.",
    "ИЛ": "Ильм", "ИР": "Ирга", "КЗ": "Кизильник", "КЛ": "Клен",
    "КЛП": "Клен полевой", "КЛО": "Клен остролист.", "КЛБ": "Клен белый",
    "КЛЯ": "Клен ясенелист.", "КШ": "Каштан", "КЛН": "Калина", "К": "Кедр",
    "КС": "Кедр сибирский", "КРС": "Крушина слабит.", "КРЛ": "Крушина ломкая",
    "Л": "Лиственница", "ЛСБ": "Лиственница сиб.", "ЛЖ": "Лжетсуга",
    "ЛП": "Липа", "ЛПК": "Липа крупнолист.", "ЛПМ": "Липа мелколист.",
    "ЛЩ": "Лещина", "МЛ": "Малина", "МЖX": "Можжевельник", "МЖ": "Можжевельник об.",
    "ОБЛ": "Облепиха", "ОЛX": "Ольха", "ОЛС": "Ольха серая", "ОЛЧ": "Ольха черная",
    "ОС": "Осина", "ОРХ": "Орех", "ОРГ": "Орех грецкий", "ОРМ": "Орех манчжур.",
    "П": "Пихта", "ПБ": "Пихта белая", "ПП": "Пузыреплодник", "Р": "Рябина",
    "РК": "Ракитник", "С": "Сосна", "СБ": "Сосна Банкса", "СВ": "Сосна Веймут.",
    "СВД": "Свидина", "СИР": "Сирень", "СЛ": "Слива", "АЛ": "Алыча",
    "СМР": "Смородина", "СПР": "Спирея", "Т": "Тополь", "ТБ": "Тополь белый",
    "ТК": "Тополь канад.", "ТЧ": "Тополь черный", "ТД": "Тополь душист.",
    "ТУЗ": "Туя западная", "ЧР": "Черемуха", "ЧРМ": "Черемуха Маака",
    "Ш": "Шелковица", "ШП": "Шиповник", "Я": "Ясень", "ЯБ": "Яблоня"
}

GEO_ZONA_LIST = ["Евразиатская таежная", "Европейская широколиственно-лесная"]
GEO_PODZONA_LIST = ["Дубово-темнохвойных подтаежных лесов", "Грабово-дубово-темнохвойных подтаежных лесов",
                    "Широколиственно-сосновых лесов"]
GEO_OKRUG_LIST = ["Западно-Двинский", "Оршанско-Могилевский", "Ошмянско-Минский", "Березинско-Предполесский",
                  "Неманско-Предполесский", "Бугско-Полесский", "Полесско-Приднепровский"]
GEO_RAJON_LIST = ["Браславский", "Дисненский", "Полоцкий", "Суражско-Лучесский", "Березинско-Друтский", "Беседский",
                  "Оршанско-Приднепровский", "Сожский", "Верхнеберезинский", "Минско-Борисовский", "Нарочано-Вилейский",
                  "Центральноберезинский", "Центральнопредполесский", "Чечерско-Приднепровский", "Беловежский",
                  "Волковысско-Новогрудский", "Западнопредполесский", "Налибокский", "Неманский", "Бугско-Припятский",
                  "Пинско-Припятский", "Гомельско-Приднепровский", "Припятско-Мозырский", "Центрально-Полесский",
                  "Южнополесский"]
DOSTUPNOST_LIST = ["Открытый доступ", "Ограниченный доступ", "По запросу"]
TIP_OBRAZTSOV_LIST = ["Керны", "Спилы", "Диски"]

# Спіс драўняных парод для выпадаючага спісу (на лаціне)
DREVESNAYA_PORODA_LIST = [
    "Pinus sylvestris L.",
    "Picea abies (L.) H.Karst.",
    "Quercus robur L.",
    "Betula pendula Roth",
    "Betula pubescens Ehrh.",
    "Populus tremula L.",
    "Alnus glutinosa (L.) Gaertn.",
    "Alnus incana (L.) Moench",
    "Tilia cordata Mill.",
    "Acer platanoides L.",
    "Fraxinus excelsior L.",
    "Carpinus betulus L.",
    "Ulmus glabra Huds.",
    "Ulmus laevis Pall.",
    "Salix alba L.",
    "Salix caprea L.",
    "Padus avium Mill.",
    "Sorbus aucuparia L.",
    "Malus sylvestris Mill.",
    "Pyrus pyraster (L.) Burgsd."
]

# Спіс тыпаў лесу для аўтадапаўнення
TIP_LESA_LIST = [
    "Баг-м", "Баг-мп", "Баг", "Сосняк", "Ельнік", "Дуброва", "Черноольховый",
    "Березняк", "Осинник", "Липняк", "Кленовник", "Пойменный", "Суходольный"
]


class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cur = self.conn.cursor()
            return True
        except Exception as e:
            messagebox.showerror("Памылка падключэння", f"Не атрымалася падключыцца да БД:\n{e}")
            return False

    def disconnect(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def get_all_probes(self):
        self.cur.execute("SELECT n_probnoy_ploshchadi FROM title ORDER BY n_probnoy_ploshchadi")
        return [row[0] for row in self.cur.fetchall()]

    def get_probe_info(self, probe_name):
        self.cur.execute("SELECT * FROM title WHERE n_probnoy_ploshchadi = %s", (probe_name,))
        row = self.cur.fetchone()
        if row:
            col_names = [desc[0] for desc in self.cur.description]
            return dict(zip(col_names, row))
        return None

    def get_all_probes_with_coords(self):
        self.cur.execute("""
            SELECT n_probnoy_ploshchadi, shirota_grd, dolgota_grd, glavnaya_poroda, 
                   posledniy_god, pervyy_god, kolichestvo_derevev_v_shkale_sht
            FROM title 
            WHERE shirota_grd IS NOT NULL AND dolgota_grd IS NOT NULL
            ORDER BY n_probnoy_ploshchadi
        """)
        return self.cur.fetchall()

    def get_all_title_columns(self):
        self.cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'title' 
            ORDER BY ordinal_position
        """)
        return [row[0] for row in self.cur.fetchall()]

    def add_title(self, data):
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ','.join(['%s'] * len(columns))
        set_clause = ','.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'n_probnoy_ploshchadi'])

        sql = f"""
            INSERT INTO title ({','.join(columns)}) 
            VALUES ({placeholders}) 
            ON CONFLICT (n_probnoy_ploshchadi) DO UPDATE SET {set_clause}
        """
        self.cur.execute(sql, values)

    def update_geometry(self, probe_name):
        try:
            self.cur.execute("""
                UPDATE title 
                SET geom = ST_SetSRID(ST_MakePoint(COALESCE(dolgota_grd, 0), COALESCE(shirota_grd, 0)), 4326)
                WHERE n_probnoy_ploshchadi = %s 
                  AND shirota_grd IS NOT NULL 
                  AND dolgota_grd IS NOT NULL
                  AND shirota_grd != 0 
                  AND dolgota_grd != 0
            """, (probe_name,))
            self.commit()
            return self.cur.rowcount
        except Exception as e:
            self.rollback()
            return 0

    def update_geometry_all(self):
        try:
            self.cur.execute("""
                UPDATE title 
                SET geom = ST_SetSRID(ST_MakePoint(dolgota_grd, shirota_grd), 4326)
                WHERE shirota_grd IS NOT NULL 
                  AND dolgota_grd IS NOT NULL
                  AND shirota_grd != 0 
                  AND dolgota_grd != 0
            """)
            self.commit()
            return self.cur.rowcount
        except Exception as e:
            self.rollback()
            return 0

    def check_postgis(self):
        try:
            self.cur.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis')")
            return self.cur.fetchone()[0]
        except:
            return False

    def execute_sql_query(self, query):
        try:
            self.cur.execute(query)
            if self.cur.description:
                rows = self.cur.fetchall()
                col_names = [desc[0] for desc in self.cur.description]
                return {'success': True, 'columns': col_names, 'rows': rows, 'rowcount': len(rows)}
            else:
                self.commit()
                return {'success': True, 'rowcount': self.cur.rowcount,
                        'message': f"Закранута {self.cur.rowcount} радкоў"}
        except Exception as e:
            self.rollback()
            return {'success': False, 'error': str(e)}

    def get_filtered_data(self, filters):
        """Атрымаць адфільтраваныя даныя для ўкладкі Фільтры"""
        conditions = []
        params = []

        # drevesnaya_poroda
        if filters.get('drevesnaya_poroda'):
            conditions.append("t.drevesnaya_poroda = %s")
            params.append(filters['drevesnaya_poroda'])

        # geobotanicheskaya_zona
        if filters.get('geobotanicheskaya_zona'):
            conditions.append("t.geobotanicheskaya_zona = %s")
            params.append(filters['geobotanicheskaya_zona'])

        # geobotanicheskaya_podzona
        if filters.get('geobotanicheskaya_podzona'):
            conditions.append("t.geobotanicheskaya_podzona = %s")
            params.append(filters['geobotanicheskaya_podzona'])

        # geobotanicheskij_okrug
        if filters.get('geobotanicheskij_okrug'):
            conditions.append("t.geobotanicheskij_okrug = %s")
            params.append(filters['geobotanicheskij_okrug'])

        # geobotanicheskij_rajon
        if filters.get('geobotanicheskij_rajon'):
            conditions.append("t.geobotanicheskij_rajon = %s")
            params.append(filters['geobotanicheskij_rajon'])

        # tip_lesa (пошук па ключавым словам)
        if filters.get('tip_lesa_keyword'):
            conditions.append("t.tip_lesa ILIKE %s")
            params.append(f"%{filters['tip_lesa_keyword']}%")

        # Год фільтр
        if filters.get('year_from'):
            conditions.append("c.year >= %s")
            params.append(filters['year_from'])
        if filters.get('year_to'):
            conditions.append("c.year <= %s")
            params.append(filters['year_to'])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Вызначаем, якія калонкі CRN выбраны
        crn_columns = filters.get('crn_columns', ['raw', 'std', 'res', 'ars'])
        crn_select = ', '.join([f"c.{col}" for col in crn_columns if col in ['raw', 'std', 'res', 'ars']])

        query = f"""
            SELECT 
                t.n_probnoy_ploshchadi as probe_name,
                t.glavnaya_poroda as species,
                t.drevesnaya_poroda as wood_species,
                t.geobotanicheskaya_zona as geo_zona,
                t.geobotanicheskaya_podzona as geo_podzona,
                t.geobotanicheskij_okrug as geo_okrug,
                t.geobotanicheskij_rajon as geo_rajon,
                t.tip_lesa as forest_type,
                c.year,
                {crn_select}
            FROM title t
            JOIN crn c ON t.n_probnoy_ploshchadi = c.n_probnoy_ploshchadi
            WHERE {where_clause}
            ORDER BY t.n_probnoy_ploshchadi, c.year
        """

        self.cur.execute(query, params)
        rows = self.cur.fetchall()
        col_names = [desc[0] for desc in self.cur.description]
        return col_names, rows

    def get_unique_drevesnaya_poroda(self):
        """Атрымаць унікальныя значэнні drevesnaya_poroda з БД"""
        self.cur.execute("""
            SELECT DISTINCT drevesnaya_poroda 
            FROM title 
            WHERE drevesnaya_poroda IS NOT NULL AND drevesnaya_poroda != ''
            ORDER BY drevesnaya_poroda
        """)
        return [row[0] for row in self.cur.fetchall()]

    def add_crn_batch(self, probe_name, data_list):
        for row in data_list:
            self.cur.execute("""
                INSERT INTO crn (n_probnoy_ploshchadi, year, num, raw, std, res, ars)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (n_probnoy_ploshchadi, year) DO UPDATE SET
                    num = EXCLUDED.num, raw = EXCLUDED.raw, std = EXCLUDED.std,
                    res = EXCLUDED.res, ars = EXCLUDED.ars
            """, (probe_name, row[0], row[1], row[2], row[3], row[4], row[5]))

    def add_crn_data(self, probe_name, year, num=None, raw=None, std=None, res=None, ars=None):
        self.cur.execute("""
            INSERT INTO crn (n_probnoy_ploshchadi, year, num, raw, std, res, ars)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (n_probnoy_ploshchadi, year) DO UPDATE SET
                num = EXCLUDED.num, raw = EXCLUDED.raw, std = EXCLUDED.std,
                res = EXCLUDED.res, ars = EXCLUDED.ars
        """, (probe_name, year, num, raw, std, res, ars))

    def add_series_batch(self, probe_name, data_list):
        for row in data_list:
            self.cur.execute("""
                INSERT INTO series (n_probnoy_ploshchadi, year, series_name, value)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (n_probnoy_ploshchadi, series_name, year) DO UPDATE SET value = EXCLUDED.value
            """, (probe_name, row[0], row[1], row[2]))

    def add_series_data(self, probe_name, year, series_name, value):
        self.cur.execute("""
            INSERT INTO series (n_probnoy_ploshchadi, year, series_name, value)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (n_probnoy_ploshchadi, series_name, year) DO UPDATE SET value = EXCLUDED.value
        """, (probe_name, year, series_name, value))

    def delete_crn_data(self, probe_name, year):
        self.cur.execute("DELETE FROM crn WHERE n_probnoy_ploshchadi = %s AND year = %s", (probe_name, year))

    def delete_series_data(self, probe_name, series_name, year):
        self.cur.execute("DELETE FROM series WHERE n_probnoy_ploshchadi = %s AND series_name = %s AND year = %s",
                         (probe_name, series_name, year))

    def get_crn_data(self, probe_name, year_from=None, year_to=None):
        if year_from and year_to:
            self.cur.execute("""
                SELECT year, num, raw, std, res, ars 
                FROM crn 
                WHERE n_probnoy_ploshchadi = %s AND year BETWEEN %s AND %s
                ORDER BY year
            """, (probe_name, year_from, year_to))
        else:
            self.cur.execute("""
                SELECT year, num, raw, std, res, ars 
                FROM crn 
                WHERE n_probnoy_ploshchadi = %s
                ORDER BY year
            """, (probe_name,))
        return self.cur.fetchall()

    def get_series_matrix(self, probe_name, year_from=None, year_to=None):
        if year_from and year_to:
            self.cur.execute("""
                SELECT year, series_name, value 
                FROM series 
                WHERE n_probnoy_ploshchadi = %s AND year BETWEEN %s AND %s
                ORDER BY year, series_name
            """, (probe_name, year_from, year_to))
        else:
            self.cur.execute("""
                SELECT year, series_name, value 
                FROM series 
                WHERE n_probnoy_ploshchadi = %s
                ORDER BY year, series_name
            """, (probe_name,))

        data = self.cur.fetchall()
        if not data:
            return None, None

        df = pd.DataFrame(data, columns=['year', 'series_name', 'value'])
        matrix = df.pivot(index='year', columns='series_name', values='value')
        matrix = matrix.sort_index()
        matrix = matrix.reindex(sorted(matrix.columns), axis=1)
        return matrix, df['series_name'].unique().tolist()

    def get_series_list(self, probe_name, year_from=None, year_to=None, series_filter=None):
        if year_from and year_to:
            self.cur.execute("""
                SELECT year, series_name, value 
                FROM series 
                WHERE n_probnoy_ploshchadi = %s AND year BETWEEN %s AND %s
                ORDER BY year, series_name
            """, (probe_name, year_from, year_to))
        else:
            self.cur.execute("""
                SELECT year, series_name, value 
                FROM series 
                WHERE n_probnoy_ploshchadi = %s
                ORDER BY year, series_name
            """, (probe_name,))

        data = self.cur.fetchall()
        if series_filter:
            data = [row for row in data if series_filter.lower() in row[1].lower()]
        return data

    def search_probes(self, search_text):
        self.cur.execute("""
            SELECT n_probnoy_ploshchadi 
            FROM title 
            WHERE n_probnoy_ploshchadi ILIKE %s
            ORDER BY n_probnoy_ploshchadi
        """, (f'%{search_text}%',))
        return [row[0] for row in self.cur.fetchall()]


class AddProbeDialog:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Дадаць новую пробную плошчу")
        self.dialog.geometry("1300x800")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.create_widgets()

    def show_poroda_help(self):
        help_dialog = tk.Toplevel(self.dialog)
        help_dialog.title("Даведка: Расшыфроўка пародаў")
        help_dialog.geometry("450x500")
        help_dialog.transient(self.dialog)
        help_dialog.grab_set()

        canvas = tk.Canvas(help_dialog)
        scrollbar = ttk.Scrollbar(help_dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(scrollable_frame, text="Расшыфроўка скарачэнняў пародаў", font=("Arial", 12, "bold")).pack(pady=10)
        tree = ttk.Treeview(scrollable_frame, columns=("code", "name"), show="headings", height=25)
        tree.heading("code", text="Скарачэнне")
        tree.heading("name", text="Поўная назва")
        tree.column("code", width=100)
        tree.column("name", width=300)
        for code, name in sorted(PORODA_DICT.items()):
            tree.insert("", tk.END, values=(code, name))
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Button(scrollable_frame, text="Закрыць", command=help_dialog.destroy).pack(pady=10)

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        self.entries = {}

        columns = [ttk.Frame(scrollable_frame) for _ in range(3)]
        for col in columns:
            col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        fields = [
            ("n_probnoy_ploshchadi", "N пробной площади:", "entry"),
            ("shirota_grd", "Широта,грд:", "entry"),
            ("dolgota_grd", "Долгота, грд:", "entry"),
            ("vysota_nad_u_m", "Высота над у.м.:", "entry"),
            ("strana", "Страна:", "entry"),
            ("oblast", "Область:", "entry"),
            ("rayon", "Район:", "entry"),
            ("blizhajshij_naselennyj_punkt", "Ближайший населенный пункт:", "entry"),
            ("leskhoz", "Лесхоз:", "entry"),
            ("lesnichestvo", "Лесничество:", "entry"),
            ("kvartal", "Квартал:", "entry"),
            ("vydel", "Выдел:", "entry"),
            ("god_lesoustrojstva", "Год лесоустройства:", "entry"),
            ("geobotanicheskaya_zona", "Геоботаническая зона:", "combobox", GEO_ZONA_LIST),
            ("geobotanicheskaya_podzona", "Геоботаническая подзона:", "combobox", GEO_PODZONA_LIST),
            ("geobotanicheskij_okrug", "Геоботанический округ:", "combobox", GEO_OKRUG_LIST),
            ("geobotanicheskij_rajon", "Геоботанический район:", "combobox", GEO_RAJON_LIST),
            ("tip_lesa", "Тип леса:", "entry"),
            ("tum", "ТУМ:", "entry"),
            ("glavnaya_poroda", "Главная порода:", "combobox", PORODA_LIST),
            ("koef_sostava", "Коэфф. состава:", "entry"),
            ("sostav_drevoj", "Состав:", "entry"),
            ("vozrast", "Возраст средний:", "entry"),
            ("predely_variacii", "Пределы вариации:", "entry"),
            ("klass_vozrasta", "Класс возраста:", "entry"),
            ("srednyaya_vysota_m", "Средняя высота, м:", "entry"),
            ("srednij_diametr_sm", "Средний диаметр, см:", "entry"),
            ("polnota", "Полнота:", "entry"),
            ("zapas_kub_m", "Запас, куб.м.:", "entry"),
            ("associaciya", "Ассоциация:", "entry"),
            ("landshaft", "Ландшафт:", "entry"),
            ("urochishche", "Урочище:", "entry"),
            ("forma_relefa", "Форма рельефа:", "entry"),
            ("pochva", "Почва:", "entry"),
            ("kategoriya_zemel", "Категория земель:", "entry"),
            ("proiskhozhdenie", "Происхождение:", "entry"),
            ("ploshchad_vydela", "Площадь выдела:", "entry"),
            ("kategoriya_zashchitnosti", "Категория защитности:", "entry"),
            ("bonitet", "Бонитет:", "entry"),
            ("podrost", "Подрост:", "entry"),
            ("podlesok", "Подлесок:", "entry"),
            ("vozdejstvie", "Воздействие:", "entry"),
            ("dopolnitelnaya_informaciya", "Дополнительная информация:", "text"),
            ("n_dendrokhronologicheskoj_shkaly", "N дендрохронологической шкалы:", "entry"),
            ("drevesnaya_poroda", "Древесная порода:", "entry"),
            ("data_otbora_obraztsov", "Дата отбора образцов:", "entry"),
            ("data_predostavleniya_v_bazu_dannykh", "Дата предоставления в базу данных:", "entry"),
            ("tip_obraztsov", "Тип образцов:", "combobox", TIP_OBRAZTSOV_LIST),
            ("otbor_obraztsov_avtor", "Отбор образцов (автор):", "entry"),
            ("izmerenie_obraztsov_avtor", "Измерение образцов (автор):", "entry"),
            ("verifikatsiya_avtor", "Верификация (автор):", "entry"),
            ("standartizatsiya_avtor", "Стандартизация (автор):", "entry"),
            ("kolichestvo_derevev_v_shkale_sht", "Количество деревьев в шкале, шт:", "entry"),
            ("protyazhennost_shkaly_let", "Протяженность шкалы, лет:", "entry"),
            ("pervyy_god", "Первый год:", "entry"),
            ("posledniy_god", "Последний год:", "entry"),
            ("mezhserialnyj_kof_korrelyatsii", "Межсериальный коэффициент корреляции:", "entry"),
            ("srednij_kof_chuvstvitelnosti", "Средний коэффициент чувствительности:", "entry"),
            ("dostupnost", "Доступность:", "combobox", DOSTUPNOST_LIST),
            ("opisanie", "Описание:", "text")
        ]

        for i, field_data in enumerate(fields):
            col_idx = i % 3
            frame = ttk.Frame(columns[col_idx])
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=field_data[1], width=35, anchor=tk.W).pack(side=tk.LEFT, padx=5)

            if field_data[2] == "combobox":
                if field_data[0] == "glavnaya_poroda":
                    poroda_frame = ttk.Frame(frame)
                    poroda_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    widget = ttk.Combobox(poroda_frame, values=field_data[3], width=28)
                    widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    ttk.Button(poroda_frame, text="?", width=3, command=self.show_poroda_help).pack(side=tk.LEFT,
                                                                                                    padx=2)
                else:
                    widget = ttk.Combobox(frame, values=field_data[3], width=32)
                    widget.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            elif field_data[2] == "text":
                widget = tk.Text(frame, height=3, width=32)
                widget.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            else:
                widget = ttk.Entry(frame, width=32)
                widget.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

            self.entries[field_data[0]] = widget

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Захаваць і перайсці да CRN", command=self.save_and_go_to_crn).pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(btn_frame, text="Толькі захаваць (без CRN)", command=self.save_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Адмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_data(self):
        data = {}
        for key, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                value = widget.get("1.0", tk.END).strip()
            else:
                value = widget.get().strip()

            if value:
                if key in ['shirota_grd', 'dolgota_grd', 'vysota_nad_u_m', 'srednyaya_vysota_m',
                           'srednij_diametr_sm', 'polnota', 'zapas_kub_m', 'koef_sostava',
                           'vozrast', 'kolichestvo_derevev_v_shkale_sht', 'protyazhennost_shkaly_let',
                           'pervyy_god', 'posledniy_god', 'mezhserialnyj_kof_korrelyatsii',
                           'srednij_kof_chuvstvitelnosti', 'god_lesoustrojstva', 'ploshchad_vydela']:
                    try:
                        value = float(value.replace(',', '.'))
                    except:
                        value = None
                elif key in ['data_otbora_obraztsov', 'data_predostavleniya_v_bazu_dannykh']:
                    try:
                        value = datetime.strptime(value, "%d.%m.%Y").date()
                    except:
                        value = None
                data[key] = value

        if 'n_probnoy_ploshchadi' not in data or not data['n_probnoy_ploshchadi']:
            messagebox.showwarning("Папярэджанне", "Назва ПП абавязковая!")
            return None

        try:
            self.db.add_title(data)
            if 'shirota_grd' in data and 'dolgota_grd' in data:
                self.db.update_geometry(data['n_probnoy_ploshchadi'])
            self.db.commit()
            return data['n_probnoy_ploshchadi']
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Памылка", f"Не атрымалася захаваць:\n{e}")
            return None

    def save_and_go_to_crn(self):
        probe_name = self.save_data()
        if probe_name:
            self.dialog.destroy()
            CrnDialog(self.parent, self.db, probe_name)

    def save_only(self):
        probe_name = self.save_data()
        if probe_name:
            messagebox.showinfo("Поспех", f"ПП {probe_name} паспяхова захавана!")
            self.dialog.destroy()


class CrnDialog:
    def __init__(self, parent, db, probe_name):
        self.parent = parent
        self.db = db
        self.probe_name = probe_name
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Увод CRN храналогіі для {probe_name}")
        self.dialog.geometry("1200x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.dialog, text=f"Даданне CRN храналогіі для ПП: {self.probe_name}",
                  font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Label(self.dialog, text="Скапіруйце даныя з Excel (year, num, raw, std, res, ars) і націсніце 'Уставіць'",
                  foreground="blue").pack(pady=5)

        frame = ttk.Frame(self.dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('year', 'num', 'raw', 'std', 'res', 'ars')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=30)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Уставіць з буфера абмену", command=self.paste_from_clipboard).pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(btn_frame, text="Ачысціць табліцу", command=self.clear_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Захаваць і перайсці да SERIES", command=self.save_and_go_to_series).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Толькі захаваць CRN", command=self.save_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Прапусціць CRN", command=self.skip).pack(side=tk.LEFT, padx=5)

    def paste_from_clipboard(self):
        try:
            text = self.dialog.clipboard_get()
            lines = text.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                parts = line.replace('\t', ' ').split()
                if len(parts) >= 2:
                    values = []
                    for i in range(6):
                        if i < len(parts):
                            try:
                                values.append(float(parts[i]))
                            except:
                                values.append(parts[i] if i == 0 else None)
                        else:
                            values.append(None)
                    self.tree.insert('', tk.END, values=values)
        except Exception as e:
            messagebox.showerror("Памылка", f"Не атрымалася ўставіць:\n{e}")

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def save_crn_data(self):
        data_list = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if values and values[0]:
                try:
                    year = int(float(values[0]))
                    row = [year]
                    for i in range(1, 6):
                        if i < len(values) and values[i]:
                            try:
                                row.append(float(values[i]))
                            except:
                                row.append(None)
                        else:
                            row.append(None)
                    data_list.append(row)
                except:
                    pass

        if data_list:
            try:
                self.db.add_crn_batch(self.probe_name, data_list)
                self.db.commit()
                messagebox.showinfo("Поспех", f"Захавана {len(data_list)} запісаў CRN")
                return True
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Памылка", f"Не атрымалася захаваць CRN:\n{e}")
                return False
        return True

    def save_and_go_to_series(self):
        if self.save_crn_data():
            self.dialog.destroy()
            SeriesDialog(self.parent, self.db, self.probe_name)

    def save_only(self):
        self.save_crn_data()
        messagebox.showinfo("Інфармацыя",
                            "CRN захаваны. Вы можаце зачыніць акно або дадаць SERIES пазней праз галоўнае меню.")
        self.dialog.destroy()

    def skip(self):
        self.dialog.destroy()
        SeriesDialog(self.parent, self.db, self.probe_name)


class SeriesDialog:
    def __init__(self, parent, db, probe_name):
        self.parent = parent
        self.db = db
        self.probe_name = probe_name
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Увод SERIES для {probe_name}")
        self.dialog.geometry("1200x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.series_columns = {}
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.dialog, text=f"Даданне SERIES для ПП: {self.probe_name}", font=("Arial", 12, "bold")).pack(
            pady=5)
        ttk.Label(self.dialog,
                  text="Скапіруйце даныя з Excel (першы слупок - year, наступныя - назвы серый з іх значэннямі)",
                  foreground="blue").pack(pady=5)

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Уставіць з буфера абмену", command=self.paste_from_clipboard).pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(btn_frame, text="Ачысціць табліцу", command=self.clear_tree).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Захаваць і скончыць", command=self.save_and_finish).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Прапусціць SERIES", command=self.skip).pack(side=tk.LEFT, padx=5)

        frame = ttk.Frame(self.dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree = ttk.Treeview(frame, show='headings')
        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    def paste_from_clipboard(self):
        try:
            text = self.dialog.clipboard_get()
            lines = text.strip().split('\n')
            if not lines:
                return
            headers = lines[0].replace('\t', ' ').split()
            columns = ['year'] + [h.strip() for h in headers[1:]]
            self.tree['columns'] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)
            for line in lines[1:]:
                if not line.strip():
                    continue
                parts = line.replace('\t', ' ').split()
                if parts:
                    self.tree.insert('', tk.END, values=parts)
            self.series_columns = {col: idx for idx, col in enumerate(columns) if col != 'year'}
        except Exception as e:
            messagebox.showerror("Памылка", f"Не атрымалася ўставіць:\n{e}")

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def save_series_data(self):
        data_list = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if values and values[0]:
                try:
                    year = int(float(values[0]))
                    for series_name, idx in self.series_columns.items():
                        if idx < len(values) and values[idx] and values[idx] != '':
                            try:
                                value = float(values[idx])
                                data_list.append([year, series_name, value])
                            except:
                                pass
                except:
                    pass

        if data_list:
            try:
                self.db.add_series_batch(self.probe_name, data_list)
                self.db.commit()
                messagebox.showinfo("Поспех", f"Захавана {len(data_list)} запісаў SERIES")
                return True
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Памылка", f"Не атрымалася захаваць SERIES:\n{e}")
                return False
        return True

    def save_and_finish(self):
        self.save_series_data()
        messagebox.showinfo("Гатова", f"ПП {self.probe_name} поўнасцю дададзена!")
        self.dialog.destroy()

    def skip(self):
        messagebox.showinfo("Гатова", f"ПП {self.probe_name} дададзена без SERIES")
        self.dialog.destroy()


class SQLQueryDialog:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("SQL Запыт")
        self.dialog.geometry("1000x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(main_frame, text="SQL Запыт:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.sql_text = tk.Text(text_frame, wrap=tk.NONE, font=("Courier", 10), height=10)
        scroll_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.sql_text.yview)
        scroll_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.sql_text.xview)
        self.sql_text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.sql_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="▶ Выканаць", command=self.execute_query).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 Уставіць з буфера", command=self.paste_sql).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Ачысціць", command=self.clear_sql).pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, text="Вынік:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)

        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.result_tree = ttk.Treeview(result_frame, show='headings')
        scroll_y2 = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        scroll_x2 = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=scroll_y2.set, xscrollcommand=scroll_x2.set)

        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y2.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x2.pack(side=tk.BOTTOM, fill=tk.X)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(status_frame, text="Гатова", foreground="blue")
        self.status_label.pack(side=tk.LEFT)

        ttk.Button(status_frame, text="📋 Капіраваць вынік у буфер", command=self.copy_to_clipboard).pack(side=tk.RIGHT,
                                                                                                         padx=5)

    def paste_sql(self):
        try:
            text = self.dialog.clipboard_get()
            self.sql_text.insert(tk.INSERT, text)
        except:
            pass

    def clear_sql(self):
        self.sql_text.delete(1.0, tk.END)

    def execute_query(self):
        query = self.sql_text.get(1.0, tk.END).strip()
        if not query:
            messagebox.showwarning("Папярэджанне", "Увядзіце SQL запыт")
            return

        self.status_label.config(text="Выкананне запыту...", foreground="orange")
        self.dialog.update()

        result = self.db.execute_sql_query(query)

        if result['success']:
            if 'columns' in result:
                for item in self.result_tree.get_children():
                    self.result_tree.delete(item)

                self.result_tree['columns'] = result['columns']
                for col in result['columns']:
                    self.result_tree.heading(col, text=col)
                    self.result_tree.column(col, width=100)

                for row in result['rows']:
                    self.result_tree.insert('', tk.END, values=row)

                self.status_label.config(text=f"✅ Выканана. Знойдзена {result['rowcount']} радкоў", foreground="green")
            else:
                self.status_label.config(text=f"✅ {result['message']}", foreground="green")
        else:
            self.status_label.config(text=f"❌ Памылка: {result['error']}", foreground="red")
            messagebox.showerror("Памылка SQL", result['error'])

    def copy_to_clipboard(self):
        if not self.result_tree.get_children():
            messagebox.showwarning("Папярэджанне", "Няма даных для капіравання")
            return

        try:
            columns = self.result_tree['columns']
            rows = []
            for item in self.result_tree.get_children():
                rows.append(self.result_tree.item(item)['values'])

            clipboard_text = []
            clipboard_text.append('\t'.join(columns))

            for row in rows:
                str_row = [str(val) if val is not None else '' for val in row]
                clipboard_text.append('\t'.join(str_row))

            result_text = '\n'.join(clipboard_text)

            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(result_text)

            self.status_label.config(text=f"📋 Капіравана {len(rows)} радкоў у буфер абмену", foreground="blue")

        except Exception as e:
            messagebox.showerror("Памылка", f"Не атрымалася скапіраваць:\n{e}")


class FilterTab:
    """Клас для ўкладкі фільтраў і пошуку"""

    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def load_drevesnaya_poroda_values(self):
        """Загрузіць унікальныя значэнні drevesnaya_poroda з БД"""
        try:
            values = self.db.get_unique_drevesnaya_poroda()
            if values:
                self.drevesnaya_poroda_combo['values'] = [""] + values
            else:
                self.drevesnaya_poroda_combo['values'] = [""] + DREVESNAYA_PORODA_LIST
        except:
            self.drevesnaya_poroda_combo['values'] = [""] + DREVESNAYA_PORODA_LIST

    def create_widgets(self):
        # Левая панэль з фільтрамі
        left_frame = ttk.LabelFrame(self.frame, text="Фільтры", width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)

        # Фільтр па драўнянай пародзе
        ttk.Label(left_frame, text="Дрэвавая парода:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        self.drevesnaya_poroda_var = tk.StringVar()
        self.drevesnaya_poroda_combo = ttk.Combobox(left_frame, textvariable=self.drevesnaya_poroda_var, width=30)
        self.drevesnaya_poroda_combo.pack(fill=tk.X, padx=5, pady=2)
        self.load_drevesnaya_poroda_values()

        # Фільтр па геабатанічнай зоне
        ttk.Label(left_frame, text="Геабатанічная зона:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        self.geo_zona_var = tk.StringVar()
        self.geo_zona_combo = ttk.Combobox(left_frame, textvariable=self.geo_zona_var, values=[""] + GEO_ZONA_LIST,
                                           width=30)
        self.geo_zona_combo.pack(fill=tk.X, padx=5, pady=2)

        # Фільтр па геабатанічнай падзоне
        ttk.Label(left_frame, text="Геабатанічная падзона:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5,
                                                                                             pady=2)
        self.geo_podzona_var = tk.StringVar()
        self.geo_podzona_combo = ttk.Combobox(left_frame, textvariable=self.geo_podzona_var,
                                              values=[""] + GEO_PODZONA_LIST, width=30)
        self.geo_podzona_combo.pack(fill=tk.X, padx=5, pady=2)

        # Фільтр па геабатанічнай акрузе
        ttk.Label(left_frame, text="Геабатанічная акруга:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        self.geo_okrug_var = tk.StringVar()
        self.geo_okrug_combo = ttk.Combobox(left_frame, textvariable=self.geo_okrug_var, values=[""] + GEO_OKRUG_LIST,
                                            width=30)
        self.geo_okrug_combo.pack(fill=tk.X, padx=5, pady=2)

        # Фільтр па геабатанічным раёне
        ttk.Label(left_frame, text="Геабатанічны раён:", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        self.geo_rajon_var = tk.StringVar()
        self.geo_rajon_combo = ttk.Combobox(left_frame, textvariable=self.geo_rajon_var, values=[""] + GEO_RAJON_LIST,
                                            width=30)
        self.geo_rajon_combo.pack(fill=tk.X, padx=5, pady=2)

        # Фільтр па тыпу лесу (пошук па ключавым слове)
        ttk.Label(left_frame, text="Тып лесу (ключ. слова):", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5,
                                                                                              pady=2)
        self.tip_lesa_var = tk.StringVar()
        self.tip_lesa_entry = ttk.Entry(left_frame, textvariable=self.tip_lesa_var, width=32)
        self.tip_lesa_entry.pack(fill=tk.X, padx=5, pady=2)

        # Фільтр па гадах
        year_frame = ttk.Frame(left_frame)
        year_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(year_frame, text="Год з:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        self.year_from_var = tk.StringVar()
        ttk.Entry(year_frame, textvariable=self.year_from_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(year_frame, text="Год па:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        self.year_to_var = tk.StringVar()
        ttk.Entry(year_frame, textvariable=self.year_to_var, width=8).pack(side=tk.LEFT, padx=5)

        # Выбар калонак CRN
        ttk.Label(left_frame, text="Від храналогіі (CRN):", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)

        self.crn_raw_var = tk.BooleanVar(value=True)
        self.crn_std_var = tk.BooleanVar(value=True)
        self.crn_res_var = tk.BooleanVar(value=True)
        self.crn_ars_var = tk.BooleanVar(value=True)

        crn_frame = ttk.Frame(left_frame)
        crn_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Checkbutton(crn_frame, text="raw", variable=self.crn_raw_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(crn_frame, text="std", variable=self.crn_std_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(crn_frame, text="res", variable=self.crn_res_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(crn_frame, text="ars", variable=self.crn_ars_var).pack(side=tk.LEFT, padx=5)

        # Кнопкі
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(btn_frame, text="🔍 Выканаць пошук", command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Ачысціць фільтры", command=self.clear_filters).pack(side=tk.LEFT, padx=5)

        # Правая панэль - вынікі
        right_frame = ttk.LabelFrame(self.frame, text="Вынікі пошуку")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Табліца вынікаў
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.result_tree = ttk.Treeview(tree_frame, show='headings')
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Статус
        self.status_label = ttk.Label(right_frame, text="", foreground="blue")
        self.status_label.pack(pady=5)

        # Кнопка капіравання
        copy_btn = ttk.Button(right_frame, text="📋 Капіраваць вынік у буфер", command=self.copy_to_clipboard)
        copy_btn.pack(pady=5)

    def get_filters(self):
        """Атрымаць значэнні фільтраў"""
        crn_columns = []
        if self.crn_raw_var.get():
            crn_columns.append('raw')
        if self.crn_std_var.get():
            crn_columns.append('std')
        if self.crn_res_var.get():
            crn_columns.append('res')
        if self.crn_ars_var.get():
            crn_columns.append('ars')

        return {
            'drevesnaya_poroda': self.drevesnaya_poroda_var.get() if self.drevesnaya_poroda_var.get() else None,
            'geobotanicheskaya_zona': self.geo_zona_var.get() if self.geo_zona_var.get() else None,
            'geobotanicheskaya_podzona': self.geo_podzona_var.get() if self.geo_podzona_var.get() else None,
            'geobotanicheskij_okrug': self.geo_okrug_var.get() if self.geo_okrug_var.get() else None,
            'geobotanicheskij_rajon': self.geo_rajon_var.get() if self.geo_rajon_var.get() else None,
            'tip_lesa_keyword': self.tip_lesa_var.get() if self.tip_lesa_var.get() else None,
            'year_from': int(self.year_from_var.get()) if self.year_from_var.get() else None,
            'year_to': int(self.year_to_var.get()) if self.year_to_var.get() else None,
            'crn_columns': crn_columns
        }

    def apply_filters(self):
        """Прымяніць фільтры і абнавіць вынікі"""
        self.status_label.config(text="Выкананне запыту...", foreground="orange")
        self.parent.update()

        filters = self.get_filters()
        columns, rows = self.db.get_filtered_data(filters)

        # Абнаўленне табліцы
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        self.result_tree['columns'] = columns
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=120)

        for row in rows:
            self.result_tree.insert('', tk.END, values=row)

        self.status_label.config(text=f"✅ Знойдзена {len(rows)} запісаў", foreground="green")

    def clear_filters(self):
        """Ачысціць усе фільтры"""
        self.drevesnaya_poroda_var.set("")
        self.geo_zona_var.set("")
        self.geo_podzona_var.set("")
        self.geo_okrug_var.set("")
        self.geo_rajon_var.set("")
        self.tip_lesa_var.set("")
        self.year_from_var.set("")
        self.year_to_var.set("")
        self.crn_raw_var.set(True)
        self.crn_std_var.set(True)
        self.crn_res_var.set(True)
        self.crn_ars_var.set(True)

        self.apply_filters()

    def copy_to_clipboard(self):
        """Капіраваць вынік у буфер абмену"""
        if not self.result_tree.get_children():
            messagebox.showwarning("Папярэджанне", "Няма даных для капіравання")
            return

        try:
            columns = self.result_tree['columns']
            rows = []
            for item in self.result_tree.get_children():
                rows.append(self.result_tree.item(item)['values'])

            clipboard_text = []
            clipboard_text.append('\t'.join(columns))

            for row in rows:
                str_row = [str(val) if val is not None else '' for val in row]
                clipboard_text.append('\t'.join(str_row))

            result_text = '\n'.join(clipboard_text)

            self.parent.clipboard_clear()
            self.parent.clipboard_append(result_text)

            self.status_label.config(text=f"📋 Капіравана {len(rows)} радкоў у буфер абмену", foreground="blue")

        except Exception as e:
            messagebox.showerror("Памылка", f"Не атрымалася скапіраваць:\n{e}")

    def get_frame(self):
        return self.frame


class DendroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dendrochronology Database Manager")
        self.root.geometry("1400x800")
        self.db = DatabaseManager()
        self.current_probe = None
        self.all_columns = self.db.get_all_title_columns()
        self.create_menu()
        self.create_main_layout()
        self.load_probes_list()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Абнавіць спіс", command=self.load_probes_list)
        file_menu.add_separator()
        file_menu.add_command(label="Выйсці", command=self.on_exit)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Выгляд", menu=view_menu)
        view_menu.add_command(label="Абнавіць карту", command=self.update_map)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Інструменты", menu=tools_menu)
        tools_menu.add_command(label="SQL Запыт", command=self.open_sql_dialog)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Даведка", menu=help_menu)
        help_menu.add_command(label="Расшыфроўка пародаў", command=self.show_poroda_help)
        help_menu.add_separator()
        help_menu.add_command(label="Аб праграме", command=self.show_about)

    def open_sql_dialog(self):
        SQLQueryDialog(self.root, self.db)

    def show_poroda_help(self):
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("Даведка: Расшыфроўка пародаў")
        help_dialog.geometry("500x600")
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        canvas = tk.Canvas(help_dialog)
        scrollbar = ttk.Scrollbar(help_dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        ttk.Label(scrollable_frame, text="Расшыфроўка скарачэнняў пародаў дрэў", font=("Arial", 14, "bold")).pack(
            pady=10)
        tree = ttk.Treeview(scrollable_frame, columns=("code", "name"), show="headings", height=30)
        tree.heading("code", text="Скарачэнне")
        tree.heading("name", text="Поўная назва")
        tree.column("code", width=100)
        tree.column("name", width=350)
        for code, name in sorted(PORODA_DICT.items()):
            tree.insert("", tk.END, values=(code, name))
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Button(scrollable_frame, text="Закрыць", command=help_dialog.destroy).pack(pady=10)

    def create_main_layout(self):
        left_frame = ttk.Frame(self.root, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(left_frame, text="Пошук ПП:").pack(anchor=tk.W)
        self.search_entry = ttk.Entry(left_frame)
        self.search_entry.pack(fill=tk.X, pady=(0, 5))
        self.search_entry.bind('<KeyRelease>', self.on_search)

        ttk.Label(left_frame, text="Пробныя плошчы:").pack(anchor=tk.W)
        self.probes_listbox = tk.Listbox(left_frame, height=25)
        self.probes_listbox.pack(fill=tk.BOTH, expand=True)
        self.probes_listbox.bind('<<ListboxSelect>>', self.on_probe_select)

        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="+ Дадаць новую ПП", command=self.add_new_probe_full).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="📊 Дадаць CRN", command=self.add_crn_to_existing).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="📈 Дадаць SERIES", command=self.add_series_to_existing).pack(fill=tk.X, pady=2)

        geo_frame = ttk.LabelFrame(left_frame, text="Геаметрыя (PostGIS)")
        geo_frame.pack(fill=tk.X, pady=5)
        ttk.Button(geo_frame, text="📍 Абнавіць геаметрыю выбранай ПП", command=self.update_selected_geometry).pack(
            fill=tk.X, pady=2, padx=5)
        ttk.Button(geo_frame, text="🗺️ Абнавіць геаметрыю ўсіх ПП", command=self.update_all_geometry).pack(fill=tk.X,
                                                                                                           pady=2,
                                                                                                           padx=5)
        if self.db.check_postgis():
            ttk.Label(geo_frame, text="✅ PostGIS: усталяваны", foreground="green").pack(pady=2)
        else:
            ttk.Label(geo_frame, text="❌ PostGIS: не ўсталяваны", foreground="red").pack(pady=2)

        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.create_notebook(right_frame)

    def add_crn_to_existing(self):
        if not self.current_probe:
            messagebox.showwarning("Папярэджанне", "Спачатку выберыце пробную плошчу са спіса")
            return
        CrnDialog(self.root, self.db, self.current_probe)
        self.load_crn_data()

    def add_series_to_existing(self):
        if not self.current_probe:
            messagebox.showwarning("Папярэджанне", "Спачатку выберыце пробную плошчу са спіса")
            return
        SeriesDialog(self.root, self.db, self.current_probe)
        self.load_series_matrix()

    def update_selected_geometry(self):
        if not self.current_probe:
            messagebox.showwarning("Папярэджанне", "Спачатку выберыце пробную плошчу")
            return
        if not self.db.check_postgis():
            messagebox.showerror("Памылка",
                                 "PostGIS не ўсталяваны!\n\nКаб усталяваць, выканайце ў PostgreSQL:\nCREATE EXTENSION postgis;")
            return
        info = self.db.get_probe_info(self.current_probe)
        if info:
            if not info.get('shirota_grd') or not info.get('dolgota_grd'):
                messagebox.showwarning("Увага",
                                       f"Для ПП {self.current_probe} не зададзены каардынаты!\nСпачатку ўвядзіце шырату і даўгату.")
                return
        count = self.db.update_geometry(self.current_probe)
        if count > 0:
            messagebox.showinfo("Поспех", f"Геаметрыя для {self.current_probe} абноўлена")
            self.load_title_info()
        else:
            messagebox.showwarning("Увага",
                                   "Не атрымалася абнавіць геаметрыю.\nПраверце, што каардынаты ўведзены карэктна.")

    def update_all_geometry(self):
        if not self.db.check_postgis():
            messagebox.showerror("Памылка",
                                 "PostGIS не ўсталяваны!\n\nКаб усталяваць, выканайце ў PostgreSQL:\nCREATE EXTENSION postgis;")
            return
        self.db.cur.execute("SELECT COUNT(*) FROM title WHERE shirota_grd IS NOT NULL AND dolgota_grd IS NOT NULL")
        count_with_coords = self.db.cur.fetchone()[0]
        if count_with_coords == 0:
            messagebox.showwarning("Увага", "Няма ПП з каардынатамі для абнаўлення")
            return
        if messagebox.askyesno("Пацверджанне", f"Будзе абноўлена геаметрыя для {count_with_coords} ПП.\nПрацягнуць?"):
            count = self.db.update_geometry_all()
            messagebox.showinfo("Поспех", f"Геаметрыя абноўлена для {count} ПП")
            if self.current_probe:
                self.load_title_info()

    def create_notebook(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="Інфармацыя аб ПП")
        self.create_info_tab()

        self.crn_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.crn_frame, text="CRN Храналогія")
        self.create_crn_tab()

        self.series_matrix_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.series_matrix_frame, text="SERIES (Матрыца)")
        self.create_series_matrix_tab()

        # Новая ўкладка - Фільтры і пошук
        self.filter_tab = FilterTab(self.notebook, self.db)
        self.notebook.add(self.filter_tab.get_frame(), text="🔍 Фільтры і пошук")

        self.map_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.map_frame, text="Карта храналогій")
        self.create_map_tab()

    def create_info_tab(self):
        main_frame = ttk.Frame(self.info_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(fields_frame)
        scrollbar = ttk.Scrollbar(fields_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.info_entries = {}
        columns = [ttk.Frame(scrollable_frame) for _ in range(3)]
        for col in columns:
            col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        for i, col in enumerate(self.all_columns):
            col_idx = i % 3
            frame = ttk.Frame(columns[col_idx])
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=col + ":", width=35, anchor=tk.W).pack(side=tk.LEFT, padx=5)
            entry = ttk.Entry(frame, width=35)
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.info_entries[col] = entry

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        save_btn = ttk.Button(btn_frame, text="💾 Захаваць змены", command=self.save_title_info)
        save_btn.pack(side=tk.LEFT, padx=5)

        refresh_btn = ttk.Button(btn_frame, text="🔄 Абнавіць", command=self.load_title_info)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_frame, text="🗑 Ачысціць", command=self.clear_info_form)
        clear_btn.pack(side=tk.LEFT, padx=5)

        info_label = ttk.Label(btn_frame, text=" | Рэдагуйце палі і націсніце 'Захаваць змены'", foreground="blue")
        info_label.pack(side=tk.LEFT, padx=10)

    def create_crn_tab(self):
        filter_frame = ttk.Frame(self.crn_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(filter_frame, text="Год з:").pack(side=tk.LEFT, padx=5)
        self.crn_year_from = ttk.Entry(filter_frame, width=10)
        self.crn_year_from.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text="Год па:").pack(side=tk.LEFT, padx=5)
        self.crn_year_to = ttk.Entry(filter_frame, width=10)
        self.crn_year_to.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Фільтраваць", command=self.load_crn_data).pack(side=tk.LEFT, padx=10)
        ttk.Button(filter_frame, text="Паказаць усе", command=self.clear_crn_filter).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(self.crn_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.crn_tree = ttk.Treeview(tree_frame, columns=('year', 'num', 'raw', 'std', 'res', 'ars'), show='headings')
        for col in ['year', 'num', 'raw', 'std', 'res', 'ars']:
            self.crn_tree.heading(col, text=col)
            self.crn_tree.column(col, width=100)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.crn_tree.yview)
        self.crn_tree.configure(yscrollcommand=scrollbar.set)
        self.crn_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        add_frame = ttk.LabelFrame(self.crn_frame, text="Дадаць/Рэдагаваць запіс")
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(add_frame, text="Год:").grid(row=0, column=0, padx=5, pady=2)
        self.crn_year_entry = ttk.Entry(add_frame, width=10)
        self.crn_year_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(add_frame, text="Num:").grid(row=0, column=2, padx=5, pady=2)
        self.crn_num_entry = ttk.Entry(add_frame, width=15)
        self.crn_num_entry.grid(row=0, column=3, padx=5, pady=2)
        ttk.Label(add_frame, text="Raw:").grid(row=0, column=4, padx=5, pady=2)
        self.crn_raw_entry = ttk.Entry(add_frame, width=15)
        self.crn_raw_entry.grid(row=0, column=5, padx=5, pady=2)
        ttk.Label(add_frame, text="Std:").grid(row=1, column=0, padx=5, pady=2)
        self.crn_std_entry = ttk.Entry(add_frame, width=15)
        self.crn_std_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(add_frame, text="Res:").grid(row=1, column=2, padx=5, pady=2)
        self.crn_res_entry = ttk.Entry(add_frame, width=15)
        self.crn_res_entry.grid(row=1, column=3, padx=5, pady=2)
        ttk.Label(add_frame, text="Ars:").grid(row=1, column=4, padx=5, pady=2)
        self.crn_ars_entry = ttk.Entry(add_frame, width=15)
        self.crn_ars_entry.grid(row=1, column=5, padx=5, pady=2)
        btn_frame = ttk.Frame(add_frame)
        btn_frame.grid(row=2, column=0, columnspan=6, pady=10)
        ttk.Button(btn_frame, text="Дадаць/Абнавіць", command=self.add_crn_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Выдаліць", command=self.delete_crn_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Ачысціць", command=self.clear_crn_form).pack(side=tk.LEFT, padx=5)

    def create_series_matrix_tab(self):
        filter_frame = ttk.Frame(self.series_matrix_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(filter_frame, text="Год з:").pack(side=tk.LEFT, padx=5)
        self.matrix_year_from = ttk.Entry(filter_frame, width=10)
        self.matrix_year_from.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text="Год па:").pack(side=tk.LEFT, padx=5)
        self.matrix_year_to = ttk.Entry(filter_frame, width=10)
        self.matrix_year_to.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Паказаць матрыцу", command=self.load_series_matrix).pack(side=tk.LEFT, padx=10)

        matrix_frame = ttk.Frame(self.series_matrix_frame)
        matrix_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.matrix_tree = ttk.Treeview(matrix_frame, show='headings')
        scrollbar_y = ttk.Scrollbar(matrix_frame, orient=tk.VERTICAL, command=self.matrix_tree.yview)
        scrollbar_x = ttk.Scrollbar(matrix_frame, orient=tk.HORIZONTAL, command=self.matrix_tree.xview)
        self.matrix_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.matrix_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.matrix_info_label = ttk.Label(self.series_matrix_frame, text="", foreground="blue")
        self.matrix_info_label.pack(pady=5)

    def create_map_tab(self):
        info_panel = ttk.Frame(self.map_frame)
        info_panel.pack(fill=tk.X, padx=5, pady=5)
        self.map_info_label = ttk.Label(info_panel, text="Націсніце 'Абнавіць карту' для паказу", foreground="blue")
        self.map_info_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(info_panel, text="Абнавіць карту", command=self.update_map).pack(side=tk.RIGHT, padx=5)
        ttk.Button(info_panel, text="Захаваць карту як HTML", command=self.save_map_as_html).pack(side=tk.RIGHT, padx=5)
        self.map_text = tk.Text(self.map_frame, wrap=tk.NONE, font=("Courier", 10))
        self.map_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def add_new_probe_full(self):
        AddProbeDialog(self.root, self.db)
        self.load_probes_list()

    def update_map(self):
        def create_map():
            try:
                probes = self.db.get_all_probes_with_coords()
                if not probes:
                    self.root.after(0, lambda: self.map_info_label.config(text="Няма ПП з каардынатамі"))
                    return
                center_lat = sum(p[1] for p in probes if p[1]) / len(probes)
                center_lon = sum(p[2] for p in probes if p[2]) / len(probes)
                m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles='OpenStreetMap')
                for probe in probes:
                    name, lat, lon, poroda, last_year, first_year, _ = probe
                    if lat and lon:
                        popup_text = f"<b>{name}</b><br>Парода: {poroda or 'н/д'}<br>Гады: {first_year or '?'}-{last_year or '?'}"
                        folium.Marker([lat, lon], popup=popup_text, tooltip=name).add_to(m)
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                    m.save(f.name)
                    webbrowser.open(f.name)
                self.root.after(0, lambda: self.map_info_label.config(text=f"✅ Карта адкрыта! {len(probes)} ПП"))
            except Exception as err:
                self.root.after(0, lambda: self.map_info_label.config(text=f"Памылка: {err}"))

        threading.Thread(target=create_map, daemon=True).start()

    def save_map_as_html(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
        if file_path:
            try:
                probes = self.db.get_all_probes_with_coords()
                if probes:
                    center_lat = sum(p[1] for p in probes if p[1]) / len(probes)
                    center_lon = sum(p[2] for p in probes if p[2]) / len(probes)
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=7)
                    for probe in probes:
                        name, lat, lon, poroda, last_year, first_year, _ = probe
                        if lat and lon:
                            folium.Marker([lat, lon], popup=name, tooltip=name).add_to(m)
                    m.save(file_path)
                    messagebox.showinfo("Поспех", f"Карта захавана: {file_path}")
            except Exception as err:
                messagebox.showerror("Памылка", str(err))

    def load_probes_list(self):
        self.probes_listbox.delete(0, tk.END)
        for probe in self.db.get_all_probes():
            self.probes_listbox.insert(tk.END, probe)

    def on_search(self, event):
        search_text = self.search_entry.get()
        self.probes_listbox.delete(0, tk.END)
        probes = self.db.search_probes(search_text) if search_text else self.db.get_all_probes()
        for probe in probes:
            self.probes_listbox.insert(tk.END, probe)

    def on_probe_select(self, event):
        selection = self.probes_listbox.curselection()
        if selection:
            self.current_probe = self.probes_listbox.get(selection[0])
            self.load_title_info()
            self.load_crn_data()
            self.load_series_matrix()

    def load_title_info(self):
        if not self.current_probe:
            return
        info = self.db.get_probe_info(self.current_probe)
        if info:
            self.clear_info_form()
            for col, value in info.items():
                if col in self.info_entries and value is not None:
                    self.info_entries[col].delete(0, tk.END)
                    self.info_entries[col].insert(0, str(value))

    def save_title_info(self):
        if not self.current_probe:
            messagebox.showwarning("Папярэджанне", "Выберыце ПП")
            return

        old_info = self.db.get_probe_info(self.current_probe)

        data = {'n_probnoy_ploshchadi': self.current_probe}
        changed_fields = []

        for col, entry in self.info_entries.items():
            value = entry.get().strip()
            old_value = old_info.get(col) if old_info else None

            if value:
                if col in ['shirota_grd', 'dolgota_grd', 'vysota_nad_u_m', 'srednyaya_vysota_m',
                           'srednij_diametr_sm', 'polnota', 'zapas_kub_m', 'koef_sostava',
                           'vozrast', 'kolichestvo_derevev_v_shkale_sht', 'protyazhennost_shkaly_let',
                           'pervyy_god', 'posledniy_god', 'mezhserialnyj_kof_korrelyatsii',
                           'srednij_kof_chuvstvitelnosti', 'god_lesoustrojstva', 'ploshchad_vydela']:
                    try:
                        value = float(value.replace(',', '.'))
                    except:
                        value = None
                data[col] = value

                if old_value is not None and str(old_value) != str(value):
                    changed_fields.append(col)
            elif old_value is not None and old_value != "":
                data[col] = None
                changed_fields.append(col)

        if not changed_fields:
            messagebox.showinfo("Інфармацыя", "Няма змен для захавання")
            return

        try:
            self.db.add_title(data)
            if 'shirota_grd' in data or 'dolgota_grd' in data:
                self.db.update_geometry(self.current_probe)
            self.db.commit()

            messagebox.showinfo("Поспех", f"Змены захаваны!\nАбноўлены палі: {', '.join(changed_fields)}")

            self.load_title_info()
            self.load_crn_data()
            self.load_series_matrix()

        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Памылка", f"Не атрымалася захаваць:\n{e}")

    def clear_info_form(self):
        for entry in self.info_entries.values():
            entry.delete(0, tk.END)

    def load_crn_data(self):
        for item in self.crn_tree.get_children():
            self.crn_tree.delete(item)
        if self.current_probe:
            for row in self.db.get_crn_data(self.current_probe):
                self.crn_tree.insert('', tk.END, values=row)

    def clear_crn_filter(self):
        self.crn_year_from.delete(0, tk.END)
        self.crn_year_to.delete(0, tk.END)
        self.load_crn_data()

    def add_crn_record(self):
        if not self.current_probe:
            messagebox.showwarning("Папярэджанне", "Выберыце ПП")
            return
        year = self.crn_year_entry.get().strip()
        if not year:
            messagebox.showwarning("Папярэджанне", "Увядзіце год")
            return
        try:
            self.db.add_crn_data(self.current_probe, int(year),
                                 float(
                                     self.crn_num_entry.get().replace(',', '.')) if self.crn_num_entry.get() else None,
                                 float(
                                     self.crn_raw_entry.get().replace(',', '.')) if self.crn_raw_entry.get() else None,
                                 float(
                                     self.crn_std_entry.get().replace(',', '.')) if self.crn_std_entry.get() else None,
                                 float(
                                     self.crn_res_entry.get().replace(',', '.')) if self.crn_res_entry.get() else None,
                                 float(
                                     self.crn_ars_entry.get().replace(',', '.')) if self.crn_ars_entry.get() else None)
            self.db.commit()
            self.load_crn_data()
            self.clear_crn_form()
            messagebox.showinfo("Поспех", "Запіс дададзены")
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Памылка", str(e))

    def delete_crn_record(self):
        selected = self.crn_tree.selection()
        if not selected:
            return
        year = self.crn_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Пацверджанне", f"Выдаліць {year} год?"):
            self.db.delete_crn_data(self.current_probe, year)
            self.db.commit()
            self.load_crn_data()

    def clear_crn_form(self):
        self.crn_year_entry.delete(0, tk.END)
        self.crn_num_entry.delete(0, tk.END)
        self.crn_raw_entry.delete(0, tk.END)
        self.crn_std_entry.delete(0, tk.END)
        self.crn_res_entry.delete(0, tk.END)
        self.crn_ars_entry.delete(0, tk.END)

    def load_series_matrix(self):
        for item in self.matrix_tree.get_children():
            self.matrix_tree.delete(item)
        if self.current_probe:
            year_from = self.matrix_year_from.get().strip()
            year_to = self.matrix_year_to.get().strip()
            if year_from and year_to:
                matrix, series_names = self.db.get_series_matrix(self.current_probe, int(year_from), int(year_to))
            else:
                matrix, series_names = self.db.get_series_matrix(self.current_probe)
            if matrix is not None and not matrix.empty:
                self.matrix_tree['columns'] = ['year'] + series_names
                for col in ['year'] + series_names:
                    self.matrix_tree.heading(col, text=col)
                    self.matrix_tree.column(col, width=80)
                for idx, row in matrix.iterrows():
                    values = [idx] + [row[col] if pd.notna(row[col]) else '' for col in series_names]
                    self.matrix_tree.insert('', tk.END, values=values)
                self.matrix_info_label.config(text=f"{len(matrix)} гадоў, {len(series_names)} серый")
            else:
                self.matrix_info_label.config(text="Няма даных")

    def on_exit(self):
        self.db.disconnect()
        self.root.quit()

    def show_about(self):
        messagebox.showinfo("Аб праграме",
                            "Dendrochronology Database Manager\nВерсія 6.0\n\n"
                            "Поўная падтрымка ўсіх палёў табліцы title\n"
                            "Аўтаматычнае абнаўленне геаметрыі PostGIS\n"
                            "Масавы ўвод CRN і SERIES\n"
                            "Інтэрактыўная карта\n\n"
                            "Кнопкі для дадавання CRN і SERIES да існуючай ПП\n"
                            "Абнаўленне геаметрыі па каардынатах\n"
                            "Кнопка 'Захаваць змены' на ўкладцы Інфармацыя аб ПП\n"
                            "📝 SQL Запыты - магчымасць выканання любых SQL запытаў\n"
                            "🔍 Фільтры і пошук - магутная сістэма фільтрацыі даных\n\n"
                            "Распрацавана для кіравання дэндрахраналагічнымі данымі")


if __name__ == "__main__":
    root = tk.Tk()
    app = DendroApp(root)
    root.mainloop()