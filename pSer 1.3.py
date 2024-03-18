from screeninfo import get_monitors
from scripts import SQLscripts, SQLException
import flet as ft
import re

#global db
#db = 'C:\\pServ\\pServ2.db'
#test_db = 'C:\\pServ\\test_db.db'
t = 'C:\\pServ\\test.db'
global sc, imgs ,c
sql = SQLscripts(t)
c = 0
imgs = list()


def main():
    """
    Легенда: 
            
        1)  # name_fun1, name_fun2 - используеться перед функцией что бы показать где данная функция используеться или может использоваться
            Примеры:
                #
                # app - может использоваться в любой функции
                # app - испольщуеться в функции app
                # main_menu - используеться в функции main_menu
    """
    # any
    def app_param(page:ft.Page, padding:int)->ft.Page:
        """функция изменения параметров окна.
        
        УЦстонавливает параметры которые меняються от окна к окну.
        Границы
        Расположения и тд"""
        
        page.padding = padding
        return page
    
    # any
    def change_theme(e:ft.ControlEvent,page:ft.Page)->ft.Page:
        """Изменение темы приложения светлай/темная"""
        
        if page.theme_mode == 'dark':
            page.theme_mode = 'light'
            e.control.icon = ft.icons.DARK_MODE
            e.control.tooltip = 'Темная тема'
        else:
            page.theme_mode = 'dark'
            e.control.icon = ft.icons.LIGHT_MODE_OUTLINED
            e.control.tooltip = 'Светлая тема'

        page.update()
        return page
    
    # any
    def alert(page:ft.Page, text:str)->ft.Page:
        """Всплывающее оповещение снизу
        
        Принимает текст - что будет в оповещении"""

        page.snack_bar = ft.SnackBar(content=ft.Text(f'{text}'))
        page.snack_bar.open = True
        page.update()
        return page
    
    # dlg_***
    def close_dlg(page:ft.Page, dlg:ft.AlertDialog) ->ft.Page:
            """Функция закрытия диологового окан """ 

            dlg.content.clean()
            dlg.open = False
            page.update()
            return page
    
    # app
    def get_monitor_wh()->tuple:
        """Возврощает разрешение монитора в виде котрежа
        
        0 - Ширена
        1 - Высота"""
        monitor = get_monitors()
        return (monitor[0].width,monitor[0].height)
    
    # app
    def app_initial_param(page:ft.Page,  width:int = 1920, height:int =1024, title:str = 'pSer 1.3', theme:str = 'dark')->ft.Page:
        """Устоновка основных параетров приложения
        
        Вызывать один раз"""

        page.title = title
        page.window_width = width
        page.window_height = height
        page.theme_mode = theme

        return page
    
    # app
    def main_menu(page:ft.Page)->ft.Page:
        """Главное меню приложения"""

        page = app_param(page, 20)

        menu_top = ft.Row(
            controls= [
                ft.IconButton(icon=ft.icons.DARK_MODE if page.theme_mode == 'light' else ft.icons.LIGHT_MODE_OUTLINED, tooltip='Светлая тема',on_click=lambda e: change_theme(e, page)),
                statistics := ft.IconButton(icon=ft.icons.QUERY_STATS, tooltip='Статистика', disabled= True)
            ],
            alignment=ft.MainAxisAlignment.END
            #alignment= ft.Alignment(1, -1)
        )

        Dropdown_menu = ft.Dropdown(
            options=[ft.dropdown.Option("Изображения"), ft.dropdown.Option("Видео"), ft.dropdown.Option("Манга")],
            label= 'Выберите категорию',
            border_radius= 45,
            width=500,
            #prefix=ft.Icon(ft.icons.HOLIDAY_VILLAGE),
            alignment=ft.Alignment(0,-0.5),
            on_change=lambda e: selected_mode(page)
        )

        pick_file_dlg = ft.FilePicker(on_result= lambda e:pick_file_result(e, page))
        page.overlay.append(pick_file_dlg)
        menu = ft.Row([ft.Column(
            controls=[
                Dropdown_menu,
                add_data_butt := ft.ElevatedButton(text='Добавить',width=500,height=50,disabled=True, on_click= lambda e: pick_file_dlg.get_directory_path()),
                go_view_butt := ft.ElevatedButton(text='Просмотр',width=500,height=50, on_click= lambda e: go_view(page), disabled= True)
            ]
        )],alignment=ft.MainAxisAlignment.CENTER)



        page.add(menu_top,ft.Divider(),menu)
        
        return page

    # selected_mode, pick_file_result, go_view
    def get_mode(page:ft.Page) -> str:
        """Так как у выпадающего меню нету получения текущего выбраного индекса, используем этот метод для разветвления логики программы"""
        mode = page.controls[2].controls[0].controls[0].value
        if mode == "Изображения":   mode = 'photo'
        elif mode == "Видео":       mode = 'video'
        elif mode == "Манга":       mode = 'manga'
        return mode

    # main_menu, pick_file_result
    def selected_mode(page:ft.Page) -> ft.Page:
        """Функция работающая при изменении выпадающего меню.
        
        Проверяет наличие изображений в выбраной категроии"""

        page.controls[2].controls[0].controls[1].disabled = False 
        global imgs
        imgs.clear()
        mode = get_mode(page)
        try:
            imgs = sql.get_request({}, mode)
        except SQLException as ex:
            page = alert(page, ex.text)

        if imgs == []:
            page.controls[2].controls[0].controls[2].disabled = True
        else:
            page.controls[2].controls[0].controls[2].disabled = False
        
        page.update()
        return page

    # main_menu 
    def pick_file_result(e:ft.FilePickerUploadEvent, page:ft.Page) -> ft.Page:
        """Оброботка результата полученого через выбар фала
        
        Звпус скрипта"""
        mode = get_mode(page)
        try:
            sql.append_db(e.path, mode)
        except SQLException as ex:
            page = alert(page, ex.text)
            if ex.res:
                page = selected_mode(page)
            

        return page

    # main_menu
    def go_view(page:ft.Page)->ft.Page:
        """Функция перехода к Просмотру
        
        e - ивент нажатия кнопки перехода,
        page - страница
        mode - выьраный режим в Dropdown_menu в main_menu"""
        mode = get_mode(page)
        sql.count_tags(mode)
        page.clean()
        page = view_menu(page=page, mode= mode)
        return page
    
    # go_view
    def view_menu(page:ft.Page, mode:str)-> ft.Page:
        """Меню просмотра выбраного режима"""
        global imgs
        try:
            imgs = sql.get_request({},mode)
        except SQLException as ex:
            page = alert(page, ex.text)
        page = app_param(page=page, padding= 20)
        page = appbar_view(page=page, mode=mode) 
        page = bottom_appbar_view(page=page,mode=mode)
 
        img_show  = ft.Image(src=imgs[c], width=page.window_width, height=page.window_height - 200) 
        
        page.add(img_show)
        return page
    
    # view_menu
    def appbar_view(page:ft.Page, mode:str)->ft.Page:
        """Верхнее паенль кнопок для режима просмотра 
        
        Астивные кнопки:
            +leading - кнопка запроса к бд по тегам (выборка изображений по тегам)
            +theme_butt - кнопка смены темы приложения светлая/теманя
            edit_tag_menu - выпадающий список действий с тегами:
                add_tag - добваить тег в таблицы mode
                delet_tag - удалить тег из таблиц mode
            request_menu - выпадающее меню работы с запросами:
                save_req - сохранение запроса в бд
                load_req - загрузка запроса в бд (открытие панели с права в которой будет списко из кнопок каждая будет отвечать за заггрузку соответсвующего запросва)
                delet_req - удалене запроса из бд (аналогично загрузки)
            go_main_butt - кнопка возврата вглавное меню

        Левая панель:
        В этой панели прокручеваемывй список чекбоксов по тегам
        Каждый чек бок имее  положения: Искать по, исключать, неважно
        Так же есть кнопка найти - находит все изображения в бд по текущем значением тегов
        search_field - текстовое поле при каждом изменении которого остаютьсятольок теги с введенм сопадением (обычный поиск)
            """
        # +left_panel
        page.drawer = ft.NavigationDrawer(
            controls= [
                ft.TextField(label='Search...', on_change=lambda e: search_tag(e,page)),
                ft.Switch(label='И/ИЛИ переключатель', value=False),
                ft.ElevatedButton(icon=ft.icons.FIND_IN_PAGE, text='Натйи',on_click=lambda e: get_request(page,mode)),
                ft.Dropdown(
                    value='Уникальный тег',
                    label = 'unique tag',
                    #alignment=ft.Alignment(0,-0.5),
                    options=[],
                    width= 50,
                    border_radius=20,
                    hint_text='Выбирети уникальный тег'
                ),
                ft.ListView(width=150, padding=20),
                ft.ElevatedButton(icon=ft.icons.FIND_IN_PAGE, text='Натйи',on_click=lambda e: get_request(page,mode)),
            ],
            on_dismiss= lambda e: close_left_panel(page)
        )
        # +
        edit_tag_menu = ft.PopupMenuButton(
            icon=ft.icons.TAG,
            tooltip='Редактирование тегов',
            items=[
                add_tag := ft.PopupMenuItem(icon=ft.icons.ADD_BOX, text='Добавить тег', on_click= lambda e: dlg_add_tag(page,mode)),
                add_tags := ft.PopupMenuItem(icon=ft.icons.LIBRARY_ADD, text='Добавить теги', on_click= lambda e: dlg_add_many_tags(page,mode) ),
                delet_tag := ft.PopupMenuItem(icon=ft.icons.DELETE, text='Удалить тег', on_click= lambda e: dlg_delet_tag(page, mode))
            ]
        )
        # +right_panel
        page.end_drawer = ft.NavigationDrawer(
            controls= [
                ft.TextField(label="Search...", on_change= lambda e: search_request(e,page)),
                ft.ListView(width=150, padding=20)
            ],
            on_dismiss= lambda e: close_right_panel(page)
        )
        # +
        request_menu = ft.PopupMenuButton(
            icon=ft.icons.REQUEST_PAGE,
            tooltip='Работа с запросами',
            items=[
                save_req := ft.PopupMenuItem(icon=ft.icons.SAVE, text='Сохранить текущей запрос', on_click= lambda e: dlg_save_request(page,mode)),
                load_req := ft.PopupMenuItem(icon=ft.icons.FILE_DOWNLOAD, text='Загрузить запрос', on_click=lambda e: open_right_panel(page,mode,True)),
                delet_req := ft.PopupMenuItem(icon=ft.icons.DELETE, text='Удалить запрос', on_click=lambda e: open_right_panel(page,mode,False))
            ]
        )

        page.appbar = ft.AppBar(
            title= ft.Text(f"Модуль {mode}"),
            leading= ft.IconButton(ft.icons.SEARCH,tooltip='Поиск по тегам', on_click=lambda e: open_left_panel(page, mode)),
            leading_width=40,
            actions= [
                theme_butt := ft.IconButton(icon=ft.icons.DARK_MODE if page.theme_mode == 'light' else ft.icons.LIGHT_MODE_OUTLINED, tooltip='Светлая тема', on_click=lambda e: change_theme(e, page)),
                #ft.IconButton(icon=ft.icons.GRID_VIEW_SHARP, tooltip='Отображение сеткой', on_click= lambda e : grid_view_img(page)),
                edit_tag_menu,
                request_menu,
                go_main_butt := ft.IconButton(ft.icons.HOME, tooltip='Вернуться на главное меню', on_click=lambda e: go_main(page))
            ]
        )
        
        return page
   
    # appbar_view
    def go_main(page:ft.Page)->ft.Page:
        """Возврат в главнео меню"""
        
        page.appbar.visible = False
        page.bottom_appbar.visible = False
        page.clean()
        
        page = main_menu(page=page)
        return page
    
    # appbar_view
    def open_left_panel(page:ft.Page, mode:str)->ft.Page:
        """Открытие левой панели"""

        
        try:
            u_tags =sql.get_unique_tags(mode)
        except SQLException as ex:
            page.drawer.controls[3].label = 'Нету уникальных тегов'
        else:
            page.drawer.controls[3].options.append(ft.dropdown.Option(f"Уникальный тег"))
            for u_tag, count in u_tags.items():
                page.drawer.controls[3].options.append(ft.dropdown.Option(f"{u_tag} ({count})"))

        try:
            tags = sql.get_tags_lsit_with_count(mode=mode)
        except SQLException as ex:
            page = alert(page, ex.text)
            return page
        else:
            for tag, count in tags.items():
                page.drawer.controls[4].controls.append(ft.Checkbox(label=f'{tag} ({count})', value=False,tristate=True))
            page.drawer.open=True
            page.drawer.update()    
            return page

    # appbar_view, open_left_panel
    def close_left_panel(page:ft.Page)->ft.Page:
        """Закрытие левой панели"""

        page.drawer.controls[3].options.clear()
        page.drawer.controls[3].value = 'Уникальный тег'
        page.drawer.controls[4].clean()
        page.drawer.controls[0].value = ''
        page.drawer.open = False
        page.drawer.update()
        return page
    
    # appbar_view
    def get_request(page:ft.Page, mode:str) ->ft.Page:
        """Получает список путей по запросу """
        
        switch = page.drawer.controls[1].value
        unique_tag = page.drawer.controls[3].value
        if unique_tag == None or unique_tag == 'Уникальный тег':
            unique_tag = 'None'
        else:
            unique_tag = unique_tag.split(' ')[0]
        global imgs,c
        req_in = ''
        req_out = ''

        tags = dict()
        t_count = 0 # Счетчик для выбраных тегов, неважно исключить или включить
        f_count = 0 # Счетчик для невыбраных тегов
        for box in page.drawer.controls[4].controls:
            box_label = box.label.split(' ')[0]
            if box.value == None:
                tags[box_label] = False
                t_count +=1
                req_out += f'{box_label}, '
            elif box.value == True:
                tags[box_label] = True
                t_count += 1
                req_in += f'{box_label}, '
            else:
                f_count += 1
                pass
       
        req_in = req_in.rstrip(', ')
        req_out = req_out.rstrip(', ')
        req = f'Запрос - Включить: {req_in}; Исключить: {req_out}.'
        try:
            imgs = sql.get_request(tags,mode,switch,unique_tag)
        except SQLException as ex:
            page = alert(page,ex.text)
            imgs = []
            page.controls[0].src = 'D:\\pServ_Storege\\system\\no_img.jpg'          
        else:
            page = alert(page, 'Запрос успешно выполнен')
            c = 0
            page.controls[0].src = imgs[c]
        
        if t_count == 0:
            req = f'Модуль {mode}'
        page.appbar.title = ft.Text(req)
        page = close_left_panel(page)
        page.update()
        return page

    # appbar_view
    def search_tag(e: ft.ControlEvent, page:ft.Page) ->ft.Page:
        """Поиск тегов в списке"""
        pattern = e.control.value
        pattern = pattern.lower() + r'.?'
        
        for box in page.drawer.controls[4].controls:
            if isinstance(box,ft.Checkbox):
                if re.search(pattern, box.label):
                    box.visible = True
                else:
                    box.visible = False
        page.drawer.update()
        return page

    # appbar_view
    def dlg_add_tag(page:ft.Page, mode:str) -> ft.Page:
        """Открывает диалоговое окно на ввод название нового тега"""

        def confirm(page:ft.Page, dlg:ft.AlertDialog, mode:str)->ft.Page:
            """Функция доболения тега в бд"""

            try:
                sql.add_tag(dlg.content.value, mode)
            except SQLException as ex:
                page = alert(page,ex.text)
            
            page = close_dlg(page, dlg)
            return page

        tag_name = ft.AlertDialog(
            modal=True,
            title= ft.Text('Добавление тега'),
            content=ft.TextField(label='Введите название тега...'),
                actions=[
                    ft.ElevatedButton(icon=ft.icons.CANCEL, text='Отмена', on_click=lambda e: close_dlg(page,tag_name)),
                    ft.ElevatedButton(icon=ft.icons.ADD, text='Добавить', on_click=lambda e: confirm(page,tag_name, mode))
                ],
                open=True
        )
        page.dialog = tag_name
        page.update()
        return page

    # appbar_view
    def dlg_add_many_tags(page:ft.Page, mode:str) -> ft.Page:
        """Диолог на добавления множество тегов"""
        
        c = 1
        def add_tag_field(page:ft.Page, dlg:ft.AlertDialog)->ft.Page:
            """Добавление нового поля для тега"""   
            nonlocal c
            c +=1
            last_tag =[]
            for tag in dlg.content.controls:
                last_tag.append(tag.value)
            last_tag.append(None)
            dlg.content = ft.ListView(expand=1, spacing= 10, padding= 10,controls=[ft.TextField(label='Введите тег..', value=last_tag[i]) for i in range(c)])
            dlg.open = True
            dlg.update()
            #page.update()
            return page

        def confirm(page:ft.Page, dlg:ft.AlertDialog, mode:str)->ft.Page:
            """Функция доболения тега в бд"""
            tags = list()
            for tag in dlg.content.controls:
                tags.append(tag.value)
            try:
                sql.add_many_tags(tags,mode)
            except SQLException as ex:
                page = alert(page,ex.text)

            page = close_dlg(page, dlg)
            return page
        
    
        tags_name = ft.AlertDialog(
            modal= True,
            title=ft.Text('Добавление нескольких тегов'),
            content= ft.ListView(expand=1,spacing= 10, padding= 10,controls=[ft.TextField(label='Введите тег..',) for i in range(c)]),
            actions= [
                ft.Row([
                    ft.ElevatedButton(icon=ft.icons.CANCEL, text='Отмена', on_click=lambda e: close_dlg(page,tags_name)),
                    ft.ElevatedButton(icon=ft.icons.ADD, text='Добавить тег', on_click=lambda e: add_tag_field(page,tags_name)),
                    ft.ElevatedButton(icon=ft.icons.SAVE, text='Сохранить теги', on_click=lambda e: confirm(page,tags_name,mode))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ],
            open=True
        )

        page.dialog = tags_name
        page.update()
        return page
    # appbar_view
    def dlg_delet_tag(page: ft.Page, mode:str) ->ft.Page:
        """Открытие диологового окна на удаление тега/тегов"""
        
        def delete(page:ft.Page, dlg:ft.AlertDialog, mode:str)->ft.Page:
            """Удаление тегов из бд"""

            tags_delet = list()
            for box in dlg.content.controls:
                if box.value == True:
                    tags_delet.append(box.label)

            try:
                sql.delet_tag(tags_delet,mode)
            except SQLException as ex:
                page = alert(page, ex.text)
            else:
                page = alert(page, 'Выбраные теги удалены')
            close_dlg(page,dlg)
            return page


        try:
            tags_list = sql.get_tags_list(mode)
        except SQLException as ex:
            page = alert(page,ex.text)
            return page
        else:
            delet_tag = ft.AlertDialog(
                modal=True,
                title=ft.Text('Выберите теги которые надо удалить'),
                content=ft.ListView(
                    expand=1, 
                    auto_scroll=True, 
                    padding=20, 
                    controls= [ft.Checkbox(label=tag, value=False) for tag in tags_list]),
                actions= [ft.Row(
                        controls=[
                            ft.ElevatedButton(icon=ft.icons.CANCEL, text='Отмена',on_click= lambda e: close_dlg(page,delet_tag)),
                            ft.ElevatedButton(icon=ft.icons.DELETE, text='Удалить',on_click= lambda e: delete(page, delet_tag, mode))
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ],
                open=True
            )
            
            #for tag in sql.get_tags_list(mode):
            #    delet_tag.content.controls.append(ft.Checkbox(label=tag, value=False))
            page.dialog = delet_tag
            page.update()
            return page

    # appbar_view
    def dlg_save_request(page:ft.Page, mode:str) -> ft.Page:
        """Сохранение текущего запроса в бд"""

        def save(page: ft.Page, dlg:ft.AlertDialog, mode:str) -> ft.Page:
            """Сохранения сапроса в бд"""

            global imgs
            name_req = dlg.content.value
            if name_req == '':
                name_req = dlg.content.label

            try:
                sql.save_reguset(name_req,imgs,mode)
            except SQLException as ex:
                page = alert(page, ex.text)
            else:
                page = alert(page, f"Запрос усешно сохронен по именем - {name_req}")

            page.appbar.title.value = f'Запрос - {name_req}'
            page = close_dlg(page,dlg)
            return page

        if page.appbar.title.value == f"Модуль {mode}":
            page = alert(page, 'Запрос небыл введен')
            return page

        save_req = ft.AlertDialog(
            modal= True,
            title=ft.Text('Сохранение запроса'),
            content= ft.TextField(label=page.appbar.title.value.lstrip('Запрос - ')),
            actions= [ft.Row(
                controls= [
                    ft.ElevatedButton(icon=ft.icons.CANCEL, text='Отмена', on_click= lambda e: close_dlg(page,save_req)),
                    ft.ElevatedButton(icon=ft.icons.SAVE, text='Сохранить', on_click=lambda e: save(page,save_req, mode))
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )],
            open=True
        )
        page.dialog = save_req
        page.update()
        return page

    # appbar_view
    def open_right_panel(page:ft.Page, mode:str,save:bool=True)->ft.Page:
        """Функция открытия правой панели
        
        save - параметр отвечающй за то будет ли правая панель рабоать на сохранение или за удаление
            save = True - сохранение
            save = False - удаление"""
        global imgs
        def confirm_load(e: ft.ControlEvent,page:ft.Page, mode:str)->ft.Page:
            """Загрузить запрос при нажатии на соответствующую скопку"""

            global imgs, c
            name_req = e.control.text.lstrip("Загрузить ")
            imgs = sql.download_request(name_req, mode)
            c = 0
            page.controls[0].src = imgs[c]
            page = close_right_panel(page)
            page = alert(page, f'Запрос {name_req} успешно загружен')
            page.appbar.title.value = f"Запрос - {name_req}"
            page.update()
            return page

        def confirm_delete(e: ft.ControlEvent,page:ft.Page, mode:str)->ft.Page:
            """Удалить запрос при нажатии на соответствующую скопку"""
            
            name_req = e.control.text.lstrip("Удалить ")
            sql.delete_request(name_req,mode)
            page = close_right_panel(page)
            page = alert(page,f"Запрос {name_req} успешно удален")
            return page


        try:
            req_list = sql.get_request_list(mode)
        except SQLException as ex:
            page = alert(page, ex.text)
        else:
            if save:
                for req in req_list:
                    page.end_drawer.controls[1].controls.append(ft.ElevatedButton(icon=ft.icons.DOWNLOAD, text=f"Загрузить {req}", on_click=lambda e:confirm_load(e,page,mode)))
            else:
                for req in req_list: 
                    page.end_drawer.controls[1].controls.append(ft.ElevatedButton(icon=ft.icons.DELETE, text=f"Удалить {req}", on_click=lambda e:confirm_delete(e,page,mode)))
        
            page.end_drawer.open = True
            page.end_drawer.update()
        return page

    # appbar_view, open_right_panel
    def close_right_panel(page:ft.Page) -> ft.Page:
        """Функция закрытия правой панели"""

        page.end_drawer.controls[1].clean()
        page.end_drawer.controls[0].value = ''
        page.end_drawer.open = False
        page.end_drawer.update()
        return page

    # appbar_view
    def search_request(e: ft.ControlEvent,page:ft.Page):
        """Поиск  сохроненого запроса по имени"""

        pattern = e.control.value
        pattern = pattern.lower() + r'.?'
        for butt in page.end_drawer.controls[1].controls:
            if isinstance(butt,ft.ElevatedButton):
                if butt.icon == 'download':
                    s = butt.text.lstrip("Загрузить ")
                elif butt.icon == 'delete':
                    s = butt.text.lstrip("Удалить ")

                if re.search(pattern, s):
                    butt.visible = True
                else:
                    butt.visible = False

        page.end_drawer.update()
        return page
    
    # appbar_view
    def grid_view_img(page:ft.Page)->ft.Page:
        """Изменяет отображение выбраного запроса на сетку картинок"""
        print(page.controls[0])
        page.controls[0].__delattr__()
        page.update()
        return page

    # view_menu
    def bottom_appbar_view(page:ft.Page, mode:str) -> ft.Page:
        """Нижняя панель режима просмотра"""
        
        global imgs, c
        # +
        page.bottom_appbar = ft.BottomAppBar(
            content= ft.Row([
                    ft.IconButton(ft.icons.SKIP_PREVIOUS, tooltip='Предыдущие изображение', on_click= lambda e: slide_img_butt(page,False)),
                    ft.IconButton(icon=ft.icons.DELETE, tooltip='Удалить текущее изображение', on_click= lambda e: delete_img(page,mode)),
                    ft.IconButton(ft.icons.EDIT, tooltip='Редактировать информацию о фотогррафии', on_click= lambda e:open_bottom_panel(page,mode)),                   
                    ft.IconButton(ft.icons.SKIP_NEXT, tooltip='Слудующее изхображение', on_click= lambda e: slide_img_butt(page,True))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

        # +bottom_panel
        edit_img_panel = ft.BottomSheet(
            content=ft.Container(
                ft.Column(controls=[
                    ft.Container(height=10),
                    ft.Row([ft.Text('Выберите нужные теги',size=15, weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER),
                    ft.TextField(label='Уникальный тег'),
                    ft.ListView(expand=1,padding=10),
                    ft.Row(controls=[
                        ft.ElevatedButton(icon=ft.icons.CANCEL, text='Назад', on_click=lambda e: close_bottom_panel(page)),
                        ft.ElevatedButton(icon=ft.icons.SAVE, text='Сохранить', on_click= lambda e: save_edit_img(page,mode))],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(height=20)
                ])
            ),
            on_dismiss=lambda e :close_bottom_panel(page),
            
        )

        page.overlay.append(edit_img_panel)
        return page

    # bottom_appbar_view
    def slide_img_butt(page:ft.Page, next_img:bool=True) -> ft.Page:
        """Функция пролистования изображения следующее/предыдущее
        
        next_img = True - следущее изображение
        next_img = False - предыдущее изображение"""

        global imgs, c
        if imgs == []:
            page = alert(page,'Нету изображений')
            page.update()
            return page

        if next_img:
            c = (c + 1) % len(imgs)
        else:
            c = (c - 1) % len(imgs)
        page.controls[0].src = imgs[c]
        page.update()
        return page

    def delete_img(page:ft.Page, mode:str) -> ft.Page:
        """Удаление текущего изображения"""

        global imgs
        if imgs == []:
            page = alert(page,"Удалять нечего")
            return page
        
        def confirm_delete(page:ft.Page,dlg:ft.AlertDialog, mode:str) -> ft.Page:
            """Потверждение удаление изорбражения"""

            global imgs,c
            

            sql.delete_img(mode, imgs[c])
            imgs = sql.get_request({}, mode)
            c = 0 
            page.controls[0].src = imgs[c]
            page = close_dlg(page,dlg)
            return page
            

        delete_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text('Удаление изображения'),
            content= ft.Text('Изображение удаляеться из бд, а не с компьютора.\nВы точно хотите удалить даное изображение?'),
            actions= [ft.Row(
                controls= [
                    ft.ElevatedButton(icon=ft.icons.CANCEL, text='Отмена', on_click= lambda e: close_dlg(page,delete_dlg)),
                    ft.ElevatedButton(icon=ft.icons.DELETE,text='Удалить', on_click= lambda e: confirm_delete(page, delete_dlg, mode))
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )],
            open=True
        )
        page.dialog = delete_dlg
        page.update()
        return page
    # bottom_appbar_view
    def open_bottom_panel(page:ft.Page, mode:str) -> ft.Page:
        """Открытие нижней понели для редактирование изображения"""
        global imgs, c
        if imgs == []:
            page = alert(page, 'Нечего редактировать')
            return page
        
        try:
            unique_tag = sql.get_unique_tag(mode,page.controls[0].src)
        except SQLException as ex:
            pass
        else:
            page.overlay[1].content.content.controls[2].value = unique_tag

        try:
            tags_dict = sql.get_tags_list_with_val(mode,page.controls[0].src)
        except SQLException as ex:
            page = alert(page, ex.text)
            return page
        else:
            for tag, val in tags_dict.items():
                page.overlay[1].content.content.controls[3].controls.append(ft.Checkbox(label=tag, value=val))
            

            page.overlay[1].open = True
            #page.overlay[0].update()
            page.update()
            return page
    
    # bottom_appbar_view, save_edit_img
    def close_bottom_panel(page:ft.Page)->ft.Page:
        """Закрытие понели снизу"""

        
        page.overlay[1].open = False
        page.overlay[1].content.content.controls[3].clean()
        page.update()
        return page
    
    # bottom_appbar_view
    def save_edit_img(page:ft.Page, mode:str)->ft.Page:
        """Сохранение тегов изображения в бд"""
        
        global imgs, c
        save_tags = dict()
        for box in page.overlay[1].content.content.controls[3].controls:
            if isinstance(box, ft.Checkbox):
                save_tags[box.label] = box.value

        unique_tag = page.overlay[1].content.content.controls[2].value
        sql.update_unique_tag(unique_tag,mode, page.controls[0].src)
        sql.update_tags(save_tags,mode, page.controls[0].src)
        sql.count_tags(mode)
        page  = alert(page, 'Теги для текущего изображения успешно сохранены')
        page = close_bottom_panel(page)
        return page
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # main
    def app(page: ft.Page):
        """Функцифя приложения"""
        

        
        max_width, max_height = get_monitor_wh()
        page = app_initial_param(page= page, width=max_width,height=max_height)
        
        page = main_menu(page)
       

    ft.app(target=app)
    pass


if __name__ == '__main__':
    main()