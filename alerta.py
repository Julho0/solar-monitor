import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from api import get_nivel_poeira, get_radiacao_solar
from utils import calcular_eficiencia, carregar_manutencao, LIMITE_ALERTA

load_dotenv()

API_KEY_OW = os.environ["API_KEY_OW"]
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
EMAIL_TO   = os.environ["EMAIL_TO"]

# Localização padrão: Belo Horizonte — pode mudar no .env
LAT = float(os.getenv("LAT", "-19.917"))
LON = float(os.getenv("LON", "-43.934"))


def enviar_email(eficiencia, dias, ultima_manutencao):
    subject = "⚠️ Alerta de Manutenção — Painéis Solares"
    body = (
        f"Relatório de Status dos Painéis Solares\n"
        f"{'=' * 40}\n\n"
        f"📅 Última manutenção : {ultima_manutencao.strftime('%d/%m/%Y')}\n"
        f"🗓️  Dias sem limpeza  : {dias} dias\n"
        f"⚡ Eficiência atual  : {eficiencia:.1f}%\n"
        f"🚨 Limite de alerta  : {LIMITE_ALERTA}%\n\n"
        f"⚠️  A eficiência está abaixo do limite aceitável.\n"
        f"   Recomenda-se realizar a limpeza dos painéis o quanto antes!\n\n"
        f"— Sistema de Monitoramento de Painéis Solares"
    )

    msg = MIMEMultipart()
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

    print("📩 E-mail enviado!")


def main():
    print("Coletando dados...")

    radiacao   = get_radiacao_solar(LAT, LON)
    poeira     = get_nivel_poeira(LAT, LON, API_KEY_OW)
    pm10       = poeira["pm10"]
    ultima_man = carregar_manutencao()
    dias       = (datetime.today() - ultima_man).days

    eficiencia, rad_media = calcular_eficiencia(pm10, radiacao, dias)

    print(f"  Radiação média : {rad_media:.2f} kWh/m²" if rad_media else "  Radiação: N/A")
    print(f"  PM10           : {pm10} µg/m³")
    print(f"  Última limpeza : {ultima_man.strftime('%d/%m/%Y')} ({dias} dias atrás)")
    print(f"  Eficiência     : {eficiencia:.1f}%")

    if eficiencia < LIMITE_ALERTA:
        print(f"\n⚠️  Eficiência abaixo de {LIMITE_ALERTA}% — enviando alerta...")
        enviar_email(eficiencia, dias, ultima_man)
    else:
        print("\n✅ Painel ok.")


if __name__ == "__main__":
    main()
