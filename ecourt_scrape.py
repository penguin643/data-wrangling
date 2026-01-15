from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import time

options = webdriver.ChromeOptions()
# WSL SPECIFIC STUFF HERE.
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)


def ecourts_data():
    try:
        print("Opening e-courts data site")
        driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index")
        time.sleep(5)
        # Working with dropdowns manually
        print(
            "Select state, district and court manually and press Enter after solving captcha.."
        )
        input("->")
        print("\n\nResults:\n")
        cases = []
        rows = driver.find_elements(By.XPATH, "//table[@id='showCaseListTable']//tr")

        for row in rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 1:
                case_data = {
                    "case_no": cols[1].text,
                    "petitioner_vs_respondent": cols[2].text,
                    "cnr_number": cols[3].text,
                }
                cases.append(case_data)

        print(f"Successfully scouted {len(cases)} cases!")
        print(cases[:3])
    finally:
        driver.quit()


if __name__ == "__main__":
    ecourts_data()
