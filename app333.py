import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import base64

# --- Helper functions ---

def get_image_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- Display Tata Power Logo ---
logo_base64 = get_image_base64("tata_logo.png")

st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{logo_base64}" width="100">
    </div>
    """,
    unsafe_allow_html=True
)

# --- Streamlit UI Header ---
st.markdown(
    "<h1 style='text-align: center; color: #003366;'>⚡ Power and Energy Analyzer - 3-Phase</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h4 style='text-align: center; color: gray;'>🔷 Designed by <span style='color: #0072C6;'>Tata Power - MMG</span></h4>",
    unsafe_allow_html=True
)

# --- Helper Functions for Power Calculation ---

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
    fig, ax = plt.subplots()
    colors = ['blue', 'green', 'red']
    labels = ['Phase R', 'Phase Y', 'Phase B']
    for i, angle_deg in enumerate(angles_deg):
        angle_rad = np.radians(angle_deg)
        Vx, Vy = v_rms[i], 0
        Ix = i_rms[i] * np.cos(angle_rad)
        Iy = i_rms[i] * np.sin(angle_rad)
        ax.quiver(0, 0, Vx, Vy, angles='xy', scale_units='xy', scale=1, color=colors[i], label=f'Voltage {labels[i]}')
        ax.quiver(0, 0, Ix, Iy, angles='xy', scale_units='xy', scale=1, color=colors[i], label=f'Current {labels[i]}')
    
    ax.set_xlim(-max(v_rms)-10, max(v_rms)+10)
    ax.set_ylim(-max(i_rms)-10, max(i_rms)+10)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title('Voltage and Current Vectors for 3 Phases')
    st.pyplot(fig)

def plot_waveforms(Vrms, Irms, angles_rad, time_vector):
    omega = 2 * np.pi * 50  # 50 Hz angular frequency
    Vpeak = [Vrms[i] * np.sqrt(2) for i in range(3)]
    Ipeak = [Irms[i] * np.sqrt(2) for i in range(3)]
    
    fig, ax = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    for i in range(3):
        v_t = Vpeak[i] * np.sin(omega * time_vector)  # Voltage waveform (peak)
        i_t = Ipeak[i] * np.sin(omega * time_vector - angles_rad[i])  # Current waveform (peak)
        p_t = v_t * i_t  # Instantaneous power
        
        ax[0].plot(time_vector, v_t, label=f'Voltage Phase {i+1}', color=['blue', 'green', 'red'][i])
        ax[1].plot(time_vector, i_t, label=f'Current Phase {i+1}', color=['blue', 'green', 'red'][i])
        ax[2].plot(time_vector, p_t, label=f'Power Phase {i+1}', color=['blue', 'green', 'red'][i])
    
    ax[0].set_ylabel('Voltage (V)')
    ax[1].set_ylabel('Current (A)')
    ax[2].set_ylabel('Power (W)')
    ax[2].set_xlabel('Time (s)')
    ax[0].legend()
    ax[1].legend()
    ax[2].legend()
    st.pyplot(fig)

# --- Streamlit UI for 3 Phases ---
st.subheader("⚡ Input Parameters for 3-Phase System")

Vrms_R = st.number_input("Voltage (R Phase RMS) [V]", min_value=0.0, value=230.0)
Vrms_Y = st.number_input("Voltage (Y Phase RMS) [V]", min_value=0.0, value=230.0)
Vrms_B = st.number_input("Voltage (B Phase RMS) [V]", min_value=0.0, value=230.0)

Irms_R = st.number_input("Current (R Phase RMS) [A]", min_value=0.0, value=10.0)
Irms_Y = st.number_input("Current (Y Phase RMS) [A]", min_value=0.0, value=10.0)
Irms_B = st.number_input("Current (B Phase RMS) [A]", min_value=0.0, value=10.0)

angle_R = st.slider("Phase Angle (R Phase) [°]", -180, 180, 0)
angle_Y = st.slider("Phase Angle (Y Phase) [°]", -180, 180, -120)
angle_B = st.slider("Phase Angle (B Phase) [°]", -180, 180, 120)

time_interval = st.number_input("Time Interval (Hours)", min_value=0.01, value=1.0)

# --- Power and Energy Calculations ---
if st.button("Calculate"):
    angles_rad = np.radians([angle_R, angle_Y, angle_B])
    
    # Active Power (kW) for each phase and total
    P_R = Vrms_R * Irms_R * np.cos(angles_rad[0])
    P_Y = Vrms_Y * Irms_Y * np.cos(angles_rad[1])
    P_B = Vrms_B * Irms_B * np.cos(angles_rad[2])
    P_total = P_R + P_Y + P_B
    
    # Reactive Power (kVAR) for each phase and total
    Q_R = Vrms_R * Irms_R * np.sin(angles_rad[0])
    Q_Y = Vrms_Y * Irms_Y * np.sin(angles_rad[1])
    Q_B = Vrms_B * Irms_B * np.sin(angles_rad[2])
    Q_total = Q_R + Q_Y + Q_B
    
    # Apparent Power (kVA) for each phase and total
    S_R = Vrms_R * Irms_R
    S_Y = Vrms_Y * Irms_Y
    S_B = Vrms_B * Irms_B
    S_total = S_R + S_Y + S_B
    
    # Energy calculations (in kWh, kVAh, kVARh)
    kWh = P_total * time_interval / 1000
    kVAh = S_total * time_interval / 1000
    kVARh = Q_total * time_interval / 1000
    
    # Display Results
    st.subheader("🔢 Results")
    st.markdown(f"**Phase R - Active Power (kW):** {P_R / 1000:.2f}")
    st.markdown(f"**Phase Y - Active Power (kW):** {P_Y / 1000:.2f}")
    st.markdown(f"**Phase B - Active Power (kW):** {P_B / 1000:.2f}")
    st.markdown(f"**Total Active Power (kW):** {P_total / 1000:.2f}")
    st.markdown(f"**Apparent Power (kVA):** {S_total / 1000:.2f}")
    st.markdown(f"**Reactive Power (kVAR):** {Q_total / 1000:.2f}")
    st.markdown(f"**Energy - kWh:** {kWh:.2f}, kVAh: {kVAh:.2f}, kVARh: {kVARh:.2f}")
    
    # Quadrant Results
    quadrant_R = get_quadrant(angle_R)
    quadrant_Y = get_quadrant(angle_Y)
    quadrant_B = get_quadrant(angle_B)
    
    st.markdown(f"**Power Quadrant for Phase R:** {quadrant_R}")
    st.markdown(f"**Power Quadrant for Phase Y:** {quadrant_Y}")
    st.markdown(f"**Power Quadrant for Phase B:** {quadrant_B}")
    
    # Generate time
