import pandas as pd
import requests
import os
from pathlib import Path
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_transcript(url, filepath, max_retries=5):
    """Download transcript with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}/{max_retries}...", end=" ")
            response = requests.get(url, verify=False, timeout=30, allow_redirects=True)
            
            if response.status_code == 200:
                # Check if we got actual PDF content
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type or response.content[:4] == b'%PDF':
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    file_size = len(response.content) / (1024 * 1024)  # MB
                    print(f"✓ Downloaded ({file_size:.2f} MB)")
                    return True
                else:
                    print(f"✗ Not a PDF (got {content_type})")
            else:
                print(f"✗ HTTP {response.status_code}")
            
            if attempt < max_retries - 1:
                time.sleep(3)  # Wait longer between retries
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {str(e)[:50]}")
            if attempt < max_retries - 1:
                time.sleep(3)
    
    return False

def retry_failed_downloads():
    """Retry downloading failed transcripts"""
    base_dir = Path(r"c:\Users\mohit1\Desktop\Data_Scraping\Cement_Concall_Transcripts")
    failed_csv = base_dir / "failed_downloads.csv"
    
    if not failed_csv.exists():
        print("No failed downloads file found!")
        return
    
    # Read failed downloads
    df_failed = pd.read_csv(failed_csv)
    print(f"Found {len(df_failed)} failed downloads to retry\n")
    
    successful = []
    still_failed = []
    
    for idx, row in df_failed.iterrows():
        company = row['company']
        url = row['url']
        filename = row['filename']
        
        # Create company folder if it doesn't exist
        company_folder = base_dir / company
        company_folder.mkdir(exist_ok=True)
        
        filepath = company_folder / filename
        
        print(f"[{idx+1}/{len(df_failed)}] {company}")
        print(f"  File: {filename}")
        print(f"  URL: {url[:80]}...")
        
        if download_transcript(url, filepath):
            successful.append({
                'company': company,
                'filename': filename,
                'url': url
            })
        else:
            still_failed.append({
                'company': company,
                'date': row['date'],
                'filename': filename,
                'url': url,
                'error': 'Still failed after retry'
            })
        
        print()
    
    # Print summary
    print("\n" + "="*80)
    print("RETRY SUMMARY")
    print("="*80)
    print(f"Total retried: {len(df_failed)}")
    print(f"Successfully downloaded: {len(successful)}")
    print(f"Still failed: {len(still_failed)}")
    
    if successful:
        print("\n✓ Successfully Downloaded:")
        for item in successful:
            print(f"  - {item['company']}: {item['filename']}")
    
    if still_failed:
        print("\n✗ Still Failed:")
        for item in still_failed:
            print(f"  - {item['company']}: {item['filename']}")
        
        # Update failed downloads CSV
        df_still_failed = pd.DataFrame(still_failed)
        df_still_failed.to_csv(failed_csv, index=False)
        print(f"\nUpdated failed_downloads.csv with {len(still_failed)} remaining failures")
    else:
        # Delete failed downloads CSV if all succeeded
        failed_csv.unlink()
        print("\n✓ All downloads successful! Deleted failed_downloads.csv")

if __name__ == "__main__":
    print("RETRYING FAILED DOWNLOADS")
    print("="*80)
    retry_failed_downloads()
