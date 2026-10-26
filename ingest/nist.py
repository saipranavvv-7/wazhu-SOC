"""NIST CSF 2.0 xlsx -> list[Chunk]  (one chunk per subcategory).

Column names are auto-detected by keyword because the real file has not been
inspected yet. Run `python inspect_nist.py` first; if detection fails, edit the
keywords in nist_to_chunks().
"""
import re
import pandas as pd
from contracts import Chunk

SUB_ID = re.compile(r"^[A-Z]{2}\.[A-Z]{2}-\d{2}")  # e.g. PR.AA-01


def _find(cols, keyword):
    for c in cols:
        if keyword in str(c).lower():
            return c
    raise ValueError(f"No column containing '{keyword}'. Columns: {list(cols)}")


def _clean(v):
    return "" if pd.isna(v) else str(v).strip()


def _short(s):
    return s.split(":")[0].strip()


def nist_to_chunks(path="data/csf2.xlsx", sheet="CSF 2.0") -> list[Chunk]:
    df = pd.read_excel(path, sheet_name=sheet, header=1)  # row 0 is a title banner
    f_col = _find(df.columns, "function")
    c_col = _find(df.columns, "category")
    s_col = _find(df.columns, "subcategory")
    try:
        e_col = _find(df.columns, "example")
    except ValueError:
        e_col = None

    func = cat = ""
    cur = None
    out = []

    def flush():
        if cur:
            text = f"{cur['id']} ({_short(cur['func'])} > {_short(cur['cat'])}): {cur['desc']}"
            if cur["examples"]:
                text += "\nExamples: " + " ".join(cur["examples"])
            out.append(Chunk(id=cur["id"], source_type="nist", title=cur["id"],
                             text=text, tags=[cur["func"], cur["cat"]]))

    for _, row in df.iterrows():
        if _clean(row[f_col]):
            flush(); cur = None; func = _clean(row[f_col]); cat = ""
        if _clean(row[c_col]):
            flush(); cur = None; cat = _clean(row[c_col])
        sub = _clean(row[s_col])
        if sub and SUB_ID.match(sub) and "[Withdrawn" in sub:
            flush(); cur = None  # skip CSF 1.1 leftovers
            continue
        if sub and SUB_ID.match(sub):
            flush()
            cur = {"id": sub.split(":")[0].strip(), "desc": sub,
                   "func": func, "cat": cat, "examples": []}
        if cur and e_col is not None and _clean(row[e_col]):
            cur["examples"].append(_clean(row[e_col]))
    flush()
    return out


if __name__ == "__main__":
    import random
    cs = nist_to_chunks()
    print(len(cs), "chunks")
    assert len({c.id for c in cs}) == len(cs), "duplicate IDs!"
    longest = max(cs, key=lambda c: len(c.text))
    print("longest chunk:", longest.id, len(longest.text), "chars")
    for c in random.sample(cs, min(5, len(cs))):
        print("-----\n", c.text[:400])
