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

async function atualizarStatus() {
  try {
    const response = await fetch('/status')
    const data = await response.json()

    const container = document.getElementById('container-condominios')
    container.innerHTML = ''
    container.classList.remove('loading')

    let totalOn = 0
    let totalOff = 0

    for (const cameras of Object.values(data)) {
      totalOn += cameras.filter((c) => c.status === 'ON').length
      totalOff += cameras.filter((c) => c.status === 'OFF').length
    }

    // Atualiza contadores
    document.getElementById('total-on').textContent = totalOn
    document.getElementById('total-off').textContent = totalOff

    // Atualiza barras dinâmicas
    updateCameraBars(totalOn, totalOff)

    // Ordena condomínios: primeiro os com offline (por número decrescente), depois os sem offline
    const condominiosOrdenados = Object.entries(data).sort(
      ([nomeA, camerasA], [nomeB, camerasB]) => {
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

    // Renderiza texto por condomínio
    for (const [condominio, cameras] of condominiosOrdenados) {
      const div = document.createElement('div')
      div.classList.add('condominio')
      div.addEventListener('click', () => {
        window.location.href = `/condominio/${encodeURIComponent(
          condominio
        )}?condominio=${encodeURIComponent(condominio)}`
      })

      const on = cameras.filter((c) => c.status === 'ON').length
      const off = cameras.length - on

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
  } catch (err) {
    console.error('Erro ao buscar status:', err)
    const container = document.getElementById('container-condominios')
    container.innerHTML = 'Erro ao carregar dados.'
    container.classList.remove('loading')
  }
}
document.addEventListener('DOMContentLoaded', () => {
  // O nome do usuário já é renderizado pelo Jinja no HTML
})

atualizarStatus()
setInterval(atualizarStatus, 600000) // Atualiza a cada 10 minutos
