import tkinter as tk
from tkinter import ttk, scrolledtext, Menu, filedialog, messagebox, simpledialog
import os
from datetime import date
from crypto import encrypt, decrypt 
import getpass

class NotepadApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("text256")
        self.root.geometry("900x600")
        self.root.iconbitmap("icon.ico")
        
        # Обработка закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.current_file = None
        self.file_path = f"C:\\Users\\{getpass.getuser()}\\txt256\\txt256"
        
        self.password = None

        # Проверка пароля при запуске
        if not self.check_password():
            self.root.destroy()
            return
        
        self.setup_ui()
        self.open_file()

    def check_password(self):
        """Пытается ввести пароль и проверить его через расшифровку."""
        while True:
            password = simpledialog.askstring("text256", "Введите пароль", parent=self.root, show='*')
            if password is None:
                return False
            if not os.path.exists(self.file_path):
                self.password = password
                return True
            try:
                with open(self.file_path, 'rb') as file:
                    encrypted_data = file.read()
                decrypt(encrypted_data, password)
                self.password = password
                return True
            except Exception:
                messagebox.showerror("text256", "Неверный пароль!")
                return False

    def open_file(self):
        """Открывает и расшифровывает файл, если есть."""
        password = self.password

        if not os.path.exists(self.file_path):
            return

        try:
            with open(self.file_path, 'rb') as file:
                encrypted_data = file.read()
            content = decrypt(encrypted_data, password)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, content)
            self.text_area.edit_modified(False)
            self.status_bar.config(text="Файл успешно загружен")
        except Exception as e:
            print(f"Не удалось расшифровать файл: {e}")
            self.status_bar.config(text="Не удалось загрузить зашифрованный файл")

    def setup_ui(self):
        # Настройка UI
        style = ttk.Style()
        style.theme_use('clam')

        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сменить пароль", command=self.new_password)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить", command=self.undo_text, accelerator="Ctrl+Z")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_command(label="Удалить", command=self.delete_text, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить все", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Время и дата", command=self.date, accelerator="F5")

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Consolas", 11), bg='white', fg='black', padx=10, pady=10, borderwidth=1, highlightthickness=0, undo=True)

        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Вырезать", command=self.cut_text)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Вставить", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выделить все", command=self.select_all)

        self.text_area.bind("<Button-3>", self.show_context_menu)
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<F5>', lambda e: self.date())

        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.text_area.focus_set()

        self.status_bar = ttk.Label(self.root, text="Готово", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def new_password(self):
        """Сменить пароль и перезаписать файл."""
        new_pw = simpledialog.askstring(
            "text256",
            "               Введите новый пароль               ",
            parent=self.root,
            show='*'
        )
        
        if new_pw:
            confirm_pw = simpledialog.askstring(
                "text256", 
                "           Подтвердите новый пароль           ", 
                parent=self.root,
                show='*'
            )
            
            if confirm_pw == new_pw:
                try:
                    content = self.text_area.get(1.0, tk.END)
                    os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                    encrypted_content = encrypt(content, new_pw)
                    with open(self.file_path, 'wb') as file:
                        file.write(encrypted_content)
                    self.password = new_pw
                    self.status_bar.config(text="Пароль успешно изменён")
                    messagebox.showinfo("text256", "Пароль успешно изменён.")
                except Exception as e:
                    messagebox.showerror("text256", f"Ошибка при смене пароля: {e}")
            elif confirm_pw is not None:
                messagebox.showerror("text256", "Пароли не совпадают!")

        
    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def check_save(self):
        # Проверка несохранённых изменений
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel(
                "Блокнот",
                "Сохранить изменения?"
            )
            if response is None:  # Нажата Отмена
                return False
            elif response:  # Нажата Да
                self.save_file()
        return True
    
    def cut_text(self):
        try:
            self.text_area.event_generate("<<Cut>>")
        except:
            # fallback
            self.text_area.clipboard_clear()
            selected = self.text_area.get("sel.first", "sel.last")
            self.text_area.clipboard_append(selected)
            self.text_area.delete("sel.first", "sel.last")
        
    def copy_text(self):
        try:
            self.text_area.event_generate("<<Copy>>")
        except:
            # fallback
            selected = self.text_area.get("sel.first", "sel.last")
            self.text_area.clipboard_clear()
            self.text_area.clipboard_append(selected)
        
    def paste_text(self):
        try:
            self.text_area.event_generate("<<Paste>>")
        except:
            # fallback
            self.text_area.insert("insert", self.root.clipboard_get())
        
    def delete_text(self):
        try:
            self.text_area.delete("sel.first", "sel.last")
        except:
            pass
        
    def select_all(self):
        self.text_area.tag_add('sel', '1.0', 'end-1c')
        return 'break'  # Прекратить дальнейшую обработку

    def date(self):
        current_date = date.today()
        date_str = current_date.strftime("%d.%m.%Y")
        self.text_area.insert("insert", date_str)
        
    def undo_text(self):
        try:
            self.text_area.edit_undo()
        except:
            pass
            
    def redo_text(self):
        try:
            self.text_area.edit_redo()
        except:
            pass
        
    def run(self):
        self.root.mainloop()
        
    def on_closing(self):
        content = self.text_area.get(1.0, tk.END)
        # Пропустить пустой текст
        if len(content.strip()) == 0:
            self.root.destroy()
            return
            
        password = self.password
        # Создать директорию и шифровать содержимое
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        try:
            encrypted_content = encrypt(content, password)
            
            # Сохраняем зашифрованные данные
            with open(self.file_path, 'wb') as file:
                file.write(encrypted_content)
                
            self.status_bar.config(text="Файл зашифрован и сохранён")
        except Exception as e:
            print(f"Ошибка при шифровании: {e}")
            # Если шифрование не удалось, сохраняем как обычный текст
            with open(self.file_path + '.txt', 'w', encoding='utf-8') as file:
                file.write(content)
        
        self.root.destroy()

if __name__ == "__main__":
    app = NotepadApp()
    app.run()