# CreditCardStatementParser
Automated Credit Card Statement PDF Parser using Python
# Credit Card Statement Parser Project

### Overview
This project automatically extracts key financial information from credit card statement PDFs of multiple banks and converts it into a structured CSV file.

### Supported Banks
- HDFC Bank  
- SBI Card  
- ICICI Bank  
- Axis Bank  
- American Express  

### Extracted Data Points
- Payment Due Date  
- Statement Date  
- Minimum Payment Due  
- New Balance  
- Credit Limit  
- Rewards Earned  

### Tech Stack
- Python  
- pdfplumber / PyPDF2  
- pandas  
- reportlab  

### Future Improvements

OCR for scanned statements (Tesseract)

AI-based layout recognition

Web dashboard using Streamlit

### How to Run
```bash
git clone https://github.com/<your-username>/CreditCardStatementParser.git
cd CreditCardStatementParser
pip install -r requirements.txt
python main.py
