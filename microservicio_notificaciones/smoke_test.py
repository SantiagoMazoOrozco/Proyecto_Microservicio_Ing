import requests
import os
import time

BASE = os.getenv('NOTIF_BASE', 'http://127.0.0.1:5003')

def main():
    print('Health check...')
    try:
        r = requests.get(BASE + '/health', timeout=3)
        print('health', r.status_code, r.text)
    except Exception as e:
        print('Health check failed:', e)
        return

    payload = {
        'type': 'email',
        'to': os.getenv('TEST_EMAIL', 'test@example.com'),
        'subject': 'Smoke test',
        'body': 'Mensaje de prueba desde smoke_test',
        'async': False
    }

    print('Posting notification...')
    try:
        r = requests.post(BASE + '/notifications', json=payload, timeout=10)
        print('POST /notifications ->', r.status_code, r.text)
    except Exception as e:
        print('POST failed:', e)
        return

    if r.status_code in (200, 202):
        nid = r.json().get('id')
        print('Created id=', nid)
        for i in range(10):
            s = requests.get(f"{BASE}/notifications/{nid}/status")
            print('status', s.status_code, s.text)
            time.sleep(1)

if __name__ == '__main__':
    main()
