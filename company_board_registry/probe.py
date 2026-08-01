#!/usr/bin/env python3
"""One-time ATS registry verification probe.

For each company we try a handful of slug candidates against Greenhouse,
Lever, and Ashby. A slug is only accepted if the live endpoint returns
valid, non-empty job data. Nothing is fabricated: unverified companies
land in the "needs manual check" bucket.
"""
import json, re, time, sys, urllib.request, urllib.error
from pathlib import Path

OUT = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

GH = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
LEVER = "https://api.lever.co/v0/postings/{slug}?mode=json"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
WORKABLE = "https://apply.workable.com/api/v3/accounts/{slug}/jobs"  # POST

def fetch(url, timeout=15, data=None):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    req = urllib.request.Request(url, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return None, str(e).encode()

def try_greenhouse(slug):
    st, body = fetch(GH.format(slug=slug))
    if st == 200:
        try:
            d = json.loads(body)
            jobs = d.get("jobs", [])
            if isinstance(jobs, list) and len(jobs) > 0:
                return {"count": len(jobs)}
        except Exception:
            pass
    return None

def try_lever(slug):
    st, body = fetch(LEVER.format(slug=slug))
    if st == 200:
        try:
            d = json.loads(body)
            if isinstance(d, list) and len(d) > 0:
                return {"count": len(d)}
        except Exception:
            pass
    return None

def try_ashby(slug):
    st, body = fetch(ASHBY.format(slug=slug))
    if st == 200:
        try:
            d = json.loads(body)
            jobs = d.get("jobs", [])
            if isinstance(jobs, list) and len(jobs) > 0:
                return {"count": len(jobs)}
        except Exception:
            pass
    return None

def try_workable(slug):
    # v3 listing endpoint is a POST with an (empty) filter body; requires total > 0
    st, body = fetch(WORKABLE.format(slug=slug),
                     data={"query": "", "location": [], "department": [], "worktype": [], "remote": []})
    if st == 200:
        try:
            d = json.loads(body)
            results = d.get("results", [])
            if isinstance(results, list) and len(results) > 0:
                return {"count": d.get("total", len(results))}
        except Exception:
            pass
    return None

PROBERS = [("greenhouse", try_greenhouse, GH), ("lever", try_lever, LEVER),
           ("ashby", try_ashby, ASHBY), ("workable", try_workable, WORKABLE)]

def gen_slugs(name, extra):
    base = name.lower()
    base = re.sub(r"\b(inc|ltd|limited|pvt|private|technologies|technology|labs|software|the)\b", "", base)
    cleaned = re.sub(r"[^a-z0-9]+", "", base)
    dash = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    cands = []
    for c in extra + [cleaned, dash, re.sub(r"[^a-z0-9]+","", name.lower())]:
        if c and c not in cands:
            cands.append(c)
    return cands

def main():
    companies = json.loads((OUT / "companies.json").read_text())
    verified = []
    failed = []
    for i, entry in enumerate(companies):
        name = entry["name"]
        extra = entry.get("slugs", [])
        found = None
        for slug in gen_slugs(name, extra):
            for ats, prober, tmpl in PROBERS:
                res = prober(slug)
                time.sleep(0.4)  # be polite; Lever asks 1s but we interleave hosts
                if res:
                    found = {"name": name, "ats": ats, "slug": slug,
                             "endpoint": tmpl.format(slug=slug).split("?")[0],
                             "open_roles": res["count"]}
                    break
            if found:
                break
        if found:
            verified.append(found)
            print(f"[OK ] {name:28s} {found['ats']:10s} {found['slug']:24s} {found['open_roles']} roles", flush=True)
        else:
            failed.append(name)
            print(f"[MISS] {name}", flush=True)
    (OUT / "verified.json").write_text(json.dumps(verified, indent=2))
    (OUT / "failed.json").write_text(json.dumps(failed, indent=2))
    print(f"\nVERIFIED={len(verified)} FAILED={len(failed)}")

if __name__ == "__main__":
    main()
