"""
Módulo para buscar dados de radiação solar via NASA POWER API.
"""

import requests
from datetime import datetime, timedelta


def get_radiacao_solar(lat: float, lon: float, dias: int = 7) -> dict:
    """
    Busca a radiação solar diária (kWh/m²) dos últimos N dias.

    Args:
        lat: Latitude do local.
        lon: Longitude do local.
        dias: Número de dias históricos a buscar (padrão: 7).

    Returns:
        Dicionário {data_str: valor_kwh} ou {} em caso de erro.
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=dias - 1)

    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters=ALLSKY_SFC_SW_DWN"
        f"&community=RE"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={start_date.strftime('%Y%m%d')}"
        f"&end={end_date.strftime('%Y%m%d')}"
        f"&format=JSON"
    )

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Erro ao conectar com NASA POWER: {e}")
    except (KeyError, ValueError) as e:
        raise ValueError(f"Erro ao processar resposta da NASA POWER: {e}")
