import re
import secrets
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, 'test-results')
from xano_admin import call, origin

group = call('POST', '/apigroup', json={'name': 'Verificacao validacao ' + secrets.token_hex(4), 'description': 'Teste temporario com dados ficticios', 'canonical': 'verificar-validacao-' + secrets.token_hex(5), 'swagger': False})
try:
    source = Path('backend/xano/api/sorriso_acesso/profissionais_POST.xs').read_text(encoding='utf-8')
    patterns = re.findall(r'regex_test:("(?:[^"\\]|\\.)*")', source)
    patterns = ['"/' + pattern[1:-1] + '/"' for pattern in patterns]
    script = '''query validar verb=POST {
      api_group = "GROUP"
      input { }
      stack {
        util.get_raw_input { encoding = "json" } as $bruto
        var $nome { value = $bruto.nome|trim }
        var $email { value = $bruto.email|trim|to_lower }
        var $cro_entrada { value = $bruto.cro|trim|to_upper }
        var $email_ok { value = EMAIL|regex_test:$email }
        var $cro_ok { value = CRO|regex_test:$cro_entrada }
      }
      response = {objeto: ($bruto|is_object), chaves: ($bruto|keys|count), nome_tipo: ($bruto.nome|is_text), nome_tamanho: ($nome|strlen), especialidade_tipo: ($bruto.especialidade_id|is_int), email_ok: $email_ok, cro_ok: $cro_ok}
      history = false
    }'''.replace('GROUP', group['name']).replace('EMAIL', patterns[0]).replace('CRO', patterns[1])
    call('POST', f"/apigroup/{group['id']}/api", data=script.encode(), headers={'Content-Type': 'text/x-xanoscript'})
    time.sleep(3)
    response = requests.post(origin + '/api:' + group['canonical'] + '/validar', json={'nome': 'Profissional Ficticio de Teste', 'email': 'teste.nome@example.com', 'senha': 'senha-ficticia-teste', 'cro': 'SP-123456', 'especialidade_id': 1}, timeout=30)
    print('Validacao isolada:', response.status_code, response.text[:700])
finally:
    call('DELETE', '/apigroup/' + str(group['id']))
