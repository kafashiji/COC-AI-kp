@echo off
chcp 65001 >nul
REM 用于 launch.json「附加到 Edge」：先启动本脚本打开带远程调试端口的 Edge，再在 Cursor 里选「3️⃣ 附加…」按 F5。
REM 请先保持前端 dev 运行（npm run dev:frontend），确保 http://127.0.0.1:3000 可访问。

set "EDGE=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE%" set "EDGE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

start "" "%EDGE%" --remote-debugging-port=9222 --user-data-dir="%TEMP%\edge-debug-coc-ai-kp" http://127.0.0.1:3000/
