import io
import csv
from typing import List, Dict, Any, Tuple
import openpyxl
from pypdf import PdfReader
from app.schemas.schemas import MemberGazetteItem, GazettePreviewResponse

def normalize_text(text: Any) -> str:
    if text is None:
        return ""
    return str(text).strip()

def parse_gazette_spreadsheet(file_bytes: bytes, filename: str) -> Tuple[List[MemberGazetteItem], List[str]]:
    items: List[MemberGazetteItem] = []
    warnings: List[str] = []
    
    if filename.lower().endswith(".csv"):
        content = file_bytes.decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(content))
        for row in reader:
            normalized_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
            item = extract_row_data(normalized_row)
            if item:
                items.append(item)
    else:
        # Excel
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        for sheetname in wb.sheetnames:
            ws = wb[sheetname]
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                continue
            
            # Find header row
            header_idx = -1
            headers = []
            for idx, r in enumerate(rows):
                str_r = [str(c).lower().strip() for c in r if c is not None]
                if any("surname" in x or "name" in x for x in str_r):
                    header_idx = idx
                    headers = [str(c).strip().lower() if c is not None else "" for c in r]
                    break
            
            if header_idx == -1:
                continue
            
            # Category inference from sheet name if applicable
            sheet_cat = None
            s_lower = sheetname.lower()
            if "woman" in s_lower or "cwr" in s_lower:
                sheet_cat = "WOMAN_REP"
            elif "nominated" in s_lower:
                sheet_cat = "NOMINATED"
            elif "mp" in s_lower or "constituency" in s_lower:
                sheet_cat = "MP"
            
            for row in rows[header_idx + 1:]:
                if not any(row):
                    continue
                row_dict = {}
                for h, val in zip(headers, row):
                    if h:
                        row_dict[h] = normalize_text(val)
                
                item = extract_row_data(row_dict, default_category=sheet_cat)
                if item:
                    items.append(item)
                    
    return items, warnings

import re

# Comprehensive list of noise / preamble patterns in Kenyan IEBC Gazette notices to ignore
NON_MEMBER_PATTERNS = [
    r"THE\s+KENYA\s+GAZETTE",
    r"PUBLISHED\s+BY\s+AUTHORITY",
    r"VOL\.\s+[A-Z0-9IVXLCDM]+",
    r"GAZETTE\s+NOTICE\s+NO\.",
    r"IN\s+EXERCISE\s+OF\s+THE\s+POWERS",
    r"CONSTITUTION\s+OF\s+KENYA",
    r"THE\s+ELECTIONS\s+ACT",
    r"INDEPENDENT\s+ELECTORAL\s+AND\s+BOUNDARIES\s+COMMISSION",
    r"DECLARATION\s+OF\s+PERSONS\s+ELECTED",
    r"PRINTED\s+AND\s+PUBLISHED\s+BY\s+THE\s+GOVERNMENT\s+PRINTER",
    r"PRICE\s+KSH",
    r"DATED\s+THE\s+\d+",
    r"RETURNING\s+OFFICER",
    r"CHAIRPERSON",
    r"COMMISSION\s+SECRETARY",
    r"CHIEF\s+EXECUTIVE\s+OFFICER",
    r"WAFULA\s+CHEBUKATI",
    r"MARJAN\s+HUSSEIN",
    r"CORRIGENDA",
    r"SPECIAL\s+ISSUE",
    r"NAIROBI,\s+\d+",
    r"^\s*PAGE\s+\d+",
    r"^\s*\[\s*\d+\s*\]\s*$",
    r"^\s*\d+\s*$"  # Standalone numbers (page numbers)
]

TABLE_HEADER_PATTERNS = [
    r"COUNTY\s+CODE",
    r"CONST\.\s+CODE",
    r"CONSTITUENCY\s+CODE",
    r"CONSTITUENCY\s+NAME",
    r"SURNAME",
    r"OTHER\s+NAMES",
    r"POLITICAL\s+PARTY",
    r"PARTY\s+NAME",
    r"SPECIAL\s+CATEGORY",
    r"ABBREVIATION",
    r"MARGIN\s+OF\s+VOTES"
]

def is_ignorable_gazette_line(line: str) -> bool:
    line_upper = line.strip().upper()
    if not line_upper or len(line_upper) < 3:
        return True
    for pat in NON_MEMBER_PATTERNS:
        if re.search(pat, line_upper):
            return True
    # Table header rows
    match_count = sum(1 for pat in TABLE_HEADER_PATTERNS if re.search(pat, line_upper))
    if match_count >= 2:
        return True
    return False

def parse_gazette_pdf(file_bytes: bytes) -> Tuple[List[MemberGazetteItem], List[str]]:
    items: List[MemberGazetteItem] = []
    warnings: List[str] = []
    seen_keys = set()
    
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        current_cat = "MP"
        
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            lines = text.split("\n")
            
            for line in lines:
                l_str = line.strip()
                if not l_str:
                    continue
                    
                u_str = l_str.upper()
                
                # Detect section switches across Kenyan National Assembly categories
                if "COUNTY WOMAN REPRESENTATIVE" in u_str or "WOMAN REPRESENTATIVE" in u_str:
                    current_cat = "WOMAN_REP"
                    continue
                elif "NOMINATED" in u_str and ("MEMBERS" in u_str or "NATIONAL ASSEMBLY" in u_str):
                    current_cat = "NOMINATED"
                    continue
                elif "MEMBERS OF THE NATIONAL ASSEMBLY" in u_str or "CONSTITUENCY MEMBERS" in u_str:
                    current_cat = "MP"
                    continue
                
                # Filter out preamble, headers, signatures, legal boilerplate
                if is_ignorable_gazette_line(l_str):
                    continue
                
                # Split table line by 2 or more spaces, tabs, or pipes
                parts = [p.strip() for p in re.split(r"\t+|\s{2,}|\|", l_str) if p.strip()]
                
                # Heuristic pattern 1: Standard tabular columns with at least 3 segments
                # e.g.: [Surname, Other Names, County, Constituency, Party] or [County, Const, Surname, Other Names, Party]
                if len(parts) >= 3:
                    surname = ""
                    other = ""
                    county = None
                    constituency = None
                    party = "Independent"
                    
                    # If first element is numeric (serial no or county code), shift or consume
                    if parts[0].isdigit() and len(parts) >= 4:
                        parts = parts[1:]
                        if parts[0].isdigit() and len(parts) >= 4:
                            parts = parts[1:]
                    
                    # Recognize column positions
                    if len(parts) == 3:
                        # [Surname, Other Names, Party]
                        surname = parts[0]
                        other = parts[1]
                        party = parts[2]
                    elif len(parts) == 4:
                        # [Surname, Other Names, County/Const, Party]
                        surname = parts[0]
                        other = parts[1]
                        if current_cat == "WOMAN_REP":
                            county = parts[2]
                        else:
                            constituency = parts[2]
                        party = parts[3]
                    elif len(parts) >= 5:
                        # [County, Constituency, Surname, Other Names, Party] or [Surname, Other Names, County, Constituency, Party]
                        if any(c in parts[0].upper() for c in ["COUNTY", "MOMBASA", "KILIFI", "NAIROBI", "KIAMBU", "NAKURU", "KISUMU"]):
                            county = parts[0]
                            constituency = parts[1]
                            surname = parts[2]
                            other = parts[3]
                            party = parts[4]
                        else:
                            surname = parts[0]
                            other = parts[1]
                            county = parts[2]
                            constituency = parts[3]
                            party = parts[4]
                            
                    # Clean names from artifacts
                    surname = re.sub(r"^[0-9\.\-\)\s]+", "", surname).strip()
                    other = re.sub(r"^[0-9\.\-\)\s]+", "", other).strip()
                    party = party.strip()
                    
                    # Sanity check: must look like a person's name (letters, min length)
                    if len(surname) >= 2 and len(other) >= 2 and not surname.isdigit():
                        # Exclude any stray uppercase titles like 'DATE', 'VOTES', 'TOTAL'
                        if surname.upper() not in ["DATE", "TOTAL", "VOTES", "REMARKS", "STAGE"]:
                            full_name = f"{surname} {other}".strip()
                            dedup_key = f"{full_name.lower()}_{current_cat}"
                            if dedup_key not in seen_keys:
                                seen_keys.add(dedup_key)
                                items.append(MemberGazetteItem(
                                    surname=surname,
                                    other_names=other,
                                    full_name=full_name,
                                    category=current_cat,
                                    constituency=constituency,
                                    county=county,
                                    party=party
                                ))
                else:
                    # Pattern 2: Single line with pattern "No. Surname Other Names - Seat (Party)"
                    match = re.match(r"^(?:\d+[\.\)]\s*)?([A-Z\s\'-]+),\s*([A-Za-z\s\'-]+?)\s*[-–]\s*([A-Za-z\s]+?)\s*\((.*?)\)", l_str)
                    if match:
                        surname = match.group(1).strip()
                        other = match.group(2).strip()
                        seat = match.group(3).strip()
                        party = match.group(4).strip()
                        full_name = f"{surname} {other}".strip()
                        
                        dedup_key = f"{full_name.lower()}_{current_cat}"
                        if dedup_key not in seen_keys:
                            seen_keys.add(dedup_key)
                            items.append(MemberGazetteItem(
                                surname=surname,
                                other_names=other,
                                full_name=full_name,
                                category=current_cat,
                                constituency=seat if current_cat == "MP" else None,
                                county=seat if current_cat == "WOMAN_REP" else None,
                                party=party or "Independent"
                            ))
                            
    except Exception as e:
        warnings.append(f"PDF parsing error: {str(e)}. Please ensure file is a legible text PDF.")
        
    return items, warnings

def extract_row_data(row: Dict[str, str], default_category: str = None) -> MemberGazetteItem:
    # Keys might be 'surname', 'other names', 'other_names', 'full name', 'full_name'
    surname = row.get("surname", "")
    other_names = row.get("other names") or row.get("other_names", "")
    full_name = row.get("full name") or row.get("full_name") or row.get("name", "")
    
    if not surname and not full_name:
        return None
        
    if not surname and full_name:
        parts = full_name.split()
        if len(parts) > 1:
            surname = parts[0]
            other_names = " ".join(parts[1:])
        else:
            surname = full_name
            other_names = ""
            
    if not full_name:
        full_name = f"{surname} {other_names}".strip()
        
    constituency = row.get("constituency") or row.get("constituency name") or None
    county = row.get("county") or row.get("county name") or None
    party = row.get("party") or row.get("political party") or "Independent"
    
    category = row.get("category") or default_category
    if not category:
        if constituency and county:
            category = "MP"
        elif county and not constituency:
            category = "WOMAN_REP"
        elif not constituency and not county:
            category = "NOMINATED"
        else:
            category = "MP"
            
    cat_upper = category.upper()
    if "WOMAN" in cat_upper or "CWR" in cat_upper:
        category = "WOMAN_REP"
    elif "NOMINAT" in cat_upper:
        category = "NOMINATED"
    elif "SPEAKER" in cat_upper:
        category = "SPEAKER"
    else:
        category = "MP"
        
    return MemberGazetteItem(
        surname=surname,
        other_names=other_names,
        full_name=full_name,
        category=category,
        constituency=constituency,
        county=county,
        party=party
    )

def preview_gazette(items: List[MemberGazetteItem], warnings: List[str]) -> GazettePreviewResponse:
    count_mp = sum(1 for x in items if x.category == "MP")
    count_cwr = sum(1 for x in items if x.category == "WOMAN_REP")
    count_nom = sum(1 for x in items if x.category == "NOMINATED")
    
    is_valid = (count_mp == 290 and count_cwr == 47 and count_nom == 12)
    
    if count_mp != 290:
        warnings.append(f"Elected Constituency MPs: found {count_mp}, expected 290.")
    if count_cwr != 47:
        warnings.append(f"County Woman Representatives: found {count_cwr}, expected 47.")
    if count_nom != 12:
        warnings.append(f"Nominated Members: found {count_nom}, expected 12.")
        
    return GazettePreviewResponse(
        total_parsed=len(items),
        count_mp=count_mp,
        count_woman_rep=count_cwr,
        count_nominated=count_nom,
        target_mp=290,
        target_woman_rep=47,
        target_nominated=12,
        is_counts_valid=is_valid,
        sample_records=items[:15],
        warnings=warnings
    )
