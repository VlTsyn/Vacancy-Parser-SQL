from typing import Dict, List

from src.create_DB import clear_database, create_tables
from src.DB_manager import DBManager
from src.employer import Employer
from src.hh import HH


def user_interface() -> None:
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

            if manager.connect() == "error":
                print(f"Базы Данных {params['database']} не существует")
            else:
                print(f"Подключение к Базе Данных {params['database']} установлено")
                database_manage(manager)

        elif choice == "3":
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Попробуйте снова")


def get_db_params() -> Dict[str, str]:
    """Запрос параметров для Базы Данных"""

    print("Введите параметры для Базы Данных или оставьте поле пустым для значений по умолчанию")
    params = {
        "host": input(f"Имя хоста [localhost]: ").strip() or "localhost",
        "database": input(f"Название базы данных [HH_DB]: ").strip() or "HH_DB",
        "user": input(f"Имя пользователя [postgres]: ").strip() or "postgres",
        "password": input("Пароль: ").strip() or "",
    }
    return params


def database_manage(manager: DBManager) -> None:
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
            print(f"Компания: {r['name']} | " f"Кол-во вакансий: {r['vacancies']}")

        database_manage(manager)

    elif choice == "2":

        result = manager.get_all_vacancies()
        for r in result:
            print(
                f"Компания: '{r['company_name']}' | "
                f"Вакансия: {r['vacancy_name']} | "
                f"Зарплата: {r['salary']} | "
                f"Ссылка: {r['url']}"
            )

        database_manage(manager)

    elif choice == "3":

        result = manager.get_avg_salary()
        print(f"Средняя зарплата: {result}")

        database_manage(manager)

    elif choice == "4":

        result = manager.get_vacancies_with_higher_salary()
        for r in result:
            print(
                f"Компания: '{r['company_name']}' | "
                f"Вакансия: {r['vacancy_name']} | "
                f"Зарплата: {r['salary']} | "
                f"Ссылка: {r['url']}"
            )

        database_manage(manager)

    elif choice == "5":

        keyword = input("Введите ключевое слово: ")
        result = manager.get_vacancies_with_keyword(keyword)

        if result:
            for r in result:
                print(
                    f"Компания: '{r['company_name']}' | "
                    f"Вакансия: {r['vacancy_name']} | "
                    f"Зарплата: {r['salary']} | "
                    f"Ссылка: {r['url']}"
                )
        else:
            print(f"Вакансий с ключевым словом '{keyword}' не найдено")

        database_manage(manager)

    elif choice == "6":

        manager.disconnect()

        return

    else:
        print("Неверный выбор. Попробуйте снова")
        database_manage(manager)


def search_employers() -> List[Employer]:
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
