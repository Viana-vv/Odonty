import re
import sys
from pathlib import Path

sys.path.insert(0, 'test-results')
from xano_admin import call

route = '/apigroup/434156/api/4068721'
remote = call('GET', route, params={'include_xanoscript': 'true'})
assert remote['auth'] == 897322
original = remote['xanoscript']['value']
assert 'history = false' in original
updated, count = re.subn(
    r'(\$email|\$cro_entrada)\|regex_matches:"((?:[^"\\]|\\.)*)"',
    lambda match: '"/' + match[2] + '/"|regex_matches:' + match[1], original,
)
assert count == 2
Path('test-results/cadastro-antes-correcao.xs').write_text(original, encoding='utf-8')
result = call('PUT', route, params={'publish': 'true'}, data=updated.encode('utf-8'), headers={'Content-Type': 'text/x-xanoscript'})
assert result['id'] == 4068721
print('Validacoes de email e CRO corrigidas no endpoint de cadastro.')
