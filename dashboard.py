import streamlit as st
import plotly.graph_objects as go
import requests
from datetime import datetime

from api import get_nivel_poeira, get_radiacao_solar
from utils import (
    calcular_eficiencia,
    prever_proxima_manutencao,
    gerar_curva_eficiencia,
    carregar_manutencao,
    salvar_manutencao,
    carregar_historico,
    salvar_historico,
    EFICIENCIA_MINIMA,
    LIMITE_ALERTA,
)

st.set_page_config(
    page_title="Solar Monitor",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo customizado — quis fugir do visual padrão do Streamlit
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
    background-color: #060910 !important;
    color: #e8eaf0 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px; }

section[data-testid="stSidebar"] {
    background: #0b0f1a !important;
    border-right: 1px solid rgba(251,176,52,0.12) !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

.sidebar-logo {
    background: linear-gradient(135deg, #fbb034 0%, #ff6b35 100%);
    padding: 1.5rem 1.2rem 1.2rem;
}
.sidebar-logo-title {
    font-size: 1.1rem; font-weight: 800; color: #060910;
    letter-spacing: -0.3px; line-height: 1.2; margin: 0.3rem 0 0;
}
.sidebar-logo-sub {
    font-size: 0.7rem; color: rgba(6,9,16,0.65); font-weight: 500;
    text-transform: uppercase; letter-spacing: 1.5px; margin: 0;
}
.sidebar-section {
    padding: 1rem 1.2rem 0.4rem;
    font-size: 0.65rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px;
    color: rgba(251,176,52,0.5);
}

section[data-testid="stSidebar"] label {
    font-size: 0.8rem !important;
    color: rgba(232,234,240,0.6) !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #e8eaf0 !important; border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
}
section[data-testid="stSidebar"] input:focus {
    border-color: rgba(251,176,52,0.4) !important;
    box-shadow: 0 0 0 2px rgba(251,176,52,0.1) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #fbb034, #ff6b35) !important;
    color: #060910 !important; border: none !important;
    border-radius: 10px !important; font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important; font-size: 0.85rem !important;
    padding: 0.6rem 1rem !important;
    box-shadow: 0 4px 15px rgba(251,176,52,0.25) !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(251,176,52,0.35) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(251,176,52,0.08) !important;
    color: #fbb034 !important;
    border: 1px solid rgba(251,176,52,0.25) !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important; font-size: 0.82rem !important;
}

.main-header {
    position: relative; padding: 2.5rem 3rem; margin-bottom: 2rem;
    border-radius: 20px; overflow: hidden;
    background: linear-gradient(135deg, #0d1420 0%, #111827 60%, #0a1628 100%);
    border: 1px solid rgba(251,176,52,0.15);
}
.main-header::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(251,176,52,0.18) 0%, transparent 65%);
    border-radius: 50%;
}
.header-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(251,176,52,0.12); border: 1px solid rgba(251,176,52,0.25);
    border-radius: 100px; padding: 4px 12px;
    font-size: 0.7rem; font-weight: 600; color: #fbb034;
    text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1rem;
}
.header-dot {
    width: 6px; height: 6px; background: #fbb034; border-radius: 50%;
    animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.7); }
}
.header-title {
    font-size: 2.4rem; font-weight: 800; color: #fff;
    margin: 0 0 0.5rem; letter-spacing: -1px; line-height: 1.1;
}
.header-title span { color: #fbb034; }
.header-sub { font-size: 0.95rem; color: rgba(232,234,240,0.45); font-weight: 400; margin: 0; }

.kpi-card {
    background: linear-gradient(145deg, #0e1520, #111827);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 1.4rem 1.6rem;
    position: relative; overflow: hidden;
    transition: border-color 0.3s, transform 0.2s;
    height: 128px; display: flex; flex-direction: column; justify-content: space-between;
}
.kpi-card:hover { border-color: rgba(251,176,52,0.25); transform: translateY(-2px); }
.kpi-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 2px; border-radius: 16px 16px 0 0;
}
.kpi-card.c-orange::after { background: linear-gradient(90deg, #fbb034, #ff6b35); }
.kpi-card.c-green::after  { background: linear-gradient(90deg, #00d68f, #00b377); }
.kpi-card.c-blue::after   { background: linear-gradient(90deg, #4facfe, #00f2fe); }
.kpi-card.c-red::after    { background: linear-gradient(90deg, #ff5e62, #ff9966); }

.kpi-label {
    font-size: 0.67rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.8px;
    color: rgba(232,234,240,0.38);
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.9rem; font-weight: 600; line-height: 1; color: #fff;
}
.kpi-value.c-orange { color: #fbb034; }
.kpi-value.c-green  { color: #00d68f; }
.kpi-value.c-blue   { color: #4facfe; }
.kpi-value.c-red    { color: #ff5e62; }
.kpi-sub { font-size: 0.7rem; color: rgba(232,234,240,0.28); }

.status-banner {
    border-radius: 12px; padding: 1rem 1.4rem;
    display: flex; align-items: center; gap: 0.8rem;
    font-size: 0.88rem; font-weight: 500; margin: 1.5rem 0;
}
.s-ok   { background: rgba(0,214,143,0.08); border: 1px solid rgba(0,214,143,0.2); color: #00d68f; }
.s-warn { background: rgba(255,94,98,0.08);  border: 1px solid rgba(255,94,98,0.2);  color: #ff5e62; }

.sec-title {
    display: flex; align-items: center; gap: 0.8rem; margin: 2rem 0 1rem;
}
.sec-line { flex: 1; height: 1px; background: rgba(255,255,255,0.06); }
.sec-text {
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 2.5px; color: rgba(251,176,52,0.55); white-space: nowrap;
}

.hist-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.45rem 1.2rem; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.hist-date { font-size: 0.73rem; color: rgba(232,234,240,0.45); }
.hist-ef   { font-size: 0.73rem; font-family: 'JetBrains Mono',monospace; color: #fbb034; }
.info-box  {
    background: rgba(79,172,254,0.06); border: 1px solid rgba(79,172,254,0.12);
    border-radius: 10px; padding: 0.8rem 1rem;
    font-size: 0.8rem; color: rgba(232,234,240,0.55); margin: 0.3rem 1.2rem 0;
}
.loc-display {
    background: rgba(251,176,52,0.06); border: 1px solid rgba(251,176,52,0.15);
    border-radius: 10px; padding: 0.7rem 1rem; margin: 0.4rem 1.2rem 0;
    font-size: 0.78rem; color: rgba(232,234,240,0.6);
}
.loc-coords {
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    color: rgba(251,176,52,0.5); margin-top: 0.2rem;
}
</style>
""", unsafe_allow_html=True)

# Carrega a chave da API do arquivo secrets.toml
try:
    API_KEY_OW = st.secrets["API_KEY_OW"]
except (FileNotFoundError, KeyError):
    st.markdown("""<div style="background:rgba(255,94,98,0.1);border:1px solid rgba(255,94,98,0.3);
    border-radius:12px;padding:1.2rem 1.5rem;margin:2rem 0;">
    <div style="color:#ff5e62;font-weight:700;margin-bottom:0.4rem">🔑 Chave de API não encontrada</div>
    <div style="color:rgba(232,234,240,0.6);font-size:0.85rem">
    Crie <code>.streamlit/secrets.toml</code> com:<br><br>
    <code>API_KEY_OW = "sua_chave_aqui"</code></div></div>""", unsafe_allow_html=True)
    st.stop()


@st.cache_data(ttl=86400)
def geocodificar_cidade(nome, api_key):
    # Uso a própria API do OpenWeather pra converter nome de cidade em coordenadas
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={nome}&limit=1&appid={api_key}"
    try:
        r = requests.get(url, timeout=8).json()
        if r:
            return r[0]["lat"], r[0]["lon"], r[0].get("name", nome), r[0].get("country", "")
    except Exception:
        pass
    return None, None, nome, ""


# Cache de 1 hora pra não bater na API a cada interação
@st.cache_data(ttl=3600)
def _get_radiacao(lat, lon):
    return get_radiacao_solar(lat, lon)

@st.cache_data(ttl=3600)
def _get_poeira(lat, lon, key):
    return get_nivel_poeira(lat, lon, key)


with st.sidebar:
    st.markdown("""<div class="sidebar-logo">
        <div style="font-size:1.8rem">☀️</div>
        <div class="sidebar-logo-title">Solar Monitor</div>
        <div class="sidebar-logo-sub">Painel de Controle</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">📍 Localização</div>', unsafe_allow_html=True)

    cidade_input = st.text_input(
        "Nome da cidade",
        value=st.session_state.get("cidade_input", "Belo Horizonte, MG, BR"),
        placeholder="Ex: São Paulo, BR",
        help="Digite o nome da cidade e clique em Buscar"
    )

    col_buscar, col_reset = st.columns([2, 1])
    buscar = col_buscar.button("🔍 Buscar", type="primary", use_container_width=True)
    reset  = col_reset.button("↺", help="Voltar para Belo Horizonte", use_container_width=True)

    if reset:
        st.session_state["cidade_input"] = "Belo Horizonte, MG, BR"
        st.session_state["cidade_nome"]  = "Belo Horizonte, MG"
        st.session_state["cidade_lat"]   = -19.917
        st.session_state["cidade_lon"]   = -43.934
        st.cache_data.clear()
        st.rerun()

    if buscar:
        with st.spinner("Buscando..."):
            lat, lon, nome_api, pais = geocodificar_cidade(cidade_input, API_KEY_OW)
        if lat is not None:
            st.session_state["cidade_lat"]   = lat
            st.session_state["cidade_lon"]   = lon
            st.session_state["cidade_nome"]  = f"{nome_api}, {pais}"
            st.session_state["cidade_input"] = cidade_input
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Cidade não encontrada. Tente adicionar o país (ex: 'Manaus, BR').")

    LAT         = st.session_state.get("cidade_lat",  -19.917)
    LON         = st.session_state.get("cidade_lon",  -43.934)
    cidade_nome = st.session_state.get("cidade_nome", "Belo Horizonte, MG")

    st.markdown(f"""<div class="loc-display">
        📌 <strong style="color:#fbb034">{cidade_nome}</strong>
        <div class="loc-coords">lat {LAT:.3f} · lon {LON:.3f}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">🔧 Manutenção</div>', unsafe_allow_html=True)
    ultima_manutencao = carregar_manutencao()
    dias_sem_limpeza  = (datetime.today() - ultima_manutencao).days

    st.markdown(f"""<div class="info-box">
        Última limpeza<br>
        <span style="color:#fbb034;font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:600">
            {ultima_manutencao.strftime('%d/%m/%Y')}
        </span><br>
        <span style="font-size:0.7rem;color:rgba(232,234,240,0.3)">{dias_sem_limpeza} dia(s) atrás</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if st.button("✅ Registrar limpeza hoje", type="primary", use_container_width=True):
        try:
            _r = get_radiacao_solar(LAT, LON)
            _p = get_nivel_poeira(LAT, LON, API_KEY_OW)["pm10"]
            _e, _ = calcular_eficiencia(_p, _r, dias_sem_limpeza)
            salvar_historico(_e)
        except Exception:
            pass
        salvar_manutencao()
        st.cache_data.clear()
        st.rerun()

    st.markdown('<div class="sidebar-section">📋 Histórico</div>', unsafe_allow_html=True)
    historico = carregar_historico()
    if historico:
        for entry in reversed(historico[-6:]):
            st.markdown(f"""<div class="hist-item">
                <span class="hist-date">{entry['data']}</span>
                <span class="hist-ef">{entry.get('eficiencia_antes','?')}%</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:0.4rem 1.2rem;font-size:0.75rem;color:rgba(232,234,240,0.25)">Nenhum registro ainda.</div>', unsafe_allow_html=True)


# Busca os dados das APIs
error_rad = error_pm10 = None

try:
    radiacao_solar = _get_radiacao(LAT, LON)
except Exception as e:
    radiacao_solar = {}
    error_rad = str(e)

try:
    poeira_data = _get_poeira(LAT, LON, API_KEY_OW)
    pm10_atual  = poeira_data["pm10"]
    pm25_atual  = poeira_data["pm2_5"]
except Exception as e:
    pm10_atual = pm25_atual = None
    error_pm10 = str(e)

ultima_manutencao = carregar_manutencao()
dias_sem_limpeza  = (datetime.today() - ultima_manutencao).days

if pm10_atual is not None:
    ef_atual, rad_media = calcular_eficiencia(pm10_atual, radiacao_solar, dias_sem_limpeza)
    previsao = prever_proxima_manutencao(ef_atual, dias_sem_limpeza, pm10_atual, rad_media)
else:
    ef_atual = rad_media = None
    previsao = "N/A"


st.markdown(f"""<div class="main-header">
    <div class="header-badge"><div class="header-dot"></div>Sistema ativo</div>
    <div class="header-title">Solar <span>Monitor</span></div>
    <p class="header-sub">Monitoramento inteligente de painéis solares · {cidade_nome} · {datetime.today().strftime('%d/%m/%Y')}</p>
</div>""", unsafe_allow_html=True)

if error_rad:
    st.markdown(f'<div class="status-banner s-warn">⚠️ Radiação indisponível: {error_rad}</div>', unsafe_allow_html=True)
if error_pm10:
    st.markdown(f'<div class="status-banner s-warn">⚠️ Poeira indisponível: {error_pm10}</div>', unsafe_allow_html=True)


c1, c2, c3, c4 = st.columns(4)

ef_color = "c-red" if (ef_atual and ef_atual < LIMITE_ALERTA) else ("c-orange" if (ef_atual and ef_atual < 92) else "c-green")

with c1:
    st.markdown(f"""<div class="kpi-card c-orange">
        <div class="kpi-label">Última Manutenção</div>
        <div class="kpi-value" style="font-size:1.35rem">{ultima_manutencao.strftime('%d/%m/%Y')}</div>
        <div class="kpi-sub">{dias_sem_limpeza} dia(s) sem limpeza</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="kpi-card c-blue">
        <div class="kpi-label">Poeira PM10</div>
        <div class="kpi-value c-blue">{f"{pm10_atual:.0f}" if pm10_atual else "—"}</div>
        <div class="kpi-sub">µg/m³ · PM2.5: {f"{pm25_atual:.1f}" if pm25_atual else "—"} µg/m³</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="kpi-card {ef_color}">
        <div class="kpi-label">Eficiência Estimada</div>
        <div class="kpi-value {ef_color}">{f"{ef_atual:.1f}%" if ef_atual else "—"}</div>
        <div class="kpi-sub">Alerta abaixo de {LIMITE_ALERTA}%</div>
    </div>""", unsafe_allow_html=True)

with c4:
    pc = "c-red" if previsao == "Imediata" else "c-green"
    st.markdown(f"""<div class="kpi-card {pc}">
        <div class="kpi-label">Próxima Limpeza</div>
        <div class="kpi-value {pc}" style="font-size:1.4rem">{previsao}</div>
        <div class="kpi-sub">Projeção do modelo</div>
    </div>""", unsafe_allow_html=True)


if ef_atual is not None:
    if ef_atual < LIMITE_ALERTA:
        st.markdown(f'<div class="status-banner s-warn">⚠️ Eficiência abaixo do limite — {ef_atual:.1f}% (mínimo {LIMITE_ALERTA}%). Realize a limpeza o quanto antes.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-banner s-ok">✅ Painéis em boas condições — Eficiência estimada: {ef_atual:.1f}% · Próxima limpeza em {previsao}</div>', unsafe_allow_html=True)


st.markdown('<div class="sec-title"><div class="sec-line"></div><div class="sec-text">⚡ Curva de Eficiência do Painel</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

if pm10_atual is not None:
    dias_lista, ef_lista = gerar_curva_eficiencia(pm10_atual, radiacao_solar, dias_sem_limpeza)
    split = dias_sem_limpeza

    hover_hist = [
        f"<b>Dia {d}</b><br>Eficiência: <b>{e:.1f}%</b><br>{'✅ Bom' if e >= LIMITE_ALERTA else '⚠️ Limpeza necessária'}"
        for d, e in zip(dias_lista[:split+1], ef_lista[:split+1])
    ]
    hover_proj = [
        f"<b>Dia {d} (projeção)</b><br>Eficiência estimada: <b>{e:.1f}%</b><br>{'✅ Ainda ok' if e >= LIMITE_ALERTA else '⚠️ Abaixo do limite — limpar!'}"
        for d, e in zip(dias_lista[split:], ef_lista[split:])
    ]

    fig = go.Figure()

    fig.add_hrect(y0=LIMITE_ALERTA, y1=101,
        fillcolor="rgba(0,214,143,0.04)", line_width=0,
        annotation_text="✅ Zona segura", annotation_position="top left",
        annotation_font=dict(size=10, color="rgba(0,214,143,0.4)"))

    fig.add_hrect(y0=EFICIENCIA_MINIMA - 3, y1=LIMITE_ALERTA,
        fillcolor="rgba(255,94,98,0.04)", line_width=0,
        annotation_text="⚠️ Limpeza necessária", annotation_position="bottom left",
        annotation_font=dict(size=10, color="rgba(255,94,98,0.4)"))

    fig.add_trace(go.Scatter(
        x=dias_lista[:split+1], y=ef_lista[:split+1],
        mode="lines", name="📊 Histórico real",
        line=dict(color="#fbb034", width=3),
        fill="tozeroy", fillcolor="rgba(251,176,52,0.06)",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_hist,
    ))

    fig.add_trace(go.Scatter(
        x=dias_lista[split:], y=ef_lista[split:],
        mode="lines", name="🔮 Projeção futura",
        line=dict(color="#ff6b35", width=2, dash="dot"),
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_proj,
    ))

    if ef_lista:
        ef_hoje = ef_lista[split]
        cor_hoje = "#00d68f" if ef_hoje >= LIMITE_ALERTA else "#ff5e62"
        fig.add_trace(go.Scatter(
            x=[split], y=[ef_hoje],
            mode="markers+text",
            name="📍 Hoje",
            marker=dict(color=cor_hoje, size=12, line=dict(color="white", width=2)),
            text=[f"  {ef_hoje:.1f}%"],
            textposition="middle right",
            textfont=dict(color=cor_hoje, size=12, family="JetBrains Mono"),
            hovertemplate=f"<b>Hoje — Dia {split}</b><br>Eficiência: <b>{ef_hoje:.1f}%</b><extra></extra>",
        ))

    fig.add_hline(y=LIMITE_ALERTA,
        line_dash="dash", line_color="rgba(255,94,98,0.5)", line_width=1.5,
        annotation_text=f"Limite de alerta: {LIMITE_ALERTA}%",
        annotation_font=dict(color="rgba(255,94,98,0.6)", size=10),
        annotation_position="bottom right")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(14,21,32,0.5)",
        margin=dict(l=0, r=10, t=10, b=0),
        height=380,
        xaxis=dict(
            title="Dias desde a última limpeza",
            title_font=dict(size=11, color="rgba(232,234,240,0.35)"),
            tickfont=dict(size=10, color="rgba(232,234,240,0.28)"),
            gridcolor="rgba(255,255,255,0.04)", zeroline=False,
            ticksuffix="d",
        ),
        yaxis=dict(
            title="Eficiência (%)",
            title_font=dict(size=11, color="rgba(232,234,240,0.35)"),
            tickfont=dict(size=10, color="rgba(232,234,240,0.28)"),
            gridcolor="rgba(255,255,255,0.04)",
            range=[EFICIENCIA_MINIMA - 3, 102],
            zeroline=False,
            ticksuffix="%",
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, x=0,
            font=dict(size=11, color="rgba(232,234,240,0.5)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor="#111827", bordercolor="rgba(251,176,52,0.3)",
            font=dict(family="Outfit", size=12),
        ),
        font=dict(family="Outfit"),
    )
    st.plotly_chart(fig, width="stretch")

    pm10_exibido = max(pm10_atual, 20.0)
    st.markdown(f"""
    <div style="display:flex;gap:1.5rem;flex-wrap:wrap;padding:0.6rem 0.2rem;
         font-size:0.72rem;color:rgba(232,234,240,0.35);">
        <span>🟠 Linha sólida = histórico real desde a última limpeza</span>
        <span>🔶 Linha pontilhada = projeção baseada no modelo</span>
        <span>📌 PM10 usado no modelo: <b style="color:rgba(251,176,52,0.6)">{pm10_exibido:.0f} µg/m³</b>
        {"(mínimo aplicado — API retornou valor suspeito)" if pm10_atual < 20 else ""}</span>
    </div>
    """, unsafe_allow_html=True)


st.markdown('<div class="sec-title"><div class="sec-line"></div><div class="sec-text">☀️ Radiação Solar — últimos 7 dias (NASA POWER)</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

if radiacao_solar:
    datas, valores, datas_completas = [], [], []
    for data_str, val in sorted(radiacao_solar.items()):
        if val >= 0:
            dt = datetime.strptime(data_str, "%Y%m%d")
            datas.append(dt.strftime("%d/%m"))
            datas_completas.append(dt.strftime("%d/%m/%Y"))
            valores.append(round(val, 2))

    if valores:
        media = sum(valores) / len(valores)
        max_v, min_v = max(valores), min(valores)

        def cor_barra(v):
            if v == max_v: return "#00d68f"
            if v >= media: return "#fbb034"
            if v == min_v: return "#ff5e62"
            return "#4facfe"

        cores = [cor_barra(v) for v in valores]

        hover_rad = [
            f"<b>{dc}</b><br>Radiação: <b>{v} kWh/m²</b><br>"
            f"{'🟢 Dia mais ensolarado' if v == max_v else ('🔴 Dia menos ensolarado' if v == min_v else ('🟡 Acima da média' if v >= media else '🔵 Abaixo da média'))}"
            for dc, v in zip(datas_completas, valores)
        ]

        fig_rad = go.Figure(go.Bar(
            x=datas, y=valores,
            text=[f"{v} kWh/m²" for v in valores],
            textposition="outside",
            textfont=dict(size=10, color="rgba(232,234,240,0.5)", family="JetBrains Mono"),
            marker=dict(color=cores, opacity=0.85, line=dict(width=0)),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hover_rad,
        ))

        fig_rad.add_hline(y=media,
            line_dash="dot", line_color="rgba(251,176,52,0.4)", line_width=1.5,
            annotation_text=f"Média do período: {media:.1f} kWh/m²",
            annotation_font=dict(color="rgba(251,176,52,0.5)", size=10),
            annotation_position="top left")

        fig_rad.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(14,21,32,0.5)",
            margin=dict(l=0, r=0, t=35, b=0),
            height=300, showlegend=False, font=dict(family="Outfit"),
            xaxis=dict(
                title="Data",
                title_font=dict(size=11, color="rgba(232,234,240,0.35)"),
                tickfont=dict(size=11, color="rgba(232,234,240,0.4)"),
                gridcolor="rgba(255,255,255,0.04)",
            ),
            yaxis=dict(
                title="Radiação (kWh/m²)",
                title_font=dict(size=11, color="rgba(232,234,240,0.35)"),
                tickfont=dict(size=10, color="rgba(232,234,240,0.28)"),
                gridcolor="rgba(255,255,255,0.04)",
                range=[0, max_v * 1.3],
                ticksuffix=" kWh",
            ),
            hoverlabel=dict(
                bgcolor="#111827", bordercolor="rgba(79,172,254,0.3)",
                font=dict(family="Outfit", size=12),
            ),
        )
        st.plotly_chart(fig_rad, width="stretch")

        st.markdown(f"""
        <div style="display:flex;gap:1.5rem;flex-wrap:wrap;padding:0.4rem 0.2rem;
             font-size:0.72rem;color:rgba(232,234,240,0.35);">
            <span><span style="color:#00d68f">■</span> Dia mais ensolarado ({max_v} kWh/m²)</span>
            <span><span style="color:#fbb034">■</span> Acima da média</span>
            <span><span style="color:#4facfe">■</span> Abaixo da média</span>
            <span><span style="color:#ff5e62">■</span> Dia menos ensolarado ({min_v} kWh/m²)</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown('<div class="info-box">☁️ Dados de radiação solar indisponíveis no momento.</div>', unsafe_allow_html=True)


st.markdown("""
<div style="margin-top:3rem;padding-top:1.5rem;border-top:1px solid rgba(255,255,255,0.05);
     display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
    <span style="font-size:0.72rem;color:rgba(232,234,240,0.18)">Solar Monitor · NASA POWER + OpenWeatherMap</span>
    <span style="font-size:0.72rem;color:rgba(232,234,240,0.18)">Cache: 1 hora</span>
</div>""", unsafe_allow_html=True)
