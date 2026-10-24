import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '../../..');
const read = name => readFileSync(resolve(root, 'backend/xano/api/sorriso_acesso', name), 'utf8');

test('rotas de exames exigem autenticação e sessão Xano', () => {
  for (const file of ['exames_GET.xs', 'exames_POST.xs', 'exames_id_situacao_PATCH.xs']) {
    const source = read(file);
    assert.match(source, /auth = "conta_acesso"/);
    assert.match(source, /function\.run sorriso_validar_sessao/);
    assert.doesNotMatch(source, /url_publica|arquivo/);
  }
});

test('POST exige vínculo entre paciente, consulta e profissional', () => {
  const source = read('exames_POST.xs');
  assert.match(source, /\$consulta\.paciente_id != \$paciente\.id/);
  assert.match(source, /\$consulta\.profissional_id != \$profissional\.id/);
});
