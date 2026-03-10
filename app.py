import os
import html
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def judge_bmi(bmi):
    if bmi <= 0:
        return "", ""
    if bmi < 18.5:
        return "低体重", "🍃"
    if bmi < 25:
        return "標準", "✅"
    if bmi < 30:
        return "肥満（1度）", "⚠️"
    if bmi < 35:
        return "肥満（2度）", "🟠"
    if bmi < 40:
        return "肥満（3度）", "🔴"
    return "肥満（4度）", "🚨"


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    params = {}

    if method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            content_length = 0
        body = environ["wsgi.input"].read(content_length).decode("utf-8")
        params = parse_qs(body)
    else:
        params = parse_qs(environ.get("QUERY_STRING", ""))

    height_cm_raw = params.get("height_cm", [""])[0]
    weight_kg_raw = params.get("weight_kg", [""])[0]

    height_cm = to_float(height_cm_raw, 0.0)
    weight_kg = to_float(weight_kg_raw, 0.0)

    bmi_text = ""
    judge_text = ""
    judge_icon = ""
    message = "身長(cm) と体重(kg) を入力してください。"

    if height_cm > 0 and weight_kg > 0:
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m * height_m)
        bmi_text = f"{bmi:.2f}"
        judge_text, judge_icon = judge_bmi(bmi)
        message = "BMIを計算しました。"
    elif height_cm_raw or weight_kg_raw:
        message = "入力値が不正な場合は 0 として扱います。身長と体重が 0 より大きい値になるよう入力してください。"

    page = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <title>BMI計算機：Kazu</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", sans-serif;
            background: #f7f9fc;
            color: #222;
        }}
        .wrap {{
            max-width: 720px;
            margin: 40px auto;
            padding: 0 16px;
        }}
        .card {{
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
            padding: 24px;
        }}
        h1 {{
            margin: 0 0 8px;
            font-size: 28px;
        }}
        .desc {{
            margin: 0 0 24px;
            color: #555;
        }}
        .row {{
            margin-bottom: 16px;
        }}
        label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 700;
        }}
        input[type="number"] {{
            width: 100%;
            box-sizing: border-box;
            padding: 12px;
            border: 1px solid #cfd8e3;
            border-radius: 10px;
            font-size: 16px;
            background: #fff;
        }}
        .buttons {{
            display: flex;
            gap: 12px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        button {{
            border: none;
            border-radius: 10px;
            padding: 12px 18px;
            font-size: 16px;
            cursor: pointer;
        }}
        .calc {{
            background: #2563eb;
            color: #fff;
        }}
        .clear {{
            background: #e5e7eb;
            color: #222;
        }}
        .result {{
            margin-top: 24px;
            padding: 18px;
            border-radius: 12px;
            background: #f3f6fb;
        }}
        .result-item {{
            margin: 8px 0;
            font-size: 18px;
        }}
        .note {{
            margin-top: 12px;
            color: #555;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 16px;
            color: #666;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="wrap">
        <div class="card">
            <h1>BMI計算機：Kazu</h1>
            <p class="desc">身長と体重を入力すると、BMIと評価を表示します。</p>

            <form method="post" action="/">
                <div class="row">
                    <label for="height_cm">身長 (cm)</label>
                    <input
                        id="height_cm"
                        name="height_cm"
                        type="number"
                        inputmode="decimal"
                        step="any"
                        min="0"
                        placeholder="例: 170"
                        value="{html.escape(height_cm_raw)}"
                    >
                </div>

                <div class="row">
                    <label for="weight_kg">体重 (kg)</label>
                    <input
                        id="weight_kg"
                        name="weight_kg"
                        type="number"
                        inputmode="decimal"
                        step="any"
                        min="0"
                        placeholder="例: 65"
                        value="{html.escape(weight_kg_raw)}"
                    >
                </div>

                <div class="buttons">
                    <button type="submit" class="calc">計算する</button>
                    <button type="reset" class="clear">クリア</button>
                </div>
            </form>

            <div class="result">
                <div class="result-item"><strong>状態:</strong> {html.escape(message)}</div>
                <div class="result-item"><strong>BMI:</strong> {html.escape(bmi_text) if bmi_text else "-"}</div>
                <div class="result-item"><strong>評価:</strong> {html.escape(judge_icon)} {html.escape(judge_text) if judge_text else "-"}</div>
                <div class="note">BMI = 体重(kg) ÷ 身長(m) ÷ 身長(m)</div>
            </div>

            <div class="footer">標準ライブラリのみ / app.py 1ファイル構成 / Render対応</div>
        </div>
    </div>
</body>
</html>
"""

    body = page.encode("utf-8")
    start_response(
        "200 OK",
        [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    print(f"Starting server on http://localhost:{port}")
    with make_server(host, port, application) as server:
        server.serve_forever()