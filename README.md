# tenko-forms

遠隔点呼・自動点呼 (業務前・業務後) の届出と、自動点呼機器の認定申請に使う様式の原本を、取得した日付付きで保存する repo です。alc-app のシステム管理者画面から、ここの最新版の様式に値を差し込んで出力します。

## 中身

| パス | 内容 |
| --- | --- |
| `catalog.json` | 取り込む様式の一覧 (id・分類・名前・取得元 URL) |
| `forms/<id>/<YYYY-MM-DD>.<拡張子>` | 様式の原本。内容が変わったときだけ、その日付のファイルが増える |
| `manifest.json` | 様式ごとの版の記録 (日付・ファイル・sha256・取得元 URL)。`latest` が最新版 |
| `scripts/fetch.py` | 取り直しのスクリプト (標準ライブラリだけ) |

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
