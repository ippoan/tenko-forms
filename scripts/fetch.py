#!/usr/bin/env python3
"""catalog.json の様式を取り直し、内容が変わったものだけ日付付きで保存する。

保存先は forms/<id>/<YYYY-MM-DD>.<拡張子>、版の記録は manifest.json。
同じ内容 (sha256 が同じ) なら何もしない。国交省は様式を差し替えるとき
URL (content の番号) ごと変えることがあるので、取れなかった様式は最後に
まとめて報告して exit 1 にする (catalog.json の url を新しいものに直す合図)。

  python3 scripts/fetch.py                 # url のある様式を全部取り直す
  python3 scripts/fetch.py --add <id> <f>  # url の無い様式 (e-Gov の参考様式など) を手で取り込む

標準ライブラリだけで動く。
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"
MANIFEST = ROOT / "manifest.json"
FORMS = ROOT / "forms"
JST = datetime.timezone(datetime.timedelta(hours=9))
# 既定の User-Agent だと弾かれる配信元があるため、ブラウザを名乗る
USER_AGENT = "Mozilla/5.0 (compatible; tenko-forms-fetch; +https://github.com/ippoan/tenko-forms)"


def load_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as res:
        body = res.read()
        ctype = res.headers.get("Content-Type", "")
    # 様式が消えたとき、配信元は 200 で HTML の案内ページを返すことがある
    if ctype.startswith("text/html"):
        raise ValueError(f"HTML が返った (Content-Type: {ctype})")
    return body


def ext_of(name):
    suffix = pathlib.PurePosixPath(name).suffix.lower()
    return suffix if suffix else ".bin"


def record(manifest, form, body, ext, date, url):
    """内容が前の版と違えば保存して True を返す。"""
    sha = hashlib.sha256(body).hexdigest()
    entry = manifest["forms"].setdefault(form["id"], {"versions": []})
    entry["title"] = form["title"]
    entry["group"] = form["group"]
    versions = entry["versions"]
    if versions and versions[-1]["sha256"] == sha:
        return False
    # 同じ日に 2 回変わったら、その日の版を置き換える (1 日 1 版)
    if versions and versions[-1]["date"] == date:
        (ROOT / versions[-1]["file"]).unlink(missing_ok=True)
        versions.pop()
    rel = pathlib.PurePosixPath("forms", form["id"], f"{date}{ext}")
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    versions.append({"date": date, "file": str(rel), "sha256": sha, "size": len(body), "url": url})
    entry["latest"] = str(rel)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--add", nargs=2, metavar=("ID", "FILE"), help="url の無い様式を手で取り込む")
    parser.add_argument("--date", help="保存する日付 (既定は今日の JST)")
    args = parser.parse_args()

    date = args.date or datetime.datetime.now(JST).date().isoformat()
    catalog = {f["id"]: f for f in load_json(CATALOG, {"forms": []})["forms"]}
    manifest = load_json(MANIFEST, {"forms": {}})
    changed, failed = [], []

    if args.add:
        form_id, file = args.add
        if form_id not in catalog:
            sys.exit(f"catalog.json に {form_id} が無い")
        body = pathlib.Path(file).read_bytes()
        if record(manifest, catalog[form_id], body, ext_of(file), date, catalog[form_id].get("url")):
            changed.append(form_id)
    else:
        for form in catalog.values():
            url = form.get("url")
            if not url:
                continue
            try:
                body = download(url)
            except Exception as e:  # noqa: BLE001 — 1 件の失敗で他を止めない
                failed.append(f"{form['id']}: {url}: {e}")
                continue
            if record(manifest, form, body, ext_of(url), date, url):
                changed.append(form["id"])

    manifest["forms"] = dict(sorted(manifest["forms"].items()))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [f"- 更新: {i}" for i in changed] + [f"- 取得失敗: {f}" for f in failed]
    report = "\n".join(lines) if lines else "- 変更なし"
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(f"## 様式の取り直し ({date})\n\n{report}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
