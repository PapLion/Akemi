"""Detached remote child supervisor. No provider/storage credentials or ML imports."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def atomic(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    with temp.open('w') as stream:
        json.dump(data, stream, indent=2); stream.flush(); os.fsync(stream.fileno())
    os.replace(temp, path)


def inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_file() and not path.is_symlink() and '.neo-worker' not in path.parts:
            h = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024*1024), b''):
                    h.update(chunk)
            result[str(path.relative_to(root))] = {'sha256': h.hexdigest(), 'bytes': path.stat().st_size}
    return result


def run(config):
    root = Path(config['cwd']); state = root/'.neo-worker';state.mkdir(parents=True, exist_ok=True)
    with (state/'lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0  # already supervised, never start duplicate training
        if (state/'status.json').exists():
            return int(json.loads((state/'status.json').read_text())['returncode'])
        # A restarted wrapper cannot safely infer that an old unobserved child exited successfully.
        if (state/'running.json').exists():
            raise RuntimeError('Prior worker disappeared without exit receipt; attach/recover, never rerun blindly')
        reason = [None]
        def interrupted(signum, frame):
            reason[0] = 'interrupted'
        signal.signal(signal.SIGTERM, interrupted);signal.signal(signal.SIGINT, interrupted)
        started = time.time(); child = None; rc = 125
        try:
            with (state/'training.log').open('ab', buffering=0) as log:
                child = subprocess.Popen(config['command'], cwd=root,
                                         env={**os.environ, **config.get('env', {})},
                                         stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                         start_new_session=True)
                atomic(state/'running.json', {'job_id':config['job_id'], 'supervisor_pid':os.getpid(),
                       'child_pid':child.pid, 'started':started})
                while child.poll() is None:
                    if time.time()-started >= config['max_seconds']:
                        reason[0] = 'timeout'
                    if reason[0]:
                        os.killpg(child.pid, signal.SIGTERM)
                        try:child.wait(timeout=config.get('term_grace_seconds', 30))
                        except subprocess.TimeoutExpired:
                            os.killpg(child.pid, signal.SIGKILL);child.wait()
                        break
                    time.sleep(.05)
                rc = child.returncode
        except BaseException:
            reason[0] = reason[0] or 'supervisor_failure'
            if child and child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL);child.wait()
            raise
        finally:
            files = inventory(root)
            valid = all(name in files and files[name]['bytes'] > 0 for name in config.get('required_files', []))
            atomic(state/'status.json', {'job_id':config['job_id'], 'started':started, 'ended':time.time(),
                   'returncode':rc, 'outcome':reason[0] or ('completed' if rc == 0 else 'failed'),
                   'outputs_valid':valid, 'files':files})
        return rc if 0 <= rc < 256 else 128 + abs(rc)


if __name__ == '__main__':
    raise SystemExit(run(json.loads(Path(sys.argv[1]).read_text())))
