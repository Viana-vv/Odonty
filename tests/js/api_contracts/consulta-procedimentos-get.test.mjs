import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { root } from './helpers.mjs';

const api = readFileSync(
  resolve(root, 'backend/xano/api/sorriso_acesso/consultas_id_procedimentos_GET.xs'),
  'utf8',
);
const client = readFileSync(resolve(root, 'sorrisomais/procedimentos_consulta.py'), 'utf8');

test('GET de Procedimentos exige autenticação e valida o escopo do Profissional', () => {
  assert.match(api, /query "consultas\/\{id\}\/procedimentos" verb=GET/);
  assert.match(api, /auth = "conta_acesso"/);
  assert.match(api, /function\.run sorriso_validar_sessao/);
  assert.match(api, /\["profissional"\]/);
  assert.match(api, /\$consulta\.profissional_id != \$profissional_autenticado\.id/);
  assert.match(api, /HTTP\/1\.1 404 Not Found/);
  assert.match(api, /db\.query consulta_procedimento/);
  assert.match(api, /"situacao", "realizado_por_profissional_id", "realizado_em"/);
});

test('cliente Python usa a rota GET própria sem executar rede neste teste', () => {
  assert.match(client, /def listar_procedimentos_consulta\(/);
  assert.match(client, /_solicitar\("GET", f"\/consultas\/\{consulta_id\}\/procedimentos", token\)/);
});
