"""
CSV metadata parser
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class MetadataParser:
    """Parse and structure metadata from CSV"""
    
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.df = None
    
    def load(self):
        """Load CSV file"""
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} records from {self.csv_path}")
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def get_metadata_for_file(self, filename: str) -> Dict:
        """Get metadata for a specific file"""
        # Match filename to CSV records
        # This needs to be customized based on your filename format
        pass
    
    def get_all_companies(self) -> List[str]:
        """Get list of all companies"""
        if self.df is not None:
            return self.df['CompanyName'].unique().tolist()
        return []
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter records by date range"""
        if self.df is not None:
            return self.df[
                (self.df['Date'] >= start_date) & 
                (self.df['Date'] <= end_date)
            ]
        return pd.DataFrame()
