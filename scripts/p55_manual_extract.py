"""
Full-document typed fact extraction for TSA23 TSR Rationale (tsa23_2012_23ts13ra).
Reads all 7 chunk files and produces typed facts in the p55 wave7 schema.
No agent-workbench/freshforge workflows used — pure Python text analysis.
"""
import json
import os

# Define chunk paths from manifest
CHUNK_DIR = "runtime/document_library/tsa23_tsr/chunks/tsa23_2012_23ts13ra"
CHUNKS = [
    ("tsa23_2012_23ts13ra::pages_001_008", 1, 8),
    ("tsa23_2012_23ts13ra::pages_008_015", 8, 15),
    ("tsa23_2012_23ts13ra::pages_015_022", 15, 22),
    ("tsa23_2012_23ts13ra::pages_022_029", 22, 29),
    ("tsa23_2012_23ts13ra::pages_029_036", 29, 36),
    ("tsa23_2012_23ts13ra::pages_036_043", 36, 43),
    ("tsa23_2012_23ts13ra::pages_043_048", 43, 48),
]

def load_all_chunks():
    """Load all chunk files and return (chunk_id, page_start, page_end, text) list."""
    result = []
    for cid, ps, pe in CHUNKS:
        path = os.path.join(CHUNK_DIR, f"{cid}.txt")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        result.append((cid, ps, pe, text))
    return result

def find_field(text, cid, page_start, keywords_func, value_parser=None, 
               default_status="not_found", extract_units=False):
    """
    Generic field finder. keywords_func returns list of strings to search for.
    Searches for nearest context around keywords and extracts value.
    """
    text_lower = text.lower()
    found = False
    value = None
    quote = None
    
    for kw in keywords_func:
        idx = text_lower.find(kw.lower())
        if idx >= 0:
            found = True
            # Extract context window (~500 chars around match)
            start = max(0, idx - 100)
            end = min(len(text), idx + len(kw) + 400)
            quote = text[start:end].strip()
            
            if value_parser:
                try:
                    value = value_parser(text[idx:idx+500])
                except Exception:
                    value = kw
            else:
                # Take next reasonable value after keyword
                segment = text[idx:idx+200]
                lines = segment.split('\n')
                for line in lines[:3]:
                    clean = line.strip().strip('"').strip("'").strip('-').strip()
                    if clean and len(clean) > 1:
                        value = clean[:200]
                        break
            
            if quote:
                quote = quote.replace('\n', ' ')[:500]
            break
    
    page_end = page_start + min(8, 48 - page_start)
    page_anchor = f"PDF pages {page_start:03d}-{page_end:03d}" if found else None
    chunk_id = cid if found else None
    status = "found" if found else default_status
    confidence = 1.0 if found else 0.0
    
    return {"status": status, "value": value, "units": None, 
            "page_anchor": page_anchor, "chunk_id": chunk_id,
            "source_quote": quote, "confidence": confidence}

def read_all_chunks_to_string():
    """Concatenate all chunks for full-document searching."""
    chunks = load_all_chunks()
    return "\n\n---SEPARATOR---\n".join([t for _, _, _, t in chunks])

def extract_aac_value(text):
    """Find AAC value — document says 2,000,000 m³ (2013-2018) then 1,000,000 m³ (2018+)."""
    # Pattern: "AAC will be X cubic metres"
    import re
    results = re.findall(r'AAC will be ([\d,]+)\s*(?:cubic metres|m3)', text.lower())
    if results:
        values = []
        for r in results:
            clean = r.replace(',', '')
            try:
                values.append(int(clean))
            except ValueError:
                pass
        return sorted(set(values)) if values else None
    
    # Fallback: find "AAC.*[0-9]" patterns
    pattern = r'(\d[\d,]*)\s*(?:cubic metres|m3)'
    matches = re.findall(r'AAC.{0,60}' + pattern, text)
    if matches:
        for m in matches:
            clean = m.replace(',', '')
            try:
                return int(clean)
            except ValueError:
                pass
    
    # Another attempt: "will be 2 000 000 cubic metres"
    pattern2 = r'be ([\d ]{6,10})\s*cubic metres'
    m2 = re.search(pattern2, text)
    if m2:
        return int(m2.group(1).replace(' ', ''))
    
    return None

def extract_aac_effective_date(text):
    """Find the effective date of AAC determination."""
    patterns = [
        r'Effective ([A-Z][a-z]+ \d+, \d{4})',
        r'effective ([A-Z][a-z]+ \d+, \d{4})',
        r'from ([A-Z][a-z]+ \d+, \d{4}) to ([A-Z][a-z]+, \d{4})',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            dates = [m.group(i) for i in range(1, m.lastindex+1) if m.group(i)]
            return '; '.join(dates) if len(dates) > 1 else dates[0]
    return None

def extract_base_case_harvest_forecast(text):
    """Find base case harvest forecast values."""
    import re
    # Look for "base case" and nearby volume numbers
    patterns = [
        r'base case.{0,200}(\d[\d,]*)\s*(?:cubic metres|m3|million)',
        r'AAC of (\d[\d,]*)\s*(?:cubic metres|m3)',
    ]
    for p in patterns:
        m = re.search(p, text.lower())
        if m:
            clean = m.group(1).replace(',', '')
            try:
                return int(clean)
            except ValueError:
                pass
    
    # Look for period-specific AAC values
    periods = re.findall(r'(?:2013|2018 to 2023|2023 to 2028).{0,200}(\d[\d,]*)\s*cubic metres', text.lower())
    if periods:
        values = []
        for p in periods:
            clean = p.replace(',', '')
            try:
                values.append(int(clean))
            except ValueError:
                pass
        return sorted(set(values)) if values else None
    
    return None

def extract_thlb_area(text):
    """Find THLB (Timelife Harvestable Land Base) area."""
    import re
    patterns = [
        r'(\d[\d,]*)\s*(?:hectares|ha)\s*(?:THLB|timber harvesting|available)',
        r'(?:THLB|timber harvesting).*?(\d[\d,]*)\s*hectares',
        r'about (\d[\d,]*)\s*(?:hectares|ha)',
    ]
    for p in patterns:
        m = re.search(p, text.lower())
        if m:
            clean = m.group(1).replace(',', '')
            try:
                return int(clean)
            except ValueError:
                pass
    return None

def main():
    import re
    
    # Load all chunks
    chunks = load_all_chunks()
    full_text = read_all_chunks_to_string()
    
    print(f"Loaded {len(chunks)} chunks")
    for cid, ps, pe, t in chunks:
        print(f"  {cid}: pages {ps}-{pe}, {len(t):,} chars")
    
    # === EXTRACT EACH FIELD ===
    
    # We need to search each chunk individually to map fields back to their source
    
    # Field 1: tsa_name
    tsa_name = find_field(
        chunks[0][3], chunks[0][0], chunks[0][1],
        lambda _: ["100 mile house", "TSA is located", "timber supply area"],
        lambda txt: re.search(r'(100 Mile House).*?(?:TSA|timber)', txt, re.IGNORECASE)
    )
    
    # Field 2: tsa_number - typically not explicitly stated as a number in these docs
    tsa_number = {"status": "not_found", "value": None, "units": None, 
                  "page_anchor": None, "chunk_id": None, "source_quote": None, "confidence": 0.0}
    
    # Field 3: document_title
    doc_title = find_field(
        chunks[0][3], chunks[0][0], chunks[0][1],
        lambda _: ["rationale for", "allowable annual cut"],
        lambda txt: re.search(r'(Rationale.*?Determination)', txt, re.IGNORECASE | re.DOTALL)
    )
    if doc_title and doc_title.get('value'):
        doc_title['value'] = str(doc_title['value']).strip()[:200]
    
    # Field 4: determination_year
    det_year = find_field(
        chunks[0][3], chunks[0][0], chunks[0][1],
        lambda _: ["effective november", "november 7, 2013"],
        lambda txt: re.search(r'(\d{4})', txt)
    )
    if det_year and det_year.get('value'):
        year = str(det_year['value'])
        if len(year) == 4:
            det_year['value'] = int(year)
    
    # Field 5: aac_value - complex, needs careful handling
    # Search across all chunks
    aac_value_raw = None
    aac_chunk_id = None
    aac_page = None
    aac_quote = None
    
    for cid, ps, pe, text in chunks:
        if re.search(r'(AAC is|AAC will be|AAC to be|the AAC).*?(\d[\d ]*\d)', text.lower(), re.IGNORECASE):
            import re as re_mod
            # Find AAC values with periods
            period_pattern = r'(?:from\s+([A-Z]\w+\s+\d+,\s+\d{4})\s+to\s+[A-Z]\w+\s+\d+,\s+\d{4}|effective\s+[A-Z]\w+\s+\d+,\s+\d{4}).{0,300}'
            period_matches = list(re_mod.finditer(period_pattern, text))
            
            if period_matches:
                periods_found = []
                for pm in period_matches:
                    ctx = text[pm.start():pm.end()+300]
                    val_match = re_mod.search(r'(\d[\d ]*\d)\s*(?:cubic metres|m3)', ctx)
                    if val_match:
                        raw_val = val_match.group(1).replace(' ', '')
                        try:
                            val_int = int(raw_val)
                            # Find the period description nearby
                            start = max(0, pm.start() - 50)
                            aac_quote = text[start:pm.end()+300].strip().replace('\n', ' ')[:500]
                            periods_found.append((val_int, text[pm.start():pm.start()+100]))
                        except ValueError:
                            pass
                
                if periods_found:
                    # Sort by period (2013-2018 first, then 2018+)
                    aac_value_raw = sorted(set([p[0] for p in periods_found]))
                    aac_chunk_id = cid
                    aac_page = f"PDF pages {ps:03d}-{pe:03d}"
                    if not aac_quote:
                        start2 = max(0, pm.start() - 50)
                        aac_quote = text[start2:pm.end()+300].strip().replace('\n', ' ')[:500]
    
    # If we didn't find period-specific values, try simple pattern
    if aac_value_raw is None:
        for cid, ps, pe, text in chunks:
            m = re.search(r'(?:AAC will be|AAC is|the AAC is)\s+(\d[\d ]*\d)\s*(?:cubic metres|m3)', text, re.IGNORECASE)
            if m:
                raw = m.group(1).replace(' ', '').replace(',', '')
                try:
                    aac_value_raw = int(raw)
                    aac_chunk_id = cid
                    aac_page = f"PDF pages {ps:03d}-{pe:03d}"
                    aac_quote = text[max(0,m.start()-50):m.end()+100].strip().replace('\n', ' ')[:500]
                except ValueError:
                    pass
    
    # The document clearly states 2,000,000 m³ (2013-2018) then 1,000,000 m³ (2018+)
    # Let's look for these specific values more carefully
    if aac_value_raw is None:
        for cid, ps, pe, text in chunks:
            patterns = [
                r'(?:AAC will be|the AAC is)\s+(\d[\d ]*)\s*cubic metres',
                r'(?:AAC of|set at|was set at)\s+(\d[\d ]*)\s*(?:cubic metres|m3)',
            ]
            for pat in patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    raw = m.group(1).replace(' ', '').replace(',', '')
                    try:
                        val = int(raw)
                        if val >= 500000:  # Filter noise
                            aac_value_raw = [val] if not isinstance(aac_value_raw, list) else aac_value_raw + [val]
                            aac_chunk_id = cid
                            aac_page = f"PDF pages {ps:03d}-{pe:03d}"
                            aac_quote = text[max(0,m.start()-50):m.end()+200].strip().replace('\n', ' ')[:500]
                    except ValueError:
                        pass
    
    # If we have multiple values (different periods), store as list
    if isinstance(aac_value_raw, list) and len(aac_value_raw) > 1:
        aac_value_final = sorted(set(aac_value_raw))
    elif isinstance(aac_value_raw, int):
        aac_value_final = [aac_value_raw]  # Single value becomes a list
    else:
        aac_value_final = None
    
    if not aac_quote and aac_value_raw is not None:
        for cid2, ps2, pe2, text2 in chunks:
            m2 = re.search(r'(?:AAC will be|the AAC is)', text2, re.IGNORECASE)
            if m2:
                aac_quote = text2[max(0,m2.start()-100):m2.end()+300].strip().replace('\n', ' ')[:500]
                break
    
    # If we found the key AAC statement about 2,000,000 and 1,000,000
    if aac_value_final is None:
        # Direct search for "2 000 000" and "1 000 000"
        for cid3, ps3, pe3, text3 in chunks:
            if '2 000 000' in text3 or '2,000,000' in text3:
                m3 = re.search(r'(?:AAC will be|the AAC is)\s+(\d[\d ]*)\s*(?:cubic metres|m3)', text3, re.IGNORECASE)
                if m3:
                    raw3 = m3.group(1).replace(' ', '').replace(',', '')
                    aac_value_final = [int(raw3)]
                    aac_chunk_id = cid3
                    aac_page = f"PDF pages {ps3:03d}-{pe3:03d}"
                    aac_quote = text3[max(0,m3.start()-100):m3.end()+500].strip().replace('\n', ' ')[:500]
    
    # The document is clear: 2,000,000 (2013-2018), then 1,000,000 (2018+)
    # Let me try one more time with the exact pattern
    if aac_value_final is None:
        for cid4, ps4, pe4, text4 in chunks:
            m4 = re.search(r'will be (\d[\d ]*)\s*(?:cubic metres|m3)', text4, re.IGNORECASE)
            if m4 and not aac_value_final:
                val4 = int(m4.group(1).replace(' ', '').replace(',', ''))
                if val4 >= 500000:
                    aac_value_final = [val4]
                    aac_chunk_id = cid4
                    aac_page = f"PDF pages {ps4:03d}-{pe4:03d}"
                    aac_quote = text4[max(0,m4.start()-100):m4.end()+500].strip().replace('\n', ' ')[:500]
            elif m4:
                val4 = int(m4.group(1).replace(' ', '').replace(',', ''))
                if val4 >= 500000 and val4 not in aac_value_final:
                    aac_value_final.append(val4)
    
    # If still not found, check chunk 1 (which we already read above - it has the AAC section)
    if aac_value_final is None:
        cid5 = chunks[0][0]
        text5 = chunks[0][3]
        ps5 = chunks[0][1]
        
        # From the text we read earlier:
        # "AAC will be 2 000 000 cubic metres" and "AAC will be 1 000 000 cubic metres"
        m5a = re.search(r'will be (\d)\s*(\d[\d, ]*)\s*cubic metres', text5)
        if m5a:
            val = int(m5a.group(1) + m5a.group(2).replace(' ', '').replace(',', ''))
            aac_value_final = [val]
            aac_chunk_id = cid5
            aac_page = f"PDF pages {ps5:03d}-{chunks[0][2]:03d}"
            aac_quote = text5[max(0,m5a.start()-100):m5a.end()+500].strip().replace('\n', ' ')[:500]
        
        # Second value
        remaining = text5[m5a.end():] if m5a else text5
        m5b = re.search(r'will be (\d)\s*(\d[\d, ]*)\s*cubic metres', remaining)
        if m5b:
            val2 = int(m5b.group(1) + m5b.group(2).replace(' ', '').replace(',', ''))
            if aac_value_final and val2 not in aac_value_final:
                aac_value_final.append(val2)
    
    # Final fallback - the document clearly contains these values from our read
    if aac_value_final is None:
        # We KNOW from the first chunk that it says "AAC will be 2 000 000" and "1 000 000"
        chunks_for_aac = [c[3] for c in chunks[:2]]
        text_aac = ' '.join(chunks_for_aac)
        
        # Pattern: "will be X YYY cubic metres" where X is the first digit and YYY rest
        m_all = list(re.finditer(r'will be (\d[\d ]*)\s*cubic metres', text_aac, re.IGNORECASE))
        if m_all:
            vals = []
            for ma in m_all:
                raw = ma.group(1).replace(' ', '').replace(',', '')
                try:
                    vals.append(int(raw))
                except ValueError:
                    pass
            if vals:
                aac_value_final = sorted(set(vals))
    
    aac_value_obj = {
        "status": "found" if aac_value_final else "not_found",
        "value": aac_value_final,
        "units": "cubic metres",
        "page_anchor": aac_page,
        "chunk_id": aac_chunk_id,
        "source_quote": aac_quote,
        "confidence": 1.0 if aac_value_final else 0.0
    }
