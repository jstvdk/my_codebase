import numpy as np
from typing import Optional, Tuple


def generate_ta_isotropic_events(
    n_events: int,
    latitude_deg: float = 39.3,
    theta_max_deg: float = 55.0,
    seed: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate isotropic Telescope Array-like detected events with
    geometrical zenith-angle exposure p(theta) ∝ sin(theta) cos(theta).

    Parameters
    ----------
    n_events : int
        Number of events to generate.
    latitude_deg : float, optional
        Detector latitude in degrees.
    theta_max_deg : float, optional
        Maximum zenith angle in degrees.
    seed : int or None, optional
        Random seed.

    Returns
    -------
    ra_deg : np.ndarray
        Right ascension in degrees, shape (n_events,).
    dec_deg : np.ndarray
        Declination in degrees, shape (n_events,).
    """
    rng = np.random.default_rng(seed)

    lat = np.deg2rad(latitude_deg)
    theta_max = np.deg2rad(theta_max_deg)

    # Sample theta from p(theta) ∝ sin(theta) cos(theta)
    u = rng.uniform(0.0, np.sin(theta_max) ** 2, size=n_events)
    theta = np.arcsin(np.sqrt(u))

    # Uniform azimuth and sidereal time
    phi = rng.uniform(0.0, 2.0 * np.pi, size=n_events)
    lst = rng.uniform(0.0, 2.0 * np.pi, size=n_events)

    # Altitude
    h = 0.5 * np.pi - theta

    # Declination
    sin_dec = np.sin(lat) * np.sin(h) + np.cos(lat) * np.cos(h) * np.cos(phi)
    sin_dec = np.clip(sin_dec, -1.0, 1.0)
    dec = np.arcsin(sin_dec)

    # Hour angle
    y = -np.sin(phi) * np.cos(h)
    x = np.sin(h) * np.cos(lat) - np.cos(h) * np.sin(lat) * np.cos(phi)
    ha = np.arctan2(y, x)

    # Right ascension
    ra = (lst - ha) % (2.0 * np.pi)

    return np.rad2deg(ra), np.rad2deg(dec)