from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

# WSL OPTIONS SETUP
options = webdriver.ChromeOptions()
# options.add_argument("--headless=new") # Debugging only.
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)


def scrape_judicial_data():
    try:
        driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index")
        input("\n\nPress enter after the rows are visible.")

        all_hearing_records = []
        rows = driver.find_elements(
            By.XPATH, "//table[contains(@class, 'table')]//tr[td]"
        )
        num_cases = len(rows)
        print(f"Detected {num_cases} cases.")

        for i in range(num_cases):
            try:
                # Click View button for every case in table
                wait = WebDriverWait(driver, 10)
                view_buttons = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//a[contains(text(), 'View')]")
                    )
                )

                print(f"[{i+1}/{num_cases}] View clicked.")
                view_buttons[i].click()
                history_table_xpath = "//table[contains(@class, 'history_table')]"
                wait.until(
                    EC.visibility_of_element_located((By.XPATH, history_table_xpath))
                )
                time.sleep(2)  # Brief pause for the DOM to settle

                cnr_text = driver.find_element(
                    By.XPATH, "//*[contains(text(), 'CNR')]"
                ).text
                cnr_number = cnr_text.split(":")[-1].strip()

                # Second, scrape the history rows
                h_rows = driver.find_elements(
                    By.XPATH, f"{history_table_xpath}//tr[td]"
                )
                for row in h_rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 4:
                        all_hearing_records.append(
                            {
                                "cnr_number": cnr_number,
                                "judge": cols[0].text.strip(),
                                "business_date": cols[1].text.strip(),
                                "hearing_date": cols[2].text.strip(),
                                "purpose": cols[3].text.strip(),
                            }
                        )
                back_button = driver.find_element(
                    By.XPATH,
                    "//button[contains(text(), 'Back')] | //input[@value='Back']",
                )
                back_button.click()

                # Wait for the main list to be visible again
                wait.until(
                    EC.invisibility_of_element_located((By.XPATH, history_table_xpath))
                )
                time.sleep(1)

            except Exception as e:
                print(f"Error on case {i+1}: {e}")
                continue

        # Save
        if all_hearing_records:
            df = pd.DataFrame(all_hearing_records)
            df.to_csv("mumbai_court_history.csv", index=False)
            print(f"Success! Captured {len(df)} hearing records.")
        else:
            print("No data captured.")

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_judicial_data()
