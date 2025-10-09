let graficoTotal;

async function atualizarStatus() {
  try {
    const response = await fetch('/status');
    const data = await response.json();

    const container = document.getElementById('container-condominios');
    container.innerHTML = '';
    container.classList.remove('loading');

    let totalOn = 0;
    let totalOff = 0;

    for (const cameras of Object.values(data)) {
      totalOn += cameras.filter(c => c.status === "ON").length;
      totalOff += cameras.filter(c => c.status === "OFF").length;
    }

    // 👉 Adicione aqui:
    document.getElementById("total-on").textContent = totalOn;
    document.getElementById("total-off").textContent = totalOff;

    // Atualiza ou cria gráfico total
    const ctx = document.getElementById('grafico-total').getContext('2d');
    const dados = {
      labels: ['Online', 'Offline'],
      datasets: [{
        data: [totalOn, totalOff],
        backgroundColor: ['#00ff66', '#ff3333'],
        borderColor: ['#111', '#111'],
        borderWidth: 2
      }]
    };

    if (graficoTotal) {
      graficoTotal.data = dados;
      graficoTotal.update();
    } else {
      graficoTotal = new Chart(ctx, {
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
                  const total = totalOn + totalOff;
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

    // Renderiza texto por condomínio
    for (const [condominio, cameras] of Object.entries(data)) {
      const div = document.createElement('div');
      div.classList.add('condominio');
      div.addEventListener('click', () => {
        window.location.href = `/condominio/${encodeURIComponent(condominio)}?condominio=${encodeURIComponent(condominio)}`;
      });

      const on = cameras.filter(c => c.status === "ON").length;
      const off = cameras.length - on;

      const h2 = document.createElement('h2');
      h2.textContent = condominio;
      div.appendChild(h2);

      const p = document.createElement('p');
      p.classList.add('totais');
      p.innerHTML = `🟢 <span class="on">${on} online</span> | 🔴 <span class="off">${off} offline</span>`;
      div.appendChild(p);

      container.appendChild(div);
    }

  } catch (err) {
    console.error('Erro ao buscar status:', err);
    const container = document.getElementById('container-condominios');
    container.innerHTML = 'Erro ao carregar dados.';
    container.classList.remove('loading');
  }
}
document.addEventListener("DOMContentLoaded", () => {
  // O nome do usuário já é renderizado pelo Jinja no HTML
});

atualizarStatus();
setInterval(atualizarStatus, 600000); // Atualiza a cada 10 minutos