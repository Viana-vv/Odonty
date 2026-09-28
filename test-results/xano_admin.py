import time
from pathlib import Path
import requests, yaml

cfg = yaml.safe_load((Path.home()/'.xano/credentials.yaml').read_text())
profile = cfg['profiles'][cfg['default']]
origin = profile['instance_origin'].rstrip('/')
meta = origin + '/api:meta/workspace/149129'
session = requests.Session()
session.headers['Authorization'] = 'Bearer ' + profile['access_token']

def call(method, path, **kwargs):
    time.sleep(1.2)
    r = session.request(method, meta+path, timeout=40, **kwargs)
    if r.status_code == 429:
        time.sleep(20)
        r = session.request(method, meta+path, timeout=40, **kwargs)
    if not r.ok:
        raise RuntimeError(f'Metadata {method} {path}: HTTP {r.status_code}')
    return r.json() if r.content else None

def all_rows(path):
    page, result = 1, []
    while page:
        d = call('GET',path,params={'per_page':100,'page':page})
        if isinstance(d,list): return d
        result.extend(d['items'])
        page=d.get('nextPage')
    return result
