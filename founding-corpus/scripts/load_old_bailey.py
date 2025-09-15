import argparse, time
from pathlib import Path
from _util import load_years, in_range, session, write_jsonl, clean_text_basic

API = "https://www.oldbaileyonline.org/obapi/ob?term0={year}&kwparse=and&count=500&start={start}"

def main(args):
    start,end = load_years(args.years)
    if not args.allow_nc: 
        print("Skipping Old Bailey (NC not allowed)." ); return
    s=session(); out=[]
    for year in range(1777, 1798):
        start_idx=0
        while True:
            url = API.format(year=year, start=start_idx)
            r = s.get(url, timeout=60)
            if r.status_code!=200: break
            js = r.json()
            trials = js.get("trials", [])
            if not trials: break
            for t in trials:
                d = t.get("trial_date") or f"{year}-01-01"
                if not in_range(d, start, end): continue
                txt = " ".join([seg.get("text","") for seg in t.get("body",[])])
                if txt.strip():
                    out.append({
                        "id": t.get("id"), "source":"old_bailey","date":d,
                        "license_tag":"CC-BY-NC",
                        "text": clean_text_basic(txt),
                        "meta":{"offence": t.get("offence_category")}
                    })
            start_idx += len(trials)
            if len(trials)<500: break
            time.sleep(0.2)
    Path(args.out).mkdir(parents=True, exist_ok=True)
    write_jsonl(Path(args.out)/"old_bailey_1777_1797.jsonl", out)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--years", required=True); p.add_argument("--out", required=True)
    p.add_argument("--allow-nc", action="store_true")
    args=p.parse_args(); main(args)
