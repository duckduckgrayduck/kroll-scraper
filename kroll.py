""" Requires some standard libraries, Selenium, requests, and python-documentcloud """
import os
import time
import argparse
from datetime import datetime
import requests
import portpicker
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from documentcloud import DocumentCloud

def download_new_files(download_path, chromedriver_path):
    """ Takes the previously generated unique.txt
        file and downloads the documents from that file
    """
    prefs = {
        "download.default_directory": download_path,
        "savefile.default_directory": download_path,
    }
    # Your input file containing URLs (unique.txt)
    input_file = "unique.txt"
    # Read URLs from the file
    with open(input_file, "r", encoding='utf-8') as file:
        urls = file.read().splitlines()

    # Loop through each URL
    for url in urls:
        try:
            options = webdriver.chrome.options.Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-dev-shm-usage")
            options.add_experimental_option("prefs", prefs)
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # Download and load the NopeCHA extension
            with open("ext.crx", "wb") as f:
                f.write(requests.get("https://nopecha.com/f/ext.crx", timeout=30).content)

            options.add_extension("ext.crx")
            driver = webdriver.Chrome(
                options=options,
                service=Service(
                    chromedriver_path, port=portpicker.pick_unused_port()
                ),
            )
            driver.set_page_load_timeout(20)
            print(f"Opening URL: {url}")
            driver.get(url)
            driver.minimize_window()
            time.sleep(60)
        except Exception as e: #pylint:disable=broad-exception-caught
            print(e)
        finally:
            print(f"{url} opened")
            driver.quit()


def grab_new_links(chromedriver_path):
    """ 
        Grabs all links from the front page of the Kroll docket
        compares the links to what we have seen before
        puts the new links in unique.txt
    """
    options = webdriver.chrome.options.Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(
        options=options,
        service=Service(chromedriver_path, port=portpicker.pick_unused_port()),
    )
    driver.set_page_load_timeout(60)  # Increase the timeout
    driver.get("https://cases.ra.kroll.com/puertorico/Home-DocketInfo")

    # Wait for the table to be present
    table_xpath = '//*[@id="results-table"]'
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, table_xpath))
    )

    pdf_links = []
    # Find all links on the page after the table is loaded
    links = driver.find_elements(By.XPATH, "//a")

    # Read old links from old.txt into old_links list
    with open("old.txt", "r", encoding='utf-8') as old_file:
        old_links = [line.strip() for line in old_file]

    # Print only new links that contain "PDF" and are not in old_links
    for link in links:
        link_str = str(link.get_attribute("href"))
        if "PDF" in link_str and link_str not in old_links:
            pdf_links.append(link_str)
            print(link_str)

    # Update create unique.txt, which gives us all of the PDFs we need to download.
    with open("unique.txt", "a", encoding='utf-8') as old_file:
        for new_link in pdf_links:
            old_file.write(new_link + "\n")

    # Update old.txt with new links
    with open("old.txt", "a", encoding='utf-8') as old_file:
        for new_link in pdf_links:
            old_file.write(new_link + "\n")

    # Close the browser
    driver.quit()


def upload_files(download_path):
    """ Uploads newly downloaded documents to DocumentCloud """
    dc_username = os.environ["DC_USERNAME"]
    dc_password = os.environ["DC_PASSWORD"]
    client = DocumentCloud(dc_username, dc_password)
    client.documents.upload_directory(download_path, projects=[210820])

def main():
    """ Renames the unique.txt from last run
        grabs the new links to download from Kroll
        downloads the files from those links
        uploads the resulting documents to DocumentCloud
    """

    # You will have to change this line for the location of your chromedriver install
    chromedriver_path = "/usr/bin/chromedriver"
    
    if os.path.exists("unique.txt"):
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        new_file_path = f"unique_{current_datetime}.txt"
        os.rename("unique.txt", new_file_path)
        print(f" unique.txt renamed to {new_file_path} successfully.") 
    
    parser = argparse.ArgumentParser(description="Script description here.")
    parser.add_argument(
        "--download-path", required=True, help="Specify the download path."
    )
    args = parser.parse_args()
    download_path = args.download_path
    grab_new_links(chromedriver_path)
    download_new_files(download_path, chromedriver_path)
    upload_files(download_path)


if __name__ == "__main__":
    main()
