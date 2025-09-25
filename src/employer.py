class Employer:
    """Класс для компаний"""

    def __init__(self, id, name, vacancies):
        self.id = id
        self.name = name
        self.vacancies = vacancies

    def __str__(self):
        return f"Компания: {self.name} | Вакансий: {self.vacancies}"

    @classmethod
    def from_json(cls, data: dict):
        id = data.get("id")
        name = data.get("name")
        vacancies = data.get("open_vacancies")

        return cls(
            id=id,
            name=name,
            vacancies=vacancies
        )