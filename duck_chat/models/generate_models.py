from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_html() -> str:
    """Get html page from duck.ai"""

    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument(
        "--disable-dev-shm-usage"
    )  # Overcome limited resource problems

    # Set up the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open a webpage duck.ai
    driver.get("https://duckduckgo.com/?q=DuckDuckGo+AI+Chat&ia=chat&duckai=1")

    html = driver.page_source

    # Close browser
    driver.quit()
    return html


def parse_html(html: str) -> dict[str, str]:
    """Get models from html page (labels tags)"""

    # Parse the content of the webpage
    soup = BeautifulSoup(html, "html.parser")

    # Find all tags and extract their names
    labels = soup.find_all("label")

    # Get models data
    data = {}
    for tag in labels:
        model_id = tag.attrs["for"]
        model_name = tag.text.split()[0].replace("-", "")
        data[model_name] = model_id
    return data


def write_models(data: dict[str, str], path: Path) -> None:
    """Generate new model_type.py"""
    with open(path, "w") as f:
        f.write("from enum import Enum\n\n\nclass ModelType(Enum):\n")
        for k, v in data.items():
            f.write(f'    {k} = "{v}"\n')


def main() -> None:
    html = get_html()
    data = parse_html(html)
    path = Path(__file__).resolve().parent / "model_type.py"
    write_models(data, path)
    print(f"Generate new models on {path}")


if __name__ == "__main__":
    main()
