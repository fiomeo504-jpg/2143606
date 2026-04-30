import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

HISTORY_FILE = "password_history.json"


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x550")
        self.root.resizable(True, True)

        self.history = []
        self.load_history()

        self.create_widgets()
        self.update_password_length_label()
        self.refresh_history_table()

    def create_widgets(self):
        # === Рамка настроек ===
        settings_frame = tk.LabelFrame(self.root, text="Настройки пароля", padx=15, pady=15)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины пароля
        tk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_scale = tk.Scale(
            settings_frame, from_=4, to=32, orient=tk.HORIZONTAL,
            variable=self.length_var, length=300, command=self.update_password_length_label
        )
        self.length_scale.grid(row=0, column=1, padx=5, pady=5)

        self.length_label = tk.Label(settings_frame, text="", width=5)
        self.length_label.grid(row=0, column=2, padx=5, pady=5)

        # Чекбоксы
        self.use_letters_var = tk.BooleanVar(value=True)
        self.use_digits_var = tk.BooleanVar(value=True)
        self.use_symbols_var = tk.BooleanVar(value=False)

        tk.Checkbutton(settings_frame, text="Буквы (a-z, A-Z)", variable=self.use_letters_var).grid(row=1, column=0, sticky="w", padx=5, pady=3)
        tk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits_var).grid(row=1, column=1, sticky="w", padx=5, pady=3)
        tk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&* и др.)", variable=self.use_symbols_var).grid(row=1, column=2, sticky="w", padx=5, pady=3)

        # Кнопка генерации
        tk.Button(settings_frame, text="🔐 Сгенерировать пароль", command=self.generate_password,
                  bg="lightgreen", font=("Arial", 11)).grid(row=2, column=0, columnspan=3, pady=15)

        # === Отображение сгенерированного пароля ===
        result_frame = tk.LabelFrame(self.root, text="Сгенерированный пароль", padx=10, pady=10)
        result_frame.pack(fill="x", padx=10, pady=5)

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(result_frame, textvariable=self.password_var, font=("Courier", 14),
                                       state="readonly", justify="center")
        self.password_entry.pack(fill="x", padx=10, pady=5)

        copy_btn = tk.Button(result_frame, text="📋 Копировать в буфер", command=self.copy_to_clipboard)
        copy_btn.pack(pady=5)

        # === Таблица истории ===
        history_frame = tk.LabelFrame(self.root, text="История паролей", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Дата и время", "Длина", "Пароль")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)

        self.tree.heading("Дата и время", text="Дата и время")
        self.tree.heading("Длина", text="Длина")
        self.tree.heading("Пароль", text="Пароль")

        self.tree.column("Дата и время", width=150)
        self.tree.column("Длина", width=60)
        self.tree.column("Пароль", width=350)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # === Кнопки управления историей ===
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text="💾 Сохранить историю", command=self.save_history, bg="lightyellow").pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Загрузить историю", command=self.load_history_interactive, bg="lightyellow").pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 Очистить историю", command=self.clear_history, bg="salmon").pack(side="left", padx=5)

    def update_password_length_label(self, event=None):
        self.length_label.config(text=f"{self.length_var.get()}")

    def get_character_set(self):
        chars = ""
        if self.use_letters_var.get():
            chars += string.ascii_letters
        if self.use_digits_var.get():
            chars += string.digits
        if self.use_symbols_var.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return chars

    def generate_password(self):
        length = self.length_var.get()
        chars = self.get_character_set()

        if not chars:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return

        password = ''.join(random.choice(chars) for _ in range(length))

        # Перемешиваем для лучшей случайности
        password_list = list(password)
        random.shuffle(password_list)
        password = ''.join(password_list)

        self.password_var.set(password)

        # Добавляем в историю
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.insert(0, {
            "timestamp": timestamp,
            "length": length,
            "password": password,
            "settings": {
                "letters": self.use_letters_var.get(),
                "digits": self.use_digits_var.get(),
                "symbols": self.use_symbols_var.get()
            }
        })

        # Ограничиваем историю 50 записями
        if len(self.history) > 50:
            self.history = self.history[:50]

        self.refresh_history_table()
        messagebox.showinfo("Успех", f"Пароль длиной {length} символов создан и добавлен в историю")

    def refresh_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for record in self.history:
            self.tree.insert("", tk.END, values=(
                record["timestamp"],
                record["length"],
                record["password"]
            ))

    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Копирование", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Внимание", "Нет сгенерированного пароля для копирования")

    def save_history(self):
        try:
            # Сохраняем без настроек для экономии места (только историю паролей)
            save_data = []
            for record in self.history:
                save_data.append({
                    "timestamp": record["timestamp"],
                    "length": record["length"],
                    "password": record["password"]
                })

            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"История сохранена в {HISTORY_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Преобразуем в нужный формат
                    self.history = []
                    for item in data:
                        self.history.append({
                            "timestamp": item.get("timestamp", ""),
                            "length": item.get("length", 0),
                            "password": item.get("password", ""),
                            "settings": {"letters": True, "digits": True, "symbols": False}
                        })
            except (json.JSONDecodeError, FileNotFoundError):
                self.history = []

    def load_history_interactive(self):
        self.load_history()
        self.refresh_history_table()
        messagebox.showinfo("Загрузка", f"Загружено записей в истории: {len(self.history)}")

    def clear_history(self):
        if messagebox.askyesno("Очистка", "Вы уверены, что хотите очистить всю историю паролей?"):
            self.history = []
            self.refresh_history_table()
            messagebox.showinfo("Очистка", "История очищена")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
  
