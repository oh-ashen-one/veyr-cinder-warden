#!/usr/bin/env python3
"""Append a gates record to a knight metrics JSON from native run evidence directories.

usage: record_native_gates.py <metrics.json> <key> <build note> <gpu note> <evidence dir>...
fps = frameCount / durationSeconds from each Evidence/native-*/unreal-*/evidence.json; GPU utilization from gpu.json.
Same fields as gates_v030s_* in round5-metrics.json (the scratch recorder that wrote that entry, now kept in the repo)."""
import glob, json, os, sys
metrics, key, build, gpu, *dirs = sys.argv[1:]
m = json.load(open(metrics))
runs = []
for d in dirs:
    ev = sorted(glob.glob(os.path.join(d, 'unreal-*', 'evidence.json')))
    g = json.load(open(os.path.join(d, 'gpu.json'))) if os.path.exists(os.path.join(d, 'gpu.json')) else {}
    if not ev:
        runs.append({'mode': os.path.basename(d).split('-')[1], 'passed': False, 'fps': None, 'evidence': d,
                     'reason': 'no evidence.json (game did not finish or did not start)', 'gpuOutcome': g.get('outcome'), 'exitCode': g.get('exit_code')})
        continue
    e = json.load(open(ev[-1]))
    fc = e.get('frameCount') or e.get('renderedFrames') or (e.get('nativeVideo') or {}).get('savedFrames')
    dur = e.get('durationSeconds') or 0
    r = {'mode': e.get('mode'), 'passed': bool(e.get('passed')), 'fps': round(fc / dur, 1) if fc and dur else None,
         'frameCount': fc, 'durationSeconds': round(dur, 1), 'evidence': d}
    if e.get('reason'):
        r['reason'] = e['reason'][:300]
    u = g.get('util_during') or {}
    r.update(gpuUtilAvg=u.get('avg'), gpuUtilMax=u.get('max'), perfValid=g.get('perf_valid'))
    runs.append(r)
ok = sum(r['passed'] for r in runs)
m[key] = {'build': build, 'gpuWait': gpu, 'runs': runs,
          'summary': '%d/%d passed: %s' % (ok, len(runs), ', '.join('%s %s %s' % (r['mode'], 'pass' if r['passed'] else 'FAIL', r['fps']) for r in runs))}
with open(metrics, 'w') as f:
    json.dump(m, f, indent=1); f.write('\n')
print(m[key]['summary'])
