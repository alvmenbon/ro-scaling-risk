"""
risk_report.py

Genera visualizaciones del riesgo de scaling estacional
combinando datos de Copernicus con el motor físico.

Outputs:
    - Gráfica de temperatura y salinidad estacional
    - Heatmap de riesgo de scaling por mes y compuesto
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

from core.water_chemistry import salinity_to_ionic_profile
from core.scaling_indices import calculate_all_indices


MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

COMPOUNDS = ["LSI_CaCO3", "SR_CaSO4", "SR_BaSO4", "SR_SrSO4", "SR_SiO2"]

THRESHOLDS = {
    "LSI_CaCO3": 0.0,
    "SR_CaSO4":  1.0,
    "SR_BaSO4":  1.0,
    "SR_SrSO4":  1.0,
    "SR_SiO2":   1.0,
}

COMPOUND_LABELS = {
    "LSI_CaCO3": "CaCO₃ (LSI)",
    "SR_CaSO4":  "CaSO₄ (SR)",
    "SR_BaSO4":  "BaSO₄ (SR)",
    "SR_SrSO4":  "SrSO₄ (SR)",
    "SR_SiO2":   "SiO₂ (SR)",
}


def compute_monthly_risk(
    climatology: pd.DataFrame,
    recovery: float = 0.45,
    pH: float = 7.8
) -> pd.DataFrame:
    """
    Calcula los índices de scaling para cada mes de la climatología.

    Parámetros:
        climatology: DataFrame con columnas month, temperature_mean, salinity_mean
        recovery:    recovery objetivo en tanto por uno
        pH:          pH del agua de alimentación

    Retorna:
        DataFrame con índices de scaling por mes
    """
    results = []

    for _, row in climatology.iterrows():
        profile = salinity_to_ionic_profile(
            salinity_psu=row["salinity_mean"],
            temperature_c=row["temperature_mean"]
        )

        indices = calculate_all_indices(
            feed_mg_L=profile,
            recovery=recovery,
            temperature_c=row["temperature_mean"],
            pH=pH
        )

        results.append({
            "month":      int(row["month"]),
            "LSI_CaCO3":  indices["LSI_CaCO3"],
            "SR_CaSO4":   indices["SR_CaSO4"],
            "SR_BaSO4":   indices["SR_BaSO4"],
            "SR_SrSO4":   indices["SR_SrSO4"],
            "SR_SiO2":    indices["SR_SiO2"],
        })

    return pd.DataFrame(results)


def plot_seasonal_conditions(climatology: pd.DataFrame, location_name: str = "") -> None:
    """
    Gráfica de temperatura y salinidad estacional.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    months = climatology["month"]

    # Temperatura
    ax1.plot(months, climatology["temperature_mean"],
             color="#E63946", linewidth=2.5, marker="o", markersize=5)
    ax1.fill_between(months,
                     climatology["temperature_min"],
                     climatology["temperature_max"],
                     alpha=0.2, color="#E63946")
    ax1.set_ylabel("Temperature (°C)", fontsize=11)
    ax1.set_ylim(0, 35)
    ax1.grid(True, alpha=0.3)
    ax1.set_title(f"Seasonal Conditions — {location_name}", fontsize=13, fontweight="bold")

    # Salinidad
    ax2.plot(months, climatology["salinity_mean"],
             color="#1D3557", linewidth=2.5, marker="o", markersize=5)
    ax2.fill_between(months,
                     climatology["salinity_min"],
                     climatology["salinity_max"],
                     alpha=0.2, color="#1D3557")
    ax2.set_ylabel("Salinity (PSU)", fontsize=11)
    ax2.set_ylim(34, 42)
    ax2.set_xlabel("Month", fontsize=11)
    ax2.set_xticks(months)
    ax2.set_xticklabels(MONTH_NAMES)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("outputs/seasonal_conditions.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Guardado: outputs/seasonal_conditions.png")


def plot_scaling_heatmap(
    risk_df: pd.DataFrame,
    recovery: float,
    location_name: str = ""
) -> None:
    """
    Heatmap de riesgo de scaling por mes y compuesto.
    """
    # Construir matriz normalizada respecto al umbral
    matrix = np.zeros((len(COMPOUNDS), 12))

    for i, compound in enumerate(COMPOUNDS):
        threshold = THRESHOLDS[compound]
        for j, month in enumerate(range(1, 13)):
            row = risk_df[risk_df["month"] == month]
            if not row.empty:
                value = row[compound].values[0]
                # Normalizar: 0=sin riesgo, 1=en umbral, >1=riesgo
                matrix[i, j] = value / threshold

    fig, ax = plt.subplots(figsize=(12, 4))

    # Colormap: verde → amarillo → rojo
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "scaling_risk",
        ["#2DC653", "#FFD166", "#EF233C"]
    )

    im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=3)

    # Etiquetas
    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTH_NAMES, fontsize=10)
    ax.set_yticks(range(len(COMPOUNDS)))
    ax.set_yticklabels([COMPOUND_LABELS[c] for c in COMPOUNDS], fontsize=10)

    # Valores en cada celda
    for i in range(len(COMPOUNDS)):
        for j in range(12):
            value = matrix[i, j] * THRESHOLDS[COMPOUNDS[i]]
            color = "white" if matrix[i, j] > 1.5 else "black"
            ax.text(j, i, f"{value:.2f}", ha="center", va="center",
                    fontsize=8, color=color)

    # Línea de umbral visual
    ax.axhline(y=-0.5, color="white", linewidth=0)

    plt.colorbar(im, ax=ax, label="Risk ratio (value / threshold)")

    title = f"Scaling Risk Heatmap — {location_name}\nRecovery: {recovery*100:.0f}%"
    ax.set_title(title, fontsize=13, fontweight="bold", pad=15)

    plt.tight_layout()
    plt.savefig("outputs/scaling_heatmap.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Guardado: outputs/scaling_heatmap.png")