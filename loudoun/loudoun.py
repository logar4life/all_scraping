from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

import os
import requests
from urllib.parse import urljoin, urlparse
import glob
import tempfile
import uuid
import random

# Credentials
USERNAME = "nmotahedy"
PASSWORD = "Logar4life!"

# URL
URL = "https://lisweb.loudoun.gov/PAXSubscription/"

# Create folder for PDF downloads
script_dir = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(script_dir, "loudoun_pdf")
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

def setup_chrome_driver():
    """Setup Chrome driver with headless mode"""
    chrome_options = Options()
    
    # Run in headless mode
    chrome_options.add_argument("--headless=new")
    print("🕶️ Running in headless mode")
    
    # Set download directory
    download_path = os.path.abspath(PDF_FOLDER)
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    # Basic options for stability
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # Generate unique user data directory
    unique_user_data_dir = os.path.join(tempfile.gettempdir(), f"chrome_user_data_{uuid.uuid4().hex[:8]}")
    chrome_options.add_argument(f"--user-data-dir={unique_user_data_dir}")
    
    # Use system chromium in Docker or webdriver-manager in development
    if os.environ.get('DOCKER_ENV'):
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
    
    return webdriver.Chrome(service=service, options=chrome_options)

def download_pdf(url, filename):
    """Download PDF from URL and save to folder"""
    try:
        # Clean filename
        clean_name = clean_filename(filename)
        unique_filename = generate_unique_filename(clean_name)
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(PDF_FOLDER, unique_filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"📄 PDF saved: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error downloading PDF {filename}: {e}")
        return False

def find_and_download_pdfs(driver):
    """Find PDF links on the current page and download them"""
    try:
        # Look for PDF links
        pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf') or contains(@href, 'PDF')]")
        
        for link in pdf_links:
            try:
                href = link.get_attribute('href')
                if href and ('.pdf' in href.lower() or 'pdf' in href.lower()):
                    # Generate filename from URL or link text
                    link_text = link.text.strip()
                    if link_text:
                        filename = f"{link_text}.pdf"
                    else:
                        # Extract from URL
                        url_path = urlparse(href).path
                        filename = os.path.basename(url_path)
                        if not filename.endswith('.pdf'):
                            filename += '.pdf'
                    
                    print(f"🔍 Found PDF link: {href}")
                    print(f"   📝 Filename: {filename}")
                    download_pdf(href, filename)
                    
            except Exception as e:
                print(f"❌ Error processing PDF link: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error finding PDFs: {e}")

def click_save_image_and_download(driver, row_index, page_number):
    """Click on the Save Image link and download the PDF"""
    try:
        # Look for the Save Image link
        save_image_link = driver.find_element(By.ID, "lnkSaveImage")
        if save_image_link:
            print(f"💾 Found Save Image link for row {row_index}")
            
            # Click on the Save Image link
            save_image_link.click()
            print(f"🖱️ Clicked Save Image link for row {row_index}")
            
            # Wait for download to start
            time.sleep(2)
            
            # Try to find any download links or PDF links that might appear
            try:
                # Look for any new PDF links that might have appeared
                pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf') or contains(@href, 'PDF')]")
                
                for link in pdf_links:
                    try:
                        href = link.get_attribute('href')
                        if href and ('.pdf' in href.lower() or 'pdf' in href.lower()):
                            # Generate unique filename with row and page info
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"row_{row_index}_page_{page_number}_saved_image_{timestamp}.pdf"
                            
                            print(f"📥 Downloading PDF from Save Image: {href}")
                            print(f"   📝 Filename: {filename}")
                            download_pdf(href, filename)
                            
                    except Exception as e:
                        print(f"❌ Error processing PDF link from Save Image: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error finding PDF links after Save Image click: {e}")
            
            return True
            
    except NoSuchElementException:
        print(f"⚠️ Save Image link not found for row {row_index}")
        return False
    except Exception as e:
        print(f"❌ Error clicking Save Image for row {row_index}: {e}")
        return False

def generate_unique_filename(base_filename):
    """Generate a unique filename to avoid duplicates"""
    if not os.path.exists(os.path.join(PDF_FOLDER, base_filename)):
        return base_filename
    
    name, ext = os.path.splitext(base_filename)
    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        if not os.path.exists(os.path.join(PDF_FOLDER, new_filename)):
            return new_filename
        counter += 1

def clean_filename(filename):
    """Clean filename to remove invalid characters"""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext
    
    return filename

def highlight(element):
    """Highlights a web element by drawing a red border around it."""
    try:
        driver.execute_script("arguments[0].style.border='3px solid red'", element)
    except Exception as e:
        print(f"⚠️ Could not highlight element: {e}")

# Initialize WebDriver
driver = setup_chrome_driver()
wait = WebDriverWait(driver, 30)

try:
    print("🌐 Accessing Loudoun County website...")
    
    # Open the login page
    driver.get(URL)
    print("✅ Successfully loaded login page")
    time.sleep(3)
    
    # Input username and password
    username_field = wait.until(EC.presence_of_element_located((By.ID, "txtUsername")))
    username_field.clear()
    username_field.send_keys(USERNAME)
    
    password_field = wait.until(EC.presence_of_element_located((By.ID, "txtPassword")))
    password_field.clear()
    password_field.send_keys(PASSWORD)
    
    # Click login button
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "btnLogin")))
    login_button.click()
    print("✅ Login credentials entered")
    
    time.sleep(3)
    
    # Navigate to search page
    print("🔍 Navigating to search page...")
    driver.get("https://lisweb.loudoun.gov/PAXSubscription/views/search")
    print("✅ Successfully loaded search page")
    
    # Click on "Advanced/Legal Search"
    wait.until(EC.element_to_be_clickable((By.ID, "btnCriteriaAdvancedNameSearch"))).click()
    print("✅ Advanced search clicked")
    
    # Expand the "DEEDS" category
    deed_expand_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@id='cat2_anchor']/preceding-sibling::i[contains(@class, 'jstree-ocl')]")))
    deed_expand_icon.click()
    print("✅ DEEDS category expanded")
    
    # Click the checkboxes for the sub-items
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[4]/div[5]/div[2]/div[1]/div/div[3]/div[2]/div/div/ul/li[2]/ul/li[41]/a"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[4]/div[5]/div[2]/div[1]/div/div[3]/div[2]/div/div/ul/li[2]/ul/li[60]/a"))).click()
    print("✅ Deed items selected")
    
    # Select From Date
    from_date_input = wait.until(EC.element_to_be_clickable((By.ID, "dtFrom")))
    from_date_input.click()
    
    # Wait for calendar to appear and go to previous month
    wait.until(EC.visibility_of_element_located((By.ID, "ui-datepicker-div")))
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ui-datepicker-prev"))).click()
    
    # Select day 1
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='ui-datepicker-div']//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()='1']"))).click()
    print("✅ From date selected")
    
    # Select To Date
    to_date_input = wait.until(EC.element_to_be_clickable((By.ID, "dtTo")))
    to_date_input.click()
    
    # Wait for calendar to appear and select today's date
    wait.until(EC.visibility_of_element_located((By.ID, "ui-datepicker-div")))
    today_day = datetime.now().day
    wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='ui-datepicker-div']//td[not(contains(@class,'ui-datepicker-other-month'))]/a[text()='{today_day}']"))).click()
    print("✅ To date selected")
    
    # Click on the Summary Search button
    wait.until(EC.element_to_be_clickable((By.ID, "btnSummarySearch"))).click()
    print("✅ Search initiated")
    
    # Wait for the results table to appear
    table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[@id='gridResults']")))
    highlight(table)
    print("✅ Results table found")
    
    page_number = 1
    print("🔍 Starting to scrape PDFs...")
    
    while True:
        print(f"📄 Scraping page {page_number}...")
        
        # Re-find the table on each page
        table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[@id='gridResults']")))
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@id='gridResults']/tbody/tr")))
        
        # Extract table rows from the current page
        rows_on_page = table.find_elements(By.XPATH, ".//tbody/tr")
        print(f"Found {len(rows_on_page)} rows on page {page_number}.")
        
        for i, tr in enumerate(rows_on_page):
            try:
                # Highlight the current row
                highlight(tr)
                print(f" Processing row {i+1} on page {page_number}")
                
                # Double-click on the row
                actions = ActionChains(driver)
                actions.double_click(tr).perform()
                print(f"🖱️ Double-clicked row {i+1} on page {page_number}")
                
                # Wait for viewer container to appear and load content
                try:
                    viewer_container = wait.until(EC.presence_of_element_located((By.ID, "viewerContainer")))
                    print(f"📋 Viewer container found for row {i+1}")
                    
                    # Wait for content to load in the viewer
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#viewerContainer .page")))
                    print(f"📄 Page content loaded for row {i+1}")
                    
                    # Additional wait for canvas to be rendered
                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#viewerContainer canvas")))
                        print(f"🎨 Canvas rendered for row {i+1}")
                    except:
                        print(f"⚠️ Canvas not found for row {i+1}, continuing anyway")
                    
                    # Wait a bit more for any additional content to load
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"⚠️ Viewer container not found or content not loaded for row {i+1}: {e}")
                
                # Look for PDFs on the current page after double-click
                print(f"🔍 Looking for PDFs after double-clicking row {i+1}...")
                find_and_download_pdfs(driver)
                
                # Click Save Image link and download PDF
                print(f"💾 Clicking Save Image link for row {i+1}...")
                click_save_image_and_download(driver, i+1, page_number)
                
                # Wait a bit before moving to next row
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error processing row {i+1} on page {page_number}: {e}")
                continue
        
        try:
            # Find the "Next" button
            next_button = driver.find_element(By.ID, "gridResults_next")
            
            # Check if the "Next" button is disabled
            if "disabled" in next_button.get_attribute("class"):
                print("🏁 Next button is disabled. End of results.")
                break
                
            # Click the "Next" button and wait for the table to become stale
            print("➡️ Clicking Next page...")
            next_button.click()
            wait.until(EC.staleness_of(table))
            page_number += 1
            
        except NoSuchElementException:
            print("🏁 No 'Next' button found. Assuming single page of results.")
            break
        except Exception as e:
            print(f"❌ Error during pagination: {e}")
            break
    
    print(f"📁 PDFs saved in: {os.path.abspath(PDF_FOLDER)}")
    
    # Optional: wait to see result
    time.sleep(5)

except Exception as e:
    print(f"❌ Error during execution: {e}")
finally:
    # Close the browser
    try:
        driver.quit()
    except:
        pass 