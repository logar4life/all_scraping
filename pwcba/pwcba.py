from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_recaptcha_solver import RecaptchaSolver
import time
import shutil
from datetime import datetime
import random
from bs4 import BeautifulSoup
import json
import csv
import os
import requests
from urllib.parse import urljoin

def handle_recaptcha(driver):
    """Handle reCAPTCHA with multiple fallback methods - fully automated"""
    print("Attempting to handle reCAPTCHA automatically...")
    
    # Method 1: Try automated solver
    try:
        solver = RecaptchaSolver(driver=driver)
        recaptcha_iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )
        solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        print("✓ Automated reCAPTCHA solver succeeded")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"✗ Automated solver failed: {e}")
    
    # Method 2: Enhanced manual checkbox click with multiple approaches
    try:
        recaptcha_iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )
        driver.switch_to.frame(recaptcha_iframe)
        
        # Try different checkbox selectors with more comprehensive coverage
        checkbox_selectors = [
            "//div[@class='recaptcha-checkbox-border']",
            "//div[@class='recaptcha-checkbox']",
            "//div[@role='checkbox']",
            "//input[@type='checkbox']",
            "//div[contains(@class, 'recaptcha')]",
            "//div[@id='recaptcha-anchor']",
            "//div[contains(@class, 'checkbox')]",
            "//span[@class='recaptcha-checkbox-border']",
            "//div[@aria-checked='false']"
        ]
        
        checkbox_clicked = False
        for selector in checkbox_selectors:
            try:
                checkbox = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                # Scroll to element to ensure it's visible
                driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                time.sleep(0.5)
                checkbox.click()
                print(f"✓ Clicked checkbox using selector: {selector}")
                checkbox_clicked = True
                break
            except Exception as click_error:
                print(f"Selector {selector} failed: {click_error}")
                continue
        
        driver.switch_to.default_content()
        
        if checkbox_clicked:
            print("Waiting for reCAPTCHA verification...")
            time.sleep(8)  # Wait longer for verification
            
            # Check if verification was successful by looking for success indicators
            try:
                # Switch back to iframe to check verification status
                driver.switch_to.frame(recaptcha_iframe)
                success_indicator = driver.find_element(By.XPATH, "//div[@aria-checked='true']")
                driver.switch_to.default_content()
                print("✓ reCAPTCHA verification successful")
                return True
            except:
                driver.switch_to.default_content()
                print("⚠ reCAPTCHA verification status unclear, continuing...")
                return True  # Continue anyway
        else:
            print("✗ Could not find or click checkbox")
            return False
            
    except Exception as e:
        print(f"✗ Manual checkbox method failed: {e}")
        driver.switch_to.default_content()
        return False
    
    return False

# Check for ffmpeg
if not shutil.which("ffmpeg"):
    print("ffmpeg is not installed or not in your PATH. Please install ffmpeg and try again.")
    exit()

# Create necessary directories
if not os.path.exists('documents'):
    os.makedirs('documents')
if not os.path.exists('pwcba_pdf'):
    os.makedirs('pwcba_pdf')

# Credentials
USERNAME = "nmotahedy"
PASSWORD = "Logar4life!"

# URL
URL = "https://www4.pwcva.gov/Web/user/disclaimer"

# Chrome Options
options = Options()
# options.headless = False  # Show browser (deprecated, removed)

# Set up download preferences
prefs = {
    "download.default_directory": os.path.abspath("documents"),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

# Setup driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Maximize window to full screen
driver.maximize_window()

# Clear cache before opening the website
# Open a blank page
driver.get('about:blank')
# Open DevTools and clear cache using Chrome DevTools Protocol (CDP)
driver.execute_cdp_cmd('Network.clearBrowserCache', {})
driver.execute_cdp_cmd('Network.clearBrowserCookies', {})

try:
    # Open the website
    driver.get(URL)
    
    # Handle reCAPTCHA if present
    try:
        recaptcha_iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )
        print("reCAPTCHA iframe found.")
        
        # Use the improved reCAPTCHA handling function
        recaptcha_success = handle_recaptcha(driver)
        
        if recaptcha_success:
            print("✓ reCAPTCHA handled successfully")
            
            # Try to find and click submit button after reCAPTCHA
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(@class, 'submit') or contains(text(), 'Submit') or contains(text(), 'Verify')]"))
                )
                submit_button.click()
                print("✓ Clicked submit button after reCAPTCHA.")
                time.sleep(2)
            except Exception as submit_error:
                print(f"Could not find submit button after reCAPTCHA: {submit_error}")
                print("Continuing anyway...")
        else:
            print("⚠ reCAPTCHA handling failed, continuing anyway...")
                
    except Exception as e:
        print(f"Could not find reCAPTCHA iframe: {e}")
        print("Continuing anyway - reCAPTCHA might not be present...")
        
    # Continue automatically without manual intervention
    print("Continuing with automated workflow...")

    # Find the accept button, scroll to it, and click it
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "submitDisclaimerAccept"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", accept_button)
        accept_button.click()
        print("Clicked disclaimer accept button.")
    except Exception as e:
        print(f"Could not find disclaimer accept button: {e}")
        print("Continuing anyway...")


    # Click on the "Log in" link
    try:
        login_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Log in")))
        login_link.click()
        print("Clicked login link.")
    except Exception as e:
        print(f"Could not find login link: {e}")
        print("Trying alternative login methods...")
        # Try alternative selectors
        try:
            login_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Log in')]")
            login_link.click()
            print("Clicked login link using alternative method.")
        except Exception as alt_e:
            print(f"Alternative login method also failed: {alt_e}")
            driver.quit()
            exit()

    # Wait for the login panel to appear
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "field_UserId")))
        print("Login form loaded.")
    except Exception as e:
        print(f"Login form did not load: {e}")
        driver.quit()
        exit()

    # Fill in the username and password
    try:
        username_field = driver.find_element(By.ID, "field_UserId")
        password_field = driver.find_element(By.ID, "field_Password")
        
        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        print("Filled in login credentials.")
        
        # Click the Submit button
        submit_button = driver.find_element(By.ID, "loginSubmit")
        submit_button.click()
        print("Clicked login submit button.")
    except Exception as e:
        print(f"Error during login: {e}")
        driver.quit()
        exit()

    # Wait for either successful login or 'already logged in' message
    time.sleep(2)
    page_source = driver.page_source
    if 'User is already logged in' in page_source:
        # Click the 'Log off other sessions' button
        try:
            logoff_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='field_ForceLogoff' and contains(text(), 'Log off other sessions')]") )
            )
            logoff_button.click()
            time.sleep(1)
            # Try logging in again
            driver.find_element(By.ID, "field_UserId").clear()
            driver.find_element(By.ID, "field_Password").clear()
            driver.find_element(By.ID, "field_UserId").send_keys(USERNAME)
            driver.find_element(By.ID, "field_Password").send_keys(PASSWORD)
            driver.find_element(By.ID, "loginSubmit").click()
            time.sleep(2)
        except Exception as e:
            print("Could not log off other sessions:", e)
            driver.quit()
            exit()

    # Wait to observe result or redirection
    time.sleep(2)

    # After login, click on the Name Search button
    name_search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//a[@href="/Web/search/DOCSEARCH114S2"]'))
    )
    name_search_button.click()

    # Wait for the document type dropdown to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "field_selfservice_documentTypes-aclist"))
    )

    # List of document types to select
    doc_types = [
        "LIS PENDENS",
        "LIS PENDENS CORRECTED",
        "LIS PENDENS RERECORDED",
        "APPOINTMENT OF SUBSTITUTE TRUSTEE",
        "APPTMT OF SUBSTITUTE TRUSTEE CORRECTED",
        "APPTMT OF SUBSTITUTE TRUSTEE RERECORDED"
    ]

    # Open the dropdown and select each document type like a human
    doc_type_input = driver.find_element(By.ID, "field_selfservice_documentTypes")
    for doc_type in doc_types:
        # Clear and type the document type
        doc_type_input.clear()
        for char in doc_type:
            doc_type_input.send_keys(char)
            time.sleep(random.uniform(0.03, 0.12))  # Mimic human typing
        time.sleep(random.uniform(0.5, 1.2))  # Wait for dropdown to populate
        # Wait for the dropdown to be visible and select the item
        item_xpath = f"//ul[@id='field_selfservice_documentTypes-aclist']//li[normalize-space(text())='{doc_type}']"
        item = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, item_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", item)
        time.sleep(random.uniform(0.1, 0.3))
        item.click()
        time.sleep(random.uniform(0.7, 1.5))  # Wait before next selection

    # Set date range: from first of the month to today
    today = datetime.today()
    first_of_month = today.replace(day=1)
    start_date_str = first_of_month.strftime('%#m/%#d/%Y')
    end_date_str = today.strftime('%#m/%#d/%Y')

    # Input the dates
    start_date_input = driver.find_element(By.ID, "field_RecordingDateID_DOT_StartDate")
    end_date_input = driver.find_element(By.ID, "field_RecordingDateID_DOT_EndDate")
    start_date_input.clear()
    start_date_input.send_keys(start_date_str)
    end_date_input.clear()
    end_date_input.send_keys(end_date_str)
    time.sleep(1)

    # Click the Search button
    search_button = driver.find_element(By.ID, "searchButton")
    search_button.click()
    time.sleep(5)

    # --- Fetch and parse all search results and save to CSV ---
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = soup.find_all('div', class_='selfServiceSearchRowRight')
    all_data = []
    for result in results:
        # Document number and type
        h1 = result.find('h1')
        doc_number = None
        doc_type = None
        if h1:
            h1_text = h1.get_text(separator=' ').strip()
            parts = [p.strip() for p in h1_text.split('•')]
            if len(parts) == 2:
                doc_number = parts[0]
                doc_type = parts[1]
            else:
                doc_number = h1_text

        # Verification status
        status_span = result.find('span', class_='wip ss-oval-button')
        verification_status = status_span.get_text(strip=True) if status_span else None

        # Recording date
        rec_date = None
        for col in result.find_all('div', class_='searchResultFourColumn'):
            label = col.find('li')
            if label and 'Recording Date' in label.text:
                val = col.find('li', class_='selfServiceSearchResultCollapsed')
                if val:
                    rec_date = val.get_text(strip=True)
                break

        # Grantors
        grantors = []
        for col in result.find_all('div', class_='searchResultFourColumn'):
            label = col.find('li')
            if label and 'Grantor/Name 1' in label.text:
                for li in col.find_all('li'):
                    b = li.find('b')
                    if b:
                        grantors.append(b.get_text(strip=True))
                break

        # Grantees
        grantees = []
        for col in result.find_all('div', class_='searchResultFourColumn'):
            label = col.find('li')
            if label and 'Grantee/Name 2' in label.text:
                for li in col.find_all('li'):
                    b = li.find('b')
                    if b:
                        grantees.append(b.get_text(strip=True))
                break

        # Legal
        legal = None
        for col in result.find_all('div', class_='searchResultFourColumn'):
            label = col.find('li')
            if label and 'Legal' in label.text:
                val = col.find('li', class_='selfServiceSearchResultCollapsed')
                if val:
                    legal = val.get_text(strip=True)
                break

        all_data.append({
            'document_number': doc_number,
            'document_type': doc_type,
            'verification_status': verification_status,
            'recording_date': rec_date,
            'grantors': '; '.join(grantors),
            'grantees': '; '.join(grantees),
            'legal': legal
        })

    # Save to CSV
    if all_data:
        with open('search_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['document_number', 'document_type', 'verification_status', 'recording_date', 'grantors', 'grantees', 'legal']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in all_data:
                writer.writerow(row)
        print(f"Saved {len(all_data)} results to search_results.csv")

        # --- Download each document page as HTML ---
        # Find all result blocks again to get the links
        for result in results:
            # Get document number for filename
            h1 = result.find('h1')
            doc_number = None
            if h1:
                h1_text = h1.get_text(separator=' ').strip()
                parts = [p.strip() for p in h1_text.split('•')]
                if len(parts) == 2:
                    doc_number = parts[0]
                else:
                    doc_number = h1_text
            # Find the 'View Document' link
            view_link = result.find('a', title='View Document')
            if view_link and view_link.has_attr('href') and doc_number:
                doc_url = view_link['href']
                # If the link is relative, make it absolute
                if doc_url.startswith('/'):
                    base_url = driver.current_url.split('/Web/')[0]
                    doc_url = base_url + doc_url
                # Open the document page in the browser
                driver.get(doc_url)
                time.sleep(3)  # Wait for page to load completely
                
                try:
                    # First try to find the iframe with PDF URL
                    pdf_iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.ss-pdfjs-lviewer"))
                    )
                    
                    # Get the PDF URL from the iframe's data-href attribute
                    pdf_url = pdf_iframe.get_attribute("data-href")
                    
                    if pdf_url:
                        # Make the URL absolute if it's relative
                        if pdf_url.startswith('/'):
                            base_url = driver.current_url.split('/Web/')[0]
                            pdf_url = base_url + pdf_url
                        
                        # Download the PDF using requests
                        # Get cookies from the current session
                        cookies = driver.get_cookies()
                        session = requests.Session()
                        
                        # Add cookies to the session
                        for cookie in cookies:
                            session.cookies.set(cookie['name'], cookie['value'])
                        
                        # Download the PDF
                        response = session.get(pdf_url, stream=True)
                        if response.status_code == 200:
                            pdf_filename = f'pwcba_pdf/{doc_number}.pdf'
                            with open(pdf_filename, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            print(f'Successfully downloaded PDF for document {doc_number}')
                        else:
                            print(f'Failed to download PDF for document {doc_number}. Status code: {response.status_code}')
                    else:
                        print(f'Could not find PDF URL for document {doc_number}')
                        
                except Exception as e:
                    print(f'Could not download PDF for document {doc_number}: {e}')
                    # Fallback to the original download button method
                    try:
                        # Wait for the download button to be present and enabled
                        download_button = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.ID, "download"))
                        )
                        
                        # Scroll to the download button to ensure it's visible
                        driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
                        time.sleep(1)
                        
                        # Check if button is disabled
                        if not download_button.get_attribute("disabled"):
                            # Try multiple approaches to click the download button
                            try:
                                # Method 1: Regular click
                                download_button.click()
                                print(f'Downloaded PDF for document {doc_number} (fallback method)')
                            except Exception as click_error:
                                print(f'Regular click failed for {doc_number}, trying JavaScript click...')
                                try:
                                    # Method 2: JavaScript click
                                    driver.execute_script("arguments[0].click();", download_button)
                                    print(f'Downloaded PDF for document {doc_number} (JavaScript click - fallback)')
                                except Exception as js_error:
                                    print(f'JavaScript click failed for {doc_number}, trying alternative...')
                                    try:
                                        # Method 3: Try finding by different selectors
                                        alt_download_button = driver.find_element(By.CSS_SELECTOR, "button[title*='Download']")
                                        alt_download_button.click()
                                        print(f'Downloaded PDF for document {doc_number} (alternative selector - fallback)')
                                    except Exception as alt_error:
                                        print(f'All download methods failed for document {doc_number}')
                                        print(f'Errors: Click={click_error}, JS={js_error}, Alt={alt_error}')
                        else:
                            print(f'Download button disabled for document {doc_number}')
                            
                        time.sleep(3)  # Wait for download to start
                            
                    except Exception as fallback_error:
                        print(f'Fallback method also failed for document {doc_number}: {fallback_error}')
                        # Try to save the page source for debugging
                        try:
                            with open(f'documents/{doc_number}_debug.html', 'w', encoding='utf-8') as f:
                                f.write(driver.page_source)
                            print(f'Saved debug HTML for document {doc_number}')
                        except:
                            pass
                
                # Go back to the results page
                driver.back()
                time.sleep(2)
    else:
        print('No search results found.')

finally:
    # Close the browser
    driver.quit()
