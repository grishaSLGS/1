import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from PIL import Image, ImageTk
import os

class Database:
    """Класс для работы с базой данных"""
    def __init__(self, db_name='educational_institutions.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Создание таблиц в базе данных"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS institutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT,
                address TEXT,
                director TEXT,
                phone TEXT,
                email TEXT,
                website TEXT,
                image_path TEXT,
                registration_date TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT,
                region TEXT,
                city TEXT,
                district TEXT,
                street TEXT,
                house TEXT,
                apartment TEXT,
                postal_code TEXT
            )
        ''')
        
        self.conn.commit()
    
    def add_institution(self, data):
        """Добавление учебного заведения"""
        self.cursor.execute('''
            INSERT INTO institutions 
            (name, type, address, director, phone, email, website, image_path, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, date('now'))
        ''', data)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_institution(self, institution_id, data):
        """Обновление данных учебного заведения"""
        self.cursor.execute('''
            UPDATE institutions 
            SET name=?, type=?, address=?, director=?, phone=?, email=?, website=?, image_path=?
            WHERE id=?
        ''', (*data, institution_id))
        self.conn.commit()
    
    def delete_institution(self, institution_id):
        """Удаление учебного заведения"""
        self.cursor.execute('DELETE FROM institutions WHERE id=?', (institution_id,))
        self.conn.commit()
    
    def get_institution(self, institution_id):
        """Получение данных учебного заведения по ID"""
        self.cursor.execute('SELECT * FROM institutions WHERE id=?', (institution_id,))
        return self.cursor.fetchone()
    
    def search_institutions(self, search_term):
        """Поиск учебных заведений"""
        self.cursor.execute('''
            SELECT * FROM institutions 
            WHERE name LIKE ? OR address LIKE ? OR director LIKE ? OR phone LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        return self.cursor.fetchall()
    
    def get_all_institutions(self):
        """Получение всех учебных заведений"""
        self.cursor.execute('SELECT * FROM institutions')
        return self.cursor.fetchall()
    
    def add_address(self, data):
        """Добавление адреса в справочник"""
        self.cursor.execute('''
            INSERT INTO addresses 
            (country, region, city, district, street, house, apartment, postal_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_addresses(self):
        """Получение всех адресов из справочника"""
        self.cursor.execute('SELECT * FROM addresses')
        return self.cursor.fetchall()
    
    def close(self):
        """Закрытие соединения с базой данных"""
        self.conn.close()

class InstitutionDetailsDialog(tk.Toplevel):
    """Диалоговое окно с полной информацией об учебном заведении"""
    def __init__(self, parent, institution_data):
        super().__init__(parent)
        self.title("Подробная информация")
        
        # Список полей для отображения
        fields = [
            ("Название:", institution_data[1]),
            ("Тип:", institution_data[2]),
            ("Адрес:", institution_data[3]),
            ("Директор:", institution_data[4]),
            ("Телефон:", institution_data[5]),
            ("Email:", institution_data[6]),
            ("Веб-сайт:", institution_data[7]),
            ("Дата регистрации:", institution_data[9])
        ]
        
        # Создаем лейблы в цикле
        for i, (label_text, value) in enumerate(fields):
            ttk.Label(self, text=label_text).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(self, text=value).grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Изображение
        if institution_data[8] and os.path.exists(institution_data[8]):
            try:
                image = Image.open(institution_data[8])
                image.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(image)
                img_label = ttk.Label(self, image=photo)
                img_label.image = photo
                img_label.grid(row=0, column=2, rowspan=len(fields), padx=10, pady=10)
            except Exception as e:
                print(f"Ошибка загрузки изображения: {e}")

class AddressBookDialog(tk.Toplevel):
    """Диалоговое окно справочника адресов"""
    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Справочник адресов")
        self.db = db
        
        self.tree = ttk.Treeview(self, columns=('country', 'region', 'city', 'district', 'street'), show='headings')
        self.tree.heading('country', text='Страна')
        self.tree.heading('region', text='Регион')
        self.tree.heading('city', text='Город')
        self.tree.heading('district', text='Район')
        self.tree.heading('street', text='Улица')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.load_addresses()
        
        select_btn = ttk.Button(self, text="Выбрать", command=self.select_address)
        select_btn.pack(pady=5)
    
    def load_addresses(self):
        """Загрузка адресов из базы данных"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for address in self.db.get_addresses():
            self.tree.insert('', tk.END, values=address[1:6])
    
    def select_address(self):
        """Выбор адреса из справочника"""
        selected_item = self.tree.focus()
        if selected_item:
            self.selected_address = self.tree.item(selected_item)['values']
            self.destroy()

class InstitutionForm(tk.Toplevel):
    """Форма для добавления/редактирования учебного заведения"""
    def __init__(self, parent, db, institution_id=None):
        super().__init__(parent)
        self.db = db
        self.institution_id = institution_id
        self.image_path = None
        
        # Список полей формы
        self.fields = [
            ("Название:", "name_entry", ttk.Entry),
            ("Тип:", "type_combobox", ttk.Combobox, {"values": ["Школа", "Колледж", "Университет", "Лицей", "Гимназия"]}),
            ("Адрес:", "address_entry", ttk.Entry),
            ("Директор:", "director_entry", ttk.Entry),
            ("Телефон:", "phone_entry", ttk.Entry),
            ("Email:", "email_entry", ttk.Entry),
            ("Веб-сайт:", "website_entry", ttk.Entry),
            ("Изображение:", "image_btn", ttk.Button, {"text": "Выбрать изображение", "command": self.select_image})
        ]
        
        # Создаем элементы интерфейса
        self.create_widgets()
        
        if institution_id:
            self.title("Редактирование учебного заведения")
            self.load_institution_data()
        else:
            self.title("Добавление учебного заведения")
    
    def create_widgets(self):
        """Создание элементов интерфейса формы"""
        for i, (label_text, attr_name, widget_class, *args) in enumerate(self.fields):
            # Создаем лейбл
            ttk.Label(self, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            
            # Создаем виджет
            kwargs = args[0] if args else {}
            widget = widget_class(self, **kwargs)
            widget.grid(row=i, column=1, padx=5, pady=5, sticky=tk.EW)
            
            # Сохраняем ссылку на виджет как атрибут
            setattr(self, attr_name, widget)
            
            # Особый случай для адреса - добавляем кнопку справочника
            if attr_name == "address_entry":
                address_book_btn = ttk.Button(self, text="Справочник адресов", command=self.open_address_book)
                address_book_btn.grid(row=i, column=2, padx=5, pady=5)
        
        # Поле для изображения
        self.image_label = ttk.Label(self)
        self.image_label.grid(row=len(self.fields), column=0, columnspan=3, padx=5, pady=5)
        
        # Кнопка сохранения
        save_btn = ttk.Button(self, text="Сохранить", command=self.save_institution)
        save_btn.grid(row=len(self.fields)+1, column=1, padx=5, pady=10, sticky=tk.E)
        
        self.grid_columnconfigure(1, weight=1)
    
    def load_institution_data(self):
        """Загрузка данных учебного заведения для редактирования"""
        institution = self.db.get_institution(self.institution_id)
        if institution:
            self.name_entry.insert(0, institution[1])
            self.type_combobox.set(institution[2])
            self.address_entry.insert(0, institution[3])
            self.director_entry.insert(0, institution[4])
            self.phone_entry.insert(0, institution[5])
            self.email_entry.insert(0, institution[6])
            self.website_entry.insert(0, institution[7])
            self.image_path = institution[8]
            
            if self.image_path and os.path.exists(self.image_path):
                self.display_image(self.image_path)
    
    def open_address_book(self):
        """Открытие справочника адресов"""
        dialog = AddressBookDialog(self, self.db)
        self.wait_window(dialog)
        
        if hasattr(dialog, 'selected_address'):
            address = ", ".join(filter(None, dialog.selected_address))
            self.address_entry.delete(0, tk.END)
            self.address_entry.insert(0, address)
    
    def select_image(self):
        """Выбор изображения для учебного заведения"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
    
    def display_image(self, file_path):
        """Отображение выбранного изображения"""
        try:
            image = Image.open(file_path)
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
    
    def save_institution(self):
        """Сохранение данных учебного заведения"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Название учебного заведения обязательно")
            return
        
        data = (
            name,
            self.type_combobox.get().strip(),
            self.address_entry.get().strip(),
            self.director_entry.get().strip(),
            self.phone_entry.get().strip(),
            self.email_entry.get().strip(),
            self.website_entry.get().strip(),
            self.image_path
        )
        
        if self.institution_id:
            self.db.update_institution(self.institution_id, data)
            messagebox.showinfo("Успех", "Данные учебного заведения обновлены")
        else:
            self.db.add_institution(data)
            messagebox.showinfo("Успех", "Учебное заведение добавлено")
        
        self.destroy()

class MainApp(tk.Tk):
    """Главное окно приложения"""
    def __init__(self):
        super().__init__()
        self.title("Реестр учебных заведений")
        self.geometry("1000x600")
        
        self.db = Database()
        self.create_widgets()
        self.load_institutions()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Панель инструментов
        toolbar_buttons = [
            ("Добавить", self.add_institution),
            ("Редактировать", self.edit_institution),
            ("Удалить", self.delete_institution),
            ("Обновить", self.load_institutions),
            ("Подробности", self.show_details)
        ]
        
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        for text, command in toolbar_buttons:
            btn = ttk.Button(toolbar, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=2)
        
        # Поиск
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_btn = ttk.Button(search_frame, text="Найти", command=self.search_institutions)
        search_btn.pack(side=tk.LEFT)
        
        # Таблица с учебными заведениями
        columns = [
            ('name', 'Название', 150),
            ('type', 'Тип', 80),
            ('address', 'Адрес', 200),
            ('director', 'Директор', 120),
            ('phone', 'Телефон', 100),
            ('email', 'Email', 120),
            ('website', 'Веб-сайт', 150)
        ]
        
        self.tree = ttk.Treeview(self, columns=[col[0] for col in columns], show='headings')
        
        for col_name, col_text, width in columns:
            self.tree.heading(col_name, text=col_text)
            self.tree.column(col_name, width=width)
        
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Двойной клик для просмотра подробностей
        self.tree.bind("<Double-1>", lambda e: self.show_details())
    
    def load_institutions(self):
        """Загрузка списка учебных заведений"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for institution in self.db.get_all_institutions():
            self.tree.insert('', tk.END, values=institution[1:8], iid=institution[0])
    
    def search_institutions(self):
        """Поиск учебных заведений"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_institutions()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for institution in self.db.search_institutions(search_term):
            self.tree.insert('', tk.END, values=institution[1:8], iid=institution[0])
    
    def get_selected_institution_id(self):
        """Получение ID выбранного учебного заведения"""
        selected_item = self.tree.focus()
        if selected_item:
            return int(selected_item)
        return None
    
    def get_selected_institution_data(self):
        """Получение данных выбранного учебного заведения"""
        institution_id = self.get_selected_institution_id()
        if institution_id:
            return self.db.get_institution(institution_id)
        return None
    
    def add_institution(self):
        """Добавление нового учебного заведения"""
        form = InstitutionForm(self, self.db)
        self.wait_window(form)
        self.load_institutions()
    
    def edit_institution(self):
        """Редактирование учебного заведения"""
        institution_id = self.get_selected_institution_id()
        if institution_id:
            form = InstitutionForm(self, self.db, institution_id)
            self.wait_window(form)
            self.load_institutions()
        else:
            messagebox.showwarning("Предупреждение", "Выберите учебное заведение для редактирования")
    
    def delete_institution(self):
        """Удаление учебного заведения"""
        institution_id = self.get_selected_institution_id()
        if institution_id:
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранное учебное заведение?"):
                self.db.delete_institution(institution_id)
                self.load_institutions()
        else:
            messagebox.showwarning("Предупреждение", "Выберите учебное заведение для удаления")
    
    def show_details(self):
        """Просмотр подробной информации об учебном заведении"""
        institution_data = self.get_selected_institution_data()
        if institution_data:
            InstitutionDetailsDialog(self, institution_data)
        else:
            messagebox.showwarning("Предупреждение", "Выберите учебное заведение для просмотра")
    
    def on_closing(self):
        """Действия при закрытии приложения"""
        self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()