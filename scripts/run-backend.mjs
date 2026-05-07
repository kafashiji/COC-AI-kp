/**
 * 从仓库根目录启动后端：固定 cwd=backend，并把 ~/.local/bin 加入 PATH（Windows 上便于找到 uv）。
 */
import { spawn } from "node:child_process"
import { homedir } from "node:os"
import { join, dirname } from "node:path"
import { fileURLToPath } from "node:url"

const root = join(dirname(fileURLToPath(import.meta.url)), "..")
const backendDir = join(root, "backend")
const uvBin = join(homedir(), ".local", "bin")
const sep = process.platform === "win32" ? ";" : ":"
const env = {
  ...process.env,
  PATH: `${uvBin}${sep}${process.env.PATH ?? ""}`,
}

const child = spawn(
  "uv",
  ["run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
  {
    cwd: backendDir,
    env,
    stdio: "inherit",
    shell: process.platform === "win32",
  },
)

function forward(sig) {
  try {
    child.kill(sig)
  } catch {
    /* ignore */
  }
}

process.on("SIGINT", () => forward("SIGINT"))
process.on("SIGTERM", () => forward("SIGTERM"))

child.on("exit", (code, sig) => {
  process.exit(code ?? (sig ? 1 : 0))
})
