# 🎥 Sistema de Monitoramento de Câmeras

Sistema de monitoramento e verificação de status de câmeras IP em tempo real.

## 🚀 Funcionalidades

- ✅ Monitoramento em tempo real de câmeras IP
- ✅ Verificação de status via RTSP
- ✅ Interface web responsiva
- ✅ Sistema de alertas automático
- ✅ Suporte a múltiplos condomínios
- ✅ Processamento paralelo
- ✅ Cache inteligente

## 📁 Estrutura do Projeto

```
📦 servidor_ping/
├── 🚀 app/                          # Aplicação principal
│   ├── 📄 main.py                   # Entry point da aplicação
│   ├── 📄 alert.py                  # Sistema de alertas
│   ├── 📁 core/                     # Núcleo da aplicação
│   ├── 📁 services/                 # Serviços da aplicação
│   ├── 📁 utils/                    # Utilitários
│   └── 📁 data/                     # Dados da aplicação
│       └── 📁 condominios/          # Arquivos JSON dos condomínios
├── 🌐 web/                          # Interface web
│   ├── 📁 static/                   # Arquivos estáticos
│   │   ├── 📄 css/                  # Estilos CSS
│   │   ├── 📄 js/                   # Scripts JavaScript
│   │   └── 📁 images/               # Imagens
│   └── 📁 templates/                # Templates HTML
├── 📄 requirements.txt              # Dependências Python
├── 📄 config.py                     # Configurações globais
└── 📄 README.md                     # Documentação
```

## 🛠️ Instalação

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd servidor_ping
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as câmeras**
- Adicione os arquivos JSON dos condomínios em `app/data/condominios/`
- Configure as URLs RTSP das câmeras

4. **Execute a aplicação**
```bash
python app/main.py
```

## ⚙️ Configuração

### Arquivo de Configuração (`config.py`)

```python
# Configurações de autenticação
USUARIO = "admin"
SENHA = "1234"

# Configurações do servidor
HOST = "0.0.0.0"
PORT = 8080

# Configurações de verificação
TIMEOUT_VERIFICACAO = 8  # segundos
TENTATIVAS_VERIFICACAO = 3
INTERVALO_VERIFICACAO = 600  # segundos
```

### Estrutura JSON dos Condomínios

```json
{
  "cliente": "9317",
  "particao": "01",
  "empresa": 1,
  "ocorrencia": 960,
  "codigomaquina": 1,
  "codigoconjuntodeocorrencias": 1,
  "cameras": [
    {
      "name": "Camera 1",
      "rtsp": "rtsp://admin:senha@ip:porta/stream",
      "identificacao": "CamGaragem01",
      "setor": 1,
      "complemento": "Camera 1"
    }
  ]
}
```

## 🌐 Uso

1. **Acesse a interface web**
   - URL: `http://localhost:8080`
   - Usuário: `admin`
   - Senha: `1234`

2. **Visualize o status das câmeras**
   - Página inicial mostra todos os condomínios
   - Clique em um condomínio para ver detalhes

3. **Monitoramento automático**
   - O sistema verifica as câmeras a cada 10 minutos
   - Alertas são enviados automaticamente

## 🔧 Desenvolvimento

### Estrutura de Código

- **`app/main.py`**: Aplicação Flask principal
- **`app/alert.py`**: Sistema de envio de alertas
- **`app/core/`**: Lógica de validação de câmeras
- **`app/services/`**: Serviços da aplicação
- **`app/utils/`**: Utilitários e helpers

### Adicionando Novas Funcionalidades

1. **Novos serviços**: Adicione em `app/services/`
2. **Utilitários**: Adicione em `app/utils/`
3. **Validações**: Adicione em `app/core/`
4. **Interface**: Modifique `web/templates/` e `web/static/`

## 📊 Monitoramento

O sistema monitora:
- ✅ Status online/offline das câmeras
- ✅ Conectividade RTSP
- ✅ Qualidade do stream de vídeo
- ✅ Alertas automáticos

## 🚨 Alertas

Os alertas são enviados para:
- API externa configurável
- Logs do sistema
- Interface web em tempo real

## 📝 Logs

O sistema gera logs para:
- Verificações de câmeras
- Alertas enviados
- Erros de conexão
- Performance do sistema

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 👥 Suporte

Para suporte, entre em contato através de:
- Email: [seu-email]
- Issues: [url-do-github] 