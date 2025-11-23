const express = require('express');
const fetch = require('node-fetch');
const cookieParser = require('cookie-parser');

const app = express();
app.use(express.json());
app.use(cookieParser());

const PORT = process.env.PORT || 8080;
const SECURITY_URL = process.env.SECURITY_URL || 'http://ms_seguridad:8000';
const MS_CONSULTA = process.env.MS_CONSULTA_URL || 'http://ms_consulta:8001';
const MS_REPORTES = process.env.MS_REPORTES_URL || 'http://ms_reportes:5002';

// Simple health
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// Login: proxy to ms_seguridad /api/login and set httpOnly cookie with access_token
app.post('/api/login', async (req, res) => {
  try {
    const r = await fetch(`${SECURITY_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });
    const data = await r.json();
    if (r.ok && data.access_token) {
      // Set cookie httpOnly
      res.cookie('access_token', data.access_token, { httpOnly: true, sameSite: 'lax' });
      return res.json({ ok: true });
    }
    return res.status(r.status).json(data);
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'bff_login_error' });
  }
});

// Proxy endpoint to get event id from ms_consulta
app.post('/api/get-event-id', async (req, res) => {
  try {
    const r = await fetch(`${MS_CONSULTA}/get-event-id/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });
    const data = await r.json();
    return res.status(r.status).json(data);
  } catch (err) {
    console.error(err);
    return res.status(502).json({ error: 'bad_gateway' });
  }
});

// Proxy to create report
app.post('/api/reports', async (req, res) => {
  try {
    // Forward cookie token as Authorization if exists
    const token = req.cookies && req.cookies.access_token;
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const r = await fetch(`${MS_REPORTES}/reports`, {
      method: 'POST',
      headers,
      body: JSON.stringify(req.body),
    });
    const data = await r.json();
    return res.status(r.status).json(data);
  } catch (err) {
    console.error(err);
    return res.status(502).json({ error: 'bad_gateway' });
  }
});

app.listen(PORT, () => console.log(`BFF listening on ${PORT}`));
