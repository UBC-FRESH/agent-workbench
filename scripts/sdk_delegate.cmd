@echo off
REM sdk_delegate.cmd — thin shim so the Coordinator can call sdk_delegate.ps1
REM without worrying about PowerShell execution policy.
REM
REM Usage (from repo root):
REM   scripts\sdk_delegate.cmd start --manifest runtime/agent_jobs/<name>_manifest.json
REM   scripts\sdk_delegate.cmd monitor --manifest runtime/agent_jobs/<name>_manifest.json

powershell -ExecutionPolicy Bypass -File "%~dp0sdk_delegate.ps1" %*
