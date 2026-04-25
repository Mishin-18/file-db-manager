from __future__ import annotations

import os
import subprocess
from typing import Iterable, Mapping, Sequence


def _hidden_kwargs() -> dict:
    if os.name != 'nt':
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = getattr(subprocess, 'SW_HIDE', 0)
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    return {
        'startupinfo': startupinfo,
        'creationflags': flags,
    }


def popen_quiet(args: Sequence[str], **kwargs):
    merged = dict(kwargs)
    merged.update(_hidden_kwargs())
    return subprocess.Popen(args, **merged)


def run_quiet(args: Sequence[str], **kwargs):
    merged = dict(kwargs)
    merged.update(_hidden_kwargs())
    return subprocess.run(args, **merged)


def run_quiet_interruptible(args: Sequence[str], *, stop_flag=None, poll_interval: float = 0.1, **kwargs):
    merged = dict(kwargs)
    check = bool(merged.pop('check', False))
    merged.update(_hidden_kwargs())
    proc = subprocess.Popen(args, **merged)
    while True:
        rc = proc.poll()
        if rc is not None:
            if check and rc != 0:
                raise subprocess.CalledProcessError(rc, args)
            return rc
        if stop_flag and stop_flag.get('stop'):
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
                try:
                    proc.wait(timeout=1)
                except Exception:
                    pass
            raise InterruptedError('Stopped by user')
        try:
            proc.wait(timeout=poll_interval)
        except subprocess.TimeoutExpired:
            continue
