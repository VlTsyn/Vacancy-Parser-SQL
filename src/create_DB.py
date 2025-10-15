from typing import List

import psycopg2
from psycopg2.extensions import connection

from src.employer import Employer
from src.hh import HH


def get_conn(host: str, database: str, user: str, password: str) -> connection:
    """Функция соединения с Базой Данных"""

    return psycopg2.connect(host=host, database=database, user=user, password=password)


def clear_database(host: str, database: str, user: str, password: str) -> None:
    """Функция пересоздания Базы Данных"""

    conn = get_conn(host, database, user, password)

    cur = conn.cursor()

    cur.execute("DROP SCHEMA public CASCADE")
    cur.execute("CREATE SCHEMA public")
    cur.execute("GRANT ALL ON SCHEMA public TO postgres")
    cur.execute("GRANT ALL ON SCHEMA public TO public")

    conn.commit()
    cur.close()
    conn.close()


def create_tables(companies: List[Employer], host: str, database: str, user: str, password: str) -> None:
    """Функция создания таблиц"""

    conn = get_conn(host, database, user, password)

    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE vacancies(
            employer_id int NOT NULL,
            vacancy_name varchar(100) NOT NULL,
            area varchar(100),
            salary_from int,
            salary_to int,
            currency varchar(3),
            url text)
    """
    )

    for company in companies:
        result = HH().load_employer_vacancies(company.id)
        for r in result:
            employer_id = company.id
            name = r["name"]
            area = r["area"]["name"]
            if r["salary"] is None:
                salary_from = None
                salary_to = None
                currency = None
            else:
                salary_from = r["salary"]["from"]
                salary_to = r["salary"]["to"]
                currency = r["salary"]["currency"]
            url = r["url"]
            cur.execute(
                "INSERT INTO vacancies VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (employer_id, name, area, salary_from, salary_to, currency, url),
            )

    cur.execute(
        """
        CREATE TABLE employers(
            employer_id int PRIMARY KEY NOT NULL,
            employer_name text,
            vacancies int)
    """
    )

    for company in companies:
        cur.execute(f"SELECT COUNT(*) FROM vacancies WHERE employer_id = {company.id}")
        vacancies_count = cur.fetchone()[0]
        employer_id = company.id
        name = company.name
        cur.execute("INSERT INTO employers VALUES (%s, %s, %s)", (employer_id, name, vacancies_count))

    cur.execute(
        """
        ALTER TABLE vacancies 
        ADD CONSTRAINT fk_employer_vacancies 
        FOREIGN KEY(employer_id) 
        REFERENCES employers(employer_id)
    """
    )

    conn.commit()

    cur.close()

    conn.close()
