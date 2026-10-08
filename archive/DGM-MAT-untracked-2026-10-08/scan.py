import os,ast,shutil
from collections import defaultdict
from datetime import datetime

ROOT=r'C:\ProgramasGodMode\DGM-MAT'
OUT=r'C:\ProgramasGodMode\DGM-MAT\reports'
os.makedirs(OUT,exist_ok=True)
TS=datetime.now().strftime('%Y%m%dT%H%M%S')

tree_lines=[]
file_counts=defaultdict(int)
py_files=[]
all_files=[]

for dirpath,dirnames,filenames in os.walk(ROOT):
    dirnames[:]=[d for d in dirnames if d not in ('__pycache__','.git','reports')]
    depth=dirpath.replace(ROOT,'').count(os.sep)
    tree_lines.append('  '*depth+os.path.basename(dirpath)+'/')
    for fname in sorted(filenames):
        ext=os.path.splitext(fname)[1] or 'no_ext'
        file_counts[ext]+=1
        fpath=os.path.join(dirpath,fname)
        all_files.append(fpath)
        if fname.endswith('.py'): py_files.append(fpath)
        tree_lines.append('  '*(depth+1)+fname)

print('FILES:'+str(len(all_files))+' PY:'+str(len(py_files)))

packages={}
for fpath in py_files:
    rel=fpath.replace(ROOT+os.sep,'')
    parts=rel.replace('.py','').split(os.sep)
    pkg='.'.join(parts[:-1]) if len(parts)>1 else '__root__'
    packages.setdefault(pkg,[]).append(parts[-1])

import_graph={}
parse_errors=[]
for fpath in py_files:
    rel=fpath.replace(ROOT+os.sep,'').replace(os.sep,'/')
    imports=[]
    try:
        src=open(fpath,encoding='utf-8',errors='replace').read()
        t=ast.parse(src)
        for node in ast.walk(t):
            if isinstance(node,ast.Import):
                for a in node.names: imports.append(a.name)
            elif isinstance(node,ast.ImportFrom):
                if node.module: imports.append(('.'*(node.level or 0))+node.module)
    except Exception as e:
        parse_errors.append(str(rel)+': '+str(e))
    import_graph[rel]=sorted(set(imports))
entrypoints=[]
for fpath in py_files:
    rel=fpath.replace(ROOT+os.sep,'').replace(os.sep,'/')
    try:
        src=open(fpath,encoding='utf-8',errors='replace').read()
        flags=[]
        if 'if __name__' in src: flags.append('__main__')
        if 'uvicorn' in src and 'run(' in src: flags.append('uvicorn')
        if 'Thread(' in src and 'daemon' in src: flags.append('daemon_thread')
        if 'while True' in src: flags.append('while_true')
        if 'BootstrapEngine' in src or 'bootstrap' in src[:300].lower(): flags.append('bootstrap')
        if flags: entrypoints.append({'file':rel,'flags':flags})
    except: pass

ext_counts=defaultdict(int)
STDLIB=set('os,sys,re,json,time,threading,datetime,typing,abc,enum,pathlib,logging,traceback,copy,io,hashlib,uuid,shutil,subprocess,socket,collections,functools,itertools,dataclasses,inspect,warnings,contextlib,asyncio,signal,atexit,base64,struct,random,math,string,urllib,http,html,xml,csv,tempfile,gc,weakref,importlib,platform,stat,glob,fnmatch,textwrap,pprint,heapq,queue,array,decimal,operator,builtins,types'.split(','))
for imps in import_graph.values():
    for i in imps:
        top=i.split('.')[0].lstrip('.')
        if top and top not in STDLIB: ext_counts[top]+=1

SAT={
    'DGM-Core-Backend':     ['core/runtime','core/bootstrap','core/storage','core/api','core/governance','core/observability','core/autonomy','core/memory','core/federation','core/realtime','core/kernel'],
    'DGM-Cockpit-Frontend': ['core/cockpit','cockpit','ui','dashboard','frontend'],
    'DGM-Contracts':        ['core/schemas','core/events','core/dto','core/models','schemas','models','contracts'],
    'DGM-Docs':             ['docs','reports','roadmap'],
    'DGM-Experimental':     ['labs','experimental','legacy','sandbox','plugins','scripts'],
}
assignment={}
for fpath in all_files:
    rel=fpath.replace(ROOT+os.sep,'').replace(os.sep,'/').lower()
    assigned='UNASSIONED'
    for sat,prefixes in SAT.items():
        if any(rel.startswith(p) for p in prefixes): assigned=sat; break
    assignment[fpath]=assigned
sat_counts=defaultdict(int)
for s in assignment.values(): sat_counts[s]+=1

def w(path,content):
    with open(path,'w',encoding='utf-8') as f: f.write(content)

# repository_tree.md
md='# DGM-MAT Repository Tree\n_Generated: '+TS+'_\n\n'
md+='**Total:** '+str(len(all_files))+' files | **Python:** '+str(len(py_files))+'\n\n## File types\n'
for ext,cnt in sorted(file_counts.items(),key=lambda x:-x[1]): md+='- `'+ext+'`: '+str(cnt)+'\n'
md+='\n## Full tree\n```\n'+'\n'.join(tree_lines)+'\n```\n\n## Python packages\n'
for pkg,mods in sorted(packages.items()):
    md+='\n### `'+pkg+'`\n'
    for m in sorted(mods): md+='- '+m+'\n'
w(OUT+r'\repository_tree.md',md)
print('DONE:repository_tree.md lines='+str(len(md.splitlines())))

# dependency_map.md
md='# Dependency Map\n_Generated: '+TS+'_\n\n## External packages (top 40)\n'
for pkg,cnt in sorted(ext_counts.items(),key=lambda x:-x[1])[:40]:
    if pkg: md+='- `'+pkg+'`: '+str(cnt)+'\n'
md+='\n## Internal dependency graph\n'
for rel,deps in sorted(import_graph.items()):
    ideps=[d for d in deps if d.startswith('core') or d.startswith('scripts')]
    if ideps:
        md+='\n**'+rel+'**\n'
        for d in ideps: md+='  - `'+d+'`\n'
md+='\n## Parse errors ('+str(len(parse_errors))+')\n'
for e in parse_errors: md+='- '+e+'\n'
w(OUT+r'\dependency_map.md',md)
print('DONE:dependency_map.md')

# runtime_entrypoints.md
md='# Runtime Entrypoints\n_Generated: '+TS+'_\n\n'
for cat in ['__main__','uvicorn','daemon_thread','while_true','bootstrap']:
    files=[ep['file'] for ep in entrypoints if cat in ep['flags']]
    md+='\n## '+cat+' ('+str(len(files))+')\n'
    for fp in sorted(files): md+='- `'+fp+'`\n'
md+='\n## All entrypoints\n'
for ep in sorted(entrypoints,key=lambda x:x['file']):
    md+='- `'+ep['file']+'` -> '+', '.join(ep['flags'])+'\n'
w(OUT+r'\runtime_entrypoints.md',md)
print('DONE:runtime_entrypoints.md')

# extraction_plan.md
md='# Extraction Plan\n_Generated: '+TS+'_\n\n## Satellite summary\n'
for sat,cnt in sorted(sat_counts.items(),key=lambda x:-x[1]): md+='- **'+sat+'**: '+str(cnt)+' files\n'
for sat in list(SAT.keys())+['UNASSIONED']:
    files=[fp.replace(ROOT+os.sep,'').replace(os.sep,'/') for fp,s in assignment.items() if s==sat]
    if files:
        md+='\n## '+str(sat)+' ('+str(len(files))+')\n'
        for fp in sorted(files)[:120]: md+='- `'+fp+'`\n'
        if len(files)>120: md+='- ...+'+str(len(files)-120)+' more\n'
w(OUT+r'\extraction_plan.md',md)
print('DONE:extraction_plan.md')

print('\n--- FINAL SUMMARY ---')
print('Total files   : '+str(len(all_files)))
print('Python files  : '+str(len(py_files)))
print('Packages      : '+str(len(packages)))
print('Entrypoints   : '+str(len(entrypoints)))
print('Parse errors  : '+str(len(parse_errors)))
print('Satellite dist: '+str(dict(sat_counts)))
