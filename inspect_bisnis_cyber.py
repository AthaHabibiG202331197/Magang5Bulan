import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "https://www.bisnis.com/topic/45191/keamanan-siber?page=1"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

try:
    print("[INFO] Membuka halaman...")
    driver.get(URL)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    time.sleep(5)

    # Cari artikel yang kita kenal dari halaman kamu
    target_text = "ITSEC Asia Bongkar Cara Kerja Ransomware"

    elements = driver.find_elements(
        By.XPATH,
        f"//*[contains(normalize-space(), '{target_text}')]"
    )

    print(f"[INFO] Elemen ditemukan: {len(elements)}")

    for i, element in enumerate(elements[:5], start=1):

        print("\n" + "=" * 80)
        print(f"ELEMENT {i}")
        print("=" * 80)

        print("TAG   :", element.tag_name)
        print("TEXT  :", element.text[:500])

        print("\nCLASS :", element.get_attribute("class"))
        print("ID    :", element.get_attribute("id"))

        print("\nOUTER HTML:")
        print(element.get_attribute("outerHTML")[:3000])

        # Tampilkan parent beberapa level
        parent = element

        for level in range(1, 5):
            try:
                parent = parent.find_element(By.XPATH, "..")

                print(f"\n--- PARENT LEVEL {level} ---")
                print("TAG   :", parent.tag_name)
                print("CLASS :", parent.get_attribute("class"))
                print(parent.get_attribute("outerHTML")[:2000])

            except Exception:
                break

finally:
    driver.quit()