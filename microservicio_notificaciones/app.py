import os
import uuid
import json
from flask import Flask, request, jsonify
from datetime import datetime

# import tasks from package to avoid ambiguity when used as a package
try:
    from . import tasks
except Exception:
    # fallback to top-level import if package import fails
    try:
        import tasks
    except Exception:
        tasks = None

BASE_DIR = os.path.dirname(__file__)
# Allow overriding storage dir via env var (useful in docker/tests)
STORAGE_DIR = os.getenv('NOTIFICATIONS_STORAGE_DIR', os.path.join(BASE_DIR, 'notifications'))
os.makedirs(STORAGE_DIR, exist_ok=True)

app = Flask(__name__)

def _meta_path(nid):
    return os.path.join(STORAGE_DIR, f"{nid}.meta.json")

def write_meta(nid, meta):
    with open(_meta_path(nid), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, default=str)

def read_meta(nid):
    p = _meta_path(nid)
    if not os.path.exists(p):
        return None
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'notificaciones'}), 200


@app.route('/notifications', methods=['POST'])
def create_notification():
    """Create and optionally send a notification.

    Expected JSON: {
      "type": "email",
      "to": "user@example.com",
      "subject": "...",
      "body": "...",
      "async": true|false
    }
    """
    payload = request.get_json(force=True)
    if not payload:
        return jsonify({'error': 'invalid json'}), 400

    ntype = payload.get('type', 'email')
    nid = str(uuid.uuid4())
    meta = {
        'id': nid,
        'type': ntype,
        'payload': payload,
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    write_meta(nid, meta)

    async_flag = bool(payload.get('async', True))

    if ntype == 'email':
        # Prefer Celery async task if available and async_flag True
        # Prefer Celery async task if available
        send_email_async = getattr(tasks, 'send_email_async', None) if tasks else None
        send_email_fn = getattr(tasks, 'send_email', None) if tasks else None

        if async_flag and send_email_async:
            try:
                send_email_async.delay(nid, payload)
                meta['status'] = 'queued'
                write_meta(nid, meta)
                return jsonify({'id': nid, 'status': 'queued'}), 202
            except Exception as e:
                meta['status'] = 'queue_failed'
                meta['error'] = str(e)
                write_meta(nid, meta)
                # fallthrough to sync

        # Fallback: attempt synchronous send
        try:
            if send_email_fn:
                send_email_fn(nid, payload)
                meta['status'] = 'sent'
                meta['sent_at'] = datetime.utcnow().isoformat() + 'Z'
                write_meta(nid, meta)
                return jsonify({'id': nid, 'status': 'sent'}), 200
            else:
                meta['status'] = 'no_sender'
                write_meta(nid, meta)
                return jsonify({'id': nid, 'status': 'no_sender', 'note': 'no send_email available'}), 500
        except Exception as e:
            meta['status'] = 'failed'
            meta['error'] = str(e)
            write_meta(nid, meta)
            return jsonify({'id': nid, 'status': 'failed', 'error': str(e)}), 500

    else:
        meta['status'] = 'unsupported_type'
        write_meta(nid, meta)
        return jsonify({'id': nid, 'status': 'unsupported_type'}), 400


@app.route('/notifications/<nid>/status', methods=['GET'])
def get_status(nid):
    meta = read_meta(nid)
    if not meta:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'id': nid, 'meta': meta}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5003)))
