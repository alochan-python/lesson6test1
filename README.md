# BMI計算機（標準ライブラリのみ）

`wsgiref` を使った、標準ライブラリのみで動く最小の Python Web アプリです。  
ローカルでも Render でも、同じ `app.py` をそのまま使えます。

## ファイル構成

- `app.py` : アプリ本体
- `requirements.txt` : 空ファイルでも可
- `.gitignore`
- `README.md`

## ローカル実行

Python 3 が入っている前提です。

```bash
python app.py