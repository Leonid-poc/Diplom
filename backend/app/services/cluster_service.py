"""Кластерный анализ маршрутов методом k-средних (раздел 1.5 ВКР).

Признаки маршрута для кластеризации:
    [длина_км, ср_время_мин, средняя_загрузка_%, частота_поломок,
     интервал_мин, сезонная_неравномерность]
"""
from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Веса по умолчанию для интегрального индекса эффективности
# (>0 — полезный признак, <0 — вредный).
DEFAULT_WEIGHTS = np.array([0.20, 0.15, 0.30, -0.10, -0.10, -0.15])


def cluster_routes(
    features: np.ndarray,
    n_clusters: int = 4,
    weights: np.ndarray | None = None,
    random_state: int = 42,
) -> dict:
    """Выполнить кластеризацию маршрутов.

    :param features: np.ndarray [n_routes, n_features]
    :return: dict с метками, центрами и интегральным индексом эффективности
    """
    if features.ndim != 2 or features.shape[0] == 0:
        return {"labels": [], "centers": [], "efficiency": []}

    weights = weights if weights is not None else DEFAULT_WEIGHTS
    # Подгоняем длину весов под количество фичей (на случай других наборов)
    if len(weights) != features.shape[1]:
        weights = np.ones(features.shape[1]) / features.shape[1]

    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    n_clusters_eff = min(n_clusters, features.shape[0])
    km = KMeans(n_clusters=n_clusters_eff, n_init=20, random_state=random_state)
    labels = km.fit_predict(X)
    centers = scaler.inverse_transform(km.cluster_centers_)

    efficiency = _integral_efficiency(features, weights)

    return {
        "labels": labels.tolist(),
        "centers": centers.tolist(),
        "efficiency": efficiency.tolist(),
    }


def _integral_efficiency(features: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Интегральный индекс на основе нормированных признаков и весов."""
    rng = features.max(axis=0) - features.min(axis=0)
    norm = (features - features.min(axis=0)) / (rng + 1e-9)
    return norm @ weights
