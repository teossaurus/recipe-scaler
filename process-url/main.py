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
import html2text
from io import BytesIO

# write function that calls a url that's taken as an argument and returns the html
def get_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        text = html2text.html2text(response.text)
        print(len(text.split(" ")));
        return text
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve HTML: {e}")
        return ""

@functions_framework.http
def handler(request):
    data = request.get_json()
    url = data["url"]
    text = get_text_from_url(url)
    return {
        "text": text
    }
