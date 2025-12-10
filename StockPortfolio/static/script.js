// ---- Config ----
const CURRENCY = '₹'

// ---- State ----
let rows = [] // {symbol, qty, price, value}
let ALL_SYMBOLS = []

// ---- Elements ----
const els = {
  select: document.getElementById('symbolSelect'),
  qty: document.getElementById('qty'),
  addBtn: document.getElementById('addBtn'),
  clearBtn: document.getElementById('clearBtn'),
  exitBtn: document.getElementById('exitBtn'),
  tableBody: document.querySelector('#table tbody'),
  total: document.getElementById('total'),
  saveCsv: document.getElementById('saveCsv'),
  saveTxt: document.getElementById('saveTxt'),
  jumpBar: document.getElementById('jumpBar')
}

// ---- SweetAlert2 helpers ----
function toast (msg, icon = 'info') {
  Swal.fire({
    toast: true,
    position: 'top-end',
    icon,
    title: msg,
    timer: 1700,
    showConfirmButton: false,
    timerProgressBar: true
  })
}

// ---- Load NSE symbols (runtime, no static list) ----
async function loadSymbols () {
  try {
    const r = await fetch('/api/symbols', { cache: 'no-store' })
    const j = await r.json()
    if (!r.ok) throw new Error(j.error || 'Failed to load symbols')
    ALL_SYMBOLS = j
    renderSelect()
    buildJumpBar()
  } catch (e) {
    els.select.innerHTML = `<option>Error loading symbols</option>`
    console.error(e)
  }
}

function renderSelect () {
  els.select.innerHTML = ''
  const frag = document.createDocumentFragment()
  ALL_SYMBOLS.forEach(s => {
    const opt = document.createElement('option')
    opt.value = s
    opt.textContent = s
    frag.appendChild(opt)
  })
  els.select.appendChild(frag)
  if (ALL_SYMBOLS.length) els.select.value = ALL_SYMBOLS[0]
}

// ---- Quick-Jump like GUI ----
function buildJumpBar () {
  els.jumpBar.innerHTML = ''
  '0123456789'.split('').forEach(d => addJumpBtn(d))
  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').forEach(ch => addJumpBtn(ch))
}

function addJumpBtn (prefix) {
  const b = document.createElement('button')
  b.textContent = prefix
  b.addEventListener('click', () => jumpToPrefix(prefix))
  els.jumpBar.appendChild(b)
}

function jumpToPrefix (prefix) {
  const p = prefix.toUpperCase()
  const idx = ALL_SYMBOLS.findIndex(s => s.startsWith(p))
  if (idx >= 0) {
    els.select.selectedIndex = idx // native select jumps to that item
    els.select.focus()
  }
}

// ---- Fetch live price from backend ----
async function fetchPrice (symbol) {
  const r = await fetch(`/api/quote?symbol=${encodeURIComponent(symbol)}`)
  const j = await r.json()
  if (!r.ok) throw new Error(j.error || 'Quote failed')
  return Number(j.price)
}

// ---- Actions ----
async function addRow () {
  const sym = (els.select.value || '').trim().toUpperCase()
  const qty = parseFloat(els.qty.value)
  if (!sym) return toast('Choose a symbol', 'warning')
  if (!(qty > 0)) return toast('Quantity must be > 0', 'warning')

  els.addBtn.disabled = true
  try {
    const price = await fetchPrice(sym)
    const value = price * qty
    rows.push({ symbol: sym, qty, price, value })
    render()
  } catch (e) {
    Swal.fire({
      title: 'Quote Error',
      text: String(e),
      icon: 'error',
      confirmButtonColor: '#ef4444'
    })
  } finally {
    els.addBtn.disabled = false
  }
}

function removeRow (i) {
  rows.splice(i, 1)
  render()
}

function clearRows () {
  if (!rows.length) return
  Swal.fire({
    title: 'Clear all items?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Clear',
    confirmButtonColor: '#ef4444'
  }).then(res => {
    if (res.isConfirmed) {
      rows = []
      render()
    }
  })
}

function calcTotal () {
  return rows.reduce((a, b) => a + Number(b.value), 0)
}

function render () {
  els.tableBody.innerHTML = rows
    .map(
      (r, i) => `
      <tr>
        <td>${r.symbol}</td>
        <td style="text-align:right">${r.qty}</td>
        <td style="text-align:right">${r.price.toFixed(2)}</td>
        <td style="text-align:right">${r.value.toFixed(2)}</td>
        <td><button class="remove" onclick="removeRow(${i})">Remove</button></td>
      </tr>`
    )
    .join('')
  els.total.textContent = `Total: ${CURRENCY}${calcTotal().toFixed(2)}`
}

// ---- Export via backend ----
async function exportFile (fmt = 'csv') {
  if (!rows.length) return toast('Nothing to save', 'info')
  const payload = { rows, fmt, total: calcTotal() }
  const r = await fetch('/api/export', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!r.ok) return toast('Export failed', 'error')

  const blob = await r.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `portfolio.${fmt === 'txt' ? 'txt' : 'csv'}`
  document.body.appendChild(a)
  a.click()
  URL.revokeObjectURL(url)
  a.remove()
  toast('File downloaded', 'success')
}

// ---- Exit ----
async function exitApp () {
  const res = await Swal.fire({
    title: 'Are you Sure?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Exit',
    confirmButtonColor: '#ef4444'
  })
  if (!res.isConfirmed) return
  try {
    await fetch('/shutdown')
  } catch {}
  window.open('', '_self')
  window.close()
}

// ---- Events ----
els.addBtn.addEventListener('click', addRow)
els.clearBtn.addEventListener('click', clearRows)
els.saveCsv.addEventListener('click', () => exportFile('csv'))
els.saveTxt.addEventListener('click', () => exportFile('txt'))
els.exitBtn.addEventListener('click', exitApp)
els.qty.addEventListener('keydown', e => {
  if (e.key === 'Enter') addRow()
})

// expose for inline onclick
window.removeRow = removeRow

// init
loadSymbols()
