import os
from src.hh import HH
from src.employer import Employer
from src.create_DB import create_tables, clear_database
from src.DB_manager import DBManager
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_DATA = os.getenv("DB_DATA")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


def user_interface():
    """Функция взаимодействия с пользователем"""

    while True:
        print("\nВыберите действие:")
        print("1. Создание новой Базы Данных")
        print("2. Использовать готовую Базу Данных")
        print("3. Выход")

        choice = input("\nВведите номер действия: ").strip()

        if choice == "1":

            params = get_db_params()

            clear_database(**params)

            company_list = search_employers()

            print("Идет создание Базы Данных...")

            create_tables(company_list, **params)

            print("База Данных создана")

            manager = DBManager(**params)

            database_manage(manager)

        elif choice == "2":

            params = get_db_params()
            manager = DBManager(**params)

            database_manage(manager)

        elif choice == "3":
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Попробуйте снова")


def get_db_params():
    """Запрос параметров для Базы Данных"""

    print("Введите параметры для Базы Данных или оставьте поле пустым для значений по умолчанию")
    params = {
        'host': input(f"Имя хоста [{DB_HOST}]: ").strip() or DB_HOST,
        'database': input(f"Название базы данных [{DB_DATA}]: ").strip() or DB_DATA,
        'user': input(f"Имя пользователя [{DB_USER}]: ").strip() or DB_USER,
        'password': input("Пароль: ").strip() or DB_PASS
    }
    return params


def database_manage(manager):
    """Функция взаимодействия с Базой Данных"""

    print("\nВыберите действие:")
    print("1. Список компаний и кол-во их вакансий")
    print("2. Список всех вакансий")
    print("3. Средняя зарплата по вакансиям")
    print("4. Список вакансий с зарплатой выше средней")
    print("5. Список вакансий по ключевому слову")
    print("6. Выход")

    choice = input("\nВведите номер действия: ").strip()

    if choice == "1":

        result = manager.get_companies_and_vacancies_count()
        for r in result:
            print(f"Компания: {r['name']} | Кол-во вакансий: {r['vacancies']}")

        database_manage(manager)

    elif choice == "2":

        result = manager.get_all_vacancies()
        for r in result:
            print(f"Компания: '{r['company_name']}' | Вакансия: {r['vacancy_name']} | Зарплата: {r['salary']} | Ссылка: {r['url']}")

        database_manage(manager)

    elif choice == "3":

        result = manager.get_avg_salary()
        print(f"Средняя зарплата: {result}")

        database_manage(manager)

    elif choice == "4":

        result = manager.get_vacancies_with_higher_salary()
        for r in result:
            print(f"Компания: '{r['company_name']}' | Вакансия: {r['vacancy_name']} | Зарплата: {r['salary']} | Ссылка: {r['url']}")

        database_manage(manager)

    elif choice == "5":

        keyword = input("Введите ключевое слово: ")
        result = manager.get_vacancies_with_keyword(keyword)
        for r in result:
            print(f"Компания: '{r['company_name']}' | Вакансия: {r['vacancy_name']} | Зарплата: {r['salary']} | Ссылка: {r['url']}")

        database_manage(manager)

    elif choice == "6":

        manager.disconnect()

        return

    else:
        print("Неверный выбор. Попробуйте снова")
        database_manage(manager)


def search_employers():
    """Функция поиска компаний"""

    print("Для создания новой Базы Данных необходимо выбрать 10 компаний")
    company_list = []
    company_list_id = []
    while len(company_list) < 10:
        remaining = 10 - len(company_list)
        if remaining == 1:
            info = f"{remaining} компания"
        elif 1 < remaining < 5:
            info = f"{remaining} компании"
        else:
            info = f"{remaining} компаний"
        print(f"Осталось для записи {info}")

        search = input("Введите название компании: ").strip()

        print("Идет поиск компаний...")

        result = HH().load_employers(search)
        employers = [Employer.from_json(r) for r in result]

        count = 0
        employer_dict = {}
        for employer in employers:
            count += 1
            employer_dict[count] = employer
            print(f"{count} {employer}")

        choice = input("Введите номер компании для записи в Базу Данных: ").strip()
        keywords = [k.strip() for k in choice.replace(",", " ").split()]

        selected_companies = []
        for key in keywords:
            employer = employer_dict.get(int(key))
            if employer:
                if employer.id not in company_list_id:
                    selected_companies.append(employer)
                    company_list_id.append(employer.id)
                else:
                    print(f"Компания '{employer.name}' уже добавлена ранее и будет пропущена")
            else:
                print(f"Компании под номером {key} нет в списке")

        if not selected_companies:
            print("Выберите другие компании")
            continue

        if len(selected_companies) > remaining:
            print(f"Для записи доступно только {info}")
            print(f"Будут записаны следующие компании: ")
            for company_id in selected_companies[:remaining]:
                for employer in employers:
                    if employer.id == company_id:
                        print(employer.name)
            selected_companies = selected_companies[:remaining]

        company_list.extend(selected_companies)
        if len(company_list) >= 10:
            break

    return company_list
