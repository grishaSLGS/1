import sqlite3
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Создание базы данных
def create_db():
    conn = sqlite3.connect('educational_institutions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS institutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT,
            image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Класс для работы с формами
class InstitutionForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление учебными заведениями")

        self.name_label = Label(root, text="Название")
        self.name_label.grid(row=0, column=0)
        self.name_entry = Entry(root)
        self.name_entry.grid(row=0, column=1)

        self.address_label = Label(root, text="Адрес")
        self.address_label.grid(row=1, column=0)
        self.address_entry = Entry(root)
        self.address_entry.grid(row=1, column=1)

        self.phone_label = Label(root, text="Телефон")
        self.phone_label.grid(row=2, column=0)
        self.phone_entry = Entry(root)
        self.phone_entry.grid(row=2, column=1)

        self.image_label = Label(root, text="Изображение")
        self.image_label.grid(row=3, column=0)
        self.image_button = Button(root, text="Загрузить изображение", command=self.load_image)
        self.image_button.grid(row=3, column=1)

        self.save_button = Button(root, text="Сохранить", command=self.save_institution)
        self.save_button.grid(row=4, column=0, columnspan=2)

        self.tree = ttk.Treeview(root, columns=('name', 'address', 'phone'), show='headings')
        self.tree.heading('name', text='Название')
        self.tree.heading('address', text='Адрес')
        self.tree.heading('phone', text='Телефон')
        self.tree.grid(row=5, column=0, columnspan=2)

        self.load_institutions()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path

    def save_institution(self):
        name = self.name_entry.get()
        address = self.address_entry.get()
        phone = self.phone_entry.get()
        image_path = getattr(self, 'image_path', '')

        conn = sqlite3.connect('educational_institutions.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO institutions (name, address, phone, image_path)
            VALUES (?, ?, ?, ?)
        ''', (name, address, phone, image_path))
        conn.commit()
        conn.close()

        self.load_institutions()

    def load_institutions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect('educational_institutions.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, address, phone FROM institutions')
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert('', END, values=row)

if __name__ == "__main__":
    create_db()
    root = Tk()
    app = InstitutionForm(root)
    root.mainloop()