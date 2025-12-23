# Concall Transcript Downloader for Screener.in

## Overview
This script automatically downloads concall (conference call) transcripts for companies from screener.in for the last 2 years.

## Files
- `download_concalls_final.py` - Main production script (USE THIS ONE)
- `download_concalls_v2.py` - Earlier version (backup)
- `download_concalls.py` - Initial version (backup)

## How to Use

### Step 1: Run the Script
```powershell
python download_concalls_final.py
```

### Step 2: Choose Mode
When prompted:
- Type `y` for TEST MODE (processes only the first company - UltraTech Cem.)
- Type `n` for FULL MODE (processes all 15 companies)

### Step 3: Let it Run
- The script will open a Chrome browser window
- DO NOT CLOSE THE BROWSER MANUALLY
- Watch the console for progress updates
- The script will:
  1. Search for each company on screener.in
  2. Navigate to the company page
  3. Scroll down to find Documents/Concalls section
  4. Download all available transcripts

### Step 4: Wait for Completion
- The script will show progress for each company
- Files are downloaded to: `concall_transcripts/<CompanyName>/`
- Press Enter when prompted to close the browser

## Output

### Downloaded Files
- Location: `concall_transcripts/`
- Each company has its own subfolder
- Transcripts are PDF files

### Results File
- `concall_results.json` - Contains detailed results for each company including:
  - Success/failure status
  - Company URL
  - List of downloaded files
  - Any errors encountered

## Companies Processed
1. UltraTech Cem.
2. Grasim Inds
3. Ambuja Cements
4. Shree Cement
5. J K Cements
6. Dalmia BharatLtd
7. ACC
8. The Ramco Cement
9. JSW Cement
10. Nuvoco Vistas
11. India Cements
12. JK Lakshmi Cem.
13. Star Cement
14. Birla Corpn.
15. Prism Johnson

## Troubleshooting

### If the script fails:
1. Make sure you're connected to the internet
2. Check if screener.in is accessible
3. Run in TEST MODE first to verify it works
4. Check the console output for specific errors

### If no files are downloaded:
- The company might not have concall transcripts available
- The Documents/Concalls section might not be present on the page
- Check the `concall_results.json` file for error details

### If the browser closes unexpectedly:
- Don't manually close the browser
- Let the script complete
- Press Enter only when prompted

## Tips
- **Always run in TEST MODE first** to verify the script works for one company
- The script adds delays between companies to avoid overwhelming the website
- Each company's transcripts are saved in a separate folder for organization
- The script automatically waits for downloads to complete before moving to the next company

## Support
If you encounter issues, check:
1. The console output for error messages
2. The `concall_results.json` file for detailed results
3. The company-specific folders to see if any files were downloaded
