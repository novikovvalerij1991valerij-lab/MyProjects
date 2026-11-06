import tkinter as tk
from tkinter import messagebox,simpledialog
from tkinter import ttk 
from datetime import datetime, timedelta
import os
os.environ["CRYPTOGRAPHY_OPENSSL_NO_LEGACY"] = "1"

from crypto_utils import get_key
from database import (load_diary, save_diary, load_finance, save_finance, 
                      load_habits, save_habits)

KEY = None

EXPENSE_CATEGORIES = ["Еда", "Транспорт", "Жилье", "Развлечения", "Здоровье", "Одежда", "Другое"]
INCOME_CATEGORIES = ["Зарплата", "Подработка", "Подарок", "Инвестиции", "Возврат долга", "Другое"]

# --- ФУНКЦИИ ДНЕВНИКА ---
def start_app():
    login_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

def open_add_note_window():
    note_window = tk.Toplevel(root)
    note_window.title("Новая запись")
    note_window.geometry("300x400")
    note_window.configure(bg="#2b2b2b")

    tk.Label(note_window, text="Что нового?", font=("Arial", 14), fg="white", bg="#2b2b2b").pack(pady=10)
    text_entry = tk.Text(note_window, height=10, width=30, font=("Arial", 12))
    text_entry.pack(pady=10)

    def save_note():
        text = text_entry.get("1.0", tk.END).strip()
        if text:
            current_text = load_diary(KEY) or ""
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            entry = f"[{now}]\n{text}\n" + ("-" * 40) + "\n"
            save_diary(current_text + entry, KEY)
            messagebox.showinfo("Успех", "Запись сохранена!")
            note_window.destroy()
        else:
            messagebox.showwarning("Ошибка", "Пустая запись!")

    tk.Button(note_window, text="💾 Сохранить", font=("Arial", 12), bg="#4CAF50", fg="white", command=save_note).pack(pady=10)

def open_view_notes_window():
    text = load_diary(KEY)
    if not text:
        messagebox.showinfo("Записи", "Записей нет.")
        return
    view_window = tk.Toplevel(root)
    view_window.title("Мои записи")
    view_window.geometry("400x500")
    text_box = tk.Text(view_window, wrap="word", font=("Arial", 11))
    text_box.insert("1.0", text)
    text_box.config(state="disabled")
    text_box.pack(fill="both", expand=True, padx=10, pady=10)

# --- ФУНКЦИИ ФИНАНСОВ ---
def open_finance_window():
    fin_window = tk.Toplevel(root)
    fin_window.title("Финансы")
    fin_window.geometry("350x450")
    fin_window.configure(bg="#2b2b2b")

    tk.Label(fin_window, text="💰 Финансы", font=("Arial", 18, "bold"), fg="white", bg="#2b2b2b").pack(pady=15)
    balance_label = tk.Label(fin_window, text="Загрузка...", font=("Arial", 12), fg="#4CAF50", bg="#2b2b2b")
    balance_label.pack(pady=10)

    def update_balance():
        text = load_finance(KEY) or ""
        income = 0
        expense = 0
        if text:
            for entry in text.split("-" * 40):
                lines = entry.strip().split("\n")
                if len(lines) > 1:
                    details = lines[1]
                    try:
                        amount = float(details.split("|")[-1].strip().replace("руб.", ""))
                        if "Доход" in details: income += amount
                        else: expense += amount
                    except: pass
        balance = income - expense
        balance_label.config(text=f"Доходы: {income}\nРасходы: {expense}\nБаланс: {balance}")

    def add_transaction():
        trans_window = tk.Toplevel(fin_window)
        trans_window.title("Новая транзакция")
        trans_window.geometry("300x350")
        trans_window.configure(bg="#2b2b2b")

        tk.Label(trans_window, text="Тип:", fg="white", bg="#2b2b2b").pack(pady=(10,0))
        type_var = tk.StringVar(value="Расход")
        
        tk.Label(trans_window, text="Категория:", fg="white", bg="#2b2b2b").pack(pady=(10,0))
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(trans_window, textvariable=category_var, state="readonly")
        
        def on_type_change(*args):
            if type_var.get() == "Расход":
                category_combo['values'] = EXPENSE_CATEGORIES
                category_combo.current(0)
            else:
                category_combo['values'] = INCOME_CATEGORIES
                category_combo.current(0)
                
        type_var.trace("w", on_type_change)

        tk.Radiobutton(trans_window, text="Расход", variable=type_var, value="Расход", bg="#2b2b2b", fg="white", selectcolor="#444").pack()
        tk.Radiobutton(trans_window, text="Доход", variable=type_var, value="Доход", bg="#2b2b2b", fg="white", selectcolor="#444").pack()
        category_combo.pack(pady=5)

        tk.Label(trans_window, text="Сумма:", fg="white", bg="#2b2b2b").pack(pady=(10,0))
        amount_entry = tk.Entry(trans_window)
        amount_entry.pack()

        def save_trans():
            try:
                amount = float(amount_entry.get().replace(",", "."))
                category = category_var.get()
                t_type = type_var.get()

                current_fin = load_finance(KEY) or ""
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                entry = f"[{now}]\n{t_type} | {category} | {amount} руб.\n" + ("-" * 40) + "\n"
                save_finance(current_fin + entry, KEY)
                update_balance()
                messagebox.showinfo("Успех", "Добавлено!")
                trans_window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")

        tk.Button(trans_window, text="Сохранить", bg="#4CAF50", fg="white", command=save_trans).pack(pady=20)
        on_type_change()

    update_balance()
    tk.Button(fin_window, text="➕ Добавить транзакцию", bg="#2196F3", fg="white", command=add_transaction).pack(pady=10)
    tk.Button(fin_window, text="🔄 Обновить баланс", bg="#9E9E9E", fg="white", command=update_balance).pack(pady=10)

# --- ФУНКЦИИ ПРИВЫЧЕК ---
def open_habits_window():
    hab_window = tk.Toplevel(root)
    hab_window.title("Мои привычки")
    hab_window.geometry("400x500")
    hab_window.configure(bg="#2b2b2b")

    tk.Label(hab_window, text="🎯 Трекер привычек", font=("Arial", 18, "bold"), fg="white", bg="#2b2b2b").pack(pady=15)

    habits_frame = tk.Frame(hab_window, bg="#2b2b2b")
    habits_frame.pack(fill="both", expand=True, padx=10)

    def refresh_habits():
        # Очищаем фрейм перед обновлением
        for widget in habits_frame.winfo_children():
            widget.destroy()

        habits_text = load_habits(KEY) or ""
        habits = {}
        if habits_text:
            for line in habits_text.split("\n"):
                if "|" in line:
                    name, dates_str = line.split("|")
                    habits[name.strip()] = dates_str.strip().split(",") if dates_str.strip() else []
        
        if not habits:
            tk.Label(habits_frame, text="У тебя пока нет привычек.", fg="gray", bg="#2b2b2b").pack()
            return

        today_str = datetime.now().strftime("%Y-%m-%d")

        for i, (name, dates) in enumerate(habits.items(), 1):
            # Считаем стрик
            streak = 0
            current_day = datetime.now()
            while True:
                day_str = current_day.strftime("%Y-%m-%d")
                if day_str in dates:
                    streak += 1
                    current_day -= timedelta(days=1)
                else:
                    break
            
            is_done = today_str in dates
            status = "✅ Сделано" if is_done else "❌ Нет"
            
            # Рамка для одной привычки
            row = tk.Frame(habits_frame, bg="#333333", pady=5, padx=5)
            row.pack(fill="x", pady=5)
            
            tk.Label(row, text=f"{i}. {name}", fg="white", bg="#333333", font=("Arial", 12)).pack(side="left")
            tk.Label(row, text=f"🔥 {streak} дн. | {status}", fg="#FF9800", bg="#333333").pack(side="left", padx=10)
            
            if not is_done:
                def mark_done(n=name):
                    h_text = load_habits(KEY) or ""
                    h_dict = {}
                    if h_text:
                        for line in h_text.split("\n"):
                            if "|" in line:
                                k, v = line.split("|")
                                h_dict[k.strip()] = v.strip().split(",") if v.strip() else []
                    
                    if today_str not in h_dict[n]:
                        h_dict[n].append(today_str)
                        new_text = "\n".join([f"{k}|{','.join(v)}" for k, v in h_dict.items()])
                        save_habits(new_text, KEY)
                        refresh_habits() # Обновляем экран
                
                tk.Button(row, text="Отметить", bg="#4CAF50", fg="white", command=mark_done).pack(side="right")

    def add_habit():
        new_name = tk.simpledialog.askstring("Новая привычка", "Введи название (например, Зарядка):")
        if new_name:
            h_text = load_habits(KEY) or ""
            # Добавляем новую привычку с пустой историей
            if h_text: h_text += "\n"
            h_text += f"{new_name}|"
            save_habits(h_text, KEY)
            refresh_habits()

    refresh_habits() # Первая отрисовка

    tk.Button(hab_window, text="➕ Добавить привычку", bg="#FF9800", fg="white", font=("Arial", 12), command=add_habit).pack(pady=10)

# --- ГЛАВНОЕ ОКНО ---
root = tk.Tk()
root.title("Мой Дневник")
root.geometry("400x500")
root.configure(bg="#2b2b2b")

login_frame = tk.Frame(root, bg="#2b2b2b")
login_frame.pack(fill="both", expand=True)
tk.Label(login_frame, text="🔐 Вход", font=("Arial", 20, "bold"), fg="white", bg="#2b2b2b").pack(pady=40)
password_entry = tk.Entry(login_frame, show="*", font=("Arial", 14), justify="center")
password_entry.pack(pady=10, ipadx=10, ipady=5)

def check_password():
    global KEY
    pwd = password_entry.get()
    if not pwd: return
    KEY = get_key(pwd)
    if os.path.exists("diary_secure.txt") and load_diary(KEY) is None:
        messagebox.showerror("Ошибка", "Неверный пароль!")
        return
    start_app()

tk.Button(login_frame, text="Войти", font=("Arial", 14), bg="#2196F3", fg="white", width=15, command=check_password).pack(pady=20)

main_frame = tk.Frame(root, bg="#2b2b2b")
tk.Label(main_frame, text="📔 МОЙ ДНЕВНИК", font=("Arial", 20, "bold"), fg="white", bg="#2b2b2b").pack(pady=20)

tk.Button(main_frame, text="✍️ Добавить запись", font=("Arial", 14), bg="#4CAF50", fg="white", width=20, command=open_add_note_window).pack(pady=10)
tk.Button(main_frame, text="📖 Мои записи", font=("Arial", 14), bg="#9C27B0", fg="white", width=20, command=open_view_notes_window).pack(pady=10)
tk.Button(main_frame, text="💰 Финансы", font=("Arial", 14), bg="#2196F3", fg="white", width=20, command=open_finance_window).pack(pady=10)
tk.Button(main_frame, text="🎯 Привычки", font=("Arial", 14), bg="#FF9800", fg="white", width=20, command=open_habits_window).pack(pady=10)
tk.Button(main_frame, text="🚪 Выход", font=("Arial", 14), bg="#f44336", fg="white", width=20, command=root.quit).pack(pady=30)

root.mainloop()