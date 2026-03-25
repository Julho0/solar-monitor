"""
Módulo para buscar dados de qualidade do ar via OpenWeatherMap API.
"""

import requests


def get_nivel_poeira(lat: float, lon: float, api_key: str) -> dict:
    """
    Busca os níveis atuais de partículas PM10 e PM2.5.

    Args:
        lat: Latitude do local.
        lon: Longitude do local.
        api_key: Chave de API do OpenWeatherMap.

    Returns:
        Dicionário com {'pm10': float, 'pm2_5': float}.

    Raises:
        ConnectionError: Se a requisição falhar.
        ValueError: Se a resposta não contiver os dados esperados.
    """
    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={lat}&lon={lon}&appid={api_key}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        components = data["list"][0]["components"]
        return {
            "pm10": components.get("pm10", 0.0),
            "pm2_5": components.get("pm2_5", 0.0),
        }
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Erro ao conectar com OpenWeather: {e}")
    except (KeyError, IndexError) as e:
        raise ValueError(f"Erro ao processar resposta do OpenWeather: {e}")
