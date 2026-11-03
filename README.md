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
