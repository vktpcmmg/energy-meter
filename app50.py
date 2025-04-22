import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd

st.set_page_config(page_title="Three-Phase Analyzer", layout="centered")

def plot_combined_three_phase_vectors(v_dict, i_dict, angles_dict):
    fig, ax = plt.subplots()
    colors = {'R': 'red', 'Y': 'green', 'B': 'blue'}

    for phase in ['R', 'Y', 'B']:
        angle_rad = np.radians(angles_dict[phase])
        Vx = v_dict[phase] * np.cos(0)
        Vy = v_dict[phase] * np.sin(0)
        Ix = i_dict[phase] * np.cos(angle_rad)
        Iy = i_dict[phase] * np.sin(angle_rad)

        ax.quiver(0, 0, Vx, Vy, angles='xy', scale_units='xy', scale=1,
                  color=colors[phase], width=0.01, label=f'{phase} Voltage')
        ax.quiver(0, 0, Ix, Iy, angles='xy', scale_units='xy', scale=1,
                  color=colors[phase], alpha=0.5, width=0.005, label=f'{phase} Current')

    max_val = max(max(v_dict.values()), max(i_dict.values())) + 50
    ax.set_xlim(-max_val, max_val)
    ax.set_ylim(-max_val, max_val)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title("Three-Phase Voltage and Current Vectors")
    return fig

def calculate_power_energy(V, I, angle_deg, hours):
    angle_rad = np.radians(angle_deg)
    P = V * I * np.cos(angle_rad)
    Q = V * I * np.sin(angle_rad)
    S = V * I
    return {
        'kW': round(P / 1000, 3),
        'kVAR': round(Q / 1000, 3),
        'kVA': round(S / 1000, 3),
        'kWh': round(P * hours / 1000, 3),
        'kVARh': round(Q * hours / 1000, 3),
        'kVAh': round(S * hours / 1000, 3)
    }

st.title("🔌 Three-Phase Voltage, Current, Power & Energy Analyzer")

st.header("Phase Settings")
phases = ['R', 'Y', 'B']
v_dict, i_dict, angle_dict = {}, {}, {}

for phase in phases:
    with st.expander(f"Settings for Phase {phase}"):
        v_dict[phase] = st.number_input(f"{phase} Voltage RMS (V)", min_value=0.0, value=230.0, key=f"v_{phase}")
        i_dict[phase] = st.number_input(f"{phase} Current RMS (A)", min_value=0.0, value=10.0, key=f"i_{phase}")
        angle_dict[phase] = st.slider(f"{phase} Angle (°)", -180, 180, 30 if phase == 'R' else (-120 if phase == 'Y' else 120), key=f"a_{phase}")

hours = st.number_input("Time Interval (in hours)", min_value=0.01, value=1.0, step=0.01)

if st.button("Generate Report"):
    fig = plot_combined_three_phase_vectors(v_dict, i_dict, angle_dict)
    st.pyplot(fig)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    st.download_button("Download Vector Diagram", data=buf, file_name="three_phase_vector_diagram.png", mime="image/png")

    st.subheader("📊 Power and Energy Calculations")
    data = []
    for phase in phases:
        result = calculate_power_energy(v_dict[phase], i_dict[phase], angle_dict[phase], hours)
        result['Phase'] = phase
        data.append(result)

    df = pd.DataFrame(data)[['Phase', 'kW', 'kVAR', 'kVA', 'kWh', 'kVARh', 'kVAh']]
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode()
    st.download_button("Download Report (CSV)", data=csv, file_name="three_phase_energy_report.csv", mime="text/csv")
