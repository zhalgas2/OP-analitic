import os
import time
import json
import base64
import requests
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6IMRm-4XobyP1JW309UYhgcMliLZNmrAeGAK84Sd7vSsw")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8824137911:AAEUUH7Sw7KFmaur1k4MLdoRp4k2sGVeyE4")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "595643168")

PROCESSED_CALLS = set()

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code != 200:
            payload.pop("parse_mode", None)
            requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram қатесі: {e}")

@app.get("/")
@app.get("/sipuni-webhook")
@app.post("/sipuni-webhook")
@app.get("/webhook")
@app.post("/webhook")
async def sipuni_webhook(request: Request):
    data = {}
    if request.query_params:
        data.update(dict(request.query_params))

    try:
        json_data = await request.json()
        if isinstance(json_data, dict):
            data.update(json_data)
    except Exception:
        pass

    try:
        form_data = await request.form()
        if form_data:
            data.update(dict(form_data))
    except Exception:
        pass

    if not data:
        return {"status": "ok"}

    call_id = str(data.get("call_id", ""))
    if not call_id:
        return {"status": "ignored"}

    if call_id in PROCESSED_CALLS:
        return {"status": "already_processed"}

    event = str(data.get("event", ""))
    if event == "1":
        return {"status": "ignored", "reason": "Started"}

    status = str(data.get("status", "")).upper()
    if status in ["NOANSWER", "BUSY", "CANCEL", "FAILED"]:
        return {"status": "ignored", "reason": status}

    duration = 0
    if data.get("duration"):
        duration = int(data.get("duration") or 0)
    elif data.get("call_answer_timestamp") and data.get("timestamp"):
        try:
            duration = int(data["timestamp"]) - int(data["call_answer_timestamp"])
        except Exception:
            duration = 0
    elif data.get("call_start_timestamp") and data.get("timestamp"):
        try:
            duration = int(data["timestamp"]) - int(data["call_start_timestamp"])
        except Exception:
            duration = 0

    if duration < 40:
        return {"status": "ignored", "reason": f"Short ({duration}s)"}

    record_url = data.get("call_record_link") or data.get("record_url") or data.get("link")
    if not record_url:
        return {"status": "error", "reason": "No audio URL"}

    PROCESSED_CALLS.add(call_id)
    if len(PROCESSED_CALLS) > 1000:
        PROCESSED_CALLS.clear()

    print(f"🔄 ОКК аудиті: {call_id} ({duration} сек)...")

    try:
        audio_content = None
        for _ in range(4):
            try:
                res = requests.get(record_url, timeout=60)
                if res.status_code == 200 and len(res.content) > 5000:
                    audio_content = res.content
                    break
            except Exception:
                pass
            time.sleep(3)

        if not audio_content:
            return {"status": "error", "reason": "Download failed"}

        manager_num = str(data.get("short_src_num") or data.get("src_num") or "Белгісіз")
        client_num = str(data.get("dst_num") or data.get("pbxdstnum") or "Белгісіз")

        prompt = """# РӨЛ
Сен — B2C/B2B сату бөлімінің сапа бақылау бөлімінің (ОКК) аға аудиторысың. Қоңырау аудиосын тыңдап, ЕКІ бөлек баға бересің: (1) МЕНЕДЖЕРГЕ, (2) ЛИДКЕ.

Шығарылатын JSON схемасы:
{
  "is_valid_conversation": true,
  "manager_name": "Аты немесе Аталмады",
  "client_name": "Аты немесе Аталмады",
  "call_summary": "Сөйлесудің нақты мазмұны мен мәні туралы 2-3 сөйлемдік толық саммари",
  "call_outcome": "Қоңырау немен шешілді: нақты келісілген қадам, күні-уақыты, төлем, немесе нақты бас тарту себебі",
  "talk_ratio": {"manager_percent": 45, "client_percent": 55},
  "manager_assessment": {
    "total_score": 60,
    "grade": "норма, нүктелік түзету қажет",
    "critical_violation": false,
    "penalties_applied": ["келесі қадам бекітілмеді (-15)"],
    "scores": {
      "contact": 7, "dialog_control": 6, "need_discovery": 5,
      "qualification_bant": 4, "presentation": 6, "objections": 5,
      "closing_next_step": 3, "speech_tone": 8
    },
    "critical_errors": [
      {
        "error_name": "Қатенің нақты аты",
        "quote": "Менеджер немесе клиент айтқан нақты сөз",
        "why_bad": "Бұл неліктен қате, сатылымға қалай зиян тигізді",
        "how_to_fix": "Осы сәтте менеджер қалай айтуы керек еді"
      }
    ],
    "recommendation_script": "Менеджерге келесі қоңырауға арналған 1 дайын сөз"
  },
  "lead_assessment": {
    "category": "B (Warm)",
    "total_score": 65,
    "summary": "Лидке қысқаша мінездеме",
    "loss_attribution": "manager"
  }
}
"""

        audio_b64 = base64.b64encode(audio_content).decode("utf-8")
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "audio/mp3", "data": audio_b64}}
                ]
            }],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        resp = requests.post(api_url, json=payload, timeout=120)
        resp_json = resp.json()

        if "candidates" not in resp_json:
            return {"status": "error", "message": "Gemini error"}

        text_content = resp_json["candidates"][0]["content"]["parts"][0]["text"]
        res_json = json.loads(text_content.strip())

        if not res_json.get("is_valid_conversation", True):
            return {"status": "ignored"}

        mgr = res_json.get("manager_assessment", {})
        lead = res_json.get("lead_assessment", {})
        talk = res_json.get("talk_ratio", {})
        scores = mgr.get("scores", {})

        m_name = str(res_json.get("manager_name") or "Аталмады")
        c_name = str(res_json.get("client_name") or "Аталмады")
        summary = str(res_json.get("call_summary") or "Анықталмады")
        outcome = str(res_json.get("call_outcome") or "Анықталмады")

        errors_parts = []
        for i, err in enumerate(mgr.get("critical_errors", [])[:4], 1):
            part = (
                f"<b>{i}. {err.get('error_name', '')}</b>\n"
                f"   💬 <i>«{err.get('quote', '')}»</i>\n"
                f"   ❌ <b>Неге қате:</b> {err.get('why_bad', '')}\n"
                f"   ✅ <b>Дұрысы:</b> {err.get('how_to_fix', '')}\n"
            )
            errors_parts.append(part)

        errors_html = "\n".join(errors_parts) or "Өрескел қателер табылмады.\n"
        penalties = ", ".join(mgr.get("penalties_applied", [])) or "Жоқ"
        m_crit = "⚠️ ИӘ" if mgr.get("critical_violation") else "Жоқ"

        report_lines = [
            f"📋 <b>ОКК АУДИТІ ({duration} сек)</b>\n",
            f"👤 <b>Менеджер:</b> {m_name} ({manager_num})",
            f"📱 <b>Клиент:</b> {c_name} (+{client_num.lstrip('+')})",
            f"🗣 <b>Talk Ratio:</b> Менеджер {talk.get('manager_percent', 0)}% / Клиент {talk.get('client_percent', 0)}%\n",
            f"📝 <b>САММАРИ (ҚОҢЫРАУ МӘНІ):</b>\n{summary}\n",
            f"🎯 <b>НЕМЕН ШЕШІЛДІ (НӘТИЖЕ):</b>\n<b>{outcome}</b>\n",
            f"📊 <b>МЕНЕДЖЕР БАҒАСЫ: {mgr.get('total_score', 0)}/100</b> ({mgr.get('grade', '')})",
            f"• Контакт: {scores.get('contact', '-')}/10 | Басқару: {scores.get('dialog_control', '-')}/10",
            f"• Қажеттілік: {scores.get('need_discovery', '-')}/10 | BANT: {scores.get('qualification_bant', '-')}/10",
            f"• Презентация: {scores.get('presentation', '-')}/10 | Қарсылық: {scores.get('objections', '-')}/10",
            f"• Жабу/Қадам: {scores.get('closing_next_step', '-')}/10 | Тон: {scores.get('speech_tone', '-')}/10",
            f"🔻 Штрафтар: {penalties} | Критикалық қате: {m_crit}\n",
            f"🔥 <b>ЛИД КВАЛИФИКАЦИЯСЫ: {lead.get('category', '-')} ({lead.get('total_score', 0)} балл)</b>",
            f"📌 {lead.get('summary', '')}\n",
            f"⚠️ <b>МЕНЕДЖЕРДІҢ НАҚТЫ ҚАТЕЛІКТЕРІ:</b>\n\n{errors_html}\n",
            f"💡 <b>РОП СКРИПТІ:</b>\n«{mgr.get('recommendation_script', '')}»"
        ]
        report = "\n".join(report_lines)
        send_telegram(report)
        print(f"✅ ОКК есебі ({call_id}) Telegram-ға жіберілді!")

    except Exception as e:
        print(f"Қате: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
