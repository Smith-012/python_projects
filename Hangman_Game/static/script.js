// ------------------ Config ------------------
const MAX_MISSES = 6
const MAX_HINTS = 3

// ------------------ State ------------------
let secret = ''
let revealed = []
let guessed = new Set()
let misses = 0
let hintsLeft = MAX_HINTS

const els = {
  word: document.getElementById('word'),
  lives: document.getElementById('lives'),
  guessed: document.getElementById('guessed'),
  kbd: document.getElementById('keyboard'),
  stage: document.getElementById('stage'),
  newGame: document.getElementById('newGame'),
  hintBtn: document.getElementById('hintBtn'),
  reveal: document.getElementById('reveal'),
  error: document.getElementById('error')
}

// optional toast helper (SweetAlert2 toast mode)
function showToast (message, icon = 'info') {
  Swal.fire({
    toast: true,
    position: 'top-end',
    icon,
    title: message,
    showConfirmButton: false,
    timer: 1800,
    timerProgressBar: true
  })
}

// ------------------ Runtime word via backend proxy ------------------
async function fetchRandomWord () {
  const r = await fetch('/api/random_word', { cache: 'no-store' })
  if (!r.ok) {
    let msg = 'Failed to fetch random word'
    try {
      const err = await r.json()
      if (err && err.error) msg = err.error
    } catch {}
    throw new Error(msg)
  }
  const j = await r.json()
  const w = (j.word || '').toString()
  if (!/^[A-Za-z]{3,14}$/.test(w))
    throw new Error('API returned an invalid word')
  return w.toUpperCase()
}

async function newGame () {
  try {
    secret = await fetchRandomWord()
  } catch (e) {
    showError(e.message || String(e))
    Swal.fire({
      title: 'Network Error',
      text: e.message || 'Could not load a word from the server.',
      icon: 'error',
      confirmButtonColor: '#ef4444'
    })
    return
  }
  revealed = Array(secret.length).fill('_')
  guessed.clear()
  misses = 0
  hintsLeft = MAX_HINTS
  hideError()
  drawBase()
  buildKeyboard()
  updateUI()
  updateHintBtn()
}

// ------------------ UI updates ------------------
function updateUI () {
  els.word.textContent = revealed.join(' ')
  els.lives.textContent = `Lives: ${MAX_MISSES - misses} / ${MAX_MISSES}`
  els.guessed.textContent = `Guessed: ${[...guessed].sort().join('') || '—'}`
}
function updateHintBtn () {
  els.hintBtn.textContent = `Hint (${hintsLeft})`
  els.hintBtn.disabled = hintsLeft <= 0 || !revealed.includes('_')
}
function showError (msg) {
  els.error.textContent = 'Network error: ' + msg
  els.error.hidden = false
}
function hideError () {
  els.error.hidden = true
  els.error.textContent = ''
}

// ------------------ Guess & Hint ------------------
function handleGuess (ch) {
  ch = ch.toUpperCase()
  if (guessed.has(ch) || !/^[A-Z]$/.test(ch)) return
  guessed.add(ch)
  const btn = document.getElementById('key-' + ch)
  if (btn) btn.disabled = true

  if (secret.includes(ch)) {
    ;[...secret].forEach((c, i) => {
      if (c === ch) revealed[i] = ch
    })
    updateUI()
    if (!revealed.includes('_')) {
      disableKeys()
      Swal.fire({
        title: 'You Win!',
        text: `Correct word: ${secret}`,
        icon: 'success',
        confirmButtonColor: '#22c55e'
      })
    }
  } else {
    misses++
    drawStage(misses)
    updateUI()
    if (misses >= MAX_MISSES) {
      disableKeys()
      els.word.textContent = secret.split('').join(' ')
      Swal.fire({
        title: 'You Lost!',
        text: `The correct word was: ${secret}`,
        icon: 'error',
        confirmButtonColor: '#ef4444'
      })
    }
  }
  updateHintBtn()
}

function useHint () {
  if (hintsLeft <= 0 || !revealed.includes('_')) return
  hintsLeft--
  const hidden = []
  for (let i = 0; i < revealed.length; i++)
    if (revealed[i] === '_') hidden.push(i)
  const idx = hidden[Math.floor(Math.random() * hidden.length)]
  const ch = secret[idx]

  guessed.add(ch)
  for (let i = 0; i < secret.length; i++) if (secret[i] === ch) revealed[i] = ch

  const btn = document.getElementById('key-' + ch)
  if (btn) btn.disabled = true

  updateUI()
  updateHintBtn()

  showToast('Hint revealed!', 'success')

  if (!revealed.includes('_')) {
    disableKeys()
    Swal.fire({
      title: 'You Win!',
      text: `Correct word: ${secret}`,
      icon: 'success',
      confirmButtonColor: '#22c55e'
    })
  }
}

// ------------------ Keyboard ------------------
function buildKeyboard () {
  els.kbd.innerHTML = ''
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')
  const rows = [letters.slice(0, 9), letters.slice(9, 18), letters.slice(18)]
  rows.forEach(row =>
    row.forEach(ch => {
      const b = document.createElement('button')
      b.textContent = ch
      b.id = 'key-' + ch
      b.addEventListener('click', () => handleGuess(ch))
      els.kbd.appendChild(b)
    })
  )
}
function disableKeys () {
  els.kbd.querySelectorAll('button').forEach(b => (b.disabled = true))
}
window.addEventListener('keydown', e => {
  const ch = e.key.toUpperCase()
  if (/^[A-Z]$/.test(ch)) handleGuess(ch)
})

// ------------------ Drawing (SVG) ------------------
function drawBase () {
  els.stage.innerHTML = ''
  line(40, 420, 560, 420, 16, '#1e293b')
  line(120, 420, 120, 60)
  line(120, 60, 320, 60)
  line(320, 60, 320, 110)
}
function drawStage (n) {
  const x = 320,
    y = 160
  if (n >= 1) circle(x, y, 36)
  if (n >= 2) line(x, y + 36, x, y + 140, 6, '#eab308')
  if (n >= 3) line(x, y + 60, x - 50, y + 95, 6, '#eab308')
  if (n >= 4) line(x, y + 60, x + 50, y + 95, 6, '#eab308')
  if (n >= 5) line(x, y + 140, x - 40, y + 190, 6, '#eab308')
  if (n >= 6) line(x, y + 140, x + 40, y + 190, 6, '#eab308')
}
function line (x1, y1, x2, y2, w = 8, col = '#64748b') {
  const l = document.createElementNS('http://www.w3.org/2000/svg', 'line')
  l.setAttribute('x1', x1)
  l.setAttribute('y1', y1)
  l.setAttribute('x2', x2)
  l.setAttribute('y2', y2)
  l.setAttribute('stroke', col)
  l.setAttribute('stroke-width', w)
  l.setAttribute('stroke-linecap', 'round')
  els.stage.appendChild(l)
}
function circle (cx, cy, r, w = 6, col = '#eab308') {
  const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
  c.setAttribute('cx', cx)
  c.setAttribute('cy', cy)
  c.setAttribute('r', r)
  c.setAttribute('fill', 'none')
  c.setAttribute('stroke', col)
  c.setAttribute('stroke-width', w)
  els.stage.appendChild(c)
}

// ------------------ Events ------------------
els.newGame.addEventListener('click', newGame)
els.hintBtn.addEventListener('click', useHint)
// Exit button: close tab + stop server
els.exitBtn = document.getElementById('exitBtn')

els.exitBtn.addEventListener('click', async () => {
  // Ask confirmation using SweetAlert2
  const confirm = await Swal.fire({
    title: 'Exit Game?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Exit',
    cancelButtonText: 'Cancel',
    confirmButtonColor: '#ef4444'
  })

  if (!confirm.isConfirmed) return

  // request server shutdown
  try {
    await fetch('/shutdown')
  } catch (e) {
    console.log('Shutdown failed:', e)
  }

  // close current tab
  window.open('', '_self')
  window.close()
})

// start
newGame()
