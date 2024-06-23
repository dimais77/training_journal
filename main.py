import tkinter as tk
from tkinter import ttk, Toplevel, messagebox, filedialog
import json
from datetime import datetime
import csv
import matplotlib.pyplot as plt
from collections import defaultdict

# Файл для сохранения данных
data_file = 'training_log.json'


def load_data():
    """Загрузка данных о тренировках из файла."""
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    """Сохранение данных о тренировках в файл."""
    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4)


def export_to_csv(data, filename):
    """Экспорт данных в CSV файл."""
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['date', 'exercise', 'weight', 'repetitions'])
        for entry in data:
            writer.writerow([entry['date'], entry['exercise'], entry['weight'], entry['repetitions']])


def import_from_csv(filename):
    """Импорт данных из CSV файла."""
    data = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


class TrainingLogApp:
    def __init__(self, root):
        self.root = root
        root.title("Дневник тренировок")
        self.create_widgets()

    def create_widgets(self):
        # Виджеты для ввода данных
        self.exercise_label = ttk.Label(self.root, text="Упражнение:")
        self.exercise_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        self.exercise_entry = ttk.Entry(self.root)
        self.exercise_entry.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5)

        self.weight_label = ttk.Label(self.root, text="Вес:")
        self.weight_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        self.weight_entry = ttk.Entry(self.root)
        self.weight_entry.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5)

        self.repetitions_label = ttk.Label(self.root, text="Повторения:")
        self.repetitions_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

        self.repetitions_entry = ttk.Entry(self.root)
        self.repetitions_entry.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)

        self.add_button = ttk.Button(self.root, text="Добавить запись", command=self.add_entry)
        self.add_button.grid(column=0, row=3, columnspan=2, pady=10)

        self.view_button = ttk.Button(self.root, text="Просмотреть записи", command=self.view_records)
        self.view_button.grid(column=0, row=4, columnspan=2, pady=10)

        self.filter_date_button = ttk.Button(self.root, text="Фильтр по дате", command=self.filter_by_date)
        self.filter_date_button.grid(column=0, row=5, columnspan=2, pady=10)

        self.filter_exercise_button = ttk.Button(self.root, text="Фильтр по упражнению",
                                                 command=self.filter_by_exercise)
        self.filter_exercise_button.grid(column=0, row=6, columnspan=2, pady=10)

        self.export_button = ttk.Button(self.root, text="Экспорт в CSV", command=self.export_records)
        self.export_button.grid(column=0, row=7, columnspan=2, pady=10)

        self.import_button = ttk.Button(self.root, text="Импорт из CSV", command=self.import_records)
        self.import_button.grid(column=0, row=8, columnspan=2, pady=10)

        self.stats_button = ttk.Button(self.root, text="Статистика", command=self.show_statistics)
        self.stats_button.grid(column=0, row=9, columnspan=2, pady=10)

        self.plot_button = ttk.Button(self.root, text="Визуализация прогресса", command=self.plot_progress)
        self.plot_button.grid(column=0, row=10, columnspan=2, pady=10)

    def add_entry(self):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exercise = self.exercise_entry.get()
        weight = self.weight_entry.get()
        repetitions = self.repetitions_entry.get()

        if not (exercise and weight and repetitions):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        entry = {
            'date': date,
            'exercise': exercise,
            'weight': weight,
            'repetitions': repetitions
        }

        data = load_data()
        data.append(entry)
        save_data(data)

        # Очистка полей ввода после добавления
        self.exercise_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.repetitions_entry.delete(0, tk.END)
        messagebox.showinfo("Успешно", "Запись успешно добавлена!")

    def view_records(self, data=None):
        if data is None:
            data = load_data()

        records_window = Toplevel(self.root)
        records_window.title("Записи тренировок")

        tree = ttk.Treeview(records_window, columns=("Дата", "Упражнение", "Вес", "Повторения"), show="headings")
        tree.heading('Дата', text="Дата")
        tree.heading('Упражнение', text="Упражнение")
        tree.heading('Вес', text="Вес")
        tree.heading('Повторения', text="Повторения")

        for entry in data:
            tree.insert('', tk.END, values=(entry['date'], entry['exercise'], entry['weight'], entry['repetitions']))

        tree.pack(expand=True, fill=tk.BOTH)

        # Добавление кнопок для редактирования и удаления записей
        edit_button = ttk.Button(records_window, text="Редактировать", command=lambda: self.edit_record(tree))
        edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        delete_button = ttk.Button(records_window, text="Удалить", command=lambda: self.delete_record(tree))
        delete_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def filter_by_date(self):
        filter_window = Toplevel(self.root)
        filter_window.title("Фильтр по дате")

        start_label = ttk.Label(filter_window, text="Начальная дата (YYYY-MM-DD):")
        start_label.grid(column=0, row=0, padx=5, pady=5)
        start_entry = ttk.Entry(filter_window)
        start_entry.grid(column=1, row=0, padx=5, pady=5)

        end_label = ttk.Label(filter_window, text="Конечная дата (YYYY-MM-DD):")
        end_label.grid(column=0, row=1, padx=5, pady=5)
        end_entry = ttk.Entry(filter_window)
        end_entry.grid(column=1, row=1, padx=5, pady=5)

        def apply_filter():
            start_date = start_entry.get()
            end_date = end_entry.get()
            data = load_data()
            filtered_data = [entry for entry in data if start_date <= entry['date'][:10] <= end_date]
            self.view_records(filtered_data)

        apply_button = ttk.Button(filter_window, text="Применить", command=apply_filter)
        apply_button.grid(column=0, row=2, columnspan=2, pady=10)

    def filter_by_exercise(self):
        filter_window = Toplevel(self.root)
        filter_window.title("Фильтр по упражнению")

        exercise_label = ttk.Label(filter_window, text="Упражнение:")
        exercise_label.grid(column=0, row=0, padx=5, pady=5)
        exercise_entry = ttk.Entry(filter_window)
        exercise_entry.grid(column=1, row=0, padx=5, pady=5)

        def apply_filter():
            exercise = exercise_entry.get()
            data = load_data()
            filtered_data = [entry for entry in data if entry['exercise'] == exercise]
            self.view_records(filtered_data)

        apply_button = ttk.Button(filter_window, text="Применить", command=apply_filter)
        apply_button.grid(column=0, row=1, columnspan=2, pady=10)

    def export_records(self):
        data = load_data()
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            export_to_csv(data, filename)
            messagebox.showinfo("Успешно", "Данные успешно экспортированы в CSV файл!")

    def import_records(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            data = import_from_csv(filename)
            save_data(data)
            messagebox.showinfo("Успешно", "Данные успешно импортированы из CSV файла!")

    def edit_record(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Не выбрана запись для редактирования!")
            return

        item = tree.item(selected_item)
        record_values = item['values']

        edit_window = Toplevel(self.root)
        edit_window.title("Редактирование записи")

        date_label = ttk.Label(edit_window, text="Дата:")
        date_label.grid(column=0, row=0, padx=5, pady=5)
        date_entry = ttk.Entry(edit_window)
        date_entry.grid(column=1, row=0, padx=5, pady=5)
        date_entry.insert(0, record_values[0])

        exercise_label = ttk.Label(edit_window, text="Упражнение:")
        exercise_label.grid(column=0, row=1, padx=5, pady=5)
        exercise_entry = ttk.Entry(edit_window)
        exercise_entry.grid(column=1, row=1, padx=5, pady=5)
        exercise_entry.insert(0, record_values[1])

        weight_label = ttk.Label(edit_window, text="Вес:")
        weight_label.grid(column=0, row=2, padx=5, pady=5)
        weight_entry = ttk.Entry(edit_window)
        weight_entry.grid(column=1, row=2, padx=5, pady=5)
        weight_entry.insert(0, record_values[2])

        repetitions_label = ttk.Label(edit_window, text="Повторения:")
        repetitions_label.grid(column=0, row=3, padx=5, pady=5)
        repetitions_entry = ttk.Entry(edit_window)
        repetitions_entry.grid(column=1, row=3, padx=5, pady=5)
        repetitions_entry.insert(0, record_values[3])

        def save_changes():
            new_values = {
                'date': date_entry.get(),
                'exercise': exercise_entry.get(),
                'weight': weight_entry.get(),
                'repetitions': repetitions_entry.get()
            }
            data = load_data()
            for entry in data:
                if entry['date'] == record_values[0] and entry['exercise'] == record_values[1] and entry['weight'] == \
                        record_values[2] and entry['repetitions'] == record_values[3]:
                    entry.update(new_values)
                    break
            save_data(data)
            edit_window.destroy()
            messagebox.showinfo("Успешно", "Запись успешно отредактирована!")
            self.view_records()

        save_button = ttk.Button(edit_window, text="Сохранить", command=save_changes)
        save_button.grid(column=0, row=4, columnspan=2, pady=10)

    def delete_record(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Не выбрана запись для удаления!")
            return

        item = tree.item(selected_item)
        record_values = item['values']

        data = load_data()
        data = [entry for entry in data if not (
                entry['date'] == record_values[0] and entry['exercise'] == record_values[1] and entry['weight'] ==
                record_values[2] and entry['repetitions'] == record_values[3])]
        save_data(data)
        messagebox.showinfo("Успешно", "Запись успешно удалена!")
        self.view_records()

    def show_statistics(self):
        data = load_data()
        exercise_stats = defaultdict(int)
        for entry in data:
            exercise_stats[entry['exercise']] += int(entry['weight'])

        stats_window = Toplevel(self.root)
        stats_window.title("Статистика по упражнениям")

        for exercise, total_weight in exercise_stats.items():
            stat_label = ttk.Label(stats_window, text=f"{exercise}: {total_weight} кг")
            stat_label.pack(padx=5, pady=5)

    def plot_progress(self):
        data = load_data()
        exercise_data = defaultdict(list)
        for entry in data:
            exercise_data[entry['exercise']].append((entry['date'], int(entry['weight']), int(entry['repetitions'])))

        plot_window = Toplevel(self.root)
        plot_window.title("Визуализация прогресса")

        exercise_label = ttk.Label(plot_window, text="Упражнение:")
        exercise_label.pack(padx=5, pady=5)
        exercise_entry = ttk.Entry(plot_window)
        exercise_entry.pack(padx=5, pady=5)

        def plot():
            exercise = exercise_entry.get()
            if exercise not in exercise_data:
                messagebox.showerror("Ошибка", "Нет данных для этого упражнения!")
                return

            dates = [datetime.strptime(entry[0], '%Y-%m-%d %H:%M:%S') for entry in exercise_data[exercise]]
            weights = [entry[1] for entry in exercise_data[exercise]]
            repetitions = [entry[2] for entry in exercise_data[exercise]]

            plt.figure(figsize=(10, 5))
            plt.plot(dates, weights, label='Вес')
            plt.plot(dates, repetitions, label='Повторения')
            plt.xlabel('Дата')
            plt.ylabel('Вес / Повторения')
            plt.title(f'Прогресс по упражнению: {exercise}')
            plt.legend()
            plt.grid(True)
            plt.show()

        plot_button = ttk.Button(plot_window, text="Построить график", command=plot)
        plot_button.pack(padx=5, pady=5)


def main():
    root = tk.Tk()
    app = TrainingLogApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
