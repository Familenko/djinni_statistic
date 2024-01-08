import csv
from urllib.parse import urljoin

import numpy as np
from tqdm import tqdm
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException

from driver import ChromeWebDriver
from models import Vacancy

BASE_URL = "https://djinni.co/"
JOBS_URL = urljoin(BASE_URL, "jobs/?primary_keyword=Python")


def pagination(driver):
    try:
        next_page = driver.find_element(By.CSS_SELECTOR, '.page-item:last-child a')
    except NoSuchElementException:
        return False

    try:
        next_page.click()
        return True
    except ElementClickInterceptedException:
        return False


def get_text_or_none(element, selector):
    try:
        return element.find_element(By.CSS_SELECTOR, selector).text.strip()
    except NoSuchElementException:
        return np.nan


def parse(product_element: WebElement) -> Vacancy:
    title = get_text_or_none(product_element, '.job-list-item__title a')
    company = get_text_or_none(product_element, '.d-flex a')
    location = get_text_or_none(product_element, '.location-text')
    category = get_text_or_none(product_element, '.job-list-item__job-info .nobr:nth-child(2)')
    employment_type = get_text_or_none(product_element, '.job-list-item__job-info .nobr:nth-child(3)')
    experience = get_text_or_none(product_element, '.job-list-item__job-info .nobr:nth-child(4)')
    language_level = get_text_or_none(product_element, '.job-list-item__job-info .nobr:nth-child(5)')
    description = get_text_or_none(product_element, '.job-list-item__description')

    return Vacancy(
        title, company, location, category,
        employment_type, experience, language_level, description
    )


def export_to_csv(vacancies: list[Vacancy], file_name: str = 'db') -> None:
    data = {
        'Title': [v.title for v in vacancies],
        'Company': [v.company for v in vacancies],
        'Location': [v.location for v in vacancies],
        'Category': [v.category for v in vacancies],
        'Employment Type': [v.employment_type for v in vacancies],
        'Experience': [v.experience for v in vacancies],
        'Language Level': [v.language_level for v in vacancies],
        'Description': [v.description for v in vacancies],
    }

    df = pd.DataFrame(data)

    df.to_csv(f'{file_name}.csv', mode='a', index=False)


def scrape_page(url, name="db"):
    with ChromeWebDriver() as driver:
        driver.get(url)
        while True:
            products = driver.find_elements(By.CLASS_NAME, 'job-list-item')
            products = [parse(product) for product in tqdm(products, desc=f"Scraping {name}")]
            export_to_csv(products)
            if not pagination(driver):
                break


if __name__ == "__main__":
    scrape_page(JOBS_URL)
