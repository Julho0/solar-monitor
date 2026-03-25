# ☀️ Solar Monitor

Projeto acadêmico (pré-TCC) desenvolvido no curso de **Ciência da Computação** para resolver um problema prático: **saber quando limpar os painéis solares sem precisar ficar adivinhando**.

A ideia surgiu em Caratinga-MG, onde o clima quente e a poeira do dia a dia afetam diretamente a eficiência de painéis fotovoltaicos. Em vez de seguir um calendário fixo de limpeza, o sistema usa dados reais de radiação solar e qualidade do ar para estimar quando a sujeira já está impactando a geração de energia — e te avisa antes que vire prejuízo.

## Como funciona

O sistema cruza dois dados em tempo real:

- **Radiação solar** via NASA POWER API — intensidade de luz que incidiu sobre os painéis nos últimos 7 dias
- **Nível de poeira PM10** via OpenWeatherMap — concentração de partículas que se depositam sobre o vidro

Com esses dados e a data da última limpeza, um modelo de decaimento exponencial estima a eficiência atual e projeta quando ela vai cair abaixo do limite recomendado.

> **Sobre o PM10:** A OpenWeatherMap usa modelo de satélite, não sensores físicos, e pode retornar valores baixos em cidades brasileiras. O sistema aplica um piso mínimo de 20 µg/m³ (média nacional brasileira) quando isso acontece — o valor bruto da API ainda aparece no dashboard para transparência.

## Funcionalidades

- 📊 Dashboard com curva de eficiência real + projeção de 120 dias
- 📍 Busca de qualquer cidade brasileira por nome
- 🗓️ Histórico de manutenções com eficiência registrada em cada limpeza
- 📧 Script de alerta por e-mail quando a eficiência cai abaixo do limite
- ☀️ Gráfico de radiação solar dos últimos 7 dias com código de cores
- 🔔 Previsão de quando a próxima limpeza será necessária

## Calibração do modelo

Calibrado com base em literatura científica para o clima tropical brasileiro:

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Alpha (α) | 0.00001 | 13% de perda em 90 dias com PM10=25 µg/m³ e radiação=6 kWh/m² |
| Limite de alerta | 87% | Perda de 13% — limiar recomendado para clima tropical úmido |
| PM10 mínimo | 20 µg/m³ | Média nacional brasileira (IQAir / dados CETESB) |
| Piso do modelo | 75% | Perdas acima de 25% são raras no Brasil com chuvas regulares |
| Teto de projeção | 365 dias | Acima de 1 ano a projeção não tem utilidade prática |

Perdas acima de 30% só são documentadas em **ambientes desérticos**. No Brasil, com chuvas que lavam os painéis naturalmente, a perda típica anual fica entre **2% e 15%** dependendo da região.

## Estrutura do projeto

```
solar-monitor/
├── api/
│   ├── __init__.py
│   ├── nasa_power.py       # Integração NASA POWER (radiação solar)
│   └── openweather.py      # Integração OpenWeather (poeira PM10/PM2.5)
├── utils/
│   ├── __init__.py
│   └── eficiencia.py       # Modelo de cálculo e gerenciamento de manutenção
├── .streamlit/
│   └── secrets.toml        # ⚠️ Não commitar — configurar no Streamlit Cloud
├── dashboard.py            # Interface Streamlit
├── alerta.py               # Script de alerta por e-mail
├── .env.example            # Template de variáveis de ambiente
├── .gitignore
├── requirements.txt
└── README.md
```

## Instalação

```bash
git clone https://github.com/seu-usuario/solar-monitor.git
cd solar-monitor

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
```

## Configuração

Crie o arquivo `.streamlit/secrets.toml`:

```toml
API_KEY_OW = "sua_chave_openweathermap_aqui"
```

Chave gratuita em: https://openweathermap.org/api

Para o script de e-mail, copie `.env.example` para `.env` e preencha com seus dados.

## Uso

```bash
# Rodar o dashboard
python -m streamlit run dashboard.py
```

Acesse `http://localhost:8501`. Na interface você pode buscar qualquer cidade, registrar limpezas e acompanhar o histórico.

```bash
# Rodar o alerta por e-mail (pode agendar com cron/Task Scheduler)
python alerta.py
```

## Deploy

Projeto disponível em: *[link do Streamlit Cloud após o deploy]*

Para rodar sua própria instância:
1. Fork este repositório
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório e adicione sua `API_KEY_OW` nos secrets
4. Clique em Deploy

## Tecnologias

- [Streamlit](https://streamlit.io/) — interface web
- [Plotly](https://plotly.com/python/) — gráficos interativos
- [NASA POWER API](https://power.larc.nasa.gov/) — radiação solar
- [OpenWeatherMap API](https://openweathermap.org/api/air-pollution) — qualidade do ar

## Autor

**Julio Gabriel** — Ciência da Computação

Projeto acadêmico (pré-TCC) desenvolvido com foco no contexto brasileiro de energia solar.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Julho-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/Julho0)
[![GitHub](https://img.shields.io/badge/GitHub-Julho0-181717?style=flat&logo=github)](https://github.com/Julho0)
