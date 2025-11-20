import os
import smtplib
import json
from email.message import EmailMessage
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
# Allow overriding storage dir through environment for tests or custom mounting
STORAGE_DIR = os.getenv('NOTIFICATIONS_STORAGE_DIR', os.path.join(BASE_DIR, 'notifications'))
os.makedirs(STORAGE_DIR, exist_ok=True)

def _meta_path(nid):
    return os.path.join(STORAGE_DIR, f"{nid}.meta.json")

def read_meta(nid):
    p = _meta_path(nid)
    if not os.path.exists(p):
        return None
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_meta(nid, meta):
    with open(_meta_path(nid), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, default=str)


def send_email(nid, payload):
    """Send an email synchronously using SMTP configured via env vars.

    Uses: NOTIFICATIONS_SMTP_HOST, NOTIFICATIONS_SMTP_PORT, NOTIFICATIONS_SMTP_USER, NOTIFICATIONS_SMTP_PASS, NOTIFICATIONS_FROM
    """
    meta = read_meta(nid) or {}
    meta.setdefault('attempts', 0)
    meta['attempts'] += 1
    write_meta(nid, meta)

    smtp_host = os.getenv('NOTIFICATIONS_SMTP_HOST')
    smtp_port = int(os.getenv('NOTIFICATIONS_SMTP_PORT', 25))
    smtp_user = os.getenv('NOTIFICATIONS_SMTP_USER')
    smtp_pass = os.getenv('NOTIFICATIONS_SMTP_PASS')
    mail_from = os.getenv('NOTIFICATIONS_FROM', smtp_user or 'no-reply@example.com')

    to = payload.get('to')
    subject = payload.get('subject', '(no subject)')
    body = payload.get('body', '')

    if not smtp_host or not to:
        meta['status'] = 'failed'
        meta['error'] = 'smtp_host_or_to_missing'
        write_meta(nid, meta)
        raise RuntimeError('SMTP host or to address missing')

    msg = EmailMessage()
    msg['From'] = mail_from
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)

    # Try SMTP
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as s:
            s.ehlo()
            if smtp_user and smtp_pass:
                s.starttls()
                s.login(smtp_user, smtp_pass)
            s.send_message(msg)

        meta['status'] = 'sent'
        meta['sent_at'] = datetime.utcnow().isoformat() + 'Z'
        write_meta(nid, meta)
        return True
    except Exception as e:
        meta['status'] = 'failed'
        meta['error'] = str(e)
        write_meta(nid, meta)
        raise


# Optional Celery integration: if a broker is configured and celery is installed,
# a Celery app can import this module and the send_email_async task will be defined.
try:
    from celery import Celery
    broker = os.getenv('CELERY_BROKER_URL') or os.getenv('REDIS_BROKER_URL') or os.getenv('REDIS_URL')
    if broker:
        celery = Celery('notificaciones', broker=broker)

        @celery.task(name='notificaciones.send_email_async')
        def send_email_async(nid, payload):
            return send_email(nid, payload)
    else:
        send_email_async = None
except Exception:
    send_email_async = None
