import csv
from urllib.parse import urljoin

from tqdm import tqdm

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
        return None


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


def export_to_csv(file_name: str, vacancies: list[Vacancy]) -> None:
    with open(file_name, "+a", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        rows = [[v.title,
                 v.company,
                 v.location,
                 v.category,
                 v.employment_type,
                 v.experience,
                 v.language_level,
                 v.description]
                for v in vacancies]

        csvwriter.writerows(rows)


def scrape_page(url, name="db"):
    with ChromeWebDriver() as driver:
        driver.get(url)
        while True:
            products = driver.find_elements(By.CLASS_NAME, 'job-list-item')
            products = [parse(product) for product in tqdm(products, desc=f"Scraping {name}")]
            export_to_csv(f"{name}.csv", products)
            if not pagination(driver):
                break


if __name__ == "__main__":
    scrape_page(JOBS_URL)
