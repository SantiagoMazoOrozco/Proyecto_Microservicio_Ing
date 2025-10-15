import os
import json
import logging
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)

# Logging to file
log_file = os.getenv('NOTIFICATIONS_LOG', 'notifications.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', filename=log_file)
logger = logging.getLogger('notifications')


def send_email(recipient: str, subject: str, body: str) -> bool:
	"""Attempt to send a simple email using SMTP settings from env.
	If MAIL_HOST is not set, the function will return False (no-op).
	"""
	mail_host = os.getenv('MAIL_HOST')
	if not mail_host:
		return False

	mail_port = int(os.getenv('MAIL_PORT') or 25)
	username = os.getenv('MAIL_USERNAME')
	password = os.getenv('MAIL_PASSWORD')
	use_tls = os.getenv('MAIL_USE_TLS', 'true').lower() in ['1', 'true', 'yes']

	msg = EmailMessage()
	msg['Subject'] = subject
	msg['From'] = os.getenv('MAIL_FROM', username or 'no-reply@example.com')
	msg['To'] = recipient
	msg.set_content(body)

	try:
		if use_tls:
			server = smtplib.SMTP(mail_host, mail_port, timeout=10)
			server.starttls()
		else:
			server = smtplib.SMTP(mail_host, mail_port, timeout=10)
		if username and password:
			server.login(username, password)
		server.send_message(msg)
		server.quit()
		return True
	except Exception as e:
		logger.exception('Failed to send email to %s: %s', recipient, e)
		return False


@app.route('/notify', methods=['POST'])
def notify():
	"""Accepts JSON payload to create/send a notification.

	Expected JSON:
	{
	  "title": "...",
	  "body": "...",
	  "recipients": ["email1@example.com", "email2@example.com"]
	}
	"""
	data = None
	if request.is_json:
		data = request.get_json()
	else:
		# try form data
		try:
			data = {**request.form}
		except Exception:
			data = {}

	title = data.get('title')
	body = data.get('body')
	recipients = data.get('recipients') or data.get('recipient')

	# normalize recipients: allow comma-separated string
	if isinstance(recipients, str):
		# allow JSON array string or comma-separated
		try:
			parsed = json.loads(recipients)
			if isinstance(parsed, list):
				recipients = parsed
		except Exception:
			recipients = [r.strip() for r in recipients.split(',') if r.strip()]

	if recipients is None:
		recipients = []

	if not title or not body:
		return jsonify({"success": False, "error": "Missing 'title' or 'body'"}), 400

	record = {
		"title": title,
		"body": body,
		"recipients": recipients,
		"status": "queued"
	}

	# Log the notification (appends to configured log file)
	logger.info('Notification queued: %s', json.dumps(record, ensure_ascii=False))

	# Try to send emails if recipients provided and SMTP configured
	send_results = []
	for r in recipients:
		sent = send_email(r, title, body)
		send_results.append({"recipient": r, "sent": sent})

	if recipients:
		record['status'] = 'sent' if all(s['sent'] for s in send_results) else 'partial' if any(s['sent'] for s in send_results) else 'failed'
		record['send_results'] = send_results
		logger.info('Notification send_results: %s', json.dumps(send_results))

	return jsonify({"success": True, "notification": record}), 200


if __name__ == '__main__':
	port = int(os.getenv('NOTIFICATIONS_PORT', 5001))
	# bind to 0.0.0.0 so it is reachable from other hosts if needed
	app.run(host='0.0.0.0', port=port, debug=os.getenv('APP_DEBUG', 'false').lower() in ['1', 'true', 'yes'])
