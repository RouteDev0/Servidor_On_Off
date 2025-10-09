let graficoCondominio;

async function atualizarStatusCondominio() {
  try {
    const urlParams = new URLSearchParams(window.location.search);
    let condominio = urlParams.get('condominio');

    if (!condominio) {
      const pathParts = window.location.pathname.split('/');
      condominio = decodeURIComponent(pathParts[pathParts.length - 1]);
      if (!condominio) {
        throw new Error('Condomínio não especificado na URL');
      }
    }

    // Busca dados do condomínio
    const response = await fetch(`/status/${encodeURIComponent(condominio)}`);
    if (!response.ok) {
      throw new Error(`Erro na requisição: ${response.status} ${response.statusText}`);
    }
    const cameras = await response.json();
    if (!Array.isArray(cameras)) {
      throw new Error('Dados recebidos não são um array');
    }

    const on = cameras.filter(c => c.status === "ON").length;
    const off = cameras.length - on;

    // Atualiza gráfico
    const ctx = document.getElementById('grafico-condominio').getContext('2d');
    const dados = {
      labels: ['Online', 'Offline'],
      datasets: [{
        data: [on, off],
        backgroundColor: ['#00ff66', '#ff3333'],
        borderColor: ['#111', '#111'],
        borderWidth: 2
      }]
    };

    if (graficoCondominio) {
      graficoCondominio.data = dados;
      graficoCondominio.update();
    } else {
      graficoCondominio = new Chart(ctx, {
        type: 'doughnut',
        data: dados,
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: 'white' }
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const total = on + off;
                  const val = context.parsed;
                  const percent = ((val / total) * 100).toFixed(1);
                  return `${context.label}: ${val} (${percent}%)`;
                }
              }
            }
          }
        }
      });
    }

    // Renderiza lista de câmeras OFF
    const offlineContainer = document.getElementById('offline-cameras');
    offlineContainer.innerHTML = '';

    const offlineList = cameras
      .filter(c => c.status === "OFF")
      .sort((a, b) => (a.nome || a.name || '').localeCompare(b.nome || b.name || ''));

    const titulo = document.createElement('h3');
    const count = document.createElement('span');
    count.className = 'offline-count';
    count.textContent = off.toString();

    titulo.textContent = "🔴 Câmeras Offline";
    titulo.classList.add("offline-title");
    titulo.appendChild(count);
    offlineContainer.appendChild(titulo);

    if (offlineList.length > 0) {
      offlineList.forEach((cam) => {
        const linha = document.createElement('div');
        linha.classList.add("offline-line");
        linha.setAttribute('tabindex', '0');
        linha.setAttribute('role', 'listitem');
        linha.textContent = `${cam.nome || cam.name || "Câmera sem nome"}`;
        offlineContainer.appendChild(linha);
      });
    } else {
      const ok = document.createElement('div');
      ok.classList.add('offline-line', 'all-ok');
      ok.textContent = 'Nenhuma câmera offline';
      offlineContainer.appendChild(ok);
    }

    // Limpa loader
    const container = document.getElementById('container-condominio');
    container.innerHTML = '';
    container.classList.remove('loading');

  } catch (err) {
    console.error('Erro ao buscar status do condomínio:', err.message);
    const container = document.getElementById('container-condominio');
    container.innerHTML = `Erro ao carregar dados do condomínio: ${err.message}`;
    container.classList.remove('loading');
  }
}

document.querySelector('.logo').addEventListener('click', () => {
  window.location.href = '/';
});

async function tentarCarregarDados() {
  await atualizarStatusCondominio();
  if (document.getElementById('container-condominio').classList.contains('loading')) {
    setTimeout(tentarCarregarDados, 5000);
  }
}

tentarCarregarDados();
setInterval(atualizarStatusCondominio, 600000); // 10 minutos