---
title: OCR for lecture scans
type: playbook
status: current
updated: 2026-10-30
runs: 4
last_run: 2026-10-30
---
# OCR for lecture scans
> Turns scanned lecture PDFs into searchable text.

## Steps
1. **Deskew the scan** — `unpaper in.pdf out.pdf`. Done when: pages are upright.
2. **Run OCR** — `ocrmypdf --language deu+eng out.pdf final.pdf`. Done when: `final.pdf` is searchable.

## Gotchas
- **Garbled umlauts** — wrong language pack; fix: install `tesseract-ocr-deu`.
