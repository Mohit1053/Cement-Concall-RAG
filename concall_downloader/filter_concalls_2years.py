"""
Filter Concall Data for Last 2 Years
Filters the ST_Concall.xlsx data to extract only records from the last 2 years
"""

import pandas as pd
from datetime import datetime, timedelta
import os

def filter_concalls_last_2_years():
    """Filter concall data for the last 2 years."""
    
    print("\n" + "="*70)
    print("FILTER CONCALL DATA - LAST 2 YEARS")
    print("="*70)
    
    # Read the Excel file
    print("\n1. Reading ST_Concall.xlsx...")
    input_file = "ST_Concall.xlsx"
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found!")
        return
    
    df = pd.read_excel(input_file, sheet_name='ST_Concall')
    print(f"   ✅ Loaded {len(df):,} total records")
    print(f"   Unique companies: {df['CompanyID'].nunique():,}")
    
    # Display columns
    print(f"\n2. Data columns:")
    for col in df.columns:
        print(f"   - {col}")
    
    # Convert Date column to datetime if needed
    print("\n3. Processing dates...")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Remove rows with invalid dates
    initial_count = len(df)
    df = df.dropna(subset=['Date'])
    print(f"   ✅ Valid dates: {len(df):,} records")
    if initial_count > len(df):
        print(f"   Removed {initial_count - len(df):,} records with invalid dates")
    
    # Calculate cutoff date (2 years ago)
    cutoff_date = datetime.now() - timedelta(days=730)  # 2 years
    print(f"\n4. Filtering for dates after: {cutoff_date.strftime('%Y-%m-%d')}")
    
    # Filter for last 2 years
    df_filtered = df[df['Date'] >= cutoff_date].copy()
    print(f"   ✅ Records from last 2 years: {len(df_filtered):,}")
    print(f"   Date range: {df_filtered['Date'].min().strftime('%Y-%m-%d')} to {df_filtered['Date'].max().strftime('%Y-%m-%d')}")
    print(f"   Unique companies: {df_filtered['CompanyID'].nunique():,}")
    
    # Remove records with missing transcript URLs
    print("\n5. Filtering for valid transcript URLs...")
    df_filtered = df_filtered[df_filtered['TranscriptUrl'].notna()].copy()
    df_filtered = df_filtered[df_filtered['TranscriptUrl'] != '\\N'].copy()
    df_filtered = df_filtered[df_filtered['TranscriptUrl'].str.strip() != ''].copy()
    print(f"   ✅ Records with valid URLs: {len(df_filtered):,}")
    
    # Sort by date (most recent first) and company
    df_filtered = df_filtered.sort_values(['CompanyID', 'Date'], ascending=[True, False])
    
    # Display summary statistics
    print("\n6. Summary by Company (Top 20):")
    company_counts = df_filtered['CompanyID'].value_counts().head(20)
    for idx, (company, count) in enumerate(company_counts.items(), 1):
        print(f"   {idx:2d}. {str(company):30s} - {count:3d} concalls")
    
    # Save filtered data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save to Excel
    output_excel = f"ST_Concall_2Years_{timestamp}.xlsx"
    print(f"\n7. Saving filtered data...")
    
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df_filtered.to_excel(writer, sheet_name='Last_2_Years', index=False)
        
        # Create summary sheet
        summary_df = df_filtered.groupby('CompanyID').agg({
            'Date': ['count', 'min', 'max'],
            'TranscriptUrl': 'count'
        }).reset_index()
        summary_df.columns = ['CompanyID', 'Total_Concalls', 'Earliest_Date', 'Latest_Date', 'Valid_URLs']
        summary_df = summary_df.sort_values('Total_Concalls', ascending=False)
        summary_df.to_excel(writer, sheet_name='Summary_By_Company', index=False)
    
    print(f"   ✅ Excel saved: {output_excel}")
    
    # Save to CSV
    output_csv = f"ST_Concall_2Years_{timestamp}.csv"
    df_filtered.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"   ✅ CSV saved: {output_csv}")
    
    # Create detailed summary report
    print("\n" + "="*70)
    print("FILTERING SUMMARY")
    print("="*70)
    print(f"\nOriginal records: {initial_count:,}")
    print(f"Records from last 2 years: {len(df_filtered):,}")
    print(f"Reduction: {initial_count - len(df_filtered):,} records ({(1 - len(df_filtered)/initial_count)*100:.1f}%)")
    print(f"\nUnique companies in filtered data: {df_filtered['CompanyID'].nunique():,}")
    print(f"Date range: {df_filtered['Date'].min().strftime('%Y-%m-%d')} to {df_filtered['Date'].max().strftime('%Y-%m-%d')}")
    
    # Show cement companies if they exist
    print("\n" + "="*70)
    print("CEMENT COMPANIES (if present)")
    print("="*70)
    
    cement_companies = [
        "UltraTech", "Grasim", "Ambuja", "Shree Cement", "J K Cements",
        "Dalmia Bharat", "ACC", "Ramco Cement", "JSW Cement", "Nuvoco",
        "India Cements", "JK Lakshmi", "Star Cement", "Birla Corp", "Prism Johnson"
    ]
    
    # Convert CompanyID to string for searching
    df_filtered['CompanyID_str'] = df_filtered['CompanyID'].astype(str)
    
    for cement in cement_companies:
        matching = df_filtered[df_filtered['CompanyID_str'].str.contains(cement, case=False, na=False)]
        if len(matching) > 0:
            company_name = str(matching['CompanyID'].iloc[0])
            count = len(matching)
            latest_date = matching['Date'].max().strftime('%Y-%m-%d')
            print(f"✅ {company_name:30s} - {count:3d} concalls (latest: {latest_date})")
    
    print("\n" + "="*70)
    print("OUTPUT FILES")
    print("="*70)
    print(f"📊 Excel (with summary): {output_excel}")
    print(f"📄 CSV: {output_csv}")
    print("="*70)
    
    print("\n✅ Filtering completed!")
    
    return df_filtered


if __name__ == "__main__":
    try:
        df_filtered = filter_concalls_last_2_years()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
