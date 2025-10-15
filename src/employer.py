from typing import Any, Dict


class Employer:
    """Класс для компаний"""

    def __init__(self, id: str, name: str, vacancies: str) -> None:
        self.id = id
        self.name = name
        self.vacancies = vacancies

    def __str__(self) -> str:
        return f"Компания: {self.name} | Вакансий: {self.vacancies}"

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Employer":
        """Функция перевода из JSON формата"""
        id = data.get("id")
        name = data.get("name")
        vacancies = data.get("open_vacancies")

        return cls(id=id, name=name, vacancies=vacancies)
