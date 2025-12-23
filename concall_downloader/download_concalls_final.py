"""
Download Concall Transcripts from Screener.in
Final Production Version - Headless Mode

This script searches for companies on screener.in and downloads their concall transcripts.
"""

import os
import sys
import time
import json
import ssl
import urllib3
import signal
from pathlib import Path
from datetime import datetime, timedelta

# Disable keyboard interrupt
signal.signal(signal.SIGINT, signal.SIG_IGN)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['WDM_SSL_VERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver(download_dir):
    """Setup Chrome WebDriver in HEADLESS mode."""
    chrome_options = Options()
    
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
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # HEADLESS MODE
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Disable images and CSS for faster loading
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set user agent
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    print("   ✅ Headless browser initialized (no UI)")
    
    return driver


def wait_for_downloads(download_dir, timeout=60):
    """Wait for downloads to complete."""
    seconds = 0
    while seconds < timeout:
        time.sleep(1)
        downloading = list(Path(download_dir).glob("*.crdownload"))
        if not downloading:
            return True
        seconds += 1
    return False


def download_concalls(driver, company_name, download_dir):
    """Download concalls for a company."""
    result = {
        "company": company_name,
        "success": False,
        "downloaded_files": [],
        "url": "",
        "errors": []
    }
    
    try:
        print(f"\n{'='*70}")
        print(f"Processing: {company_name}")
        print(f"{'='*70}")
        
        # Create company-specific download folder
        company_folder = os.path.join(download_dir, company_name.replace(" ", "_").replace(".", ""))
        os.makedirs(company_folder, exist_ok=True)
        
        # Update download directory for this company
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": company_folder
        })
        
        # Step 1: Go to homepage
        print("1. Opening screener.in...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.get("https://www.screener.in/")
                time.sleep(2)
                # Verify page loaded
                page_title = driver.title
                print(f"   ✅ Page loaded: {page_title[:50]}")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"   ⚠️ Connection error, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    raise Exception(f"Failed to load page after {max_retries} attempts: {e}")
        
        # Step 2: Find search box
        print("2. Finding search box...")
        
        search_input = None
        
        # Try multiple selectors
        selectors = [
            "input[placeholder*='Search']",
            "input[name='q']",
            "input[id*='search']",
            "input[type='text']",
            "input[type='search']"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    search_input = elements[0]
                    print(f"   ✅ Found search using: {selector}")
                    break
            except:
                continue
        
        if not search_input:
            raise Exception("Could not find search input")
        
        # Step 3: Search
        print(f"3. Searching for '{company_name}'...")
        
        # Make sure search box is ready
        try:
            # Wait a bit for page to fully load
            time.sleep(1)
            
            # Try clicking first using JavaScript
            driver.execute_script("arguments[0].focus();", search_input)
            time.sleep(0.5)
            
            # Type using JavaScript (more reliable in headless)
            driver.execute_script(f"""
                arguments[0].value = '{company_name}';
                arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                arguments[0].dispatchEvent(new Event('keyup', {{ bubbles: true }}));
                arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            """, search_input)
            
            # Verify value was set
            actual_value = driver.execute_script("return arguments[0].value;", search_input)
            print(f"   ✅ Search input set to: '{actual_value}'")
            
            print("   Waiting for autocomplete dropdown...")
            time.sleep(4)  # Longer wait for autocomplete
        except Exception as e:
            print(f"   Warning during input: {str(e)[:100]}")
            time.sleep(4)
        
        # Step 4: Click best matching result
        print("4. Selecting best matching result...")
        
        try:
            # Find the best matching search result - look for exact company name match
            # Split company name to handle cases like "UltraTech Cem." -> search for "ultratech"
            search_words = company_name.lower().replace('.', '').split()
            primary_word = search_words[0] if search_words else company_name.lower()
            
            result_data = driver.execute_script(f"""
                var primaryWord = '{primary_word}';
                var links = document.querySelectorAll('a[href*="/company/"]');
                var results = [];
                var bestMatch = null;
                var highestScore = -1;
                
                // First, collect all visible links with details
                for (var i = 0; i < links.length; i++) {{
                    var link = links[i];
                    if (link.offsetParent !== null) {{  // visible check
                        var text = link.textContent.toLowerCase().replace(/\\./g, '').trim();
                        results.push({{
                            text: link.textContent.trim(),
                            textLower: text,
                            index: i
                        }});
                    }}
                }}
                
                // Log what we found
                console.log('Found ' + results.length + ' company links');
                for (var i = 0; i < Math.min(5, results.length); i++) {{
                    console.log(i + ': ' + results[i].text);
                }}
                
                // Find best matching link based on primary word
                for (var i = 0; i < results.length; i++) {{
                    var text = results[i].textLower;
                    var score = 0;
                    
                    // Check if primary word is at the start (highest priority)
                    if (text.startsWith(primaryWord)) {{
                        score = 100 + (50 / (text.length + 1));
                    }}
                    // Check if primary word is in the text
                    else if (text.includes(primaryWord)) {{
                        score = 50 + (30 / (text.length + 1));
                    }}
                    
                    if (score > highestScore) {{
                        highestScore = score;
                        bestMatch = results[i];
                    }}
                }}
                
                // Click the best match
                if (bestMatch) {{
                    links[bestMatch.index].click();
                    return {{
                        success: true, 
                        text: bestMatch.text, 
                        score: highestScore,
                        total_found: results.length,
                        all_options: results.slice(0, 5).map(r => r.text)
                    }};
                }}
                
                // Fallback: click first result
                if (links.length > 0) {{
                    links[0].click();
                    return {{
                        success: true, 
                        text: links[0].textContent.trim(), 
                        score: 0,
                        total_found: results.length,
                        all_options: results.slice(0, 5).map(r => r.text)
                    }};
                }}
                
                return {{success: false, total_found: results.length}};
            """)
            
            if result_data.get('success'):
                print(f"   ✅ Selected: {result_data.get('text', 'Unknown')[:50]} (score: {result_data.get('score', 0):.2f})")
                print(f"   Total options found: {result_data.get('total_found', 0)}")
                if result_data.get('all_options'):
                    print(f"   Available options were:")
                    for idx, opt in enumerate(result_data['all_options'], 1):
                        print(f"      {idx}. {opt[:60]}")
            else:
                print("   ⚠️ No results found, pressing Enter...")
                search_input.send_keys(Keys.RETURN)
        except Exception as e:
            print(f"   Warning: {str(e)[:100]}")
            try:
                search_input.send_keys(Keys.RETURN)
            except:
                print("   ⚠️ Could not press Enter, continuing anyway...")
        
        time.sleep(3)
        
        try:
            current_url = driver.current_url
            result["url"] = current_url
            page_title = driver.title
            print(f"   ✅ Navigated to: {current_url}")
            print(f"   Page title: {page_title[:50]}")
        except Exception as e:
            print(f"   Warning getting URL: {str(e)[:100]}")
            result["url"] = "Unknown"
        
        # Step 5: Scroll to find Documents section
        print("5. Scrolling to find Documents/Concalls...")
        
        # Faster scrolling with error handling
        try:
            for i in range(10):
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(0.1)
            time.sleep(1)
            
            # Check what's on the page
            page_text = driver.execute_script("return document.body.innerText;")[:500]
            print(f"   Page content preview: {page_text[:100]}...")
            
            has_documents = "document" in page_text.lower()
            has_concall = "concall" in page_text.lower() or "conference" in page_text.lower()
            print(f"   Has 'Documents': {has_documents}, Has 'Concall': {has_concall}")
            
        except Exception as e:
            print(f"   Warning during scroll: {str(e)[:100]}")
            time.sleep(1)
        
        # Step 6: Find transcript/concall links
        print("6. Looking for concall transcript links...")
        
        try:
            links = driver.execute_script("""
            var results = [];
            var allLinks = document.querySelectorAll('a');
            
            for (var i = 0; i < allLinks.length; i++) {
                var link = allLinks[i];
                var href = link.href || '';
                var text = (link.textContent || '').trim().toLowerCase();
                
                // More specific filtering for concalls and transcripts
                // Prioritize actual transcript PDFs and concall documents
                if ((href.includes('transcript') && href.includes('.pdf')) ||
                    (text.includes('transcript') && !text.includes('audio')) ||
                    (text.includes('concall') && text.includes('transcript')) ||
                    (text.includes('conference call') && text.includes('transcript'))) {
                    
                    if (href && href.startsWith('http')) {
                        results.push({
                            href: href,
                            text: link.textContent.trim().substring(0, 100)
                        });
                    }
                }
            }
            
            // Remove duplicates
            var unique = [];
            var seen = {};
            for (var i = 0; i < results.length; i++) {
                if (!seen[results[i].href]) {
                    seen[results[i].href] = true;
                    unique.push(results[i]);
                }
            }
            
            return unique;
            """)
        except Exception as e:
            print(f"   ⚠️ Error finding links: {str(e)[:100]}")
            links = []
        
        if links:
            print(f"   ✅ Found {len(links)} potential transcript links")
            
            # Show sample of what we found
            print(f"   Sample links:")
            for i, link in enumerate(links[:5], 1):
                print(f"      {i}. {link['text'][:60] if link['text'] else 'No text'}")
            
            # Limit to first 20 links to avoid excessive downloads
            if len(links) > 20:
                print(f"   ⚠️ Limiting to first 20 links (found {len(links)})")
                links = links[:20]
        else:
            print("   ⚠️ No transcript links found")
            result["errors"].append("No transcript links found")
            return result
        
        # Step 7: Download transcripts
        print(f"7. Downloading {len(links)} transcripts...")
        print(f"   Target folder: {company_folder}")
        
        files_before = set(os.listdir(company_folder)) if os.path.exists(company_folder) else set()
        print(f"   Files before: {len(files_before)}")
        downloaded = 0
        
        for i, link in enumerate(links, 1):
            try:
                print(f"   [{i}/{len(links)}] {link['text'][:40]}...")
                
                # Open in new tab with retry
                retry_count = 2
                for retry in range(retry_count):
                    try:
                        driver.execute_script(f"window.open('{link['href']}', '_blank');")
                        time.sleep(1.5)
                        break
                    except Exception as retry_e:
                        if retry < retry_count - 1:
                            print(f"      Retry {retry + 1}...")
                            time.sleep(1)
                        else:
                            raise retry_e
                
                # Close the new tab and switch back
                try:
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(0.5)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(0.3)
                except Exception as switch_e:
                    print(f"      Warning switching tabs: {str(switch_e)[:50]}")
                    # Try to get back to main window
                    try:
                        driver.switch_to.window(driver.window_handles[0])
                    except:
                        pass
                
                downloaded += 1
                
            except Exception as e:
                print(f"      ⚠️ Error: {str(e)[:100]}")
                continue
        
        # Wait for downloads
        if downloaded > 0:
            print(f"   Waiting for {downloaded} downloads to complete...")
            initial_wait = 5
            print(f"   Initial wait: {initial_wait}s")
            time.sleep(initial_wait)
            
            # Check progress
            files_after = set(os.listdir(company_folder)) if os.path.exists(company_folder) else set()
            new_files = list(files_after - files_before)
            print(f"   Current file count: {len(new_files)} new files")
            
            # Wait for remaining downloads
            remaining_wait = 25
            print(f"   Waiting {remaining_wait}s more for completion...")
            wait_for_downloads(company_folder, timeout=remaining_wait)
        
        # Check new files
        files_after = set(os.listdir(company_folder)) if os.path.exists(company_folder) else set()
        new_files = list(files_after - files_before)
        
        if new_files:
            print(f"\n   ✅ Downloaded {len(new_files)} files:")
            for file in new_files:
                print(f"      - {file}")
                result["downloaded_files"].append(file)
            result["success"] = True
        else:
            print("   ⚠️ No new files detected")
            result["errors"].append("No files downloaded")
        
    except Exception as e:
        error_msg = str(e)[:200]
        print(f"\n   ❌ Error: {error_msg}")
        result["errors"].append(error_msg)
        
        # Check if it's a connection error but browser is still open
        if "connection" in error_msg.lower() or "10054" in error_msg:
            print("   ℹ️ Connection error detected - browser may still be open")
            print("   Attempting to continue...")
            time.sleep(2)
    
    return result


def main():
    """Main function."""
    
    print("\n" + "="*70)
    print("SCREENER.IN CONCALL TRANSCRIPT DOWNLOADER")
    print("="*70)
    
    # Companies list
    companies = [
        "UltraTech Cem.",
        "Grasim Inds",
        "Ambuja Cements",
        "Shree Cement",
        "J K Cements",
        "Dalmia BharatLtd",
        "ACC",
        "The Ramco Cement",
        "JSW Cement",
        "Nuvoco Vistas",
        "India Cements",
        "JK Lakshmi Cem.",
        "Star Cement",
        "Birla Corpn.",
        "Prism Johnson"
    ]
    
    download_dir = os.path.abspath(os.path.join(os.getcwd(), "concall_transcripts"))
    print(f"\nDownload directory: {download_dir}")
    
    # Ask if test mode
    print("\n" + "="*70)
    # Auto-run in test mode for verification
    test_mode = True  # Change to False for all companies
    
    if test_mode:
        companies = companies[:1]
        print(f"✅ TEST MODE: Processing {len(companies)} company")
    else:
        print(f"✅ FULL MODE: Processing {len(companies)} companies")
    
    print("="*70)
    
    driver = None
    results = []
    
    try:
        print("\nInitializing browser...")
        driver = setup_driver(download_dir)
        print("✅ Browser opened\n")
        
        for i, company in enumerate(companies, 1):
            print(f"\n[{i}/{len(companies)}] {company}")
            
            # Check if driver is still responsive
            try:
                _ = driver.current_url
            except Exception as e:
                print(f"⚠️ Driver connection issue: {str(e)[:100]}")
                print("Attempting to continue anyway...")
                time.sleep(1)
            
            result = download_concalls(driver, company, download_dir)
            results.append(result)
            
            if i < len(companies):
                print("\nWaiting 3 seconds before next company...")
                time.sleep(3)
        
        # Save results
        results_file = os.path.join(os.getcwd(), "concall_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        # Summary
        print("\n" + "="*70)
        print("DOWNLOAD SUMMARY")
        print("="*70)
        
        successful = sum(1 for r in results if r["success"])
        total_files = sum(len(r["downloaded_files"]) for r in results)
        
        print(f"\n✅ Successful: {successful}/{len(companies)} companies")
        print(f"📥 Total files: {total_files}")
        
        print("\nDetails:")
        for r in results:
            status = "✅" if r["success"] else "❌"
            print(f"\n{status} {r['company']}")
            print(f"   URL: {r['url']}")
            print(f"   Files: {len(r['downloaded_files'])}")
            if r["errors"]:
                print(f"   Errors: {', '.join(r['errors'])}")
        
        print("\n" + "="*70)
        print(f"Transcripts saved to: {download_dir}")
        print(f"Results saved to: {results_file}")
        print("="*70)
        
        print("\n✅ Script completed! Closing browser...")
        time.sleep(2)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            try:
                driver.quit()
                print("Browser closed.")
            except:
                pass


if __name__ == "__main__":
    main()