import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const clientSource = readFileSync(resolve(root, 'sorrisomais/api.py'), 'utf8');

export function assertApiContract(method, route, exportPath) {
  const escapedRoute = route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const call = new RegExp(`_request\\(\\"${method}\\",\\s*\\"${escapedRoute}\\"`);
  assert.match(clientSource, call, `cliente sem chamada ${method} ${route}`);
  const xanoExport = resolve(root, 'backend/xano', exportPath);
  assert.ok(existsSync(xanoExport), `export Xano ausente: ${exportPath}`);
  return readFileSync(xanoExport, 'utf8');
}

export function assertClientContract(method, route, methodName) {
  const escapedRoute = route
    .split(/(\\{[^}]+\\})/g)
    .map((parte) => parte.startsWith('{') ? '\\{[^}]+\\}' : parte.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    .join('');
  const call = new RegExp(`_request\\(\\"${method}\\",\\s*f?\\"${escapedRoute}\\"`);
  assert.match(clientSource, call, `cliente sem chamada ${method} ${route}`);
  assert.match(clientSource, new RegExp(`def ${methodName}\\(`), `método ${methodName} ausente`);
}
