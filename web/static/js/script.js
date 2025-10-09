// Função para atualizar barras de câmeras dinamicamente
function updateCameraBars(onlineCameras, offlineCameras) {
  const totalCameras = onlineCameras + offlineCameras

  if (totalCameras === 0) {
    createProgressBar(0, 0)
    return
  }

  const greenPercentage = (onlineCameras / totalCameras) * 100
  const redPercentage = (offlineCameras / totalCameras) * 100

  createProgressBar(greenPercentage, redPercentage)
}

function createProgressBar(greenPercent, redPercent) {
  const progressContainer = document.getElementById('grafico-total')
  progressContainer.innerHTML = `
    <div class="loading-bar-container">
      <div class="loading-bar-track">
        <div class="loading-bar-fill-green" style="width: ${greenPercent}%"></div>
        <div class="loading-bar-fill-red" style="width: ${redPercent}%"></div>
      </div>
    </div>
  `
}

let dadosGlobais = null

async function atualizarStatus() {
  try {
    const response = await fetch('/status')
    const data = await response.json()
    dadosGlobais = data

    let totalOn = 0
    let totalOff = 0

    for (const condominioData of Object.values(data)) {
      const cameras = condominioData.cameras || condominioData
      totalOn += cameras.filter((c) => c.status === 'ON').length
      totalOff += cameras.filter((c) => c.status === 'OFF').length
    }

    // Atualiza contadores
    document.getElementById('total-on').textContent = totalOn
    document.getElementById('total-off').textContent = totalOff

    // Atualiza barras dinâmicas
    updateCameraBars(totalOn, totalOff)

    // Renderiza com filtros aplicados
    renderizarCondominios()
  } catch (err) {
    console.error('Erro ao buscar status:', err)
    const container = document.getElementById('container-condominios')
    container.innerHTML = 'Erro ao carregar dados.'
    container.classList.remove('loading')
  }
}

function renderizarCondominios() {
  if (!dadosGlobais) return

  const container = document.getElementById('container-condominios')
  container.innerHTML = ''
  container.classList.remove('loading')

  // Verifica se os filtros existem antes de acessá-los
  const statusFilterElement = document.getElementById('status-filter')
  const typeFilterElement = document.getElementById('type-filter')

  const statusFilter = statusFilterElement
    ? statusFilterElement.value
    : 'offline'
  const typeFilter = typeFilterElement ? typeFilterElement.value : 'all'

  // Ordena condomínios: primeiro os com offline (por número decrescente), depois os sem offline
  const condominiosOrdenados = Object.entries(dadosGlobais).sort(
    ([nomeA, condominioDataA], [nomeB, condominioDataB]) => {
      const camerasA = condominioDataA.cameras || condominioDataA
      const camerasB = condominioDataB.cameras || condominioDataB

      const offA = camerasA.filter((c) => c.status === 'OFF').length
      const offB = camerasB.filter((c) => c.status === 'OFF').length

      // Se um tem offline e outro não, prioriza o que tem offline
      if (offA > 0 && offB === 0) return -1
      if (offA === 0 && offB > 0) return 1

      // Se ambos têm offline, ordena por maior número de offline
      if (offA > 0 && offB > 0) return offB - offA

      // Se ambos não têm offline, ordena alfabeticamente
      return nomeA.localeCompare(nomeB)
    }
  )

  // Renderiza condomínios com filtros aplicados
  for (const [condominio, condominioData] of condominiosOrdenados) {
    const cameras = condominioData.cameras || condominioData
    const metadata = condominioData.metadata || {}

    const on = cameras.filter((c) => c.status === 'ON').length
    const off = cameras.length - on

    // Filtro de tipo (baseado no código da empresa) - aplicado primeiro
    if (typeFilter !== 'all') {
      const codigoEmpresa = metadata.empresa

      // Debug simplificado
      const passa = codigoEmpresa?.toString() === typeFilter
      console.log(
        `${
          passa ? '✅' : '❌'
        } ${condominio} - Empresa: ${codigoEmpresa} (Filtro: ${typeFilter})`
      )

      if (codigoEmpresa?.toString() !== typeFilter) continue
    }

    // Filtro de status (aplicado após o filtro de tipo)
    if (statusFilter === 'offline' && off === 0) continue

    const div = document.createElement('div')
    div.classList.add('condominio')
    div.addEventListener('click', () => {
      window.location.href = `/condominio/${encodeURIComponent(
        condominio
      )}?condominio=${encodeURIComponent(condominio)}`
    })

    const h2 = document.createElement('h2')
    h2.textContent = condominio
    div.appendChild(h2)

    if (off > 0) {
      const p = document.createElement('p')
      p.classList.add('totais')
      p.innerHTML = `🔴 <span class="off">${off} offline</span>`
      div.appendChild(p)
    }

    container.appendChild(div)
  }
}
document.addEventListener('DOMContentLoaded', () => {
  // Event listeners para os filtros (só adiciona se existirem)
  const statusFilter = document.getElementById('status-filter')
  const typeFilter = document.getElementById('type-filter')

  if (statusFilter) {
    statusFilter.addEventListener('change', renderizarCondominios)
  }

  if (typeFilter) {
    typeFilter.addEventListener('change', (e) => {
      // Quando selecionar Usinas ou Corporativo, muda automaticamente para "Todos"
      if (e.target.value !== 'all' && statusFilter) {
        statusFilter.value = 'all'
      }
      renderizarCondominios()
    })
  }
})

atualizarStatus()
setInterval(atualizarStatus, 600000) // Atualiza a cada 10 minutos
