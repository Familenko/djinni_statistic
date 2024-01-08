import csv
from urllib.parse import urljoin

import numpy as np
from tqdm import tqdm

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException

from driver import ChromeWebDriver
from models import Vacancies

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


def parse(product_element: WebElement) -> Vacancies:
    title = get_text_or_none(product_element, '.job-list-item__title a')
    location = get_text_or_none(product_element, '.location-text')
    description = get_text_or_none(product_element, '.job-list-item__description')

    views_count = get_text_or_none(product_element, '.mr-2[title*="відгуків"]')
    reviews_count = get_text_or_none(product_element, '.mr-2[title*="переглядів"]')

    requirements_elements = product_element.find_elements(By.CSS_SELECTOR, '.job-list-item__job-info .nobr')
    requirements = [element.text.strip() for element in requirements_elements]

    company_element = product_element.find_element(By.CSS_SELECTOR, '.mr-2[href*="/jobs/?company="]')
    company = company_element.text.strip() if company_element else np.nan

    return Vacancies(
        title=title,
        company=company,
        location=location,
        requirements=requirements,
        description=description,
        views_count=views_count,
        reviews_count=reviews_count
    )


def create_csv(file_name: str) -> None:
    with open(file_name, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        rows = [["title", "company", "location", "requirements",
                 "description", "views_count", "reviews_count"]]
        csvwriter.writerows(rows)


def export_to_csv(file_name: str, vacancies: list[Vacancies]) -> None:
    with open(file_name, "+a", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        rows = [[v.title, v.company, v.location, v.requirements, v.description, v.views_count,
                 v.reviews_count]
                for v in vacancies]

        csvwriter.writerows(rows)


def scrape_page(url, name="analytic/db"):
    create_csv(f"{name}.csv")
    with ChromeWebDriver() as driver:
        driver.get(url)
        while True:
            vacancies = driver.find_elements(By.CLASS_NAME, 'job-list-item')
            vacancies = [parse(vacancy) for vacancy in tqdm(vacancies, desc=f"Scraping {name}")]
            export_to_csv(f"{name}.csv", vacancies)
            if not pagination(driver):
                break


if __name__ == "__main__":
    scrape_page(JOBS_URL)
