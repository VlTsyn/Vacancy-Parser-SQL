from typing import Any, Dict, List, Optional

import psycopg2


class DBManager:
    """Класс для работы с Базой Данных"""

    def __init__(self, host: str, database: str, user: str, password: str) -> None:
        self.params = {"host": host, "database": database, "user": user, "password": password}
        self.conn = None
        self.connect()

    def connect(self) -> Optional[str]:
        """Установка соединения с базой данных"""

        try:
            self.conn = psycopg2.connect(**self.params)
        except Exception:
            return "error"

    def disconnect(self) -> None:
        """Закрытие соединения с базой данных"""

        if self.conn:
            self.conn.close()
            print("Отключение от Базы Данных")

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получение списка компаний и кол-ва их вакансий"""

        cur = self.conn.cursor()
        cur.execute("SELECT employer_name, vacancies FROM employers")
        result = cur.fetchall()

        companies = []
        for r in result:
            companies.append({"name": r[0], "vacancies": r[1]})

        return companies

    @staticmethod
    def calculate_avg_salary(salary_from: int, salary_to: int) -> float:
        """Вычисление среднего значения зарплаты"""

        if salary_from is not None and salary_to is not None:
            return (salary_from + salary_to) / 2
        elif salary_from is not None:
            return salary_from
        elif salary_to is not None:
            return salary_to
        else:
            return 0

    def get_salary_info(self, salary_from: int, salary_to: int, currency: str) -> str:
        """Информация по зарплате"""

        if self.calculate_avg_salary(salary_from, salary_to) == 0:
            return "Зарплата не указана"

        salary_info = ""
        if salary_from is not None:
            salary_info += f"от {salary_from}"
        if salary_to is not None:
            if salary_info:
                salary_info += " "
            salary_info += f"до {salary_to}"

        salary_info += f" {currency}"

        return salary_info

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получение списка вакансий"""

        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT employer_name, vacancy_name, salary_from, salary_to, currency, url 
            FROM employers 
            JOIN vacancies USING(employer_id)
            """
        )
        result = cur.fetchall()

        vacancies = []
        for r in result:
            vacancies.append(
                {
                    "company_name": r[0],
                    "vacancy_name": r[1],
                    "salary": self.get_salary_info(r[2], r[3], r[4]),
                    "currency": r[4],
                    "url": r[5],
                }
            )

        return vacancies

    def get_avg_salary(self) -> float:
        """Получение средней зарплаты"""

        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT AVG(
                CASE 
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                        THEN (salary_from + salary_to) / 2
                    WHEN salary_from IS NOT NULL THEN salary_from
                    WHEN salary_to IS NOT NULL THEN salary_to
                    ELSE NULL
                END
            ) as avg_salary
            FROM vacancies
        """
        )

        result = cur.fetchone()
        avg_salary = result[0] if result[0] is not None else 0
        return round(avg_salary, 2)

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получение вакансий с зарплатой выше среднего"""

        cur = self.conn.cursor()
        cur.execute(
            """
             WITH avg_salary AS (
                SELECT AVG(
                    CASE 
                        WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                            THEN (salary_from + salary_to) / 2
                        WHEN salary_from IS NOT NULL THEN salary_from
                        WHEN salary_to IS NOT NULL THEN salary_to
                        ELSE NULL
                    END
                ) as avg_value
                FROM vacancies
            )
            SELECT employer_name, vacancy_name, salary_from, salary_to, currency, url 
            FROM employers 
            JOIN vacancies USING(employer_id)
            WHERE (
                CASE 
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                        THEN (salary_from + salary_to) / 2
                    WHEN salary_from IS NOT NULL THEN salary_from
                    WHEN salary_to IS NOT NULL THEN salary_to
                    ELSE NULL
                END
            ) > (SELECT avg_value FROM avg_salary)
        """
        )
        result = cur.fetchall()

        vacancies_with_higher_salary = []
        for r in result:
            vacancies_with_higher_salary.append(
                {
                    "company_name": r[0],
                    "vacancy_name": r[1],
                    "salary": self.get_salary_info(r[2], r[3], r[4]),
                    "currency": r[4],
                    "url": r[5],
                }
            )

        return vacancies_with_higher_salary

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получение вакансий с ключевым словом"""

        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT employer_name, vacancy_name, salary_from, salary_to, currency, url 
            FROM employers 
            JOIN vacancies 
            USING(employer_id)
            WHERE LOWER(vacancy_name) LIKE LOWER(%s)
        """,
            (f"%{keyword}%",),
        )

        result = cur.fetchall()

        vacancies_with_keyword = []
        for r in result:
            vacancies_with_keyword.append(
                {
                    "company_name": r[0],
                    "vacancy_name": r[1],
                    "salary": self.get_salary_info(r[2], r[3], r[4]),
                    "currency": r[4],
                    "url": r[5],
                }
            )

        return vacancies_with_keyword
