// ---------- Helpers ----------
function toast (msg, icon = 'info') {
  Swal.fire({
    toast: true,
    position: 'top-end',
    icon,
    title: msg,
    timer: 1800,
    showConfirmButton: false,
    timerProgressBar: true
  })
}
const IMAGE_EXTS = /\.(jpg|jpeg|png|gif|bmp|webp|tif|tiff|heic|heif|svg)$/i
const supportsFS = !!window.showDirectoryPicker

// ---------- State ----------
let srcHandle = null // FileSystemDirectoryHandle
let dstHandle = null // FileSystemDirectoryHandle
let previewList = [] // [{name, relPath, fileHandle, parentHandle}]
let lastMovePairs = [] // for undo [{srcParent, name, destParent, destName}]
let lastUrl = '',
  lastTitle = '',
  lastEmails = []

// ---------- UI refs ----------
const els = {
  pickSrc: document.getElementById('pickSrc'),
  pickDst: document.getElementById('pickDst'),
  srcLabel: document.getElementById('srcLabel'),
  dstLabel: document.getElementById('dstLabel'),
  includeSub: document.getElementById('includeSub'),
  previewBtn: document.getElementById('previewBtn'),
  moveAllBtn: document.getElementById('moveAllBtn'),
  moveSelectedBtn: document.getElementById('moveSelectedBtn'),
  previewBox: document.getElementById('previewBox'),
  undoBtn: document.getElementById('undoBtn'),
  emailText: document.getElementById('emailText'),
  extractBtn: document.getElementById('extractBtn'),
  downloadEmails: document.getElementById('downloadEmails'),
  emailResult: document.getElementById('emailResult'),
  url: document.getElementById('url'),
  titleBtn: document.getElementById('titleBtn'),
  saveTitleBtn: document.getElementById('saveTitleBtn'),
  titleOut: document.getElementById('titleOut'),
  exitBtn: document.getElementById('exitBtn')
}

// ---------- Folder pickers ----------
els.pickSrc.addEventListener('click', async () => {
  if (!supportsFS) {
    Swal.fire({
      title: 'Not supported',
      text: 'Please use Chrome/Edge/Brave.',
      icon: 'warning'
    })
    return
  }
  try {
    srcHandle = await showDirectoryPicker({ mode: 'readwrite' })
    els.srcLabel.textContent = srcHandle.name || 'Source selected'
  } catch (e) {}
})
els.pickDst.addEventListener('click', async () => {
  if (!supportsFS) {
    Swal.fire({
      title: 'Not supported',
      text: 'Please use Chrome/Edge/Brave.',
      icon: 'warning'
    })
    return
  }
  try {
    dstHandle = await showDirectoryPicker({ mode: 'readwrite' })
    els.dstLabel.textContent = dstHandle.name || 'Destination selected'
  } catch (e) {}
})

// ---------- Directory iteration ----------
async function* walkDir (dirHandle, parentPath = '') {
  for await (const [name, handle] of dirHandle.entries()) {
    const relPath = parentPath ? `${parentPath}/${name}` : name
    if (handle.kind === 'file') {
      if (IMAGE_EXTS.test(name)) {
        yield { name, relPath, fileHandle: handle, parentHandle: dirHandle }
      }
    } else if (handle.kind === 'directory') {
      yield {
        name,
        relPath,
        dirHandle: handle,
        parentHandle: dirHandle,
        isDir: true
      }
      yield* walkDir(handle, relPath)
    }
  }
}

async function listImages (includeSubfolders) {
  if (!srcHandle) throw new Error('Pick a source folder')
  previewList = []
  if (includeSubfolders) {
    for await (const entry of walkDir(srcHandle)) {
      if (entry.fileHandle) previewList.push(entry)
    }
  } else {
    for await (const [name, handle] of srcHandle.entries()) {
      if (handle.kind === 'file' && IMAGE_EXTS.test(name)) {
        previewList.push({
          name,
          relPath: name,
          fileHandle: handle,
          parentHandle: srcHandle
        })
      }
    }
  }
  return previewList
}

// ---------- Preview UI ----------
els.previewBtn.addEventListener('click', async () => {
  try {
    await listImages(els.includeSub.checked)
  } catch (e) {
    toast(e.message || String(e), 'warning')
    return
  }
  const box = els.previewBox
  if (!previewList.length) {
    box.style.display = 'block'
    box.textContent = els.includeSub.checked
      ? 'No images found in source (recursive).'
      : 'No images found in source root.'
    return
  }
  box.style.display = 'block'
  box.innerHTML = ''
  const sa = document.createElement('div')
  sa.className = 'line'
  sa.innerHTML = `<label class="ck"><input type="checkbox" id="selAll"> <span><b>Select all (${previewList.length})</b></span></label>`
  box.appendChild(sa)
  document.getElementById('selAll').addEventListener('change', e => {
    const on = e.target.checked
    document
      .querySelectorAll('#previewBox input[type=checkbox].sel')
      .forEach(c => (c.checked = on))
  })
  previewList.forEach((it, idx) => {
    const d = document.createElement('div')
    d.className = 'line'
    d.innerHTML = `<label class="ck"><input class="sel" type="checkbox" data-index="${idx}"><span>${it.relPath}</span></label>`
    box.appendChild(d)
  })
})

// ---------- Move core (copy then delete) ----------
async function ensureUniqueFile (destDir, name) {
  // returns {handle, finalName}
  let base = name,
    ext = ''
  const dot = name.lastIndexOf('.')
  if (dot !== -1) {
    base = name.slice(0, dot)
    ext = name.slice(dot)
  }
  let final = name
  let i = 1
  while (true) {
    try {
      const h = await destDir.getFileHandle(final, { create: false })
      // exists, try next
      i += 1
      final = `${base}_${i}${ext}`
    } catch {
      // doesn't exist: create it
      const handle = await destDir.getFileHandle(final, { create: true })
      return { handle, finalName: final }
    }
  }
}

async function moveOne (item) {
  // read file
  const file = await item.fileHandle.getFile()
  // create destination
  const { handle: destFileHandle, finalName } = await ensureUniqueFile(
    dstHandle,
    item.name
  )
  // write
  const writable = await destFileHandle.createWritable()
  await writable.write(await file.arrayBuffer())
  await writable.close()
  // delete original (from its parent directory)
  await item.parentHandle.removeEntry(item.name)
  // record for undo
  lastMovePairs.push({
    srcParent: item.parentHandle,
    name: item.name,
    destParent: dstHandle,
    destName: finalName
  })
}

async function moveMany (items) {
  if (!dstHandle) throw new Error('Pick a destination folder')
  lastMovePairs = []
  let moved = 0
  for (const it of items) {
    try {
      await moveOne(it)
      moved += 1
    } catch (e) {
      /* skip one */
    }
  }
  return moved
}

// ---------- Actions ----------
els.moveAllBtn.addEventListener('click', async () => {
  if (!srcHandle || !dstHandle) {
    toast('Pick both source and destination', 'warning')
    return
  }
  try {
    await listImages(els.includeSub.checked)
    if (!previewList.length) {
      toast(
        els.includeSub.checked
          ? 'No images found in source (recursive)'
          : 'No images in source root',
        'info'
      )
      return
    }
    const moved = await moveMany(previewList)
    toast(`Moved ${moved} file(s)`, 'success')
  } catch (e) {
    Swal.fire({ title: 'Move failed', text: String(e), icon: 'error' })
  }
})

els.moveSelectedBtn.addEventListener('click', async () => {
  if (!srcHandle || !dstHandle) {
    toast('Pick both source and destination', 'warning')
    return
  }
  const checkedIdx = [
    ...document.querySelectorAll('#previewBox input.sel:checked')
  ]
    .map(i => Number(i.dataset.index))
    .filter(i => !Number.isNaN(i))
  if (!checkedIdx.length) {
    toast('Select files in preview', 'info')
    return
  }
  const subset = checkedIdx.map(i => previewList[i])
  try {
    const moved = await moveMany(subset)
    toast(`Moved ${moved} selected file(s)`, 'success')
  } catch (e) {
    Swal.fire({ title: 'Move failed', text: String(e), icon: 'error' })
  }
})

els.undoBtn.addEventListener('click', async () => {
  if (!lastMovePairs.length) {
    toast('Nothing to undo', 'info')
    return
  }
  let restored = 0
  for (let i = lastMovePairs.length - 1; i >= 0; i--) {
    const p = lastMovePairs[i]
    try {
      // read from dest
      const destFile = await p.destParent.getFileHandle(p.destName, {
        create: false
      })
      const file = await (await destFile.getFile()).arrayBuffer()

      // ensure original slot (or _restored_N)
      let base = p.name,
        ext = ''
      const dot = p.name.lastIndexOf('.')
      if (dot !== -1) {
        base = p.name.slice(0, dot)
        ext = p.name.slice(dot)
      }
      let targetName = p.name
      let n = 1
      while (true) {
        try {
          await p.srcParent.getFileHandle(targetName, { create: false })
          // exists -> try restored_N
          targetName = `${base}_restored_${n}${ext}`
          n++
        } catch {
          break
        }
      }
      const targetHandle = await p.srcParent.getFileHandle(targetName, {
        create: true
      })
      const w = await targetHandle.createWritable()
      await w.write(file)
      await w.close()

      // delete from dest
      await p.destParent.removeEntry(p.destName)
      restored += 1
    } catch (e) {
      /* skip */
    }
  }
  lastMovePairs = []
  toast(`Restored ${restored} file(s)`, 'success')
})

// ---------- Emails ----------
els.extractBtn.addEventListener('click', async () => {
  const text = els.emailText.value
  try {
    const r = await fetch('/api/extract_emails', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    })
    const j = await r.json()
    if (!r.ok) throw new Error(j.error || 'Extraction failed')
    lastEmails = j.emails || []
    els.emailResult.textContent =
      `Found ${j.count} email(s):\n\n` + lastEmails.join('\n')
  } catch (e) {
    toast(String(e), 'error')
  }
})
els.downloadEmails.addEventListener('click', () => {
  if (!lastEmails.length) {
    toast('Nothing to download', 'info')
    return
  }
  const blob = new Blob([lastEmails.join('\n')], {
    type: 'text/plain;charset=utf-8'
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'emails.txt'
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
})

// ---------- Title ----------
els.titleBtn.addEventListener('click', async () => {
  const url = els.url.value.trim()
  if (!url) {
    toast('Enter a URL', 'warning')
    return
  }
  try {
    const r = await fetch(`/api/scrape_title?url=${encodeURIComponent(url)}`)
    const j = await r.json()
    if (!r.ok) throw new Error(j.error || 'Failed')
    lastUrl = url
    lastTitle = j.title || ''
    els.titleOut.textContent = `URL: ${lastUrl}\nTitle: ${lastTitle}`
  } catch (e) {
    Swal.fire({ title: 'Scrape failed', text: String(e), icon: 'error' })
  }
})
els.saveTitleBtn.addEventListener('click', async () => {
  if (!lastUrl || !lastTitle) {
    toast('Get a title first', 'info')
    return
  }
  const r = await fetch('/api/export_title', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: lastUrl, title: lastTitle })
  })
  if (!r.ok) {
    toast('Download failed', 'error')
    return
  }
  const blob = await r.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'page_title.txt'
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
})

// ---------- Exit ----------
els.exitBtn.addEventListener('click', async () => {
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
  } catch (e) {}
  window.open('', '_self')
  window.close()
})
