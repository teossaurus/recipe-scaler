# Standard library imports
import requests
import time
from requests.exceptions import RequestException

import functions_framework

# Third party imports
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import justext
from io import BytesIO


def trim_website_body(website_body: str) -> str:
    encoded = website_body.split(" ")
    num_tokens = len(encoded)
    if num_tokens > 5000:
        return " ".join(encoded[:5000])
    else:
        return website_body


def call_url(url, fallback_on_selenium=True):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
    except:
        return "Could not open website."
    else:
        html_page = res.content
        print(html_page)
        paragraphs = justext.justext(
            html_page, justext.get_stoplist("English"), no_headings=False
        )
        plain_text = "\n".join(
            [p.text for p in paragraphs if not p.is_boilerplate or p.is_heading]
        )
        if (
            not plain_text.strip() and fallback_on_selenium
        ):  # Check if plain_text is empty after justext processing
            print(
                "Request failed or empty content after justext processing. Trying Selenium..."
            )
            html_page = get_html_with_selenium(url)
            if (
                not html_page.strip()
            ):  # Check if the html_page is not just whitespace after Selenium fetch
                msg = "No HTML content retrieved from the URL."
                print(msg)
                return msg
            paragraphs = justext.justext(
                html_page, justext.get_stoplist("English"), no_headings=False
            )
            plain_text = "\n".join(
                [p.text for p in paragraphs if not p.is_boilerplate or p.is_heading]
            )

    return trim_website_body(plain_text)


def get_html_with_selenium(url, time_to_sleep=None, tag_to_await=None):
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)  # Set the page load timeout
        driver.get(url)

        if time_to_sleep:
            time.sleep(time_to_sleep)  # Wait for 10 seconds

        elif tag_to_await:
            # Wait for the necessary element to ensure the page has loaded
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, tag_to_await))
            )

        else:
            time.sleep(5)

        html_page = driver.page_source
    except Exception as e:
        print(f"Selenium failed with error: {e}")
        html_page = ""
    finally:
        if driver:
            driver.quit()
    return html_page

@functions_framework.http
def handler(request):
    data = request.get_json()
    image = data["image"]