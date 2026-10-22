"""Run commands in isolated dependency/source paths, persist stdout/stderr/exit codes."""
from pathlib import Path
import argparse,importlib.metadata,json,os,subprocess,sys
H=Path(__file__).resolve().parent;W=H.parents[1];A=W/'audit_workspace'
env=os.environ.copy();env['PYTHONPATH']=str(A/'deps')+os.pathsep+str(A/'FactSculpt')+os.pathsep+str(H)
env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
for k in ['FACTSCULPT_API_KEY','GEMINI_API_KEY','OPENAI_API_KEY']:env.pop(k,None)
cmds=[('normal_import_after_install',[sys.executable,'-c','import factsculpt.classifier; print("normal import succeeded, no initializer bypass")']),('environment_after_install',[sys.executable,'-c','import sys,importlib.metadata as m,json; print(sys.version); print(json.dumps({x:m.version(x) for x in ["numpy","scipy","scikit-learn","pytest","pydantic"]},indent=2))']),('audit_pytest',[sys.executable,'-m','pytest',str(H/'test_audit.py'),'-q','--junitxml='+str(H/'audit_tests.xml')]),('diagnostic_experiments',[sys.executable,str(H/'run_diagnostics.py')]),('original_offline_smoke_after_install',[sys.executable,str(H.parent/'verify_snapshot.py')])]
cmds.extend([('cli_detection_copy',[sys.executable,str(A/'FactSculpt/app/detect.py'),'--source','I assisted with developing an EV charger monitoring system.','--enhanced','I led the development of an advanced EV charger monitoring system.']),('cli_repair_copy',[sys.executable,str(A/'FactSculpt/app/repair.py'),'--source','I assisted with developing a system.','--enhanced','I spearheaded an advanced system.']),('original_tests_after_install',[sys.executable,'-m','pytest',str(W/'FactSculpt/tests'),'-q']),('genuine_nli_blocked',[sys.executable,str(H/'run_genuine_nli.py'),'--data',str(A/'FactSculpt/data/splits/minimal_pairs.json'),'--output',str(H/'results/genuine_nli_predictions.jsonl'),'--model','facebook/bart-large-mnli','--revision','d7645e127eaf1aefc7862fd59a17a5aa8558b8ce'])])
parser=argparse.ArgumentParser();parser.add_argument('--only');options=parser.parse_args()
if options.only:cmds=[(n,a) for n,a in cmds if n==options.only]
manifest=[]
for name,args in cmds:
    p=subprocess.run(args,cwd=W,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (H/'logs'/f'{name}.txt').write_text('COMMAND: '+subprocess.list2cmdline(args)+'\nCWD: '+str(W)+'\nENV: PYTHONPATH=audit_workspace/deps;audit_workspace/FactSculpt;paper_foundation/audit; HF_HUB_OFFLINE=1; TRANSFORMERS_OFFLINE=1; PYTEST_DISABLE_PLUGIN_AUTOLOAD=1\nEXIT: '+str(p.returncode)+'\nSTDOUT:\n'+p.stdout+'\nSTDERR:\n'+p.stderr,encoding='utf-8')
    manifest.append(dict(name=name,command=args,exit=p.returncode));print(name,p.returncode,flush=True)
existing=json.loads((H/'execution_manifest.json').read_text()) if options.only and (H/'execution_manifest.json').exists() else []
existing=[r for r in existing if r['name'] not in {r['name'] for r in manifest}]
(H/'execution_manifest.json').write_text(json.dumps(existing+manifest,indent=2))
