import csv
from urllib.parse import urljoin

from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support import expected_conditions as EC

from driver import ChromeWebDriver
from models import Vacancy

BASE_URL = "https://djinni.co/"
JOBS_URL = urljoin(BASE_URL, "jobs/?primary_keyword=Python&")

PAGES = {
    "one_year": 'https://djinni.co/jobs/?primary_keyword=Python&exp_level=1y',
    "two_years": 'https://djinni.co/jobs/?primary_keyword=Python&exp_level=2y',
    "three_years": 'https://djinni.co/jobs/?primary_keyword=Python&exp_level=3y',
    # "no_experience": urljoin(JOBS_URL, "exp_level=no_exp"),
    # "one_year": urljoin(JOBS_URL, "exp_level=1y"),
    # "two_years": urljoin(JOBS_URL, "exp_level=2y"),
    # "three_years": urljoin(JOBS_URL, "exp_level=3y"),
    # "five_years": urljoin(JOBS_URL, "exp_level=5y"),
    #
    # "remote": urljoin(JOBS_URL, "employment=remote"),
    # "part_time": urljoin(JOBS_URL, "employment=parttime"),
    # "office": urljoin(JOBS_URL, "employment=office"),
}


def pagination(driver):
    next_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "bi-chevron-right")))
    next_button.click()


def parse(product_element: WebElement) -> Vacancy:
    title = product_element.find_element(By.CSS_SELECTOR, '.job-list-item__title a').text.strip()
    # company = product_element.find_element(By.CSS_SELECTOR, '.d-flex a').text.strip()
    # location = product_element.find_element(By.CSS_SELECTOR, '.location-text').text.strip()
    # category = product_element.find_element(By.CSS_SELECTOR, '.job-list-item__job-info .nobr:nth-child(2)').text.strip()
    # employment_type = product_element.find_element(By.CSS_SELECTOR, '.job-list-item__job-info .nobr:nth-child(3)').text.strip()
    # experience = product_element.find_element(By.CSS_SELECTOR, '.job-list-item__job-info .nobr:nth-child(4)').text.strip()
    # language_level = product_element.find_element(By.CSS_SELECTOR, '.job-list-item__job-info .nobr:nth-child(5)').text.strip()
    # description = product_element.find_element(By.CSS_SELECTOR, '.job-list-item__description').text.strip()

    return Vacancy(title,)
                   # company,
                   # location,
                   # category,
                   # employment_type,
                   # experience,
                   # language_level,
                   # description)


def export_to_csv(file_name: str, vacancies: list[Vacancy]) -> None:
    with open(file_name, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        rows = [[v.title]
                for v in vacancies]

        csvwriter.writerows(rows)


def scrape_page(name, url):
    with ChromeWebDriver() as driver:
        driver.get(url)
        products = driver.find_elements(By.CLASS_NAME, 'job-list-item')
        print(products)
        products = [parse(product) for product in tqdm(products, desc=f"Scraping {name}")]
        export_to_csv(f"{name}.csv", products)
        # pagination(driver)


def get_all_products() -> None:
    for name, url in PAGES.items():
        scrape_page(name, url)


if __name__ == "__main__":
    get_all_products()
