# Private Markets Fund Data Validator 📊

> A Python tool for extracting, validating, and managing fund data from documents - supporting Private Markets Quantitative Due Diligence workflows.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 Project Overview

This tool automates the extraction and validation of fund information from documents, ensuring data quality and completeness for Private Markets analysis. Inspired by workflows at **Albourne Partners' QDD-ACR Team**, it demonstrates practical data validation and quality control techniques essential for fund due diligence.

### What It Does:

- **Extracts** fund data from documents (PDFs, text files)
- **Validates** data against industry standards and business rules
- **Stores** fund information in SQLite database
- **Generates** validation reports highlighting issues and completeness
- **Tracks** validation history for audit purposes

---

## 💡 Why This Matters

### The Problem:
Private Markets teams process hundreds of fund documents monthly. Manual data entry is:
- ❌ Time-consuming and error-prone
- ❌ Difficult to track completeness
- ❌ Hard to identify inconsistencies
- ❌ Challenging to maintain audit trails

### The Solution:
Automated validation ensures:
- ✅ **Data Quality** - Catch errors before they enter the system
- ✅ **Completeness Tracking** - Know which funds need follow-up
- ✅ **Consistency** - Apply validation rules uniformly
- ✅ **Audit Trail** - Log all validation attempts

---

## 🚀 Features

### 1. Smart Data Extraction
- Pattern-based extraction from text documents
- Handles common fund data fields:
  - Assets Under Management (AUM)
  - Management & Performance Fees
  - Vintage Year
  - Target IRR
  - Fund Type & Strategy
  - Geography

### 2. Comprehensive Validation
- **Range Checks**: Ensures values are realistic
- **Completeness Analysis**: Tracks missing fields
- **Business Rules**: Applies industry standards
- **Issue Flagging**: Identifies problems requiring review

### 3. Database Management
- **SQLite Storage**: Persistent fund database
- **Update Detection**: Prevents duplicate entries
- **History Tracking**: Logs all validation attempts
- **Query Support**: Easy data retrieval

### 4. Reporting
- **Validation Summary**: Pass/Fail/Warning status
- **Completeness Metrics**: Percentage of filled fields
- **CSV Exports**: Compatible with Excel/analysis tools
- **Audit Logs**: Full validation history

---

## 📋 Requirements

```bash
python >= 3.8
pandas >= 1.3.0
```

That's it! No heavy dependencies - uses Python standard library for core functionality.

---

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/MinasKaragiorgi/private-markets-validator.git
cd private-markets-validator

# Install dependencies
pip install pandas

# Run the validator
python fund_validator.py
```

---

## 📊 Usage Examples

### Basic Validation

```python
from fund_validator import FundData, DataValidator, FundDatabase

# Create fund data
fund = FundData(
    fund_name="Alpha Growth Partners IV",
    aum=500_000_000,  # $500M
    management_fee=0.02,  # 2%
    performance_fee=0.20,  # 20%
    vintage_year=2020,
    target_irr=0.15,  # 15%
    fund_type="Private Equity"
)

# Validate
validator = DataValidator()
result = validator.validate_fund(fund)

print(f"Status: {result['status']}")
print(f"Completeness: {result['completeness']:.1f}%")
```

### Batch Processing

```python
# Initialize
validator = DataValidator(strict_mode=True)
db = FundDatabase()

# Process multiple funds
for fund in fund_list:
    validation = validator.validate_fund(fund)
    db.insert_fund(fund)
    db.log_validation(validation)

# Generate report
report = validator.generate_report()
report.to_csv('validation_summary.csv')
```

### Extract from Text

```python
from fund_validator import PDFExtractor

document_text = """
Fund Name: Beta Ventures Fund III
AUM: $250M
Management Fee: 2.5%
Performance Fee: 25%
Vintage: 2021
Target IRR: 25%
"""

fund = PDFExtractor.extract_from_text(document_text)
print(f"Extracted: {fund.fund_name}")
print(f"AUM: ${fund.aum:,.0f}")
```

---

## 🎓 Sample Output

```
======================================================================
PRIVATE MARKETS FUND DATA VALIDATION
======================================================================

Fund: Alpha Growth Partners IV
  Status: PASS
  Completeness: 100.0%

Fund: Beta Ventures Fund III
  Status: PASS
  Completeness: 87.5%

Fund: Gamma Real Estate Fund
  Status: WARNING
  Completeness: 75.0%
  Warnings: Missing performance fee

Fund: Incomplete Fund Data
  Status: WARNING
  Completeness: 12.5%
  Warnings: Missing management fee, Missing performance fee, ...

======================================================================
VALIDATION SUMMARY
======================================================================

Total Funds Validated: 4
  ✓ Passed: 2 (50%)
  ✗ Failed: 0 (0%)
  ⚠ Warnings: 2 (50%)

Average Completeness: 68.8%

✓ Reports exported:
  - validation_report.csv
  - fund_database.csv
  - fund_data.db (SQLite database)
```

---

## 🔍 Validation Rules

### Field Validation:

| Field | Valid Range | Action if Invalid |
|-------|-------------|-------------------|
| AUM | > $0 | Flag as issue |
| Management Fee | 0% - 5% | Flag as issue |
| Performance Fee | 0% - 50% | Flag as issue |
| Vintage Year | 1980 - Current+1 | Flag as issue |
| Target IRR | 0% - 50% | Flag as issue |

### Completeness Scoring:

- **100%** - All fields present
- **75-99%** - Most fields present, minor gaps
- **50-74%** - Significant gaps
- **<50%** - Requires substantial data collection

---

## 📈 Real-World Applications

### Private Markets QDD Team Use Cases:

1. **Initial Data Entry**
   - Extract data from new fund documents
   - Validate before database entry
   - Flag incomplete submissions

2. **Data Quality Audits**
   - Batch validate existing fund database
   - Identify records needing updates
   - Track improvement over time

3. **Quarterly Reviews**
   - Re-validate fund data against updates
   - Ensure consistency with latest documents
   - Maintain audit trail

4. **Reporting**
   - Generate completeness metrics for management
   - Track data quality KPIs
   - Support regulatory compliance

---

## 🛣️ Roadmap

Future enhancements:

- [ ] **PDF Processing**: Direct PDF extraction using pdfplumber
- [ ] **OCR Support**: Handle scanned documents
- [ ] **Machine Learning**: Improve extraction accuracy
- [ ] **Web Interface**: Dashboard for validation management
- [ ] **API Integration**: Connect to existing systems
- [ ] **Advanced Reports**: Data quality dashboards
- [ ] **Batch Upload**: Process multiple documents at once

---

## 📚 Technical Details

### Architecture:

```
fund_validator.py
├── FundData (dataclass)      # Data structure
├── PDFExtractor              # Text extraction
├── DataValidator             # Validation logic
├── FundDatabase              # SQLite operations
└── validate_sample_funds()   # Example usage
```

### Database Schema:

**funds table:**
- Fund information fields
- Created/updated timestamps
- Unique constraint on fund_name

**validation_history table:**
- Validation attempt logs
- Status and completeness scores
- Issues and warnings (JSON)

---

## 🤝 Relevance to Albourne QDD Role

This project demonstrates:

✅ **Data Processing Skills** - Extract and structure fund information  
✅ **Attention to Detail** - Comprehensive validation rules  
✅ **Database Management** - SQLite storage and queries  
✅ **Quality Control** - Systematic approach to data validation  
✅ **Documentation** - Clear code and user guidance  
✅ **Domain Knowledge** - Understanding of fund structures  

**Connection to Role:**
> "Review of fund documentation, checking information and making correct associations between documents and folders in database. Review of fund information, making sure the relevant fund details are accurately captured in the Company's database."

This tool automates and standardizes exactly these processes!

---

## 👤 Author

**Minas Karagiorgis**  
Computer Science Student | University of Cyprus  
📧 minaskaragiorgi28@gmail.com  
🐱 GitHub: github.com/MinasKaragiorgi  

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Albourne Partners** for publicly sharing insights about QDD workflows
- **University of Cyprus** Computer Science Department
- Open-source Python community

---

## ⚠️ Disclaimer

This tool is for educational and demonstration purposes. Real-world fund data processing requires:
- Proper data security and access controls
- Regulatory compliance (GDPR, etc.)
- Human review of automated validations
- Integration with official systems

Always consult fund documentation and qualified professionals for investment decisions.

---

<div align="center">

**If this project helped you understand fund data validation, please give it a ⭐!**

Made with Python and ❤️

</div>
