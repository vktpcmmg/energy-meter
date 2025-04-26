import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# --- Helper functions ---
def plot_vectors(v_rms, i_rms, current_angles_deg):
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ['red', 'yellow', 'blue']
    labels = ['Phase R', 'Phase Y', 'Phase B']
    voltage_angles_deg = [0, 120, 240]  # Voltages are fixed 120 deg apart

    for i in range(3):
        Vx = v_rms[i] * np.cos(np.radians(voltage_angles_deg[i]))
        Vy = v_rms[i] * np.sin(np.radians(voltage_angles_deg[i]))

        Ix = i_rms[i] * np.cos(np.radians(voltage_angles_deg[i] + current_angles_deg[i]))
        Iy = i_rms[i] * np.sin(np.radians(voltage_angles_deg[i] + current_angles_deg[i]))

        # Voltage solid
        ax.quiver(0, 0, Vx, Vy, angles='xy', scale_units='xy', scale=1, color=colors[i], label=f'Voltage {labels[i]}', linewidth=2)
        # Current dashed
        ax.quiver(0, 0, Ix, Iy, angles='xy', scale_units='xy', scale=1, color=colors[i], linestyle='dashed', label=f'Current {labels[i]}', linewidth=2)

    ax.set_xlim(-max(v_rms+i_rms)-10, max(v_rms+i_rms)+10)
    ax.set_ylim(-max(v_rms+i_rms)-10, max(v_rms+i_rms)+10)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title('Voltage and Current Vectors (3-Phase)')

    st.pyplot(fig)

def plot_waveforms(Vrms, Irms, angles_deg, time_vector):
    omega = 2 * np.pi * 50  # 50 Hz
    Vpeak = [Vrms[i] * np.sqrt(2) for i in range(3)]
    Ipeak = [Irms[i] * np.sqrt(2) for i in range(3)]

    voltage_angles = [0, 120, 240]

    v_t = [Vpeak[i] * np.sin(omega * time_vector + np.radians(voltage_angles[i])) for i in range(3)]
    i_t = [Ipeak[i] * np.sin(omega * time_vector + np.radians(voltage_angles[i] + angles_deg[i])) for i in range(3)]

    fig, ax = plt.subplots(figsize=(12, 8))

    colors = ['red', 'yellow', 'blue']
    labels = ['R', 'Y', 'B']

    for i in range(3):
        # Voltage solid
        ax.plot(time_vector, v_t[i], label=f'Voltage {labels[i]}', color=colors[i], linestyle='-')
        # Current dashed
        ax.plot(time_vector, i_t[i], label=f'Current {labels[i]}', color=colors[i], linestyle='--')

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

# --- Streamlit App ---
st.title("\u26A1 Three-Phase Voltage and Current Analyzer")

Vrms_R = st.number_input("Phase R Voltage (Vrms)", value=230.0)
Vrms_Y = st.number_input("Phase Y Voltage (Vrms)", value=230.0)
Vrms_B = st.number_input("Phase B Voltage (Vrms)", value=230.0)

Irms_R = st.number_input("Phase R Current (Irms)", value=10.0)
Irms_Y = st.number_input("Phase Y Current (Irms)", value=10.0)
Irms_B = st.number_input("Phase B Current (Irms)", value=10.0)

angle_R = st.slider("Phase R Current Angle (deg)", -180, 180, 0)
angle_Y = st.slider("Phase Y Current Angle (deg)", -180, 180, 0)
angle_B = st.slider("Phase B Current Angle (deg)", -180, 180, 0)

if st.button("Plot Vectors and Waveforms"):
    time_vector = np.linspace(0, 0.04, 1000)  # one cycle at 50Hz
    plot_vectors([Vrms_R, Vrms_Y, Vrms_B], [Irms_R, Irms_Y, Irms_B], [angle_R, angle_Y, angle_B])
    plot_waveforms([Vrms_R, Vrms_Y, Vrms_B], [Irms_R, Irms_Y, Irms_B], [angle_R, angle_Y, angle_B], time_vector)
