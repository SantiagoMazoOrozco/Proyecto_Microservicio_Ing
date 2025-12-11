const jwt = require('jsonwebtoken');

const secret = process.env.JWT_SECRET || 'mysecret';
const username = process.argv[2] || 'admin';

const token = jwt.sign({ sub: username }, secret, { expiresIn: '1h' });
console.log(token);
