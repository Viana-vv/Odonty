import sys,secrets,re,time,requests
from pathlib import Path
sys.path.insert(0,'test-results')
from xano_admin import call,origin
group=call('POST','/apigroup',json={'name':'Verificacao cadastro '+secrets.token_hex(4),'canonical':'verificar-cadastro-'+secrets.token_hex(5),'swagger':False})
account=None
try:
 senha=secrets.token_urlsafe(24)
 account=call('POST','/table/897322/content',json={'nome':'Administrador Ficticio','email':'teste.'+secrets.token_hex(8)+'@example.com','senha':senha,'perfis':['administrador'],'situacao':'ativo'})
 source=Path('backend/xano/api/sorriso_acesso/profissionais_POST.xs').read_text(encoding='utf-8')
 source=re.sub(r'^\s*guid = .*$', '', source,flags=re.MULTILINE).replace('api_group = "Sorriso Acesso"', 'api_group = "'+group['name']+'"')
 counter=iter(range(1,10))
 source=re.sub('Confira os dados do profissional.',lambda m:'Validacao '+str(next(counter)),source)
 call('POST',f"/apigroup/{group['id']}/api",data=source.encode(),headers={'Content-Type':'text/x-xanoscript'})
 main=call('GET','/apigroup/434156')
 r=requests.post(origin+'/api:'+main['canonical']+'/auth/login',json={'email':account['email'],'senha':senha},timeout=30)
 r.raise_for_status();token=r.json()['token'];time.sleep(3)
 dados={'nome':'Dentista Ficticio','email':'teste@example.com','senha':secrets.token_urlsafe(24),'cro':'SP-123456','especialidade_id':1}
 r=requests.post(origin+'/api:'+group['canonical']+'/profissionais',headers={'Authorization':'Bearer '+token},json=dados,timeout=30)
 print('Etapa rejeitada',r.status_code,r.text[:500])
finally:
 if account: call('PUT','/table/897322/content/'+str(account['id']),json={'situacao':'inativo'})
 call('DELETE','/apigroup/'+str(group['id']))
