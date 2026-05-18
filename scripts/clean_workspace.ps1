param(
    [switch]$RemoveGitHistory,
    [switch]$RemoveLocalEnvs,
    [switch]$ClearPipCache,
    [switch]$ClearNpmCache,
    [switch]$PruneDocker,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$workspace = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Show-Size {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    $bytes = (Get-ChildItem -LiteralPath $Path -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    [PSCustomObject]@{
        Path = $Path
        SizeGB = [math]::Round(($bytes / 1GB), 2)
    }
}

function Remove-PathSafely {
    param(
        [string]$Path,
        [string]$Reason
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Host "Skip missing path: $Path"
        return
    }

    $resolved = (Resolve-Path -LiteralPath $Path).Path
    if (-not $resolved.StartsWith($workspace, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove path outside workspace: $resolved"
    }

    Write-Host "Target: $resolved"
    Write-Host "Reason: $Reason"

    if ($DryRun) {
        Write-Host "Dry run only. No files removed."
        return
    }

    Remove-Item -LiteralPath $resolved -Recurse -Force
    Write-Host "Removed: $resolved"
}

Write-Host "Workspace: $workspace"
Write-Host "Current large local paths:"
Show-Size (Join-Path $workspace ".git")
Show-Size (Join-Path $workspace "mlops-env")
Show-Size (Join-Path $workspace "frontened\cryptopredictpro\node_modules")
Show-Size (Join-Path $workspace "frontened\cryptopredictpro\build")

if ($RemoveGitHistory) {
    Remove-PathSafely -Path (Join-Path $workspace ".git") -Reason "Old Git history from the previous repository is not needed for a fresh upload."
}

if ($RemoveLocalEnvs) {
    Remove-PathSafely -Path (Join-Path $workspace "mlops-env") -Reason "Local Python environment can be recreated from requirements."
    Remove-PathSafely -Path (Join-Path $workspace "venv") -Reason "Local Python environment can be recreated from requirements."
}

if ($ClearPipCache) {
    $pipCache = Join-Path $env:LOCALAPPDATA "pip\cache"
    if (Test-Path -LiteralPath $pipCache) {
        Write-Host "Clearing pip cache: $pipCache"
        if (-not $DryRun) {
            python -m pip cache purge
        }
    }
}

if ($ClearNpmCache) {
    Write-Host "Clearing npm cache"
    if (-not $DryRun) {
        npm cache clean --force
    }
}

if ($PruneDocker) {
    Write-Host "Docker disk usage before prune:"
    docker system df
    if (-not $DryRun) {
        docker builder prune --force
        docker image prune --all --force
        docker container prune --force
    }
    Write-Host "Docker disk usage after prune:"
    docker system df
}
