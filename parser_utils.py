import re
import pdfplumber
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from all pages of a PDF using pdfplumber.
    Returns a single cleaned string with newlines replaced by spaces and collapsed whitespace.
    """
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            ptext = page.extract_text()
            if ptext:
                text.append(ptext)
    full = " ".join(text)
    # Replace newlines/tabs with space and collapse multiple spaces
    full = re.sub(r"[\r\n\t]+", " ", full)
    full = re.sub(r"\s{2,}", " ", full).strip()
    return full

def clean_amount(raw: str):
    """Take a matched amount string like 'Rs. 1,23,456' or '₹1,23,456' or '1,23,456' and return '123456'."""
    if not raw:
        return None
    s = str(raw)
    # remove currency symbols and words
    s = re.sub(r"[₹Rs\.\s]", "", s, flags=re.IGNORECASE)
    # remove commas
    s = s.replace(",", "")
    # if there's a minus at start (for credits), keep it
    s = s.strip()
    # final numeric check
    m = re.match(r"^-?\d+$", s)
    return s if m else s  # return raw numeric-ish string (we don't convert to int to avoid locale issues)

# Multiple pattern variants to improve match robustness
PATTERNS = {
    # Name (various labels)
    "name": r"(?:Cardholder\s*Name|Statement\s*for|Statement for)[:\s]*([A-Za-z][A-Za-z\s\.&'-]{1,80})",
    # Card number (XXXX-XXXX-XXXX-1234 or last4)
    "card_number": r"(?:Credit\s*Card\s*Number|Card Number|Card No)[:\s]*([Xx0-9\-\s]{4,30})",
    # Billing / statement period
    "billing_period": r"(?:Statement\s*Period|Billing\s*Period)[:\s]*([0-9A-Za-z\s\-/to]+)",
    # Payment due date variations
    "payment_due_date": r"(?:Payment\s*Due\s*Date|Payment\s*Due)[:\s\-]*([0-9]{1,2}[/\-][0-9]{1,2}[/\-][A-Za-z0-9]{2,4})",
    # Statement date
    "statement_date": r"(?:Statement\s*Date)[:\s\-]*([0-9]{1,2}[/\-][0-9]{1,2}[/\-][A-Za-z0-9]{2,4})",
    # Minimum payment due variants
    "min_payment_due": r"(?:Minimum\s*(?:Payment\s*)?Due|Minimum\s*Amount\s*Due|Min\s*Due)[:\s\-]*[₹Rs\. ]*([\-]?[0-9,]+)",
    # New balance / current balance variants
    "new_balance": r"(?:New\s*Balance|Current\s*Balance|Total\s*Amount\s*Due|Amount\s*Due)[:\s\-]*[₹Rs\. ]*([\-]?[0-9,]+)",
    # Total credit limit variants
    "credit_limit": r"(?:Total\s*Credit\s*Limit|Credit\s*Limit|Total\s*Limit)[:\s\-]*[₹Rs\. ]*([0-9,]+)",
    # Rewards
    "rewards_earned": r"(?:Reward\s*Points\s*Earned|Reward\s*Points)[:\s\-]*([0-9,]+)",
}

def apply_pattern(pattern, text, flags=re.IGNORECASE):
    """Try a regex, return group(1) or None."""
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None

def parse_statement(pdf_path: str) -> dict:
    """Parse a single PDF statement and return a dict of extracted fields."""
    text = extract_text_from_pdf(pdf_path)
    result = {}

    # Bank identification heuristics (useful if needed)
    t = text.lower()
    if "hdfc" in t:
        result["bank_name"] = "HDFC"
    elif "sbi" in t:
        result["bank_name"] = "SBI"
    elif "icici" in t:
        result["bank_name"] = "ICICI"
    elif "axis" in t:
        result["bank_name"] = "Axis"
    elif "amex" in t or "american express" in t:
        result["bank_name"] = "Amex"
    else:
        result["bank_name"] = "Unknown"

    # Apply patterns
    for key, pattern in PATTERNS.items():
        raw = apply_pattern(pattern, text)
        if key in ("min_payment_due", "new_balance", "credit_limit"):
            normalized = clean_amount(raw)
            result[key] = normalized
        else:
            result[key] = raw

    # Also return full text length for debugging if needed
    result["_text_len"] = len(text)

    return result
