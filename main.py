import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.trainings = []
        self.load_data()

        # Поля формы
        tk.Label(root, text="Дата (ГГГГ-ММ-ДД, ДД.ММ.ГГГГ или ДД/ММ/ГГГГ):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Тип тренировки:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.type_entry = ttk.Combobox(root, values=["Кардио", "Силовая", "Йога", "Растяжка"])
        self.type_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="Длительность (мин):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.duration_entry = tk.Entry(root)
        self.duration_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка добавления
        tk.Button(root, text="Добавить тренировку", command=self.add_training).grid(row=3, column=0, columnspan=2, pady=10)

        # Таблица
        self.tree = ttk.Treeview(root, columns=("Дата", "Тип", "Длительность"), show="headings")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип", text="Тип")
        self.tree.heading("Длительность", text="Длительность (мин)")
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Фильтры
        tk.Label(root, text="Фильтр по типу:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.filter_type = ttk.Combobox(root, values=["Все", "Кардио", "Силовая", "Йога", "Растяжка"])
        self.filter_type.set("Все")
        self.filter_type.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(root, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.filter_date = tk.Entry(root)
        self.filter_date.grid(row=6, column=1, padx=5, pady=5)

        tk.Button(root, text="Применить фильтры", command=self.apply_filters).grid(row=7, column=0, columnspan=2, pady=5)
        tk.Button(root, text="Сбросить фильтры", command=self.reset_filters).grid(row=8, column=0, columnspan=2, pady=5)
        tk.Button(root, text="Удалить выбранную", command=self.delete_training).grid(row=9, column=0, columnspan=2, pady=5)


        # Статус-бар
        self.status_label = tk.Label(root, text="Всего тренировок: 0", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=10, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.update_table()

    def validate_date(self, date_str):
        """Проверяет и преобразует дату в формат ГГГГ-ММ-ДД"""
        formats = ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def add_training(self):
        date_str = self.date_entry.get()
        training_type = self.type_entry.get()
        duration_str = self.duration_entry.get()

        # Валидация даты
        date_formatted = self.validate_date(date_str)
        if not date_formatted:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД, ДД.ММ.ГГГГ или ДД/ММ/ГГГГ.")
            return

        # Валидация длительности
        try:
            duration = int(duration_str)
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным целым числом.")
            return

        # Добавление в таблицу и список
        self.trainings.append({"date": date_formatted, "type": training_type, "duration": duration})
        self.update_table()
        self.save_data()

        # Очистка полей
        self.date_entry.delete(0, tk.END)
        self.type_entry.set("")
        self.duration_entry.delete(0, tk.END)

    def apply_filters(self):
        filter_type = self.filter_type.get()
        filter_date = self.filter_date.get()

        filtered = self.trainings

        if filter_type != "Все":
            filtered = [t for t in filtered if t["type"] == filter_type]
        if filter_date:
            try:
                datetime.strptime(filter_date, "%Y-%m-%d")
                filtered = [t for t in filtered if t["date"] == filter_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты фильтра. Используйте ГГГГ-ММ-ДД.")
                return

        self.update_table(filtered)

    def reset_filters(self):
        self.filter_type.set("Все")
        self.filter_date.delete(0, tk.END)
        self.update_table()

    def delete_training(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления.")
            return

        item_values = self.tree.item(selected_item[0])["values"]
        # Ищем в списке тренировок запись с такими же данными
        for i, training in enumerate(self.trainings):
            if (training["date"] == item_values[0] and
                training["type"] == item_values[1] and
                training["duration"] == item_values[2]):
                del self.trainings[i]
                break

        self.update_table()
        self.save_data()
        messagebox.showinfo("Успех", "Тренировка удалена.")

    def update_table(self, data=None):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        source = data if data is not None else self.trainings
        for training in source:
            self.tree.insert("", "end", values=(training["date"], training["type"], training["duration"]))

        # Обновляем статус-бар
        self.status_label.config(text=f"Всего тренировок: {len(source)}")

    def save_data(self):
        try:
            with open("trainings.json", "w", encoding="utf-8") as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        try:
            if os.path.exists("trainings.json"):
                with open("trainings.json", "r", encoding="utf-8") as f:
                    self.trainings = json.load(f)
            else:
                self.trainings = []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            self.trainings = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()