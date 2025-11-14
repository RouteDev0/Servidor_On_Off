// Ajusta dinamicamente as larguras das barras verde e vermelha com base em online/offline
;(function () {
  // Seletor dos elementos - ajuste se necessário
  const greenBar = document.querySelector('.loading-bar-fill-green')
  const redBar = document.querySelector('.loading-bar-fill-red')
  const statusText = document.querySelector('.resumo-geral')

  // Se os elementos não existirem, não faz nada
  if (!greenBar || !redBar) return

  // EXEMPLO: dados estáticos. Substitua por dados dinâmicos se desejar
  let onlineCameras = 28
  let offlineCameras = 4

  // Função que aplica as larguras garantindo soma de 100%
  function atualizarBarras(online, offline) {
    const total = (Number(online) || 0) + (Number(offline) || 0)

    // Se total for zero, definiu ambos como 0 e aplica 0/100 ou 100/0 conforme preferir
    if (total === 0) {
      greenBar.style.width = '100%'
      redBar.style.width = '0%'
      if (statusText) statusText.innerHTML = 'Nenhuma câmera configurada'
      return
    }

    // Cálculo de porcentagens bruto
    let greenPct = (online / total) * 100
    let redPct = (offline / total) * 100

    // Ajuste para problemas de arredondamento: garante soma exata de 100
    // Arredondamos para uma casa decimal (pode ser integer se preferir)
    const greenRounded = Math.round(greenPct * 10) / 10
    let redRounded = Math.round(redPct * 10) / 10

    // Corrige pequeno erro de soma por arredondamento
    const diff = 100 - (greenRounded + redRounded)
    if (Math.abs(diff) >= 0.1) {
      // Se diferença grande, ajusta red
      redRounded = +(redRounded + diff).toFixed(1)
    } else {
      // Pequena correção trivial
      redRounded = +(redRounded + diff).toFixed(1)
    }

    // Garantir não-negatividade
    if (greenRounded < 0) greenRounded = 0
    if (redRounded < 0) redRounded = 0

    // Aplicar estilos
    greenBar.style.width = `${greenRounded}%`
    redBar.style.width = `${redRounded}%`

    // Atualiza texto de resumo se existir
    if (statusText) {
      statusText.innerHTML = `<span class=\"on\">${online} câmeras online</span> | <span class=\"off\">${offline} câmeras offline</span>`
    }
  }

  // Inicializa com os valores de exemplo
  atualizarBarras(onlineCameras, offlineCameras)

  // Exporta função globalmente para permitir atualizações externas
  window.atualizarBarras = atualizarBarras
})()
