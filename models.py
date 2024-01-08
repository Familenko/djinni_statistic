from dataclasses import dataclass


@dataclass
class Vacancy:
    title: str
    company: str
    location: str
    category: str
    employment_type: str
    experience: str
    language_level: str
    description: str
