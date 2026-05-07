# 在项目根目录打开：后端 + 前端各一个 PowerShell 窗口
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$UvBin = Join-Path $env:USERPROFILE ".local\bin"

if (Test-Path $UvBin) {
    $env:Path = "$UvBin;$env:Path"
}

$BackendDir = Join-Path $RepoRoot "backend"
$FrontendDir = Join-Path $RepoRoot "frontend"

if (-not (Test-Path (Join-Path $BackendDir "pyproject.toml"))) {
    Write-Error "未找到 backend\pyproject.toml，请确认脚本位于仓库内。"
}

if (-not (Test-Path (Join-Path $BackendDir ".env"))) {
    Write-Warning "未找到 backend\.env：请复制根目录 .env.example 为 backend\.env 并填写 DEEPSEEK_API_KEY。"
}

if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Warning "未找到 frontend\node_modules：请先在该目录执行 npm install。"
}

$uvExe = Join-Path $UvBin "uv.exe"
if (-not (Test-Path $uvExe)) {
    Write-Warning "未找到 $uvExe。请先安装 uv，或将 uv 加入 PATH。参见 README。"
}

$backendCmd = "`$env:Path = '$UvBin;' + `$env:Path; uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Write-Host "启动后端: http://0.0.0.0:8000  （工作目录: $BackendDir）"
Start-Process powershell.exe -WorkingDirectory $BackendDir -ArgumentList @(
    "-NoExit", "-NoProfile", "-Command", $backendCmd
) | Out-Null

Start-Sleep -Seconds 1

Write-Host "启动前端: npm run dev  （工作目录: $FrontendDir）"
Start-Process powershell.exe -WorkingDirectory $FrontendDir -ArgumentList @(
    "-NoExit", "-NoProfile", "-Command", "npm run dev"
) | Out-Null

Write-Host "已打开两个窗口。关闭对应窗口即可停止服务（或在该窗口按 Ctrl+C）。"
