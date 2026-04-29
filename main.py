import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Ибрагимов Егор")
        self.root.geometry("620x580")
        self.root.resizable(True, True)
        
        # Установка цвета фона
        self.root.configure(bg='#f0f0f0')
        
        # Предопределённые задачи
        self.predefined_tasks = [
            ("Решить 3 задачи по математике", "учёба"),
            ("Сделать 10 отжиманий", "спорт"),
            ("Написать код на Python", "работа"),
            ("Выпить стакан воды", "спорт"),
            ("Повторить параграф по истории", "учёба"),
            ("Сделать план на завтра", "работа"),
            ("Помыть посуду", "работа"),
            ("Пробежать 1 км", "спорт"),
            ("Прочитать главу книги", "учёба"),
            ("Выучить 5 новых слов", "учёба")
        ]
        
        self.task_types = ["учёба", "спорт", "работа", "все"]
        self.filter_type = tk.StringVar(value="все")
        
        # Загружаем историю из JSON
        self.history = self.load_history()
        
        self.create_widgets()
        self.display_history()
    
    def create_widgets(self):
        # Стиль для кнопок
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)
        
        # --- Рамка генератора ---
        frame_gen = tk.LabelFrame(self.root, text="🎲 Генератор случайной задачи", 
                                   font=('Arial', 11, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        frame_gen.pack(fill="x", padx=10, pady=5)
        
        self.gen_button = ttk.Button(frame_gen, text="✨ Сгенерировать задачу", 
                                      command=self.generate_task)
        self.gen_button.pack(pady=5)
        
        self.current_task_label = tk.Label(frame_gen, text="", font=('Arial', 11, 'bold'),
                                            fg='green', bg='#f0f0f0')
        self.current_task_label.pack(pady=5)
        
        # --- Рамка добавления ---
        frame_add = tk.LabelFrame(self.root, text="➕ Добавить новую задачу",
                                   font=('Arial', 11, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        frame_add.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_add, text="Название задачи:", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.new_task_entry = ttk.Entry(frame_add, width=35, font=('Arial', 10))
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_add, text="Тип задачи:", bg='#f0f0f0', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.new_type_combo = ttk.Combobox(frame_add, values=self.task_types[:-1], 
                                            state="readonly", width=32, font=('Arial', 10))
        self.new_type_combo.current(0)
        self.new_type_combo.grid(row=1, column=1, padx=5, pady=5)
        
        self.add_button = ttk.Button(frame_add, text="📌 Добавить задачу", command=self.add_task)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # --- Рамка фильтрации ---
        frame_filter = tk.LabelFrame(self.root, text="🔍 Фильтрация истории",
                                      font=('Arial', 11, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        frame_filter.pack(fill="x", padx=10, pady=5)
        
        for t in self.task_types:
            rb = tk.Radiobutton(frame_filter, text=t.capitalize(), variable=self.filter_type,
                                value=t, command=self.display_history, bg='#f0f0f0',
                                font=('Arial', 10))
            rb.pack(side="left", padx=15)
        
        # --- Рамка истории ---
        frame_history = tk.LabelFrame(self.root, text="📜 История задач",
                                       font=('Arial', 11, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        frame_history.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создаём фрейм для списка и скролла
        list_frame = tk.Frame(frame_history, bg='#f0f0f0')
        list_frame.pack(fill="both", expand=True)
        
        self.history_listbox = tk.Listbox(list_frame, height=12, font=('Arial', 10),
                                           selectmode=tk.SINGLE)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- Кнопка сохранения ---
        self.save_button = ttk.Button(self.root, text="💾 Сохранить историю в JSON", 
                                       command=self.save_history_to_json)
        self.save_button.pack(pady=10)
        
        # --- Информационная метка ---
        self.info_label = tk.Label(self.root, text="Всего задач в истории: 0", 
                                    bg='#f0f0f0', font=('Arial', 9, 'italic'))
        self.info_label.pack(pady=5)
    
    def update_info_label(self):
        count = len(self.history)
        self.info_label.config(text=f"Всего задач в истории: {count}")
    
    def generate_task(self):
        """Генерирует случайную задачу"""
        task, task_type = random.choice(self.predefined_tasks)
        self.history.append({"task": task, "type": task_type})
        self.current_task_label.config(text=f"✅ {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()
        self.update_info_label()
    
    def add_task(self):
        """Добавляет новую задачу с валидацией"""
        task = self.new_task_entry.get().strip()
        task_type = self.new_type_combo.get()
        
        # Валидация: проверка на пустую строку
        if not task:
            messagebox.showerror("Ошибка ввода", "❌ Название задачи не может быть пустым!")
            return
        
        # Проверка на слишком длинную строку
        if len(task) > 100:
            messagebox.showerror("Ошибка ввода", "❌ Название задачи слишком длинное (макс. 100 символов)!")
            return
        
        self.predefined_tasks.append((task, task_type))
        self.history.append({"task": task, "type": task_type})
        
        self.new_task_entry.delete(0, tk.END)
        self.current_task_label.config(text=f"➕ Добавлено: {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()
        self.update_info_label()
        
        messagebox.showinfo("Успех", f"✅ Задача '{task}' успешно добавлена!")
    
    def display_history(self):
        """Отображает историю с учётом фильтра"""
        self.history_listbox.delete(0, tk.END)
        current_filter = self.filter_type.get()
        
        if not self.history:
            self.history_listbox.insert(tk.END, "📭 История пуста. Сгенерируйте или добавьте задачу.")
            return
        
        for i, item in enumerate(self.history, 1):
            if current_filter == "все" or item["type"] == current_filter:
                display_text = f"{i}. {item['task']} — [{item['type']}]"
                self.history_listbox.insert(tk.END, display_text)
    
    def load_history(self):
        """Загружает историю из JSON файла"""
        if not os.path.exists("tasks.json"):
            return []
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []
    
    def save_history_to_json(self):
        """Сохраняет историю в JSON файл"""
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except IOError:
            messagebox.showerror("Ошибка", "❌ Не удалось сохранить историю в JSON!")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()
  
