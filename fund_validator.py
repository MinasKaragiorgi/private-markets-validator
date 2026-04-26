"""
Private Markets Fund Data Validator
====================================

A tool for extracting, validating, and storing fund data from PDF documents.
Designed to support Private Markets Quantitative Due Diligence workflows.

Author: Minas Karagiorgis
Inspired by: Albourne Partners' QDD-ACR Team workflows
"""

import pandas as pd
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class FundData:
    """Structure for fund information extracted from documents"""
    fund_name: str
    aum: Optional[float] = None  # Assets Under Management
    management_fee: Optional[float] = None  # % as decimal
    performance_fee: Optional[float] = None  # % as decimal
    vintage_year: Optional[int] = None
    target_irr: Optional[float] = None  # % as decimal
    fund_type: Optional[str] = None  # PE, VC, Real Estate, etc.
    geography: Optional[str] = None
    strategy: Optional[str] = None
    document_date: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)


class DataValidator:
    """
    Validates fund data for completeness and consistency
    
    Validation rules based on industry standards:
    - AUM should be positive
    - Fees should be between 0-100%
    - Vintage year should be reasonable (1980-current)
    - Target IRR should be realistic (0-50%)
    """
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.validation_results = []
        
    def validate_fund(self, fund: FundData) -> Dict[str, any]:
        """
        Validate a single fund's data
        
        Returns:
            Dictionary with validation status and issues found
        """
        issues = []
        warnings = []
        
        # Required field checks
        if not fund.fund_name:
            issues.append("Missing fund name")
        
        # AUM validation
        if fund.aum is not None:
            if fund.aum <= 0:
                issues.append(f"Invalid AUM: ${fund.aum:,.0f} (must be positive)")
            elif fund.aum > 100_000_000_000:  # $100B seems unrealistic for most funds
                warnings.append(f"Unusually high AUM: ${fund.aum:,.0f}")
        else:
            warnings.append("Missing AUM")
        
        # Management fee validation
        if fund.management_fee is not None:
            if fund.management_fee < 0 or fund.management_fee > 0.05:  # 0-5%
                issues.append(f"Invalid management fee: {fund.management_fee*100:.2f}%")
        else:
            warnings.append("Missing management fee")
        
        # Performance fee validation
        if fund.performance_fee is not None:
            if fund.performance_fee < 0 or fund.performance_fee > 0.50:  # 0-50%
                issues.append(f"Invalid performance fee: {fund.performance_fee*100:.2f}%")
        else:
            warnings.append("Missing performance fee")
        
        # Vintage year validation
        current_year = datetime.now().year
        if fund.vintage_year is not None:
            if fund.vintage_year < 1980 or fund.vintage_year > current_year + 1:
                issues.append(f"Invalid vintage year: {fund.vintage_year}")
        else:
            warnings.append("Missing vintage year")
        
        # Target IRR validation
        if fund.target_irr is not None:
            if fund.target_irr < 0 or fund.target_irr > 0.50:  # 0-50%
                issues.append(f"Invalid target IRR: {fund.target_irr*100:.2f}%")
        else:
            warnings.append("Missing target IRR")
        
        # Determine overall status
        if issues:
            status = "FAIL"
        elif warnings and self.strict_mode:
            status = "WARNING"
        else:
            status = "PASS"
        
        validation_result = {
            'fund_name': fund.fund_name,
            'status': status,
            'issues': issues,
            'warnings': warnings,
            'completeness': self._calculate_completeness(fund)
        }
        
        self.validation_results.append(validation_result)
        return validation_result
    
    def _calculate_completeness(self, fund: FundData) -> float:
        """Calculate data completeness percentage"""
        fields = [
            fund.aum, fund.management_fee, fund.performance_fee,
            fund.vintage_year, fund.target_irr, fund.fund_type,
            fund.geography, fund.strategy
        ]
        
        filled = sum(1 for f in fields if f is not None)
        return (filled / len(fields)) * 100
    
    def generate_report(self) -> pd.DataFrame:
        """Generate validation summary report"""
        if not self.validation_results:
            return pd.DataFrame()
        
        return pd.DataFrame(self.validation_results)


class FundDatabase:
    """SQLite database for storing fund information"""
    
    def __init__(self, db_path: str = "fund_data.db"):
        self.db_path = db_path
        self.conn = None
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS funds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_name TEXT NOT NULL UNIQUE,
            aum REAL,
            management_fee REAL,
            performance_fee REAL,
            vintage_year INTEGER,
            target_irr REAL,
            fund_type TEXT,
            geography TEXT,
            strategy TEXT,
            document_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS validation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_name TEXT NOT NULL,
            validation_date TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            completeness REAL,
            issues TEXT,
            warnings TEXT
        )
        ''')
        
        self.conn.commit()
    
    def insert_fund(self, fund: FundData) -> bool:
        """
        Insert or update fund data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            # Convert fund to dict
            fund_dict = fund.to_dict()
            
            # Check if fund exists
            cursor.execute("SELECT id FROM funds WHERE fund_name = ?", (fund.fund_name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                set_clause = ", ".join([f"{k} = ?" for k in fund_dict.keys() if k != 'fund_name'])
                values = [v for k, v in fund_dict.items() if k != 'fund_name']
                values.append(fund.fund_name)
                
                cursor.execute(f'''
                    UPDATE funds 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE fund_name = ?
                ''', values)
            else:
                # Insert new record
                columns = ', '.join(fund_dict.keys())
                placeholders = ', '.join(['?' for _ in fund_dict])
                
                cursor.execute(f'''
                    INSERT INTO funds ({columns})
                    VALUES ({placeholders})
                ''', list(fund_dict.values()))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting fund: {e}")
            return False
    
    def log_validation(self, validation_result: Dict):
        """Log validation result to history"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO validation_history 
                (fund_name, status, completeness, issues, warnings)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                validation_result['fund_name'],
                validation_result['status'],
                validation_result['completeness'],
                json.dumps(validation_result['issues']),
                json.dumps(validation_result['warnings'])
            ))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Error logging validation: {e}")
    
    def get_all_funds(self) -> pd.DataFrame:
        """Retrieve all funds as DataFrame"""
        return pd.read_sql_query("SELECT * FROM funds", self.conn)
    
    def get_validation_history(self) -> pd.DataFrame:
        """Retrieve validation history"""
        return pd.read_sql_query(
            "SELECT * FROM validation_history ORDER BY validation_date DESC", 
            self.conn
        )
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


class PDFExtractor:
    """
    Extract fund data from PDF documents
    
    Note: This is a simplified version using text patterns.
    In production, would use pdfplumber or PyPDF2 for actual PDF parsing.
    """
    
    @staticmethod
    def extract_from_text(text: str) -> FundData:
        """
        Extract fund information from text content
        
        Uses regex patterns to find common fund data fields
        """
        fund_data = {}
        
        # Extract fund name (simplified - look for "Fund Name:" pattern)
        name_match = re.search(r'(?:Fund Name|Fund):\s*([A-Za-z0-9\s&]+)', text, re.IGNORECASE)
        fund_data['fund_name'] = name_match.group(1).strip() if name_match else "Unknown Fund"
        
        # Extract AUM (look for patterns like "$500M", "AUM: 500M", etc.)
        aum_match = re.search(r'(?:AUM|Assets Under Management):\s*\$?([0-9,.]+)\s*(M|B|Million|Billion)', text, re.IGNORECASE)
        if aum_match:
            amount = float(aum_match.group(1).replace(',', ''))
            unit = aum_match.group(2).upper()
            multiplier = 1_000_000 if unit.startswith('M') else 1_000_000_000
            fund_data['aum'] = amount * multiplier
        
        # Extract management fee (look for "2%" or "2.0%")
        mgmt_match = re.search(r'(?:Management Fee):\s*([0-9.]+)%', text, re.IGNORECASE)
        if mgmt_match:
            fund_data['management_fee'] = float(mgmt_match.group(1)) / 100
        
        # Extract performance/carried interest fee
        perf_match = re.search(r'(?:Performance Fee|Carried Interest|Carry):\s*([0-9.]+)%', text, re.IGNORECASE)
        if perf_match:
            fund_data['performance_fee'] = float(perf_match.group(1)) / 100
        
        # Extract vintage year
        vintage_match = re.search(r'(?:Vintage|Year):\s*(20[0-9]{2})', text)
        if vintage_match:
            fund_data['vintage_year'] = int(vintage_match.group(1))
        
        # Extract target IRR
        irr_match = re.search(r'(?:Target IRR|Target Return):\s*([0-9.]+)%', text, re.IGNORECASE)
        if irr_match:
            fund_data['target_irr'] = float(irr_match.group(1)) / 100
        
        # Extract fund type
        if re.search(r'(?:Private Equity|PE Fund)', text, re.IGNORECASE):
            fund_data['fund_type'] = 'Private Equity'
        elif re.search(r'(?:Venture Capital|VC Fund)', text, re.IGNORECASE):
            fund_data['fund_type'] = 'Venture Capital'
        elif re.search(r'(?:Real Estate)', text, re.IGNORECASE):
            fund_data['fund_type'] = 'Real Estate'
        
        return FundData(**fund_data)


# Example usage functions
def validate_sample_funds():
    """Example: Validate sample fund data"""
    
    # Sample funds (in practice, these would be extracted from PDFs)
    sample_funds = [
        FundData(
            fund_name="Alpha Growth Partners IV",
            aum=500_000_000,
            management_fee=0.02,
            performance_fee=0.20,
            vintage_year=2020,
            target_irr=0.15,
            fund_type="Private Equity",
            geography="North America",
            strategy="Growth Equity"
        ),
        FundData(
            fund_name="Beta Ventures Fund III",
            aum=250_000_000,
            management_fee=0.025,
            performance_fee=0.25,  # High but not invalid
            vintage_year=2021,
            target_irr=0.25,
            fund_type="Venture Capital",
            geography="Global"
        ),
        FundData(
            fund_name="Gamma Real Estate Fund",
            aum=1_000_000_000,
            management_fee=0.015,
            # Missing performance fee - will trigger warning
            vintage_year=2019,
            target_irr=0.12,
            fund_type="Real Estate",
            geography="Europe"
        ),
        FundData(
            fund_name="Incomplete Fund Data",
            aum=100_000_000,
            # Missing most fields - will show low completeness
        )
    ]
    
    # Initialize validator and database
    validator = DataValidator(strict_mode=False)
    db = FundDatabase()
    
    print("="*70)
    print("PRIVATE MARKETS FUND DATA VALIDATION")
    print("="*70)
    print()
    
    # Validate and store each fund
    for fund in sample_funds:
        validation = validator.validate_fund(fund)
        db.insert_fund(fund)
        db.log_validation(validation)
        
        print(f"Fund: {fund.fund_name}")
        print(f"  Status: {validation['status']}")
        print(f"  Completeness: {validation['completeness']:.1f}%")
        
        if validation['issues']:
            print(f"  Issues: {', '.join(validation['issues'])}")
        if validation['warnings']:
            print(f"  Warnings: {', '.join(validation['warnings'])}")
        print()
    
    # Generate summary report
    print("="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    report = validator.generate_report()
    
    total_funds = len(report)
    passed = len(report[report['status'] == 'PASS'])
    failed = len(report[report['status'] == 'FAIL'])
    warned = len(report[report['status'] == 'WARNING'])
    
    print(f"\nTotal Funds Validated: {total_funds}")
    print(f"  ✓ Passed: {passed} ({passed/total_funds*100:.0f}%)")
    print(f"  ✗ Failed: {failed} ({failed/total_funds*100:.0f}%)")
    print(f"  ⚠ Warnings: {warned} ({warned/total_funds*100:.0f}%)")
    print(f"\nAverage Completeness: {report['completeness'].mean():.1f}%")
    
    # Export reports
    report.to_csv('validation_report.csv', index=False)
    db.get_all_funds().to_csv('fund_database.csv', index=False)
    
    print("\n✓ Reports exported:")
    print("  - validation_report.csv")
    print("  - fund_database.csv")
    print("  - fund_data.db (SQLite database)")
    
    db.close()
    print("\n" + "="*70)


if __name__ == "__main__":
    validate_sample_funds()
