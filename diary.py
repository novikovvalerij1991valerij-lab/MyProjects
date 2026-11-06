import os
from datetime import datetime, timedelta
import base64
import hashlib
from cryptography.fernet import Fernet
import collections

# Отключаем проверку старых алгоритмов OpenSSL
os.environ["CRYPTOGRAPHY_OPENSSL_NO_LEGACY"] = "1"

FILE_NAME = "diary_secure.txt"
TRASH_FILE = "trash_secure.txt"
FINANCE_FILE = "finance_secure.txt"
LIMITS_FILE = "limits_secure.txt"
HABITS_FILE = "habits_secure.txt"

CATEGORIES = ["Личное", "Работа", "Идеи", "Разное"]
EXPENSE_CATEGORIES = ["Еда", "Транспорт", "Жилье", "Развлечения", "Здоровье", "Одежда", "Другое"]
INCOME_CATEGORIES = ["Зарплата", "Подработка", "Подарок", "Инвестиции", "Возврат долга", "Другое"]

def get_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

def load_data(key, filename):
    if not os.path.exists(filename):
        return ""
    with open(filename, "rb") as f:
        encrypted_data = f.read()
    try:
        f_obj = Fernet(key)
        return f_obj.decrypt(encrypted_data).decode("utf-8")
    except Exception:
        return None

def save_data(key, text, filename):
    f_obj = Fernet(key)
    encrypted_data = f_obj.encrypt(text.encode("utf-8"))
    with open(filename, "wb") as f:
        f.write(encrypted_data)

# ================= ФУНКЦИИ ДНЕВНИКА =================

def show_calendar(current_text):
    if not current_text:
        print("\nЗаписей нет.")
        return

    dates = []
    entries = [e.strip() for e in current_text.split("-" * 40) if e.strip()]
    for entry in entries:
        date_str = entry.split("\n")[0].split("]")[0].replace("[", "")
        dates.append(date_str.split(" ")[0])

    print("\n📅 КАЛЕНДАРЬ АКТИВНОСТИ (последние 30 дней)")
    print("🟩 - была запись, ⬜ - нет записи\n")

    today = datetime.now()
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_display = day.strftime("%d.%m")
        
        if day_str in dates:
            print(f"{day_display}: 🟩", end="  ")
        else:
            print(f"{day_display}: ⬜", end="  ")
            
        if i % 5 == 0 and i != 0:
            print()
    print("\n")

def change_password(old_key, current_text):
    print("\n--- 🔑 СМЕНА ПАРОЛЯ ---")
    new_password = input("Придумай новый пароль: ").strip()
    if not new_password:
        print("Пароль не может быть пустым. Отмена.")
        return old_key
    confirm_password = input("Повтори новый пароль для проверки: ").strip()
    if new_password != confirm_password:
        print("❌ Пароли не совпадают! Отмена.")
        return old_key

    new_key = get_key(new_password)
    save_data(new_key, current_text, FILE_NAME)
    print("✅ Пароль успешно изменён! Файл перешифрован.")
    return new_key

def search_entries(current_text):
    if not current_text:
        print("\nЗаписей нет, искать нечего.")
        return
    query = input("\n🔍 Что ищем? Введи слово или фразу: ").strip().lower()
    if not query: return
    entries = [e.strip() for e in current_text.split("-" * 40) if e.strip()]

    found = False
    print("\n🔍 РЕЗУЛЬТАТЫ ПОИСКА:")
    print("=" * 40)
    for entry in entries:
        if query in entry.lower():
            print(entry)
            print("-" * 40)
            found = True
    if not found:
        print(f"Ничего не найдено по запросу: '{query}'")
    print("=" * 40)

def search_by_category(current_text):
    if not current_text:
        print("\nЗаписей нет.")
        return

    print("\n📂 ДОСТУПНЫЕ КАТЕГОРИИ:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"{i}. {cat}")
    
    try:
        choice = int(input("Выбери номер категории для поиска (0 - отмена): "))
        if choice == 0: return
        if 1 <= choice <= len(CATEGORIES):
            category = CATEGORIES[choice-1]
        else:
            print("Нет такой категории.")
            return
    except ValueError:
        print("Нужно ввести число!")
        return

    search_str = f"[{category}]"
    entries = [e.strip() for e in current_text.split("-" * 40) if e.strip()]

    found = False
    print(f"\n📂 ЗАПИСИ В КАТЕГОРИИ: {category.upper()}")
    print("=" * 40)
    for entry in entries:
        if search_str in entry:
            print(entry)
            print("-" * 40)
            found = True
    if not found:
        print(f"Записей в категории '{category}' не найдено.")
    print("=" * 40)

def search_by_tag(current_text):
    if not current_text:
        print("\nЗаписей нет.")
        return
    tag = input("\n🏷️ Введи тег для поиска (например, Спорт): ").strip().lower()
    if not tag: return
    search_tag = f"#{tag}"
    entries = [e.strip() for e in current_text.split("-" * 40) if e.strip()]

    found = False
    print(f"\n🏷️ ЗАПИСИ С ТЕГОМ {search_tag.upper()}:")
    print("=" * 40)
    for entry in entries:
        if search_tag in entry.lower():
            print(entry)
            print("-" * 40)
            found = True
    if not found:
        print(f"Записей с тегом '{search_tag}' не найдено.")
    print("=" * 40)

def edit_entry(key, current_text):
    if not current_text:
        print("\nЗаписей нет, редактировать нечего.")
        return current_text
    
    entries = [e.strip() for e in current_text.split("-" * 40) if e.strip()]
    if not entries: return ""

    print("\n--- ✏️ РЕДАКТИРОВАНИЕ ЗАПИСИ ---")
    for i, entry in enumerate(entries, 1):
        lines = entry.split("\n")
        date = lines[0] if len(lines) > 0 else ""
        short_text = lines[1][:20] if len(lines) > 1 else ""
        print(f"{i}. {date} — {short_text}...")

    try:
        num = int(input("\nВведи номер записи для редактирования (или 0 для отмены): "))
        if num == 0: return current_text
        
        if 1 <= num <= len(entries):
            entry_to_edit = entries[num-1]
            lines = entry_to_edit.split("\n")
            
            print(f"\nТекущий текст:\n{lines[1] if len(lines) > 1 else ''}")
            new_text = input("\nВведи НОВЫЙ текст записи: ").strip()
            
            if new_text:
                header = lines[0]
                new_entry = f"{header}\n{new_text}"
                new_diary = ("-" * 40 + "\n").join([e + "\n" for e in entries if e != entry_to_edit])
                new_diary += new_entry + "\n" + ("-" * 40) + "\n"
                save_data(key, new_diary, FILE_NAME)
                print("✅ Запись отредактирована!")
                return new_diary
            else:
                print("Пустой текст — отмена.")
                return current_text
        else:
            print("Нет записи с таким номером.")
    except ValueError:
        print("Нужно ввести число!")
    return current_text

def delete_entry(key, current_text, trash_text):
    if not current_text:
        print("\nЗаписей нет, удалять нечего.")
        return current_text, trash_text
    
    entries = [e.strip() for e in current_text.split("-" * 40) if e.strip()]
    if not entries: return "", trash_text

    print("\n--- 🗑️ УДАЛЕНИЕ ---")
    for i, entry in enumerate(entries, 1):
        lines = entry.split("\n")
        date = lines[0] if len(lines) > 0 else ""
        short_text = lines[1][:20] if len(lines) > 1 else ""
        print(f"{i}. {date} — {short_text}...")

    try:
        num = int(input("\nВведи номер для удаления (или 0 для отмены): "))
        if num == 0: return current_text, trash_text
        
        if 1 <= num <= len(entries):
            entry_to_delete = entries[num-1]
            trash_entry = entry_to_delete + "\n" + ("-" * 40) + "\n"
            new_trash = trash_text + trash_entry
            save_data(key, new_trash, TRASH_FILE)
            new_text = ("-" * 40 + "\n").join([e + "\n" for e in entries if e != entry_to_delete])
            save_data(key, new_text, FILE_NAME)
            print("🗑️ Запись перемещена в корзину!")
            return new_text, new_trash
        else:
            print("Нет записи с таким номером.")
    except ValueError:
        print("Нужно ввести число!")
    return current_text, trash_text

def manage_trash(key, current_text, trash_text):
    if not trash_text:
        print("\n🗑️ Корзина пуста.")
        return current_text, trash_text

    entries = [e.strip() for e in trash_text.split("-" * 40) if e.strip()]
    print("\n--- 🗑️ КОРЗИНА ---")
    for i, entry in enumerate(entries, 1):
        lines = entry.split("\n")
        date = lines[0] if len(lines) > 0 else ""
        short_text = lines[1][:20] if len(lines) > 1 else ""
        print(f"{i}. {date} — {short_text}...")

    print("\nЧто делать?")
    print("1. ♻️ Восстановить запись")
    print("2. 🔥 Очистить корзину навсегда")
    print("3. 🔙 Назад")
    
    choice = input("Выбери (1-3): ").strip()
    
    if choice == "1":
        try:
            num = int(input("Введи номер для восстановления: "))
            if 1 <= num <= len(entries):
                entry_to_restore = entries[num-1]
                new_text = current_text + entry_to_restore + "\n" + ("-" * 40) + "\n"
                save_data(key, new_text, FILE_NAME)
                new_trash = ("-" * 40 + "\n").join([e + "\n" for e in entries if e != entry_to_restore])
                save_data(key, new_trash, TRASH_FILE)
                print("♻️ Запись восстановлена!")
                return new_text, new_trash
        except ValueError:
            print("Ошибка ввода.")
    elif choice == "2":
        confirm = input("Ты уверен, что хочешь стереть корзину навсегда? (да/нет): ").strip().lower()
        if confirm == "да":
            save_data(key, "", TRASH_FILE)
            print("🔥 Корзина очищена.")
            return current_text, ""
    return current_text, trash_text

# ================= ФУНКЦИИ ФИНАНСОВ =================

def show_finance(finance_text):
    if not finance_text:
        print("\n💰 Транзакций пока нет.")
        return

    entries = [e.strip() for e in finance_text.split("-" * 40) if e.strip()]
    print("\n--- 💰 ТВОИ ФИНАНСЫ ---")
    
    total_income = 0
    total_expense = 0
    
    for i, entry in enumerate(entries, 1):
        lines = entry.split("\n")
        date = lines[0] if len(lines) > 0 else ""
        details = lines[1] if len(lines) > 1 else ""
        
        print(f"{i}. {date} | {details}")
        
        try:
            amount = float(details.split("|")[-1].strip().replace("руб.", ""))
            if "Доход" in details:
                total_income += amount
            else:
                total_expense += amount
        except:
            pass

    print("=" * 40)
    print(f"📈 Всего доходов: {total_income} руб.")
    print(f"📉 Всего расходов: {total_expense} руб.")
    print(f"💰 ТЕКУЩИЙ БАЛАНС: {total_income - total_expense} руб.")
    print("=" * 40)

def add_finance(key, finance_text, limits_text):
    print("\n--- 💰 НОВАЯ ТРАНЗАКЦИЯ ---")
    print("1. 📉 Расход (потратил)")
    print("2. 📈 Доход (заработал)")
    
    trans_type = input("Выбери тип (1 или 2): ").strip()
    
    if trans_type == "1":
        t_type = "Расход"
        categories = EXPENSE_CATEGORIES
    elif trans_type == "2":
        t_type = "Доход"
        categories = INCOME_CATEGORIES
    else:
        print("Неверный тип.")
        return finance_text

    print("\n📂 Категории:")
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")
    
    try:
        cat_choice = int(input("Выбери категорию: "))
        category = categories[cat_choice-1] if 1 <= cat_choice <= len(categories) else "Другое"
    except ValueError:
        category = "Другое"

    try:
        amount = float(input("Введи сумму (только число): ").replace(",", "."))
    except ValueError:
        print("Ошибка: сумма должна быть числом.")
        return finance_text

    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M")
    entry = f"[{now_str}]\n{t_type} | {category} | {amount} руб.\n" + ("-" * 40) + "\n"
    
    new_finance = finance_text + entry
    save_data(key, new_finance, FINANCE_FILE)
    print("✅ Транзакция добавлена и зашифрована!")
    
    if t_type == "Расход" and limits_text:
        limits = {}
        for line in limits_text.split("\n"):
            if ":" in line:
                cat_name, limit_val = line.split(":")
                limits[cat_name.strip()] = float(limit_val.strip())
        
        if category in limits:
            limit = limits[category]
            current_month = now.strftime("%Y-%m")
            spent = 0
            for e in new_finance.split("-" * 40):
                lines = e.strip().split("\n")
                if len(lines) > 1:
                    date_part = lines[0].replace("[", "").replace("]", "")
                    details = lines[1]
                    if date_part.startswith(current_month) and f"| {category} |" in details and "Расход" in details:
                        try:
                            spent += float(details.split("|")[-1].strip().replace("руб.", ""))
                        except:
                            pass
            
            percent = (spent / limit) * 100
            if percent >= 100:
                print(f"\n🚨 ВНИМАНИЕ! Ты превысил лимит на '{category}' ({spent}/{limit} руб.)!")
            elif percent >= 80:
                print(f"\n⚠️ Ты потратил уже {percent:.0f}% от лимита на '{category}' ({spent}/{limit} руб.)!")
                
    return new_finance

def show_period_stats(finance_text):
    if not finance_text:
        print("\n💰 Транзакций пока нет.")
        return

    entries = [e.strip() for e in finance_text.split("-" * 40) if e.strip()]
    
    print("\n--- 📅 СТАТИСТИКА ЗА ПЕРИОД ---")
    print("1. За текущий месяц")
    print("2. За конкретный месяц (ГГГГ-ММ)")
    print("3. За текущий год")
    print("4. За конкретный год (ГГГГ)")
    print("5. Отмена")
    
    choice = input("Выбери (1-5): ").strip()
    
    now = datetime.now()
    target_year = str(now.year)
    target_month = f"{now.year}-{now.month:02d}"
    
    if choice == "1":
        period_name = f"Месяц {now.month}.{now.year}"
        filter_type = "month"
    elif choice == "2":
        target_month = input("Введи месяц (например, 2026-11): ").strip()
        period_name = f"Месяц {target_month}"
        filter_type = "month"
    elif choice == "3":
        period_name = f"Год {now.year}"
        filter_type = "year"
    elif choice == "4":
        target_year = input("Введи год (например, 2026): ").strip()
        period_name = f"Год {target_year}"
        filter_type = "year"
    else:
        return

    period_income = 0
    period_expense = 0

    for entry in entries:
        lines = entry.split("\n")
        date_str = lines[0].replace("[", "").replace("]", "").strip()
        details = lines[1] if len(lines) > 1 else ""
        
        match = False
        if filter_type == "month" and date_str.startswith(target_month):
            match = True
        elif filter_type == "year" and date_str.startswith(target_year + "-"):
            match = True
            
        if match:
            try:
                amount = float(details.split("|")[-1].strip().replace("руб.", ""))
                if "Доход" in details:
                    period_income += amount
                else:
                    period_expense += amount
            except:
                pass

    print("\n" + "=" * 40)
    print(f"📅 ПЕРИОД: {period_name}")
    print(f"📈 Доходы:  {period_income} руб.")
    print(f"📉 Расходы: {period_expense} руб.")
    balance = period_income - period_expense
    if balance >= 0:
        print(f"💰 Прибыль:  +{balance} руб. 🤑")
    else:
        print(f"💸 Убыток:  {balance} руб. 🥲")
    print("=" * 40)

def show_expense_chart(finance_text):
    if not finance_text:
        print("\nРасходов нет.")
        return

    expenses = {}
    entries = [e.strip() for e in finance_text.split("-" * 40) if e.strip()]
    
    for entry in entries:
        lines = entry.split("\n")
        if len(lines) > 1:
            details = lines[1]
            if "Расход" in details:
                parts = details.split("|")
                if len(parts) >= 3:
                    category = parts[1].strip()
                    try:
                        amount = float(parts[2].strip().replace("руб.", ""))
                        expenses[category] = expenses.get(category, 0) + amount
                    except:
                        pass

    if not expenses:
        print("\nРасходов пока нет.")
        return

    max_amount = max(expenses.values())
    print("\n📈 ГРАФИК РАСХОДОВ (по категориям):")
    print("=" * 40)
    
    for cat, amount in sorted(expenses.items(), key=lambda x: x[1], reverse=True):
        bar_length = int((amount / max_amount) * 20)
        bar = "█" * bar_length
        print(f"{cat:<12} |{bar:<20}| {amount} руб.")
    print("=" * 40)

def manage_limits(key, limits_text):
    while True:
        print("\n--- 🎯 ЛИМИТЫ БЮДЖЕТА ---")
        if limits_text:
            print("Текущие лимиты:")
            for line in limits_text.split("\n"):
                if ":" in line:
                    cat, val = line.split(":")
                    print(f"  • {cat}: {val} руб.")
        else:
            print("Лимитов пока нет.")
            
        print("\n1. Добавить/Изменить лимит")
        print("2. Удалить лимит")
        print("3. Назад")
        
        choice = input("Выбери (1-3): ").strip()
        
        if choice == "1":
            print("\nДоступные категории расходов:")
            for i, cat in enumerate(EXPENSE_CATEGORIES, 1):
                print(f"{i}. {cat}")
            
            try:
                cat_choice = int(input("Выбери категорию: "))
                category = EXPENSE_CATEGORIES[cat_choice-1] if 1 <= cat_choice <= len(EXPENSE_CATEGORIES) else "Другое"
            except ValueError:
                category = "Другое"
                
            try:
                limit_val = float(input(f"Введи лимит для '{category}' (руб.): ").replace(",", "."))
            except ValueError:
                print("Ошибка: нужно ввести число.")
                continue
                
            new_limits = ""
            found = False
            if limits_text:
                for line in limits_text.split("\n"):
                    if line.startswith(category + ":"):
                        new_limits += f"{category}: {limit_val}\n"
                        found = True
                    elif line.strip():
                        new_limits += line + "\n"
            if not found:
                new_limits += f"{category}: {limit_val}\n"
                
            limits_text = new_limits.strip()
            save_data(key, limits_text, LIMITS_FILE)
            print("✅ Лимит установлен!")
            
        elif choice == "2":
            if not limits_text:
                print("Лимитов нет.")
                continue
            print("\nСуществующие лимиты:")
            lines = [l for l in limits_text.split("\n") if l.strip()]
            for i, line in enumerate(lines, 1):
                print(f"{i}. {line}")
            
            try:
                num = int(input("Выбери номер для удаления (0 - отмена): "))
                if 1 <= num <= len(lines):
                    del lines[num-1]
                    limits_text = "\n".join(lines)
                    save_data(key, limits_text, LIMITS_FILE)
                    print("✅ Лимит удален.")
            except ValueError:
                pass
        elif choice == "3":
            break
    return limits_text

# ================= ФУНКЦИИ ПРИВЫЧЕК =================

def manage_habits(key, habits_text):
    while True:
        print("\n--- 🎯 ТРЕКЕР ПРИВЫЧЕК ---")
        print("1. 📖 Посмотреть мой список привычек")
        print("2. ➕ Добавить новую привычку")
        print("3. 🔙 Назад в главное меню")
        
        choice = input("Выбери (1-3): ").strip()
        
        if choice == "1":
            while True:
                print("\n--- 📖 ТВОИ ПРИВЫЧКИ ---")
                
                habits = {}
                if habits_text:
                    for line in habits_text.split("\n"):
                        if "|" in line:
                            name, dates_str = line.split("|")
                            habits[name.strip()] = dates_str.strip().split(",") if dates_str.strip() else []
                
                if not habits:
                    print("У тебя пока нет привычек.")
                    break
                
                today_str = datetime.now().strftime("%Y-%m-%d")
                for i, (name, dates) in enumerate(habits.items(), 1):
                    streak = 0
                    current_day = datetime.now()
                    while True:
                        day_str = current_day.strftime("%Y-%m-%d")
                        if day_str in dates:
                            streak += 1
                            current_day -= timedelta(days=1)
                        else:
                            break
                    
                    status = "✅ Сделано" if today_str in dates else "❌ Нет"
                    short_name = name[:15] + ".." if len(name) > 15 else name
                    print(f"{i}. {short_name:<17} | 🔥 {streak} дн. | {status}")

                print("\n1. ✅ Отметить выполнение на сегодня")
                print("2. 🗑️ Удалить привычку")
                print("3. 🔙 Назад")
                
                inner_choice = input("Выбери (1-3): ").strip()
                
                if inner_choice == "1":
                    try:
                        num = int(input("Выбери номер привычки для отметки: "))
                        habit_names = list(habits.keys())
                        if 1 <= num <= len(habit_names):
                            name = habit_names[num-1]
                            if today_str not in habits[name]:
                                habits[name].append(today_str)
                                new_text = "\n".join([f"{n}|{','.join(d)}" for n, d in habits.items()])
                                save_data(key, new_text, HABITS_FILE)
                                habits_text = new_text
                                print(f"✅ Отлично! Привычка '{name}' отмечена на сегодня.")
                            else:
                                print("Ты уже отмечал эту привычку сегодня.")
                    except ValueError:
                        print("Ошибка ввода.")
                
                elif inner_choice == "2":
                    try:
                        num = int(input("Выбери номер привычки для удаления: "))
                        habit_names = list(habits.keys())
                        if 1 <= num <= len(habit_names):
                            name = habit_names[num-1]
                            del habits[name]
                            new_text = "\n".join([f"{n}|{','.join(d)}" for n, d in habits.items()])
                            save_data(key, new_text, HABITS_FILE)
                            habits_text = new_text
                            print(f"🗑️ Привычка '{name}' удалена.")
                    except ValueError:
                        print("Ошибка ввода.")
                
                elif inner_choice == "3":
                    break

        elif choice == "2":
            name = input("Введи название привычки (например, Зарядка): ").strip()
            if name:
                habits = {}
                if habits_text:
                    for line in habits_text.split("\n"):
                        if "|" in line:
                            n, d = line.split("|")
                            habits[n.strip()] = d.strip().split(",") if d.strip() else []
                
                habits[name] = []
                new_text = "\n".join([f"{n}|{','.join(d)}" for n, d in habits.items()])
                save_data(key, new_text, HABITS_FILE)
                habits_text = new_text
                print(f"✅ Привычка '{name}' добавлена!")
                
        elif choice == "3":
            break
            
    return habits_text

# ================= ГЛАВНОЕ МЕНЮ =================

def main():
    print("🔐 Добро пожаловать в зашифрованный дневник!")
    
    if os.path.exists(FILE_NAME):
        password = input("Введи пароль: ").strip()
        key = get_key(password)
        current_text = load_data(key, FILE_NAME)
        if current_text is None:
            print("❌ Неверный пароль!")
            return
        trash_text = load_data(key, TRASH_FILE)
        if trash_text is None: trash_text = ""
        finance_text = load_data(key, FINANCE_FILE)
        if finance_text is None: finance_text = ""
        limits_text = load_data(key, LIMITS_FILE)
        if limits_text is None: limits_text = ""
        habits_text = load_data(key, HABITS_FILE)
        if habits_text is None: habits_text = ""
        print("✅ Дневник разблокирован.")
    else:
        password = input("Придумай пароль: ").strip()
        key = get_key(password)
        current_text = ""
        trash_text = ""
        finance_text = ""
        limits_text = ""
        habits_text = ""

    while True:
        print("\n📔 ГЛАВНОЕ МЕНЮ")
        print("1. 📝 МОИ ЗАПИСИ (Дневник)")
        print("2. 💰 МОИ ФИНАНСЫ")
        print("3. 🎯 МОИ ПРИВЫЧКИ")
        print("4. ⚙️ НАСТРОЙКИ И КОРЗИНА")
        print("5. 🚪 ВЫХОД")

        choice = input("Выбери раздел (1-5): ").strip()

        # --- РАЗДЕЛ 1: ЗАПИСИ ---
        if choice == "1":
            while True:
                print("\n📝 РАЗДЕЛ ЗАПИСЕЙ")
                print("1. ✍️ Добавить запись (текст)")
                print("2. 📖 Показать все записи")
                print("3. 🔍 Поиск по тексту")
                print("4. 📂 Поиск по категории")
                print("5. 🏷️ Поиск по тегу")
                print("6. ✏️ Редактировать запись")
                print("7. 🗑️ Удалить запись (в корзину)")
                print("8. 📅 Календарь активности")
                print("9. 🔙 Назад в главное меню")
                
                sub_choice = input("Выбери (1-9): ").strip()
                
                if sub_choice == "1":
                    text = input("\nЧто нового? Напиши запись:\n> ").strip()
                        
                    if text:
                        print("\n📂 Выбери категорию:")
                        for i, cat in enumerate(CATEGORIES, 1):
                            print(f"{i}. {cat}")
                        try:
                            cat_choice = int(input("Твой выбор (1-4): "))
                            category = CATEGORIES[cat_choice-1] if 1 <= cat_choice <= len(CATEGORIES) else "Разное"
                        except ValueError:
                            category = "Разное"

                        tag_input = input("Добавить тег? (Enter - пропустить): ").strip()
                        tag_str = f"#{tag_input} " if tag_input else ""
                        
                        now = datetime.now().strftime("%Y-%m-%d %H:%M")
                        entry = f"[{now}] [{category}] {tag_str}\n{text}\n" + ("-" * 40) + "\n"
                        current_text += entry
                        save_data(key, current_text, FILE_NAME)
                        print("✅ Сохранено!")
                    else:
                        print("Пустая запись — отменяю.")
                        
                elif sub_choice == "2":
                    if not current_text: print("\nПусто.")
                    else: print("\n" + "=" * 40 + f"\n{current_text}" + "=" * 40)
                elif sub_choice == "3": search_entries(current_text)
                elif sub_choice == "4": search_by_category(current_text)
                elif sub_choice == "5": search_by_tag(current_text)
                elif sub_choice == "6": current_text = edit_entry(key, current_text)
                elif sub_choice == "7": current_text, trash_text = delete_entry(key, current_text, trash_text)
                elif sub_choice == "8": show_calendar(current_text)
                elif sub_choice == "9": break
                else: print("Нет такого пункта.")

        # --- РАЗДЕЛ 2: ФИНАНСЫ ---
        elif choice == "2":
            while True:
                print("\n💰 РАЗДЕЛ ФИНАНСОВ")
                print("1. 📊 Показать баланс и историю")
                print("2. ➕ Добавить доход/расход")
                print("3. 📅 Статистика за месяц/год")
                print("4. 📈 График расходов")
                print("5. 🎯 Настроить лимиты")
                print("6. 🔙 Назад в главное меню")
                fin_choice = input("Выбери (1-6): ").strip()
                
                if fin_choice == "1": show_finance(finance_text)
                elif fin_choice == "2": finance_text = add_finance(key, finance_text, limits_text)
                elif fin_choice == "3": show_period_stats(finance_text)
                elif fin_choice == "4": show_expense_chart(finance_text)
                elif fin_choice == "5": limits_text = manage_limits(key, limits_text)
                elif fin_choice == "6": break
                else: print("Нет такого пункта.")

        # --- РАЗДЕЛ 3: ПРИВЫЧКИ ---
        elif choice == "3":
            habits_text = manage_habits(key, habits_text)

        # --- РАЗДЕЛ 4: НАСТРОЙКИ И КОРЗИНА ---
        elif choice == "4":
            while True:
                print("\n⚙️ НАСТРОЙКИ И КОРЗИНА")
                print("1. 🔑 Сменить пароль")
                print("2. ♻️ Открыть корзину")
                print("3. 🔙 Назад в главное меню")
                set_choice = input("Выбери (1-3): ").strip()
                
                if set_choice == "1":
                    key = change_password(key, current_text)
                elif set_choice == "2":
                    current_text, trash_text = manage_trash(key, current_text, trash_text)
                elif set_choice == "3":
                    break
                else:
                    print("Нет такого пункта.")

        # --- РАЗДЕЛ 5: ВЫХОД ---
        elif choice == "5":
            print("Пока! 👋")
            break
        else:
            print("❌ Нет такого пункта, попробуй ещё.")

if __name__ == "__main__":
    main()