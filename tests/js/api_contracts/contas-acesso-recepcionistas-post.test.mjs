import test from 'node:test';
import assert from 'node:assert/strict';
import { assertApiContract, assertClientContract } from './helpers.mjs';

test('POST de Recepcionista exige sessão administrativa e grava privilégio fixo', () => {
  const route = '/contas-acesso/recepcionistas';
  const source = assertApiContract(
    'POST', route, 'api/sorriso_acesso/contas_acesso_recepcionistas_POST.xs',
  );
  assertClientContract('POST', route, 'cadastrar_recepcionista');
  assert.match(source, /auth = "conta_acesso"/);
  assert.match(source, /sorriso_validar_sessao/);
  assert.match(source, /solicitante.situacao != "ativo"/);
  assert.match(source, /perfis\|intersect:\["administrador"\]/);
  assert.match(source, /keys\|count\) != 3/);
  for (const field of ['nome', 'email', 'senha']) {
    assert.ok(source.includes(`$bruto|get:"${field}"|is_text`));
  }
  assert.match(source, /bruto.email\|trim\|to_lower/);
  assert.match(source, /perfis: \["recepcionista"\], situacao: "ativo"/);
  const projection = source.split('  response = ')[1].split('  history')[0];
  assert.match(projection, /conta: \{/);
  assert.doesNotMatch(projection, /senha|token/);
  assert.deepEqual([...projection.matchAll(/^\s+(\w+):/gm)].map((match) => match[1]),
    ['conta', 'id', 'nome', 'email', 'perfis', 'situacao']);
  assert.match(source, /201 Created/);
  assert.match(source, /409 Conflict/);
  assert.match(source, /history = false/);
});
