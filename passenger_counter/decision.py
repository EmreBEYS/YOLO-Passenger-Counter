"""Yolcu sayisina gore yogunluk karari uretir."""


LOW_DENSITY_MAX = 10
MEDIUM_DENSITY_MAX = 25


def get_density_status(passenger_count: int) -> str:
    """0-10 dusuk, 11-25 orta, 26 ve ustu yuksek yogunluktur."""
    if passenger_count < 0:
        raise ValueError("passenger_count negatif olamaz")
    if passenger_count <= LOW_DENSITY_MAX:
        return "Low Density"
    if passenger_count <= MEDIUM_DENSITY_MAX:
        return "Medium Density"
    return "High Density"
