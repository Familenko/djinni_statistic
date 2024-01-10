import dataclasses


@dataclasses.dataclass
class Vacancies:
    title: str
    company: str
    location: str
    requirements: list[str]
    description: str
    views_count: str
    reviews_count: str
