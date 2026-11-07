import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('POST /auth/recuperacao-senha usa SendGrid e não retorna OTP', () => {
  const source = assertApiContract('POST', '/auth/recuperacao-senha', 'api/sorriso_acesso/auth/recuperacao-senha_POST.xs');
  assert.match(source, /api\.request/);
  assert.match(source, /\$conta\.email/);
  assert.match(source, /mascote-sorriso-email\.png/);
  assert.match(source, /PASSWORD_OTP_TTL_SECONDS/);
  assert.doesNotMatch(source, /331904/);
  assert.doesNotMatch(source, /response\s*=\s*\{[^}]*otp\s*:/i);
});
