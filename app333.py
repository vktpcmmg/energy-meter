import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# --- Helper functions ---

def get_quadrant(angle_deg):
    if 0 <= angle_deg <= 90:
        return "Quadrant I (Inductive Load)"
    elif 90 < angle_deg <= 180:
        return "Quadrant II (Generator - Lead)"
    elif -180 <= angle_deg < -90:
        return "Quadrant III (Generator - Lag)"
    elif -90 <= angle_deg < 0:
        return "Quadrant IV (Capacitive Load)"
    else:
        return "Unknown"

def plot_vectors(v_rms, i_rms, angles_deg):
    fig, ax = plt.subplots(figsize=(8, 8))
    
    voltage_colors = {'R': 'red', 'Y': 'gold', 'B': 'blue'}
    current_colors = {'R': 'red', 'Y': 'gold', 'B': 'blue'}
    phases = ['R', 'Y', 'B']
    
    # Voltage angles (fixed 0°, 120°, 240°)
    voltage_angles_deg = [0, 120, 240]
    
    for idx, phase in enumerate(phases):
        # Voltage vector (solid arrow)
        v_angle_rad = np.radians(voltage_angles_deg[idx])
        Vx = v_rms[idx] * np.cos(v_angle_rad)
        Vy = v_rms[idx] * np.sin(v_angle_rad)
        ax.quiver(0, 0, Vx, Vy, angles='xy', scale_units='xy', scale=1,
                  color=voltage_colors[phase], label=f'Voltage {phase}', width=0.005)

        # Current vector (solid arrow but thinner)
        i_angle_rad = np.radians(angles_deg[idx])
        Ix = i_rms[idx] * np.cos(i_angle_rad)
        Iy = i_rms[idx] * np.sin(i_angle_rad)
        ax.quiver(0, 0, Ix, Iy, angles='xy', scale_units='xy', scale=1,
                  color=current_colors[phase], alpha=0.5, label=f'Current {phase}', width=0.003)

    ax.set_xlim(-max(v_rms + i_rms) - 20, max(v_rms + i_rms) + 20)
    ax.set_ylim(-max(v_rms + i_rms) - 20, max(v_rms + i_rms) + 20)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title('Voltage and Current Vectors for 3 Phases')
    
    st.pyplot(fig)

def plot_waveforms(Vrms, Irms, angles_rad, time_vector):
    omega = 2 * np.pi * 50  # 50 Hz angular frequency
    Vpeak = [Vrms[i] * np.sqrt(2) for i in range(3)]
    Ipeak = [Irms[i] * np.sqrt(2) for i in range(3)]
    
    v_t = [Vpeak[i] * np.sin(omega * time_vector + np.radians(i * 120)) for i in range(3)]
    i_t = [Ipeak[i] * np.sin(omega * time_vector + np.radians(i * 120) - angles_rad[i]) for i in range(3)]
    p_t = [v_t[i] * i_t[i] for i in range(3)]
    
    fig, ax = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    
    colors = ['red', 'gold', 'blue']
    phases = ['R', 'Y', 'B']
    
    for i in range(3):
        ax[0].plot(time_vector, v_t[i], label=f'Voltage {phases[i]}', color=colors[i], linestyle='-')
        ax[1].plot(time_vector, i_t[i], label=f'Current {phases[i]}', color=colors[i], linestyle='--')
        ax[2].plot(time_vector, p_t[i], label=f'Power {phases[i]}', color=colors[i], linestyle='-')
    
    ax[0].set_ylabel('Voltage (V)')
    ax[1].set_ylabel('Current (A)')
    ax[2].set_ylabel('Power (W)')
    ax[2].set_xlabel('Time (s)')
    
    for a in ax:
        a.legend()
        a.grid(True)

    st.pyplot(fig)

# --- Streamlit UI ---

st.set_page_config(page_title="Three Phase Analyzer", layout="wide")

st.title("⚡ Three-Phase Power and Energy Analyzer")
st.markdown("<h4 style='text-align: center; color: gray;'>🔷 Designed by <span style='color: #0072C6;'>Tata Power - MMG</span></h4>", unsafe_allow_html=True)

# Inputs
Vrms_R = st.number_input("Phase R Voltage (RMS) [V]", min_value=0.0, value=230.0)
Vrms_Y = st.number_input("Phase Y Voltage (RMS) [V]", min_value=0.0, value=230.0)
Vrms_B = st.number_input("Phase B Voltage (RMS) [V]", min_value=0.0, value=230.0)

Irms_R = st.number_input("Phase R Current (RMS) [A]", min_value=0.0, value=10.0)
Irms_Y = st.number_input("Phase Y Current (RMS) [A]", min_value=0.0, value=10.0)
Irms_B = st.number_input("Phase B Current (RMS) [A]", min_value=0.0, value=10.0)

angle_R = st.slider("Phase R Current Angle (°)", -180, 180, 0)
angle_Y = st.slider("Phase Y Current Angle (°)", -180, 180, 0)
angle_B = st.slider("Phase B Current Angle (°)", -180, 180, 0)

time_interval = st.number_input("Time Interval (Hours)", min_value=0.01, value=1.0)

if st.button("Calculate and Plot"):
    angles_rad = np.radians([angle_R, angle_Y, angle_B])

    # Powers
    P_R = Vrms_R * Irms_R * np.cos(angles_rad[0])
    P_Y = Vrms_Y * Irms_Y * np.cos(angles_rad[1])
    P_B = Vrms_B * Irms_B * np.cos(angles_rad[2])
    P_total = P_R + P_Y + P_B

    Q_R = Vrms_R * Irms_R * np.sin(angles_rad[0])
    Q_Y = Vrms_Y * Irms_Y * np.sin(angles_rad[1])
    Q_B = Vrms_B * Irms_B * np.sin(angles_rad[2])
    Q_total = Q_R + Q_Y + Q_B

    S_R = Vrms_R * Irms_R
    S_Y = Vrms_Y * Irms_Y
    S_B = Vrms_B * Irms_B
    S_total = S_R + S_Y + S_B

    # Energy (kWh etc.)
    kWh_total = P_total * time_interval / 1000
    kVAh_total = S_total * time_interval / 1000
    kVARh_total = Q_total * time_interval / 1000

    st.subheader("🔢 Results")
    st.markdown(f"**Total Active Power (kW):** {P_total / 1000:.2f}")
    st.markdown(f"**Total Apparent Power (kVA):** {S_total / 1000:.2f}")
    st.markdown(f"**Total Reactive Power (kVAR):** {Q_total / 1000:.2f}")
    st.markdown(f"**Energy - kWh Total:** {kWh_total:.2f}, kVAh Total: {kVAh_total:.2f}, kVARh Total: {kVARh_total:.2f}")

    # Phase wise quadrant
    quadrant_R = get_quadrant(angle_R)
    quadrant_Y = get_quadrant(angle_Y)
    quadrant_B = get_quadrant(angle_B)
    st.markdown(f"**Phase R Current Quadrant:** {quadrant_R}")
    st.markdown(f"**Phase Y Current Quadrant:** {quadrant_Y}")
    st.markdown(f"**Phase B Current Quadrant:** {quadrant_B}")

    # Plot vector diagram
    plot_vectors([Vrms_R, Vrms_Y, Vrms_B], [Irms_R, Irms_Y, Irms_B], [angle_R, angle_Y, angle_B])

    # Create time vector
    time_vector = np.linspace(0, 0.06, 1000)  # ~1 cycle for 50 Hz

    # Plot waveforms
    plot_waveforms([Vrms_R, Vrms_Y, Vrms_B], [Irms_R, Irms_Y, Irms_B], angles_rad, time_vector)
