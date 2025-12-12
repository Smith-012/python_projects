const buttons = document.querySelectorAll('button[data-choice]')
const resBox = document.getElementById('result')
const pChoice = document.getElementById('pChoice')
const cChoice = document.getElementById('cChoice')
const playerScoreEl = document.getElementById('playerScore')
const compScoreEl = document.getElementById('computerScore')
const roundsEl = document.getElementById('rounds')
const modalBg = document.getElementById('modalBg')
const historyTable = document.getElementById('historyTable')

let playerScore = 0,
  compScore = 0,
  rounds = 0
let history = []

function flash (color) {
  resBox.style.background = color
  setTimeout(() => (resBox.style.background = '#0b1220'), 220)
}

async function play (choice) {
  const r = await fetch('/api/play', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ choice })
  })

  const data = await r.json()

  if (data.error) {
    Swal.fire('Error', data.error, 'error')
    return
  }

  rounds++
  pChoice.textContent = data.player_emoji
  cChoice.textContent = data.computer_emoji

  if (data.winner === 'Player') playerScore++
  if (data.winner === 'Computer') compScore++

  playerScoreEl.textContent = `You: ${playerScore}`
  compScoreEl.textContent = `Computer: ${compScore}`
  roundsEl.textContent = `Rounds: ${rounds}`

  resBox.textContent =
    data.winner === 'Tie'
      ? "It's a tie!"
      : data.winner === 'Player'
      ? `You win — ${data.detail}!`
      : `Computer wins — ${data.detail}!`

  flash(
    data.winner === 'Tie'
      ? '#fde68a'
      : data.winner === 'Player'
      ? '#a7f3d0'
      : '#fecaca'
  )

  history.push({
    round: rounds,
    player: data.player,
    computer: data.computer,
    winner: data.winner,
    detail: data.detail,
    pEmoji: data.player_emoji,
    cEmoji: data.computer_emoji
  })
}

function resetScores () {
  Swal.fire({
    title: 'Reset Scores?',
    text: 'This will clear all rounds and restart the game.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, reset!'
  }).then(result => {
    if (result.isConfirmed) {
      playerScore = 0
      compScore = 0
      rounds = 0
      history = []

      playerScoreEl.textContent = 'You: 0'
      compScoreEl.textContent = 'Computer: 0'
      roundsEl.textContent = 'Rounds: 0'
      pChoice.textContent = '—'
      cChoice.textContent = '—'
      resBox.textContent = 'Pick Rock, Paper, or Scissors to start.'

      Swal.fire('Reset!', 'The game has been restarted.', 'success')
    }
  })
}

function openHistory () {
  if (history.length === 0) {
    Swal.fire('No Rounds', 'Play at least one round!', 'info')
    return
  }

  historyTable.innerHTML = `
    <tr>
      <th>Round</th>
      <th>You</th>
      <th>Computer</th>
      <th>Winner</th>
      <th>Detail</th>
    </tr>
  `

  history.forEach(h => {
    historyTable.insertAdjacentHTML(
      'beforeend',
      `
      <tr>
        <td>${h.round}</td>
        <td>${h.pEmoji} ${h.player}</td>
        <td>${h.cEmoji} ${h.computer}</td>
        <td>${h.winner}</td>
        <td>${h.detail}</td>
      </tr>
    `
    )
  })

  modalBg.style.display = 'flex'
}

function closeHistory () {
  modalBg.style.display = 'none'
}

// Buttons
buttons.forEach(b => b.addEventListener('click', () => play(b.dataset.choice)))

document.getElementById('resetBtn').addEventListener('click', resetScores)

document.getElementById('rulesBtn').addEventListener('click', () => {
  Swal.fire({
    title: 'Rules',
    html: `
      • Rock beats Scissors<br>
      • Scissors beat Paper<br>
      • Paper beats Rock<br><br>
      Click a button or press R/P/S.
    `,
    icon: 'info',
    confirmButtonText: 'OK'
  })
})

document.getElementById('historyBtn').addEventListener('click', openHistory)
document.getElementById('closeModal').addEventListener('click', closeHistory)

modalBg.addEventListener('click', e => {
  if (e.target === modalBg) closeHistory()
})

// Keyboard shortcuts
document.addEventListener('keydown', e => {
  if (['r', 'R'].includes(e.key)) play('Rock')
  if (['p', 'P'].includes(e.key)) play('Paper')
  if (['s', 'S'].includes(e.key)) play('Scissors')
  if (e.key === 'Escape') closeHistory()
})
