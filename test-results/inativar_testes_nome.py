import sys
sys.path.insert(0, 'test-results')
from xano_admin import all_rows, call

contas = [r for r in all_rows('/table/897322/content')
          if r.get('nome') == 'Profissional Ficticio de Teste'
          and r.get('email', '').startswith('teste.nome.')
          and r.get('email', '').endswith('@example.com')]
ids = {r['id'] for r in contas}
profissionais = [r for r in all_rows('/table/883768/content') if r.get('conta_acesso_id') in ids]
for conta in contas:
    if conta.get('situacao') != 'inativo':
        call('PUT', f"/table/897322/content/{conta['id']}", json={'situacao': 'inativo'})
for profissional in profissionais:
    if profissional.get('situacao') != 'Inativo':
        call('PUT', f"/table/883768/content/{profissional['id']}", json={'situacao': 'Inativo'})
print(f'Inativados {len(contas)} cadastros ficticios do teste automatizado; historicos preservados.')
