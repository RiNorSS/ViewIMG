import sqlite3
import re, os

class SQLException(Exception):
    def __init__(self, text:str, res:bool = False) -> None:
        self.text = text
        self.res = res 

class SQLscripts:
    """SQL скрипты для приложения pSer 
    
    Принимает:
        db - абсолютный путь к базе данных sqlite3
        
    P.S. Многие методы возврощают интовские значения обозначающее ту или иную ошибку.
    Вместо этого сделать собственые исключения """

    def __init__(self,db:str) -> None:
        self.db = db
        self.satrt()

    def satrt(self) -> None:
        """Скрипт который запускается при старте приложения.
        
        Создает файл бд
        В файле бд создает нужные отношения"""

        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            for t in ['photo', 'video', 'manga']:
                cur.execute(f"""CREATE TABLE IF NOT EXISTS '{t}' (id INTEGER PRIMARY KEY, path TEXT, unique_tag TEXT)""")
                conn.commit()
                cur.execute(f"""CREATE TABLE IF NOT EXISTS '{t}_tags' (id INTEGER PRIMARY KEY, name_tag TEXT, count_tag INTEGER)""")
                conn.commit()
                cur.execute(f"""CREATE TABLE IF NOT EXISTS '{t}_save_req' (id INTEGER PRIMARY KEY, name_req TEXT, list_req TEXT, len_req INTEGER)""")
                conn.commit()

    def append_db(self,path_dir:str, mode:str) -> None:
        """Метод добалвения в бд путей к изображением/видио/директориями которые находяться в указаном пути"""
        s = re.search(r'\s', path_dir)
        if s:
            raise SQLException(f"В пути директории не должно быть пробелов")
        
        os.chdir(path_dir)
        if mode == 'photo':
            types = ['.jpg', '.jpeg', '.png', '.webp']
            dir_files_list = list(map(os.path.abspath ,os.listdir(path_dir)))
            
            with sqlite3.connect(self.db) as conn:
                cur = conn.cursor()
                sql = f"""INSERT INTO photo (path) VALUES """
                alert = ''
                c,j = 0, 0
                for path in dir_files_list:
                    if os.path.splitext(path)[1].lower() in types:
                        cur.execute(f"""SELECT path FROM photo WHERE path LIKE '{path}'""")
                        if cur.fetchone():
                            conn.commit()
                            alert += f'{path}, '
                            j += 1
                            continue
                        sql += f"""('{path}'), """
                        c +=1
                sql = sql.rstrip(', ')
                alert = alert.rstrip(', ')
                if c == 0:
                    raise SQLException('Все изоброжения в выбраной диретории уже находять в бд')
                elif j == 0:
                    cur.execute(sql)
                    conn.commit()
                    raise SQLException('Все изображения добавлены в бд', True)
                else:
                    cur.execute(sql)
                    conn.commit()
                    raise SQLException(f"Изображения {alert} не были добалвнеы, так как уже находились в бд")
        elif mode == 'video':
            raise SQLException(f"Нереализовано")
        elif mode == 'manga':
            raise SQLException(f"Нереализовано")

    def get_normal_list(self,non_normal_list)-> list:
        """Преоброзования списка кортежий в список"""

        self.normal_list = list()
        for i in non_normal_list:
            self.normal_list.append(i[0])
        return self.normal_list
    
    def get_tags_list(self,mode:str)->list:
        """Запрос на получения списка тегов"""

        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT name_tag FROM '{mode}_tags'""")
            tags_list = self.get_normal_list(cur.fetchall())
            conn.commit()
        conn.close()
        
        if tags_list == []:
            raise SQLException(f"В данной катероии пока нету тегов.")
        return tags_list

    def get_tags_lsit_with_count(self, mode:str)->dict:
        """Возврощает список тегво с количиством фотогрофйи с таким тегом"""

        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT name_tag, count_tag FROM '{mode}_tags'""")
            res = cur.fetchall()
            conn.commit()

            current_c_tags = dict()
            for r in res:
                current_c_tags[r[0]] = r[1]
        
        return current_c_tags

    def get_tags_list_with_val(self, mode:str, path:str) -> dict:
        """Возврощает словарь всех тегов где
            Ключ: Название тега
            Значение: значение тега"""
        
        tags = {}
        # много небольших запросов/один запрос побольше как же быть???7
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            for tag in self.get_tags_list(mode):
                sql = f"""SELECT {tag} FROM '{mode}' WHERE path = '{path}'"""
                cur.execute(sql)
                tags[tag] = cur.fetchone()[0]
                conn.commit()
        return tags
    
    def get_unique_tag(self,mode:str,path:str)->str:
        """Возврощает уникальный тег для текущего изображения"""

        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT unique_tag FROM '{mode}' WHERE path = '{path}'""")
            r = cur.fetchone()[0]
            conn.commit()
        return r
    
    def get_unique_tags(self, mode:str) ->dict:
        """Возварощает словарб уникальныйх тегов - количиство"""

        unique_tags = dict()

        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT unique_tag, count(unique_tag) FROM '{mode}' GROUP BY unique_tag""")
            res = cur.fetchall()
            conn.commit()

            unique_tags = dict()
            for r in res:
                unique_tags[r[0]] = r[1]

        if len(unique_tags) == 1 and None in unique_tags:
            raise SQLException('Уникальных тегов на данный момент нету')
        elif len(unique_tags) > 1 and None in unique_tags:
            del unique_tags[None]
        
        return unique_tags

    def add_tag(self,tag:str, mode:str)->int:
        """Добавление тега в таблицу тегов, и создание нового столбца в таблице. 
    
        Работает тольео если тега еще нету в таблице тегов
        структура таблицы:
            mode_tags - таблица тегов
            mode - таблица с основной информацией
            
        Принимает:
            tag - имя тего который будет добовляться в таблицы
            mode - индификатор таблиц в которые доболвтья тег
            
        Возврощает: 
            1 - тег успешно создан

            -1 - Ошибка: Тег небыл введен
            -2 - Ошибка: Имя состоит только из пробельных символов
            -3 - Ошибка: Тег уже существует"""
        
        if tag == '':
            raise SQLException("Тег небыл введен")
        if re.fullmatch(r'\s*', tag):
            raise SQLException("Тег не может состоять только из пробельных символов")
        
        sql = f"""SELECT '{mode}_tags.name_tag' FROM '{mode}_tags' WHERE name_tag LIKE '{tag}'""" 
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(sql)      
            a = cur.fetchone()
            if a == None:
                sql = f"""INSERT INTO '{mode}_tags'(name_tag) VALUES ('{tag}')"""
                cur.execute(sql)  
                sql = f"""ALTER TABLE '{mode}' ADD {tag} Boolean DEFAULT False"""
                cur.execute(sql)  
                conn.commit()
                raise SQLException('Тег успешно создан и добавлен в бд', True)
            else:
                conn.commit()
                raise SQLException("Такой тег уже существует")
    
    def add_many_tags(self,tags:list, mode:str)->None:
        """Скрипт которой доболвяет множество тегов"""
        all_ex = ''
        i = 0
        for tag in tags:
            try:
                self.add_tag(tag,mode)
            except SQLException as ex:
                if ex.res:
                    i += 1
                    continue
                if ex.text == "Тег небыл введен":
                    pass
                elif ex.text == "Тег не может состоять только из пробельных символов":
                    all_ex += ex.text
                elif ex.text == "Такой тег уже существует":
                    all_ex += f'\n\tТег {tag} уже существует'

        
        if i == 0:
            raise SQLException("Ни один тег не был добавлен. Либо они уже существуют либо что-то пошле не так")
        elif i == len(tags):
            raise SQLException("Все теги успешно добавлены", True)
        elif i > 1 and i < len(tags):
            raise SQLException(f'При добовлении некоторых тегов произошли ошибки: {all_ex}')

    def delet_tag(self, tags:list, mode:str)->int:
        """Удаление тегов из таблицы тего и из таблицы {mode}
    
        В него могут передоваться только существующие теги из-за логики програмы.
        (Желательно все же сделать проверку на существование тегов в таблицы)
        структура таблицы:
            mode_tags - таблица тегов
            mode - таблица с основной информацией
            
        Принимает:
            tags - список тегов которые надо удалить из бд
            mode - из каких таблиц удалять теги
            
        Возврошает:
            -1 - Ошибка: Не выбран ни один тег для удаления
            
            1 - Выбраные теги удалены"""

        if tags == []:
            raise SQLException('Не выбран ни один тег для удаления')
        
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            for tag in tags:
                cur.execute(f"DELETE FROM '{mode}_tags' WHERE name_tag = '{tag}'")
                conn.commit()
                cur.execute(f"ALTER TABLE '{mode}' DROP COLUMN '{tag}'")
                conn.commit()
    
        return 1

    def update_tags(self, tags:dict,mode:str, img:str) -> int:
        """Скрипт который обновляет занчения тегов для опеределеноый картинки"""

        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            for tag, val in tags.items():
                cur.execute(f"""UPDATE {mode} SET {tag} = '{val}' WHERE path = '{img}'""")
                conn.commit()
        return 1
    
    def update_unique_tag(self, unique_tag:str, mode:str, img:str)->None:
        """Обновление уникального тега для текущей картиник"""
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(f"""UPDATE {mode} SET unique_tag = '{unique_tag}' WHERE path = '{img}'""")
            conn.commit()

    def get_request(self,tags:dict,mode:str, switch:bool=False, unique_tag:str = 'None')->list:
        """Поиск изображений с выбраными тегами.

        Принимает:
            tags - словарь тегов для поиска совпадений
                если пустой то показывается вся бд
            mode - из какой таблицы
            
        Возврощает:
            photos - список с путями до изображений с выбраными тегами"""
        

        if switch: x = 'OR'
        else: x = 'AND'



        if tags == {} and  unique_tag == 'None':
            sql = f"""SELECT path FROM {mode}"""
        else:
            sql = f"""SELECT path FROM {mode} WHERE """
            for tag, value in tags.items():
                if value == True:
                    sql = sql + f"""{tag} = 'True' {x} """
                else:
                    sql = sql + f"""{tag} = ({0} or False) {x} """
            if unique_tag == 'None':
                sql = sql.rstrip(f'{x} ')
            else:
                sql += f"""unique_tag = '{unique_tag}'"""
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            photos = self.get_normal_list(cur.fetchall())
            conn.commit()

        if len(photos) == 0:
            raise SQLException(f"В выбраной категроии нету изображений.")
        return photos

    def save_reguset(self,name:str,data:list,mode:str)->int:
        """Функция сохранениея запроса
    
        Принимает:
            #
            # name - имя под которым сохроняется запрос. Уникальное
            # data - списко путей до изображений 
            # mode - в какие таблицы  сохронять
            
        Возврощает:
            1 - Запрос удачно сохранен

            -1 - Ошибка: Нельзя сохранить запрос с таким именим, Имя уже занято
        """
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT 'name_req' FROM '{mode}_save_req' WHERE name_req LIKE '{name}'""" )      
            a = cur.fetchone()
            if a == None:
                sql = f"""INSERT INTO '{mode}_save_req'(name_req, list_req, len_req) VALUES ('{name}', "{data}", '{len(data)}')"""
                cur.execute(sql)
                conn.commit()
                return 1
            else:
                conn.commit()
                raise SQLException('Нельзя сохранить запрос с таким именим, Имя уже занято')

    def get_request_list(self, mode:str)-> dict:
        """Запрос на получение списка всех сохраненых запросов
        
        Принимает:
            mode - из какой таблицы брать запросы 
            
        Возврощает словарь состоящий из: имя запроса - количиство изображений """

        with sqlite3.connect(self.db) as  conn :
            cur = conn.cursor()
            cur.execute(f"""SELECT name_req, len_req FROM '{mode}_save_req'""")
            data = cur.fetchall()
            conn.commit()
            res = dict()
            for row in data:
                res[row[0]] = row[1]


        if res == {}:
            raise SQLException('Нету сохраненых запросов')
        return res

    def download_request(self, name:str,mode:str)->list:
        """Загрузка результата запроса
        
        Принимает:
            name - имя запроса
            mode - из какой таблицы брать
            
        ВОзврощает списк путй до изображений по запросу"""
        
        
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            sql = f"""SELECT list_req FROM '{mode}_save_req' WHERE name_req = '{name}'"""
            
            cur.execute(sql)
            res = cur.fetchone()
            conn.commit()
            ### полуаем в res[0] строку а не список передалать в список тута
            
            l_res = res[0].lstrip('[').rstrip(']').replace("'", '').replace(" ", '').split(',')
        
        return list(map(os.path.abspath,l_res))

    def delete_request(self, naem:str, mode:str) ->int:
        """Скрипт по удалению запроса из бд"""
        
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM '{mode}_save_req' WHERE name_req = '{naem}'")
            conn.commit()

        return 1

    def delete_img(self,mode:str, path:str) -> None:
        """Скрипт на удалении изображения по пути из бд"""

        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            cur.execute(f"""DELETE FROM '{mode}' WHERE path = '{path}'""")
            conn.commit()

            
    def count_tags(self, mode:str) -> None:
        """Подсчитывает количисто записей с каждыйм тегом и записвыает в таблицу тегов"""

        current_c_tags =self.get_tags_lsit_with_count(mode)
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()
            
            for tag, c in current_c_tags.items():
                cur.execute(f"""SELECT count({tag}) FROM photo WHERE {tag} = 'True'""")
                new_c = cur.fetchone()[0]
                conn.commit()
                cur.execute(f"""UPDATE '{mode}_tags' SET count_tag = {new_c} WHERE name_tag = '{tag}'""")
                conn.commit()


