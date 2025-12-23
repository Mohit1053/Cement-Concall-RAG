"""
Extract Concall URLs from Last 2 Years
Extract URLs for all cement company concall transcripts from screener.in

This script searches for companies and extracts all concall transcript URLs 
from the last 2 years without downloading the files.
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
import re

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


def setup_driver():
    """Setup Chrome WebDriver in HEADLESS mode."""
    chrome_options = Options()
    
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
    
    print("   ✅ Headless browser initialized")
    
    return driver


def extract_date_from_text(text):
    """
    Extract date from text like 'Q3 FY24' or 'Nov 2023' or '2024'
    Returns a datetime object or None
    """
    if not text:
        return None
    
    text = text.strip()
    current_year = datetime.now().year
    
    # Pattern 1: Q3 FY24, Q1 FY25, etc.
    fy_pattern = r'Q[1-4]\s*FY[\'"]?(\d{2})'
    match = re.search(fy_pattern, text, re.IGNORECASE)
    if match:
        fy_year = int(match.group(1))
        # FY24 means financial year 2023-24, so FY ends in 2024
        full_year = 2000 + fy_year if fy_year < 50 else 1900 + fy_year
        return datetime(full_year, 3, 31)  # Approximate to March end
    
    # Pattern 2: Month Year (Nov 2023, November 2023)
    month_year_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})'
    match = re.search(month_year_pattern, text, re.IGNORECASE)
    if match:
        month_str = match.group(1)
        year = int(match.group(2))
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        month = month_map.get(month_str.lower()[:3])
        if month:
            return datetime(year, month, 1)
    
    # Pattern 3: Just year (2024, 2023)
    year_pattern = r'\b(20\d{2})\b'
    match = re.search(year_pattern, text)
    if match:
        year = int(match.group(1))
        return datetime(year, 6, 30)  # Approximate to mid-year
    
    # Pattern 4: FY 2023-24 or FY2023-24
    fy_range_pattern = r'FY[\'"]?\s*(\d{4})-(\d{2,4})'
    match = re.search(fy_range_pattern, text, re.IGNORECASE)
    if match:
        year2 = int(match.group(2))
        if year2 < 100:
            year2 = 2000 + year2
        return datetime(year2, 3, 31)
    
    return None


def is_within_last_2_years(date_obj):
    """Check if a date is within the last 2 years."""
    if not date_obj:
        return False
    
    cutoff_date = datetime.now() - timedelta(days=730)  # 2 years = ~730 days
    return date_obj >= cutoff_date


def extract_concall_urls(driver, company_name):
    """Extract all concall URLs from the last 2 years for a company."""
    result = {
        "company": company_name,
        "success": False,
        "company_url": "",
        "concall_urls": [],
        "all_found_links": 0,
        "filtered_links": 0,
        "errors": []
    }
    
    try:
        print(f"\n{'='*70}")
        print(f"Processing: {company_name}")
        print(f"{'='*70}")
        
        # Step 1: Go to homepage
        print("1. Opening screener.in...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.get("https://www.screener.in/")
                time.sleep(2)
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
        
        try:
            time.sleep(1)
            driver.execute_script("arguments[0].focus();", search_input)
            time.sleep(0.5)
            
            driver.execute_script(f"""
                arguments[0].value = '{company_name}';
                arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                arguments[0].dispatchEvent(new Event('keyup', {{ bubbles: true }}));
                arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            """, search_input)
            
            actual_value = driver.execute_script("return arguments[0].value;", search_input)
            print(f"   ✅ Search input set to: '{actual_value}'")
            
            print("   Waiting for autocomplete dropdown...")
            time.sleep(4)
        except Exception as e:
            print(f"   Warning during input: {str(e)[:100]}")
            time.sleep(4)
        
        # Step 4: Click best matching result
        print("4. Selecting best matching result...")
        
        try:
            search_words = company_name.lower().replace('.', '').split()
            primary_word = search_words[0] if search_words else company_name.lower()
            
            result_data = driver.execute_script(f"""
                var primaryWord = '{primary_word}';
                var links = document.querySelectorAll('a[href*="/company/"]');
                var results = [];
                var bestMatch = null;
                var highestScore = -1;
                
                for (var i = 0; i < links.length; i++) {{
                    var link = links[i];
                    if (link.offsetParent !== null) {{
                        var text = link.textContent.toLowerCase().replace(/\\./g, '').trim();
                        results.push({{
                            text: link.textContent.trim(),
                            textLower: text,
                            index: i
                        }});
                    }}
                }}
                
                for (var i = 0; i < results.length; i++) {{
                    var text = results[i].textLower;
                    var score = 0;
                    
                    if (text.startsWith(primaryWord)) {{
                        score = 100 + (50 / (text.length + 1));
                    }}
                    else if (text.includes(primaryWord)) {{
                        score = 50 + (30 / (text.length + 1));
                    }}
                    
                    if (score > highestScore) {{
                        highestScore = score;
                        bestMatch = results[i];
                    }}
                }}
                
                if (bestMatch) {{
                    links[bestMatch.index].click();
                    return {{
                        success: true, 
                        text: bestMatch.text, 
                        score: highestScore,
                        total_found: results.length
                    }};
                }}
                
                if (links.length > 0) {{
                    links[0].click();
                    return {{
                        success: true, 
                        text: links[0].textContent.trim(), 
                        score: 0,
                        total_found: results.length
                    }};
                }}
                
                return {{success: false, total_found: results.length}};
            """)
            
            if result_data.get('success'):
                print(f"   ✅ Selected: {result_data.get('text', 'Unknown')[:50]}")
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
            result["company_url"] = current_url
            page_title = driver.title
            print(f"   ✅ Company page: {current_url}")
            print(f"   Page title: {page_title[:60]}")
        except Exception as e:
            print(f"   Warning getting URL: {str(e)[:100]}")
            result["company_url"] = "Unknown"
        
        # Step 5: Scroll to find Documents section
        print("5. Scrolling to find Documents/Concalls...")
        
        try:
            for i in range(10):
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(0.1)
            time.sleep(1)
        except Exception as e:
            print(f"   Warning during scroll: {str(e)[:100]}")
            time.sleep(1)
        
        # Step 6: Extract all concall transcript links with dates
        print("6. Extracting concall transcript links...")
        
        try:
            links_data = driver.execute_script("""
            var results = [];
            var allLinks = document.querySelectorAll('a');
            
            for (var i = 0; i < allLinks.length; i++) {
                var link = allLinks[i];
                var href = link.href || '';
                var text = (link.textContent || '').trim();
                var textLower = text.toLowerCase();
                
                // Filter for transcript links
                if ((href.includes('transcript') && href.includes('.pdf')) ||
                    (textLower.includes('transcript') && !textLower.includes('audio')) ||
                    (textLower.includes('concall') && textLower.includes('transcript')) ||
                    (textLower.includes('conference call') && textLower.includes('transcript'))) {
                    
                    if (href && href.startsWith('http')) {
                        results.push({
                            href: href,
                            text: text.substring(0, 150)
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
            print(f"   ⚠️ Error extracting links: {str(e)[:100]}")
            links_data = []
        
        result["all_found_links"] = len(links_data)
        
        if not links_data:
            print("   ⚠️ No transcript links found")
            result["errors"].append("No transcript links found on page")
            return result
        
        print(f"   ✅ Found {len(links_data)} total transcript links")
        
        # Step 7: Filter by date (last 2 years)
        print("7. Filtering by date (last 2 years)...")
        
        cutoff_date = datetime.now() - timedelta(days=730)
        print(f"   Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")
        
        filtered_urls = []
        
        for link_data in links_data:
            text = link_data['text']
            url = link_data['href']
            
            # Extract date from text
            date_obj = extract_date_from_text(text)
            
            if date_obj:
                is_recent = is_within_last_2_years(date_obj)
                date_str = date_obj.strftime('%Y-%m-%d')
                
                if is_recent:
                    filtered_urls.append({
                        "url": url,
                        "text": text,
                        "extracted_date": date_str,
                        "is_recent": True
                    })
                    print(f"   ✅ {date_str}: {text[:60]}")
                else:
                    print(f"   ❌ {date_str}: {text[:60]} (too old)")
            else:
                # If no date found, include it (might be recent)
                filtered_urls.append({
                    "url": url,
                    "text": text,
                    "extracted_date": "unknown",
                    "is_recent": "unknown"
                })
                print(f"   ⚠️ No date: {text[:60]} (including anyway)")
        
        result["concall_urls"] = filtered_urls
        result["filtered_links"] = len(filtered_urls)
        result["success"] = True
        
        print(f"\n   ✅ Extracted {len(filtered_urls)} URLs from last 2 years")
        
    except Exception as e:
        error_msg = str(e)[:200]
        print(f"\n   ❌ Error: {error_msg}")
        result["errors"].append(error_msg)
    
    return result


def main():
    """Main function."""
    
    print("\n" + "="*70)
    print("EXTRACT CONCALL URLs - LAST 2 YEARS")
    print("="*70)
    
    # Cement Companies List
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
    
    print(f"\nTotal companies to process: {len(companies)}")
    
    # Ask for test mode
    print("\n" + "="*70)
    test_mode = input("Run in TEST MODE (1 company)? (y/n): ").strip().lower() == 'y'
    
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
        driver = setup_driver()
        print("✅ Browser ready\n")
        
        for i, company in enumerate(companies, 1):
            print(f"\n{'='*70}")
            print(f"[{i}/{len(companies)}] {company}")
            print(f"{'='*70}")
            
            result = extract_concall_urls(driver, company)
            results.append(result)
            
            if i < len(companies):
                print("\nWaiting 3 seconds before next company...")
                time.sleep(3)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = os.path.join(os.getcwd(), f"concall_urls_2years_{timestamp}.json")
        
        with open(results_file, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Create CSV summary
        csv_file = os.path.join(os.getcwd(), f"concall_urls_2years_{timestamp}.csv")
        with open(csv_file, "w", encoding='utf-8') as f:
            f.write("Company,Total Links Found,Links from Last 2 Years,Company URL,Success,Errors\n")
            for r in results:
                errors = "; ".join(r["errors"]) if r["errors"] else "None"
                f.write(f'"{r["company"]}",{r["all_found_links"]},{r["filtered_links"]},"{r["company_url"]}",{r["success"]},"{errors}"\n')
        
        # Generate detailed summary
        print("\n" + "="*70)
        print("EXTRACTION SUMMARY")
        print("="*70)
        
        successful = sum(1 for r in results if r["success"])
        total_links_found = sum(r["all_found_links"] for r in results)
        total_filtered_links = sum(r["filtered_links"] for r in results)
        
        print(f"\n✅ Successful: {successful}/{len(companies)} companies")
        print(f"📊 Total links found: {total_links_found}")
        print(f"📅 Links from last 2 years: {total_filtered_links}")
        
        print("\n" + "="*70)
        print("DETAILS BY COMPANY")
        print("="*70)
        
        for r in results:
            status = "✅" if r["success"] else "❌"
            print(f"\n{status} {r['company']}")
            print(f"   Company URL: {r['company_url'][:80]}")
            print(f"   Total links found: {r['all_found_links']}")
            print(f"   Links from last 2 years: {r['filtered_links']}")
            
            if r["concall_urls"]:
                print(f"   Recent concalls:")
                for idx, url_data in enumerate(r["concall_urls"][:3], 1):
                    date_str = url_data.get('extracted_date', 'unknown')
                    text = url_data.get('text', 'No title')[:60]
                    print(f"      {idx}. [{date_str}] {text}")
                if len(r["concall_urls"]) > 3:
                    print(f"      ... and {len(r['concall_urls']) - 3} more")
            
            if r["errors"]:
                print(f"   ⚠️ Errors: {', '.join(r['errors'])}")
        
        print("\n" + "="*70)
        print("OUTPUT FILES")
        print("="*70)
        print(f"📄 JSON: {results_file}")
        print(f"📊 CSV: {csv_file}")
        print("="*70)
        
        print("\n✅ Extraction completed! Closing browser...")
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
