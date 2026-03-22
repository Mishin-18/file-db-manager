from __future__ import annotations

import atexit
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path

from core.ui_common import get_app_icon_ico_path


class TrayIcon:
    """Windows tray helper backed by a tiny PowerShell NotifyIcon process.

    Avoids unsafe ctypes callbacks inside the main Python process. The helper reads
    a tooltip file and writes a restore-signal file when the user clicks the tray icon.
    """

    def __init__(self, app, on_restore):
        self.app = app
        self.on_restore = on_restore
        self.visible = False
        self._destroyed = False
        self._proc = None
        self._base = Path(tempfile.mkdtemp(prefix='fdbm_tray_'))
        self._tip_file = self._base / 'tip.txt'
        self._restore_file = self._base / 'restore.flag'
        self._stop_file = self._base / 'stop.flag'
        self._script_file = self._base / 'tray_helper.ps1'
        self._tip_file.write_text('File DB Manager', encoding='utf-8')
        self._icon_path = get_app_icon_ico_path() or ''
        self._write_script()
        atexit.register(self.shutdown)

    def _write_script(self):
        script = textwrap.dedent(r'''
            param(
                [string]$TipFile,
                [string]$RestoreFile,
                [string]$StopFile,
                [int]$ParentPid,
                [string]$IconPath
            )
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            [System.Windows.Forms.Application]::EnableVisualStyles()
            $notify = New-Object System.Windows.Forms.NotifyIcon
            if (-not [string]::IsNullOrWhiteSpace($IconPath) -and (Test-Path -LiteralPath $IconPath)) {
                try {
                    $notify.Icon = New-Object System.Drawing.Icon($IconPath)
                } catch {
                    $notify.Icon = [System.Drawing.SystemIcons]::Application
                }
            } else {
                $notify.Icon = [System.Drawing.SystemIcons]::Application
            }
            $notify.Visible = $true
            function Set-Tip([string]$t) {
                if ([string]::IsNullOrWhiteSpace($t)) { $t = 'File DB Manager' }
                if ($t.Length -gt 63) { $t = $t.Substring(0, 63) }
                try { $notify.Text = $t } catch {}
            }
            try {
                if (Test-Path -LiteralPath $TipFile) {
                    Set-Tip ([System.IO.File]::ReadAllText($TipFile, [System.Text.Encoding]::UTF8).Trim())
                } else {
                    Set-Tip 'File DB Manager'
                }
            } catch {
                Set-Tip 'File DB Manager'
            }
            $menu = New-Object System.Windows.Forms.ContextMenuStrip
            $miRestore = $menu.Items.Add('Restore')
            $miExit = $menu.Items.Add('Hide tray icon')
            $notify.ContextMenuStrip = $menu
            $signal = {
                try { [System.IO.File]::WriteAllText($RestoreFile, 'restore', [System.Text.Encoding]::UTF8) } catch {}
            }
            $miRestore.Add_Click($signal)
            $notify.Add_DoubleClick($signal)
            $notify.Add_MouseClick({
                param($sender, $e)
                if ($e.Button -eq [System.Windows.Forms.MouseButtons]::Left) {
                    & $signal
                }
            })
            $miExit.Add_Click({
                try { [System.IO.File]::WriteAllText($StopFile, 'stop', [System.Text.Encoding]::UTF8) } catch {}
                $notify.Visible = $false
                [System.Windows.Forms.Application]::ExitThread()
            })
            $timer = New-Object System.Windows.Forms.Timer
            $timer.Interval = 500
            $timer.Add_Tick({
                try {
                    if (Test-Path -LiteralPath $StopFile) {
                        $notify.Visible = $false
                        [System.Windows.Forms.Application]::ExitThread()
                        return
                    }
                    $parentAlive = $true
                    try {
                        $null = Get-Process -Id $ParentPid -ErrorAction Stop
                    } catch {
                        $parentAlive = $false
                    }
                    if (-not $parentAlive) {
                        $notify.Visible = $false
                        [System.Windows.Forms.Application]::ExitThread()
                        return
                    }
                    if (Test-Path -LiteralPath $TipFile) {
                        $txt = [System.IO.File]::ReadAllText($TipFile, [System.Text.Encoding]::UTF8).Trim()
                        Set-Tip $txt
                    }
                } catch {}
            })
            $timer.Start()
            [System.Windows.Forms.Application]::Run()
            $timer.Stop()
            $notify.Visible = $false
            $notify.Dispose()
        ''')
        self._script_file.write_text(script, encoding='utf-8')

    def _ensure_process(self):
        if self._destroyed:
            return
        if self._proc is not None and self._proc.poll() is None:
            return
        self._stop_file.unlink(missing_ok=True)
        self._restore_file.unlink(missing_ok=True)
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if os.name == 'nt' else 0
        cmd = [
            'powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', str(self._script_file),
            '-TipFile', str(self._tip_file),
            '-RestoreFile', str(self._restore_file),
            '-StopFile', str(self._stop_file),
            '-ParentPid', str(os.getpid()),
            '-IconPath', str(self._icon_path),
        ]
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=flags,
        )

    def _write_tip(self, tooltip: str):
        text = (tooltip or 'File DB Manager').replace('\r', ' ').replace('\n', ' | ').strip()
        self._tip_file.write_text(text[:63], encoding='utf-8')

    def show(self, tooltip: str):
        if self._destroyed:
            return
        self._write_tip(tooltip)
        self._ensure_process()
        self.visible = True

    def update_tooltip(self, tooltip: str):
        if self._destroyed:
            return
        self._write_tip(tooltip)
        if self.visible:
            self._ensure_process()

    def has_restore_request(self) -> bool:
        if self._destroyed:
            return False
        if self._restore_file.exists():
            try:
                self._restore_file.unlink()
            except Exception:
                pass
            return True
        return False

    def hide(self):
        if self._destroyed:
            return
        self.visible = False
        try:
            self._stop_file.write_text('stop', encoding='utf-8')
        except Exception:
            pass
        proc = self._proc
        self._proc = None
        if proc is not None:
            try:
                proc.wait(timeout=1.5)
            except Exception:
                try:
                    proc.terminate()
                except Exception:
                    pass

    def shutdown(self):
        if self._destroyed:
            return
        self.hide()
        self._destroyed = True
        for p in [self._tip_file, self._restore_file, self._stop_file, self._script_file]:
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass
        try:
            self._base.rmdir()
        except Exception:
            pass
