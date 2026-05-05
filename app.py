"""
app.py

Streamlit interface for the RO Scaling Risk Estimator.
"""

import streamlit as st
import matplotlib.pyplot as plt
from copernicus.fetcher import fetch_temperature_salinity, monthly_climatology
from outputs.risk_report import compute_monthly_risk, plot_seasonal_conditions, plot_scaling_heatmap

# --- Page config ---
st.set_page_config(
    page_title="RO Scaling Risk Estimator",
    layout="wide"
)

st.title("RO Scaling Risk Estimator")
st.markdown("""
Estimate scaling risk in RO membranes for any coastal location using 
historical oceanographic data from **Copernicus Marine Service**.
""")

# --- Sidebar inputs ---
st.sidebar.header("Plant Parameters")

latitude = st.sidebar.number_input(
    "Latitude (°N)",
    min_value=-90.0,
    max_value=90.0,
    value=36.0,
    step=0.1,
    format="%.1f"
)

longitude = st.sidebar.number_input(
    "Longitude (°E)",
    min_value=-180.0,
    max_value=180.0,
    value=14.0,
    step=0.1,
    format="%.1f"
)

recovery = st.sidebar.slider(
    "Recovery rate (%)",
    min_value=30,
    max_value=60,
    value=45,
    step=1
)

start_year = st.sidebar.number_input(
    "Start year",
    min_value=1993,
    max_value=2023,
    value=2010
)

end_year = st.sidebar.number_input(
    "End year",
    min_value=1993,
    max_value=2023,
    value=2020
)

pH = st.sidebar.number_input(
    "Feed pH",
    min_value=6.5,
    max_value=8.5,
    value=7.8,
    step=0.1,
    format="%.1f"
)

location_name = f"{abs(latitude):.1f}°{'N' if latitude >= 0 else 'S'}, {abs(longitude):.1f}°{'E' if longitude >= 0 else 'W'}"

# --- Run button ---
if st.sidebar.button("🔍 Analyse", type="primary"):

    with st.spinner("Retrieving data from Copernicus Marine Service..."):
        try:
            df_raw = fetch_temperature_salinity(
                latitude=latitude,
                longitude=longitude,
                start_year=int(start_year),
                end_year=int(end_year)
            )
            climatologia = monthly_climatology(df_raw)

        except Exception as e:
            st.error(f"Error retrieving Copernicus data: {e}")
            st.stop()

    with st.spinner("Computing scaling risk..."):
        risk_df = compute_monthly_risk(
            climatologia,
            recovery=recovery / 100,
            pH=pH
        )

    st.success(f"Analysis complete: {len(df_raw)} monthly records retrieved ({start_year}-{end_year})")

    # --- Results ---
    col1, col2, col3 = st.columns(3)
    worst = climatologia.loc[climatologia["temperature_mean"].idxmax()]
    col1.metric("Max temperature", f"{worst['temperature_mean']:.1f} °C", "August")
    col2.metric("Max salinity", f"{climatologia['salinity_mean'].max():.2f} PSU")
    col3.metric("Recovery", f"{recovery}%")

    st.markdown("---")

    st.subheader("Seasonal Conditions")
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    months = climatologia["month"]
    ax1.plot(months, climatologia["temperature_mean"], color="#E63946", linewidth=2.5, marker="o", markersize=5)
    ax1.fill_between(months, climatologia["temperature_min"], climatologia["temperature_max"], alpha=0.2, color="#E63946")
    ax1.set_ylabel("Temperature (°C)")
    ax1.grid(True, alpha=0.3)
    ax2.plot(months, climatologia["salinity_mean"], color="#1D3557", linewidth=2.5, marker="o", markersize=5)
    ax2.fill_between(months, climatologia["salinity_min"], climatologia["salinity_max"], alpha=0.2, color="#1D3557")
    ax2.set_ylabel("Salinity (PSU)")
    ax2.set_xlabel("Month")
    ax2.set_xticks(months)
    ax2.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig1)

    st.subheader("Scaling Risk Heatmap")
    plot_scaling_heatmap(risk_df, recovery=recovery/100, location_name=location_name)
    from pathlib import Path
    heatmap_path = Path(__file__).parent / "outputs" / "scaling_heatmap.png"
    st.image(str(heatmap_path))

    st.subheader("Monthly Scaling Indices")
    st.dataframe(risk_df.set_index("month").round(3), use_container_width=True)

    st.markdown("---")
    st.caption("""
    **Limitations**: Valid for open ocean and semi-enclosed seas. 
    Less accurate near river mouths or estuaries. 
    CaCO₃ LSI may be underestimated without real alkalinity data.
    Activity coefficients are fixed approximations for seawater ionic strength.
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### About
**RO Scaling Risk Estimator** is an open source tool for 
process engineers working on seawater desalination projects.

Built by **Álvaro Mendoza**, Process Engineer specialized 
in water treatment and desalination.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/alvaro-mendoza-bonilla)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black)](https://github.com/alvmenbon/ro-scaling-risk)

*Data source: Copernicus Marine Service (CMEMS)*
""")