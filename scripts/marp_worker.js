'use strict'

/**
 * Marp CLI 퍼시스턴트 워커
 *
 * FastAPI 서버 시작 시 함께 실행되어 Node.js 프로세스를 재사용.
 * 매 HTML 변환마다 Node.js를 새로 띄우는 오버헤드(~500ms~1s) 제거.
 *
 * POST /render  { markdown: "..." }  → { html: "..." }
 * GET  /health                       → "ok"
 */

const http = require('http')
const fs = require('fs')
const path = require('path')
const os = require('os')
const crypto = require('crypto')

const PORT = parseInt(process.env.MARP_SERVER_PORT || '37717', 10)
const HOST = '127.0.0.1'

// 임시 디렉토리 (프로세스 수명과 동일)
const TEMP_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'marp_worker_'))

// marp-cli 모듈을 미리 로드해 Node.js 모듈 캐시에 올림
// → 이후 marpCli() 호출마다 require 비용 없음
let marpCli
try {
  marpCli = require('@marp-team/marp-cli').marpCli
} catch (e) {
  process.stderr.write(`[marp_worker] @marp-team/marp-cli 로드 실패: ${e.message}\n`)
  process.stderr.write('[marp_worker] npm install 을 실행해주세요.\n')
  process.exit(1)
}

// ── 변환 함수 ─────────────────────────────────────────────────────
async function convertMarkdown(markdown) {
  const id = crypto.randomUUID()
  const mdFile  = path.join(TEMP_DIR, `${id}.md`)
  const htmlFile = path.join(TEMP_DIR, `${id}.html`)

  fs.writeFileSync(mdFile, markdown, 'utf8')

  try {
    const exitCode = await marpCli(
      ['--html', '--output', htmlFile, mdFile],
      { baseUrl: `file://${TEMP_DIR}/` }
    )
    if (exitCode !== 0) {
      throw new Error(`marpCli exit code: ${exitCode}`)
    }
    return fs.readFileSync(htmlFile, 'utf8')
  } finally {
    try { fs.unlinkSync(mdFile)  } catch (_) {}
    try { fs.unlinkSync(htmlFile) } catch (_) {}
  }
}

// ── HTTP 서버 ──────────────────────────────────────────────────────
const server = http.createServer(async (req, res) => {
  // 헬스체크
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'text/plain' })
    res.end('ok')
    return
  }

  // 변환 엔드포인트
  if (req.method === 'POST' && req.url === '/render') {
    let body = ''
    req.on('data', chunk => { body += chunk })
    req.on('end', async () => {
      try {
        const { markdown } = JSON.parse(body)
        if (!markdown) throw new Error('markdown 필드 없음')

        const html = await convertMarkdown(markdown)
        res.writeHead(200, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ html }))
      } catch (err) {
        process.stderr.write(`[marp_worker] 변환 오류: ${err.message}\n`)
        res.writeHead(500, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ error: err.message }))
      }
    })
    return
  }

  res.writeHead(404)
  res.end()
})

server.listen(PORT, HOST, () => {
  // Python이 준비 완료를 감지할 수 있도록 stderr에 출력
  process.stderr.write(`[marp_worker] ready on ${HOST}:${PORT}\n`)
})

// ── 종료 처리 ──────────────────────────────────────────────────────
const shutdown = () => {
  try { fs.rmSync(TEMP_DIR, { recursive: true, force: true }) } catch (_) {}
  server.close(() => process.exit(0))
}
process.on('SIGTERM', shutdown)
process.on('SIGINT',  shutdown)
