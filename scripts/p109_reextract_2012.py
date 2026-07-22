import requests, hashlib, json, ssl
from pathlib import Path
from pypdf import PdfReader
DOCS = [
    ("tsa23_2012_23tsdp12", "data_package", 2012, "https://www.for.gov.bc.ca/ftp/HTS/external/!publish/Timber_Supply_Review/TSA/100_Mile_House_23/TSR_2012/Data_Package/23tsdp12.pdf"),
    ("tsa23_2012_23ts13ra", "rationale", 2012, "https://www.for.gov.bc.ca/ftp/HTS/external/!publish/Timber_Supply_Review/TSA/100_Mile_House_23/TSR_2012/Rationale/23ts13ra.pdf"),
    ("tsa23_2012_23ts13pdp", "discussion_paper", 2012, "https://www.for.gov.bc.ca/ftp/HTS/external/!publish/Timber_Supply_Review/TSA/100_Mile_House_23/TSR_2012/PDP/23ts13pdp.pdf"),
]
BASE = Path(__file__).resolve().parent.parent
CACHE = BASE / "tmp" / "pdf_cache" / "2012"
CACHE.mkdir(parents=True, exist_ok=True)
for did, dtype, cyr, url in DOCS:
    pdf = CACHE / f"{did}.pdf"
    if not pdf.exists():
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        r = requests.get(url, verify=False, timeout=120); r.raise_for_status()
        pdf.write_bytes(r.content)
    h = hashlib.sha256(pdf.read_bytes()).hexdigest()
    rd = PdfReader(pdf); n = len(rd.pages)
    print(f"{did}: {n} pages")
    ed = BASE / "runtime" / "extracts" / "tsa23" / did; ed.mkdir(parents=True, exist_ok=True)
    ch = []; pg = 1; nc = 0
    while pg <= n:
        nc += 1; end = min(pg + 3, n)
        tx = "\n".join(rd.pages[i].extract_text() or "" for i in range(pg-1, end))
        (ed / f"chunk_{nc:02d}.txt").write_text(tx, "utf-8")
        ch.append({"chunk_id": f"{did}_c{nc:02d}", "page_start": pg, "page_end": end, "page_count": end-pg+1, "raw_text_path": f"runtime/extracts/tsa23/{did}/chunk_{nc:02d}.txt", "extraction_status": "extracted"})
        pg = end + 1
    bm = BASE / "benchmarks" / "document_library" / "tsa23_tsr" / did; bm.mkdir(parents=True, exist_ok=True)
    with open(bm / "chunk_manifest.json", "w") as f:
        json.dump({"document_id": did, "source_url": url, "source_sha256": h, "total_pages": n, "chunk_count": len(ch), "chunks": ch, "schema_version": 1}, f, indent=2)
    with open(bm / "provenance.json", "w") as f:
        json.dump({"document_id": did, "source_sha256": h, "total_pages": n}, f, indent=2)
    print(f"  {len(ch)} chunks written")
print("Done.")