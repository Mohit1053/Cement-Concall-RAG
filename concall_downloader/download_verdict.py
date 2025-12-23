"""
Download verdict reports from MarketsMojo by searching companies on the verdict page.
Using JavaScript to directly click dropdown items.
"""

import os
import sys
import time
import json
import ssl
import urllib3
from pathlib import Path

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['WDM_SSL_VERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from config import EMAIL, PASSWORD


def setup_driver(download_dir):
    """Set up Chrome WebDriver with download preferences."""
    chrome_options = Options()
    
    # Ensure download directory exists
    os.makedirs(download_dir, exist_ok=True)
    
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--ignore-certificate-errors")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


def login(driver, email, password):
    """Log in to MarketsMojo."""
    print("Logging in...")
    driver.get("https://www.marketsmojo.com/mojofeed/login")
    time.sleep(3)
    
    try:
        # Find email field
        email_field = driver.find_element(
            By.XPATH, "//input[@type='text' and contains(@placeholder, 'Email')]"
        )
        email_field.clear()
        email_field.send_keys(email)
        
        # Find password field
        password_field = driver.find_element(By.XPATH, "//input[@type='password']")
        password_field.clear()
        password_field.send_keys(password)
        
        # Click login button
        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_btn.click()
        
        time.sleep(5)
        
        print(f"✅ Login successful! Current URL: {driver.current_url}")
        return True
        
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return False


def wait_for_downloads(download_dir, timeout=60):
    """Wait for downloads to complete."""
    seconds = 0
    while seconds < timeout:
        time.sleep(1)
        # Check if there are any .crdownload files (Chrome's temp download files)
        downloading = list(Path(download_dir).glob("*.crdownload"))
        if not downloading:
            return True
        seconds += 1
    return False


def download_verdict_report(driver, company_name, download_dir):
    """
    Download verdict report for a company by searching on the verdict page.
    
    Args:
        driver: Selenium WebDriver instance
        company_name: Name of the company to search
        download_dir: Directory to save downloads
        
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        print(f"\n{'='*60}")
        print(f"Processing: {company_name}")
        print(f"{'='*60}")
        
        # Navigate to verdict page
        print("1. Navigating to verdict page...")
        driver.get("https://www.marketsmojo.com/mojo/verdict")
        time.sleep(3)
        
        # Find search input
        print("2. Looking for search input...")
        search_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'stock')]")
        print(f"   ✅ Found search input")
        
        # Clear and type company name
        print(f"3. Typing '{company_name}'...")
        search_input.clear()
        time.sleep(0.5)
        
        # Type the full name at once (not character by character to avoid frame detachment)
        search_input.send_keys(company_name)
        
        # Wait for dropdown to appear
        print("4. Waiting for dropdown (3 seconds)...")
        time.sleep(3)
        
        # Take a screenshot
        driver.save_screenshot(f"before_click_{company_name.replace(' ', '_')}.png")
        print("   Screenshot saved")
        
        # Use JavaScript to find ANY clickable element containing the company name
        print("5. Using JavaScript to find and click dropdown item...")
        
        # Get first few words of company name for matching
        search_terms = company_name.split()[:2]  # First 2 words
        search_text = ' '.join(search_terms)
        
        js_click_dropdown = f"""
        console.log('Searching for: {search_text}');
        
        // Find ALL links on the page
        const allLinks = document.querySelectorAll('a');
        console.log('Total links found:', allLinks.length);
        
        // Look for a link containing our search text
        for (let link of allLinks) {{
            const linkText = link.innerText || link.textContent || '';
            const isVisible = link.offsetParent !== null;
            
            if (isVisible && linkText.includes('{search_text}')) {{
                console.log('Found matching link:', linkText);
                console.log('Link href:', link.href);
                console.log('Link visible:', isVisible);
                
                // Click it
                link.click();
                
                return {{
                    success: true,
                    text: linkText,
                    href: link.href
                }};
            }}
        }}
        
        // If no link found, try divs, spans, li elements
        const allElements = document.querySelectorAll('div, span, li, p');
        console.log('Total elements found:', allElements.length);
        
        for (let elem of allElements) {{
            const elemText = elem.innerText || elem.textContent || '';
            const isVisible = elem.offsetParent !== null;
            
            if (isVisible && elemText.includes('{search_text}') && elemText.length < 200) {{
                console.log('Found matching element:', elem.tagName, elemText.substring(0, 50));
                
                // Try to click it
                elem.click();
                
                return {{
                    success: true,
                    text: elemText.substring(0, 100),
                    tag: elem.tagName
                }};
            }}
        }}
        
        return {{success: false, message: 'No matching element found'}};
        """
        
        result = driver.execute_script(js_click_dropdown)
        print(f"   Click result: {result}")
        
        if result.get('success'):
            print(f"   ✅ Clicked on: {result.get('text', 'Unknown')[:50]}")
        else:
            print(f"   ⚠️ JavaScript click failed")
            print("   Trying keyboard navigation as fallback...")
            search_input.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)
            search_input.send_keys(Keys.RETURN)
        
        # Wait for page to navigate
        print("6. Waiting for page to load (30 seconds)...")
        
        # Check URL multiple times during wait
        for i in range(6):
            time.sleep(5)
            current_url = driver.current_url
            print(f"   After {(i+1)*5}s: {current_url}")
            if "verdict" not in current_url or "/verdict" not in current_url:
                print(f"   URL changed! Breaking wait...")
                break
        
        time.sleep(2)  # Extra buffer
        
        current_url = driver.current_url
        print(f"7. Final URL: {current_url}")
        
        # Check if URL changed
        if current_url == "https://www.marketsmojo.com/mojo/verdict":
            print("   ⚠️ URL didn't change - but content may have loaded dynamically")
            print("   Proceeding to look for download button anyway...")
        else:
            print(f"   ✅ Successfully navigated to: {current_url}")
        
        # Take screenshot of the company page
        driver.save_screenshot(f"company_page_{company_name.replace(' ', '_')}.png")
        
        # Look for download button
        print("8. Looking for download button...")
        
        # First try with JavaScript to find any element with "download" text
        js_find_download = """
        // Search for download button/link
        const allElements = document.querySelectorAll('*');
        const results = [];
        
        for (let elem of allElements) {
            const text = (elem.innerText || elem.textContent || '').toLowerCase();
            const className = (elem.className || '').toLowerCase();
            const id = (elem.id || '').toLowerCase();
            
            // Check if element contains "download" or "pdf"
            if ((text.includes('download') || text.includes('pdf') || 
                 className.includes('download') || id.includes('download')) &&
                elem.offsetParent !== null) {
                results.push({
                    tag: elem.tagName,
                    text: (elem.innerText || elem.textContent || '').substring(0, 100),
                    className: className,
                    id: id
                });
            }
        }
        
        return results.slice(0, 10);  // Return first 10 matches
        """
        
        download_elements = driver.execute_script(js_find_download)
        if download_elements:
            print(f"   Found {len(download_elements)} potential download elements:")
            for elem in download_elements[:5]:
                print(f"     {elem['tag']}: {elem['text'][:50]}")
        
        # Use JavaScript to find and click the download button (same approach as dropdown)
        print("8. Using JavaScript to find and click download button...")
        
        js_click_download = """
        function clickDownloadButton() {
            // Look for elements containing "DOWNLOAD" text
            const allElements = document.querySelectorAll('*');
            
            for (let elem of allElements) {
                const text = elem.textContent.trim().toUpperCase();
                const isVisible = elem.offsetWidth > 0 && elem.offsetHeight > 0;
                
                // Look specifically for button-like elements with DOWNLOAD text
                if (isVisible && text.includes('DOWNLOAD')) {
                    const tagName = elem.tagName.toLowerCase();
                    
                    // Check if it's a button, link, or clickable div
                    if (tagName === 'button' || tagName === 'a' || 
                        (tagName === 'div' && (elem.onclick || elem.getAttribute('onclick')))) {
                        
                        // Make sure it's not a container with lots of text
                        if (text.length < 100) {
                            elem.click();
                            return {
                                success: true,
                                tag: tagName,
                                text: elem.textContent.trim(),
                                classes: elem.className
                            };
                        }
                    }
                }
            }
            
            return {success: false, message: 'Download button not found'};
        }
        
        return clickDownloadButton();
        """
        
        try:
            # Get files before download
            files_before = set(os.listdir(download_dir))
            
            click_result = driver.execute_script(js_click_download)
            print(f"   Click result: {click_result}")
            
            if click_result.get('success'):
                print(f"   ✅ Clicked download button: {click_result.get('text', '')[:50]}")
                
                # Wait for download to complete
                print("9. Waiting for download to complete...")
                if wait_for_downloads(download_dir, timeout=30):
                    files_after = set(os.listdir(download_dir))
                    new_files = files_after - files_before
                    
                    if new_files:
                        print(f"    ✅ Downloaded: {', '.join(new_files)}")
                        return True
                    else:
                        print("    ⚠️ No new file detected")
                        return True
                else:
                    print("    ⚠️ Download timeout")
                    return False
            else:
                print(f"   ❌ Could not click download button: {click_result.get('message')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error clicking download button: {str(e)}")
            return False
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to download verdict reports."""
    
    print("=" * 70)
    print("MarketsMojo Verdict Report Downloader v6 (JS Click)")
    print("=" * 70)
    
    # Setup download directory
    download_dir = os.path.abspath(os.path.join(os.getcwd(), "verdict_reports"))
    print(f"\nDownload directory: {download_dir}")
    
    # Load test companies
    try:
        with open("test_companies.json", "r") as f:
            companies = json.load(f)
        print(f"Loaded {len(companies)} companies from test_companies.json")
    except FileNotFoundError:
        print("❌ test_companies.json not found.")
        return
    
    driver = None
    
    try:
        # Setup driver
        print("\nInitializing Chrome WebDriver...")
        driver = setup_driver(download_dir)
        print("✅ WebDriver initialized")
        
        # Login
        if not login(driver, EMAIL, PASSWORD):
            print("❌ Login failed. Exiting.")
            return
        
        # Download reports for each company
        results = {
            "success": [],
            "failed": []
        }
        
        for i, company in enumerate(companies, 1):
            company_name = company["name"]
            print(f"\n\n[{i}/{len(companies)}] Processing: {company_name}")
            
            success = download_verdict_report(driver, company_name, download_dir)
            
            if success:
                results["success"].append(company)
            else:
                results["failed"].append(company)
            
            # Add delay between downloads
            time.sleep(2)
        
        # Save results
        with open("verdict_download_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 70)
        print("DOWNLOAD SUMMARY")
        print("=" * 70)
        print(f"✅ Successful: {len(results['success'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        
        if results['failed']:
            print("\nFailed companies:")
            for company in results['failed']:
                print(f"  - {company['name']}")
        
        print("\n" + "=" * 70)
        print(f"Reports saved to: {download_dir}")
        print("=" * 70)
        
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close...")
        
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")


if __name__ == "__main__":
    main()
