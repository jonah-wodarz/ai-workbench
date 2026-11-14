#!/usr/bin/env python3
"""Convert a semicolon-separated CSV export to a Markdown table.

Usage: convert.py INPUT [--encoding ENC]
"""
import argparse
import csv
import os
import sys

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("--encoding", default="utf-8")
args = ap.parse_args()

out_dir = os.environ["OUT_DIR"]
if not os.path.isdir(out_dir):
    sys.exit(f"output directory {out_dir} does not exist")

with open(args.input, encoding=args.encoding, newline="") as f:
    rows = list(csv.reader(f, delimiter=";"))

lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])]
lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
stem = os.path.splitext(os.path.basename(args.input))[0]
path = os.path.join(out_dir, stem + ".md")
with open(path, "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
print("wrote", path)
