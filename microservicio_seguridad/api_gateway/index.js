const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

const JWT_SECRET = process.env.JWT_SECRET || 'mysecret';

// Simple login endpoint for demo: POST /auth/login { "username": "admin", "password": "password" }
app.post('/auth/login', (req, res) => {
  const { username, password } = req.body || {};
  if (username === 'admin' && password === 'password') {
    const token = jwt.sign({ sub: username, role: 'admin' }, JWT_SECRET, { expiresIn: '1h' });
    return res.json({ token });
  }
  return res.status(401).json({ error: 'Invalid credentials' });
});

function checkToken(req, res, next) {
  const auth = req.headers['authorization'] || '';
  const token = (auth.split(' ')[1]) || null;

  // Define protected prefixes (adjust as needed)
  const protectedPrefixes = ['/consulta/protected', '/notificaciones/protected', '/auditoria/protected', '/reportes/protected'];
  const isProtected = protectedPrefixes.some(p => req.path.startsWith(p));

  if (isProtected) {
    if (!token) return res.status(401).json({ error: 'Unauthorized - token missing' });
    try {
      const payload = jwt.verify(token, JWT_SECRET);
      req.user = payload;
      return next();
    } catch (e) {
      return res.status(401).json({ error: 'Unauthorized - token invalid' });
    }
  }
  next();
}

app.use(checkToken);

// Helper to forward parsed JSON bodies to proxied services (prevents empty bodies)
function proxyWithBody(options) {
  const { target, pathRewrite } = options;
  return createProxyMiddleware({
    target,
    changeOrigin: true,
    pathRewrite,
    onProxyReq: (proxyReq, req, res) => {
      // If body-parser (express.json) already parsed the body, re-send it to the proxied service
      if (req.body && Object.keys(req.body).length) {
        const bodyData = JSON.stringify(req.body);
        proxyReq.setHeader('Content-Type', 'application/json');
        proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
        proxyReq.write(bodyData);
      }
    }
  });
}

app.use('/auditoria', proxyWithBody({ target: 'http://auditoria:5001', pathRewrite: {'^/auditoria': ''} }));
app.use('/consulta', proxyWithBody({ target: 'http://consulta:8000', pathRewrite: {'^/consulta': ''} }));
app.use('/notificaciones', proxyWithBody({ target: 'http://notificaciones:80', pathRewrite: {'^/notificaciones': ''} }));
app.use('/reportes', proxyWithBody({ target: 'http://reportes:5003', pathRewrite: {'^/reportes': ''} }));
// Proxy to seguridad (Laravel) service
app.use('/seguridad', proxyWithBody({ target: 'http://seguridad:80', pathRewrite: {'^/seguridad': ''} }));

app.get('/', (req, res) => res.json({ ok: true, info: 'API Gateway running' }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`API Gateway listening on ${PORT}`));
