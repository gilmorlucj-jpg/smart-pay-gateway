import uuid
import urllib.parse
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="SmartLotto Pay Gateway")

payments_db = {}

class CreatePaymentRequest(BaseModel):
    qr_text: str

@app.post("/api/create-payment")
def create_payment(data: CreatePaymentRequest):
    raw_text = data.qr_text
    if not raw_text.startswith("ST000"):
        raise HTTPException(status_code=400, detail="Неверный формат строки. Ожидается ST000...")

    payment_id = str(uuid.uuid4())[:8]
    payments_db[payment_id] = raw_text
    
    return {
        "payment_id": payment_id,
        "pay_url": f"https://pay.smartlotto.tech/pay/{payment_id}"
    }

@app.get("/pay/{payment_id}", response_class=HTMLResponse)
def render_pay_page(payment_id: str):
    raw_text = payments_db.get(payment_id)
    if not raw_text:
        return HTMLResponse(content="<h2 style='text-align:center;margin-top:50px;color:white;'>Ошибка: Платеж не найден</h2>", status_code=404)

    # Правильное кодирование под Альфа-Банк
    encoded_gost = urllib.parse.quote(raw_text)
    alfa_deeplink = f"alfabank://pay?qr={encoded_gost}"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SmartLotto Pay — Оплата</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #0f172a;
                color: #fff;
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 90vh;
            }}
            .card {{
                background: #1e293b;
                padding: 28px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 360px;
                text-align: center;
                border: 1px solid #334155;
            }}
            h2 {{ margin-top: 0; font-size: 22px; color: #f8fafc; }}
            p {{ color: #94a3b8; font-size: 14px; margin-bottom: 24px; }}
            .btn {{
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                padding: 16px 0;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 600;
                font-size: 16px;
                color: white;
                background-color: #ef3124; /* Фирменный красный Альфы */
                box-sizing: border-box;
                margin-bottom: 12px;
                cursor: pointer;
                border: none;
            }}
            .btn:active {{ transform: scale(0.98); }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>SmartLotto Pay</h2>
            <p>Нажмите кнопку для оплаты через Альфа-Банк:</p>
            
            <a href="{alfa_deeplink}" class="btn">Открыть Альфа-Банк</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
