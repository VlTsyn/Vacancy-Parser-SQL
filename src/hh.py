import requests

from src.base_api import BaseAPI


class HH(BaseAPI):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.url = "https://api.hh.ru"
        self.headers = {"User-Agent": "HH-User-Agent"}
        self.params = {"text": "", "page": 0, "per_page": 100}
        self.employers = []
        self.vacancies = []

    def load_employers(self, keyword: str):
        self.params["text"] = keyword
        while self.params.get("page") != 20:
            response = requests.get(f"{self.url}/employers", headers=self.headers, params=self.params)
            employers = response.json()["items"]
            self.employers.extend(employers)
            self.params["page"] += 1
        return self.employers

    def load_employer_vacancies(self, employer_id: str):
        page = 0
        while True:
            response = requests.get(f"{self.url}/vacancies?employer_id={employer_id}&page={page}")
            vacancies = response.json()["items"]
            if not vacancies:
                break
            page += 1
            self.vacancies.extend(vacancies)
        return self.vacancies
