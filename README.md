# tenko-forms

遠隔点呼・自動点呼 (業務前・業務後) の届出と、自動点呼機器の認定申請に使う様式の原本を、取得した日付付きで保存する repo です。alc-app のシステム管理者画面から、ここの最新版の様式に値を差し込んで出力します。

## 中身

| パス | 内容 |
| --- | --- |
| `catalog.json` | 取り込む様式の一覧 (id・分類・名前・取得元 URL) |
| `forms/<id>/<YYYY-MM-DD>.<拡張子>` | 様式の原本。内容が変わったときだけ、その日付のファイルが増える |
| `manifest.json` | 様式ごとの版の記録 (日付・ファイル・sha256・取得元 URL)。`latest` が最新版 |
| `scripts/fetch.py` | 取り直しのスクリプト (標準ライブラリだけ) |
| `product/ippoan-tenko.json` | 一歩庵点呼 (自動点呼機器) の製品の設定。名称と版・認定番号・版の履歴・自己チェック表の答え |
| `product/photos/` | 認定申請の添付資料の外観図に使う実機の写真と、その一覧 `index.json` |
| `product/figures/` | 添付資料の構造図 (`structure.html`)・システム図 (`system.html`) |

取得元は国土交通省の[点呼の在り方について](https://www.mlit.go.jp/jidosha/jidosha_tk2_000082.html)と[自動車運送事業のオンライン申請](https://www.mlit.go.jp/jidosha/jidosha_tk3_000132.html)です。e-Gov の参考様式 (`egov-tenko-todokede-sankou`) は e-Gov 電子申請の手続のページからしか取れないので、手で取り込みます。

## 更新

`.github/workflows/fetch.yml` が毎週月曜 09:00 (JST) に取り直します。内容が変わった様式があれば、日付付きのファイルを足した PR を作ります。取れなかった様式があると job が落ちます。国交省が様式を差し替えるときは URL も変わるので、ページから新しい URL を引いて `catalog.json` を直してください。

手元で回すとき:

```bash
python3 scripts/fetch.py
```

URL の無い様式を手で取り込むとき:

```bash
python3 scripts/fetch.py --add egov-tenko-todokede-sankou ~/Downloads/a15596A069500001.xlsx
```

様式を足すときは `catalog.json` に 1 行足してから `fetch.py` を回します。

## 製品の設定 (`product/ippoan-tenko.json`)

一歩庵点呼の認定申請 (auth.ippoan.org の開発者専用ページ) と、alc-app の点呼の届出 (使用する機器の名称の既定) が読みます。機器の名称は `product` と `version` をつないだもの (例 `一歩庵点呼 v1`) です。

| 欄 | 内容 |
| --- | --- |
| `version` | 製品番号の版。上げると両方の画面の名称が切り替わる |
| `product_url` | 機器の概要が載ったウェブサイトの URL (様式2。国交省のウェブサイトに載る)。いまは GitHub Pages の操作マニュアル |
| `certification.pre` / `.post` | 国交省の認定番号 (業務前・業務後)。認定が出たら入れる |
| `history` | 版の履歴 (新しい順)。`summary` = 変更の内容及び理由、`date` = 変更の時期 (YYYY-MM-DD)、`impact` = 要件への影響。先頭と 2 件目から様式5 (仕様変更申請書) を作る |
| `self_check.pre` / `.post` | 様式3-1・3-2 の要件ごとの答え。key は項目 (`一`〜`二十三`・`ア`〜`エ`)、値は `{"ok": "適", "detail": "…", "evidence": "…"}`。`evidence` は「資料番号①」の後ろに足す文 |
| `discontinue` | 様式7 (認定廃止届出書) の廃止時期と理由 |

版を上げる手順: 様式5 の仕様変更申請を先に出して承認を受けてから、`version` を変え、`history` の先頭に 1 件足す。

```json
"history": [
  { "version": "v2", "date": "2027-04-01", "summary": "…を変更する。理由は…", "impact": "なし" },
  { "version": "v1", "date": null, "summary": "初版", "impact": null }
]
```

## 認定申請の添付資料 (`product/photos/`・`product/figures/`)

様式2 の注 2「外観図、構造図、システム図を示した資料」です。auth.ippoan.org の認定申請ページの「添付資料」が、ここから読んで A4 横の 3 ページ (外観図・構造図・システム図) に組みます。ブラウザの印刷で PDF に保存して添付します。

### 写真 (外観図)

写真は `product/photos/<YYYY-MM-DD>-<何を写したか>.<jpg|png|webp>` に置き、`index.json` に 1 件足します。並び順は一覧の順です。

```json
{
  "photos": [
    { "file": "2026-11-10-tenko-set.jpg", "caption": "点呼端末一式 (正面)", "date": "2026-11-10" },
    { "file": "2026-11-10-cores3.jpg", "caption": "制御装置 (CoreS3)", "date": "2026-11-10" }
  ]
}
```

- `file` は英数字・`-`・`_`・`.` だけ (ほかの文字の名前は読まない)。`caption` は写真の見出しとして出す
- 写真を撮り直したら、古いファイルは消さずに新しい日付で足し、一覧の `file` を差し替える (manifest.json と同じ考え方)
- **public repo です。営業所の中・人の顔や体・車両のナンバー・画面に出た氏名などが写らないように撮ってください。** 機器だけを無地の背景で撮るのが確実です。写真の位置情報 (Exif の GPS) も消してから置いてください
- 一覧が空のあいだは、外観図のページに「写真未登録」と出ます

### 構造図・システム図

`structure.html`・`system.html` は 1 ページぶんの HTML の部品 (見出し `h1`・補足 `.sub`・インライン SVG・注記 `.note`) です。差し替えるときはファイルごと書き換えます。`{機器の名称}` は版の付いた名称 (例 `一歩庵点呼 v1`)、`{製作事業者名}` は認定申請ページに保存した申請者の名称に置き換わります (申請者の名称・住所はここに書かない)。script は動きません。
