import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { root } from './helpers.mjs';

export function contractOperation(method, route) {
  const spec = JSON.parse(readFileSync(resolve(root, 'backend/contratos/redefinicao_senha.json'), 'utf8').replace(/^\uFEFF/, ''));
  assert.equal(spec.openapi, '3.1.0');
  const operation = spec.paths[route]?.[method.toLowerCase()];
  assert.ok(operation, `${method} ${route} ausente no contrato local`);
  return { spec, operation };
}

// Executa o cliente Python real com transporte substituído antes de qualquer chamada.
// Estes testes verificam o contrato local; não acessam nem provam transações no Xano.
export function pythonAssertions(source) {
  const local = resolve(root, '.venv-win/Scripts/python.exe');
  const python = process.env.PYTHON_TEST_BIN || (existsSync(local) ? local : 'python');
  const result = spawnSync(python, ['-B', '-c', `
import json, sys
from unittest.mock import Mock, patch
import requests
from sorrisomais.api import ClienteXano, ErroAcesso
from sorrisomais.config import Configuracao
from sorrisomais import api_redefinicao_senha as api

def response(payload=None, status=200, headers=None):
    r = Mock(status_code=status, headers=headers or {}, content=b'')
    r.__enter__ = Mock(return_value=r)
    r.__exit__ = Mock(return_value=False)
    r.json.return_value = payload
    return r

cliente = api.ClienteRedefinicaoSenha(Configuracao('https://exemplo.invalid/api:teste', timeout=3))
operacao = '019a44d4-5c00-7000-8000-000000000001'
projecao = {
    'operacao_id': operacao, 'criada_em': '2026-11-07T12:00:00.000Z',
    'consultavel_ate': '2026-12-07T12:00:00.000Z',
    'estado_envio': 'aceito', 'estado_link': 'ativo',
    'expira_em': '2026-11-07T12:15:00.000Z',
    'envio_limite_em': '2026-11-07T12:00:20.000Z',
}
with patch.object(requests, 'request', side_effect=AssertionError('rede real proibida')) as http:
    exec(json.loads(sys.stdin.read()), globals())
`], { cwd: root, input: JSON.stringify(source), encoding: 'utf8', timeout: 30000, windowsHide: true });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr || result.stdout || 'subprocesso Python falhou');
}
