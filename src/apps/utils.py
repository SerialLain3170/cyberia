import numpy as np

from typing import List


def norm(v: float,
         v_max: float,
         v_min: float) -> float:

    return (v - v_min) / (v_max - v_min)


def cosine_sim(v1: List[float], v2: List[float]) -> float:
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))