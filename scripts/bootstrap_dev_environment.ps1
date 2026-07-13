[CmdletBinding()]
param(
    [string]$VenvPath = ".venv",
    [switch]$ForceNativeTools
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvRoot = if ([IO.Path]::IsPathRooted($VenvPath)) {
    [IO.Path]::GetFullPath($VenvPath)
} else {
    [IO.Path]::GetFullPath((Join-Path $repoRoot $VenvPath))
}
$scriptsDir = Join-Path $venvRoot "Scripts"
$python = Join-Path $scriptsDir "python.exe"
$toolsDir = Join-Path $venvRoot "tools"

$ghVersion = "2.96.0"
$ghSha256 = "c2d6acc935cd2f00e2144d7e036d5cd82e6b6bd5594e8c75aa75ef2a4ed6aac3"
$rgVersion = "15.1.0"
$rgSha256 = "124510b94b6baa3380d051fdf4650eaa80a302c876d611e9dba0b2e18d87493a"
$nodeVersion = "26.5.0"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$ArgumentList
    )

    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $FilePath $($ArgumentList -join ' ')"
    }
}

function Install-VerifiedZipTool {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][string]$Sha256,
        [Parameter(Mandatory = $true)][string]$ExecutableName
    )

    $target = Join-Path $scriptsDir $ExecutableName
    if ((Test-Path -LiteralPath $target) -and -not $ForceNativeTools) {
        return
    }

    $toolRoot = Join-Path $toolsDir $Name
    $archive = Join-Path $toolsDir "$Name.zip"
    if (Test-Path -LiteralPath $toolRoot) {
        Remove-Item -LiteralPath $toolRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $toolRoot | Out-Null
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $archive

    $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
    if ($actualHash -ne $Sha256) {
        throw "$Name archive checksum mismatch: expected $Sha256, received $actualHash"
    }

    Expand-Archive -LiteralPath $archive -DestinationPath $toolRoot -Force
    $source = Get-ChildItem -LiteralPath $toolRoot -Recurse -File -Filter $ExecutableName |
        Select-Object -First 1
    if (-not $source) {
        throw "$ExecutableName was not present in the verified $Name archive"
    }
    Copy-Item -LiteralPath $source.FullName -Destination $target -Force
    Remove-Item -LiteralPath $archive -Force
}

function Install-CommandShim {
    param([Parameter(Mandatory = $true)][string]$CommandName)

    $localExe = Join-Path $scriptsDir "$CommandName.exe"
    $localCmd = Join-Path $scriptsDir "$CommandName.cmd"
    if (Test-Path -LiteralPath $localExe) {
        return
    }

    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if (-not $command -or -not $command.Source) {
        throw "Required host command '$CommandName' was not found after bootstrap"
    }
    if ([IO.Path]::GetFullPath($command.Source).StartsWith($scriptsDir, [StringComparison]::OrdinalIgnoreCase)) {
        return
    }

    $content = "@echo off`r`n`"$($command.Source)`" %*`r`n"
    [IO.File]::WriteAllText($localCmd, $content, [Text.Encoding]::ASCII)
}

if (-not (Test-Path -LiteralPath $python)) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        Invoke-Checked -FilePath $launcher.Source -ArgumentList @("-3", "-m", "venv", $venvRoot)
    } else {
        $systemPython = Get-Command python -ErrorAction Stop
        Invoke-Checked -FilePath $systemPython.Source -ArgumentList @("-m", "venv", $venvRoot)
    }
}

Push-Location $repoRoot
try {
    Invoke-Checked -FilePath $python -ArgumentList @("-m", "pip", "install", "--upgrade", "pip")
    Invoke-Checked -FilePath $python -ArgumentList @("-m", "pip", "install", "-e", ".[dev]")
} finally {
    Pop-Location
}

New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null
Install-VerifiedZipTool `
    -Name "gh-$ghVersion" `
    -Url "https://github.com/cli/cli/releases/download/v$ghVersion/gh_${ghVersion}_windows_amd64.zip" `
    -Sha256 $ghSha256 `
    -ExecutableName "gh.exe"
Install-VerifiedZipTool `
    -Name "ripgrep-$rgVersion" `
    -Url "https://github.com/BurntSushi/ripgrep/releases/download/$rgVersion/ripgrep-$rgVersion-x86_64-pc-windows-msvc.zip" `
    -Sha256 $rgSha256 `
    -ExecutableName "rg.exe"

$node = Join-Path $scriptsDir "node.exe"
if ((-not (Test-Path -LiteralPath $node)) -or $ForceNativeTools) {
    $env:VIRTUAL_ENV = $venvRoot
    $env:PATH = "$scriptsDir;$env:PATH"
    & $python -m nodeenv -p --node=$nodeVersion
    if (($LASTEXITCODE -ne 0) -and -not (Test-Path -LiteralPath $node)) {
        throw "nodeenv failed to install Node $nodeVersion into $venvRoot"
    }
}

Install-CommandShim -CommandName "git"
Install-CommandShim -CommandName "codex"

$checks = @(
    @{ Name = "python"; Path = $python; Args = @("--version") },
    @{ Name = "pytest"; Path = (Join-Path $scriptsDir "pytest.exe"); Args = @("--version") },
    @{ Name = "ruff"; Path = (Join-Path $scriptsDir "ruff.exe"); Args = @("--version") },
    @{ Name = "mypy"; Path = (Join-Path $scriptsDir "mypy.exe"); Args = @("--version") },
    @{ Name = "pre-commit"; Path = (Join-Path $scriptsDir "pre-commit.exe"); Args = @("--version") },
    @{ Name = "sphinx-build"; Path = (Join-Path $scriptsDir "sphinx-build.exe"); Args = @("--version") },
    @{ Name = "twine"; Path = (Join-Path $scriptsDir "twine.exe"); Args = @("--version") },
    @{ Name = "node"; Path = $node; Args = @("--version") },
    @{ Name = "npm"; Path = (Join-Path $scriptsDir "npm.cmd"); Args = @("--version") },
    @{ Name = "gh"; Path = (Join-Path $scriptsDir "gh.exe"); Args = @("--version") },
    @{ Name = "rg"; Path = (Join-Path $scriptsDir "rg.exe"); Args = @("--version") },
    @{ Name = "git"; Path = (Join-Path $scriptsDir "git.cmd"); Args = @("--version") },
    @{ Name = "codex"; Path = (Join-Path $scriptsDir "codex.cmd"); Args = @("--version") }
)

Write-Output "Project development environment: $venvRoot"
foreach ($check in $checks) {
    if (-not (Test-Path -LiteralPath $check.Path)) {
        throw "Bootstrap did not provide $($check.Name) at $($check.Path)"
    }
    $output = @(& $check.Path @($check.Args) 2>&1)
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "$($check.Name) validation failed at $($check.Path)"
    }
    $version = $output | Select-Object -First 1
    Write-Output ("{0,-14} {1}" -f $check.Name, $version)
}
