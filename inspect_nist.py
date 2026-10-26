"""Step 1: look at the file BEFORE trusting the converter."""
import pandas as pd

xl = pd.ExcelFile("data/csf2.xlsx")
print("sheets:", xl.sheet_names)
df = pd.read_excel(xl, sheet_name="CSF 2.0")
print(df.shape)
print(df.columns.tolist())
print(df.head(12).to_string())
