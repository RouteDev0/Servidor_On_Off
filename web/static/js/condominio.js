async function atualizarStatusCondominio() {
  try {
    const urlParams = new URLSearchParams(window.location.search)
    let condominio = urlParams.get('condominio')

    if (!condominio) {
      const pathParts = window.location.pathname.split('/')
      condominio = decodeURIComponent(pathParts[pathParts.length - 1])
      if (!condominio) {
        throw new Error('Condomínio não especificado na URL')
      }
    }

    // Busca dados do condomínio
    const response = await fetch(`/status/${encodeURIComponent(condominio)}`)
    if (!response.ok) {
      throw new Error(
        `Erro na requisição: ${response.status} ${response.statusText}`
      )
    }
    const cameras = await response.json()
    if (!Array.isArray(cameras)) {
      throw new Error('Dados recebidos não são um array')
    }

    const on = cameras.filter((c) => c.status === 'ON').length
    const off = cameras.length - on

    // Atualiza barra de loading
    const total = on + off
    const percentOnline = total > 0 ? (on / total) * 100 : 0

    const progressContainer = document.getElementById('grafico-condominio')
    progressContainer.innerHTML = `
      <div class="loading-bar-container">
        <div class="loading-bar-track">
          <div class="loading-bar-fill-green" style="width: ${percentOnline}%"></div>
          <div class="loading-bar-fill-red" style="width: ${
            100 - percentOnline
          }%"></div>
        </div>
      </div>
    `

    // Renderiza listas de câmeras lado a lado
    const camerasContainer = document.getElementById('offline-cameras')
    camerasContainer.innerHTML = ''

    // Cria container com duas colunas
    const camerasGrid = document.createElement('div')
    camerasGrid.className = 'cameras-grid'

    // Coluna OFFLINE
    const offlineColumn = document.createElement('div')
    offlineColumn.className = 'camera-column offline-column'

    const offlineList = cameras
      .filter((c) => c.status === 'OFF')
      .sort((a, b) =>
        (a.nome || a.name || '').localeCompare(b.nome || b.name || '')
      )

    const offlineTitle = document.createElement('h3')
    const offlineCount = document.createElement('span')
    offlineCount.className = 'offline-count'
    offlineCount.textContent = off.toString()

    offlineTitle.textContent = '🔴 Câmeras Offline '
    offlineTitle.classList.add('offline-title')
    offlineTitle.appendChild(offlineCount)
    offlineColumn.appendChild(offlineTitle)

    if (offlineList.length > 0) {
      offlineList.forEach((cam) => {
        const linha = document.createElement('div')
        linha.classList.add('offline-line')
        linha.setAttribute('tabindex', '0')
        linha.setAttribute('role', 'listitem')
        linha.textContent = `${cam.nome || cam.name || 'Câmera sem nome'}`
        offlineColumn.appendChild(linha)
      })
    } else {
      const ok = document.createElement('div')
      ok.classList.add('offline-line', 'all-ok')
      ok.textContent = 'Nenhuma câmera offline'
      offlineColumn.appendChild(ok)
    }

    // Coluna ONLINE
    const onlineColumn = document.createElement('div')
    onlineColumn.className = 'camera-column online-column'

    const onlineList = cameras
      .filter((c) => c.status === 'ON')
      .sort((a, b) =>
        (a.nome || a.name || '').localeCompare(b.nome || b.name || '')
      )

    const onlineTitle = document.createElement('h3')
    const onlineCount = document.createElement('span')
    onlineCount.className = 'online-count'
    onlineCount.textContent = on.toString()

    onlineTitle.textContent = '🟢 Câmeras Online '
    onlineTitle.classList.add('online-title')
    onlineTitle.appendChild(onlineCount)
    onlineColumn.appendChild(onlineTitle)

    if (onlineList.length > 0) {
      onlineList.forEach((cam) => {
        const linha = document.createElement('div')
        linha.classList.add('online-line')
        linha.setAttribute('tabindex', '0')
        linha.setAttribute('role', 'listitem')
        linha.textContent = `${cam.nome || cam.name || 'Câmera sem nome'}`
        onlineColumn.appendChild(linha)
      })
    }

    // Adiciona as colunas ao grid
    camerasGrid.appendChild(offlineColumn)
    camerasGrid.appendChild(onlineColumn)
    camerasContainer.appendChild(camerasGrid)

    // Limpa loader
    const loadingContainer = document.getElementById('container-condominio')
    loadingContainer.innerHTML = ''
    loadingContainer.classList.remove('loading')
  } catch (err) {
    console.error('Erro ao buscar status do condomínio:', err.message)
    const loadingContainer = document.getElementById('container-condominio')
    loadingContainer.innerHTML = `Erro ao carregar dados do condomínio: ${err.message}`
    loadingContainer.classList.remove('loading')
  }
}

document.querySelector('.logo').addEventListener('click', () => {
  window.location.href = '/'
})

async function tentarCarregarDados() {
  await atualizarStatusCondominio()
  if (
    document
      .getElementById('container-condominio')
      .classList.contains('loading')
  ) {
    setTimeout(tentarCarregarDados, 5000)
  }
}

tentarCarregarDados()
setInterval(atualizarStatusCondominio, 600000) // 10 minutos
