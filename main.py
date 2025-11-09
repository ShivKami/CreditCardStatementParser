import os
import pandas as pd
from parser_utils import parse_statement
import sys

# Input folder where your PDFs live
INPUT_FOLDER = "sample_statements"   # set to the folder you actually use
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def main():
    if not os.path.exists(INPUT_FOLDER):
        print(f"Input folder '{INPUT_FOLDER}' not found. Please create it and add PDF files.")
        sys.exit(1)

    records = []
    for fname in sorted(os.listdir(INPUT_FOLDER)):
        if not fname.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(INPUT_FOLDER, fname)
        print(f"→ Parsing {fname} ...")
        data = parse_statement(pdf_path)

        # Ensure file_name is basename only (no folder path)
        data["file_name"] = os.path.basename(fname)

        # Optional: warn which important fields are missing for this file
        missing = [k for k in ("min_payment_due", "new_balance", "credit_limit") if not data.get(k)]
        if missing:
            print(f"Missing fields in {fname}: {', '.join(missing)}")

        records.append(data)

    if not records:
        print("No PDFs parsed.")
        return

    df = pd.DataFrame(records)
    output_file = os.path.join(OUTPUT_FOLDER, "All_Banks_Parsed_Statements.csv")

    # Try to save; if permission error, write to a new filename
    try:
        df.to_csv(output_file, index=False)
        print(f"\nSaved parsed data to: {output_file}")
    except PermissionError:
        alt = os.path.join(OUTPUT_FOLDER, "All_Banks_Parsed_Statements_new.csv")
        df.to_csv(alt, index=False)
        print(f"\nCould not write to {output_file}. Saved to {alt} instead.")

if __name__ == "__main__":
    main()
