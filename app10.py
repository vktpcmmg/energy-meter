
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# --- Helper functions ---

def get_quadrant(angle_deg):
    if 0 <= angle_deg <= 90:
        return "Quadrant I (Inductive Load)"
    elif 90 < angle_deg <= 180:
        return "Quadrant II (Generator - lag)"
    elif -180 <= angle_deg < -90:
        return "Quadrant III (Generator - lead)"
    elif -90 <= angle_deg < 0:
        return "Quadrant IV (Capacitive Load)"
    else:
        return "Unknown"

def plot_vectors(v_rms, i_rms, angle_deg):
    angle_rad = np.radians(angle_deg)
    Vx, Vy = v_rms, 0
    Ix = i_rms * np.cos(angle_rad)
    Iy = i_rms * np.sin(angle_rad)

    fig, ax = plt.subplots()
    ax.quiver(0, 0, Vx, Vy, angles='xy', scale_units='xy', scale=1, color='blue', label='Voltage')
    ax.quiver(0, 0, Ix, Iy, angles='xy', scale_units='xy', scale=1, color='red', label='Current')
    ax.set_xlim(-max(v_rms, i_rms)-10, max(v_rms, i_rms)+10)
    ax.set_ylim(-max(v_rms, i_rms)-10, max(v_rms, i_rms)+10)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title('Voltage and Current Vectors')
    st.pyplot(fig)

def plot_waveforms(Vrms, Irms, angle_rad, time_vector):
    omega = 2 * np.pi * 50  # 50 Hz
    # RMS values directly for waveforms (No RMS to Peak conversion)
    v_t = Vrms * np.sin(omega * time_vector)  # Use RMS value directly for voltage waveform
    i_t = Irms * np.sin(omega * time_vector + angle_rad)  # Use RMS value directly for current waveform
    p_t = v_t * i_t  # Instantaneous power

    fig, ax = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    ax[0].plot(time_vector, v_t, label='Voltage', color='blue')
    ax[0].set_ylabel('Voltage (V)')
    ax[0].legend()
    ax[1].plot(time_vector, i_t, label='Current', color='red')
    ax[1].set_ylabel('Current (A)')
    ax[1].legend()
    ax[2].plot(time_vector, p_t, label='Power (W)', color='green')
    ax[2].set_ylabel('Power (W)')
    ax[2].set_xlabel('Time (s)')
    ax[2].legend()
    st.pyplot(fig)

# --- Streamlit UI ---

st.title("⚡ Voltage & Current Analyzer with Quadrant, Vectors & Waveforms")

Vrms = st.number_input("Voltage (RMS) [V]", min_value=0.0, value=230.0)
Irms = st.number_input("Current (RMS) [A]", min_value=0.0, value=10.0)
angle = st.slider("Phase Angle between V and I (°)", -180, 180, 30)
time_interval = st.number_input("Time Interval (Hours)", min_value=0.01, value=1.0)

if st.button("Calculate"):
    angle_rad = np.radians(angle)
    Vp = Vrms * np.sqrt(2)
    Ip = Irms * np.sqrt(2)
    omega = 2 * np.pi * 50  # 50 Hz
    t = np.linspace(0, 0.04, 1000)  # One 50Hz cycle

    # Use RMS values directly for waveforms
    v_t = Vrms * np.sin(omega * t)
    i_t = Irms * np.sin(omega * t + angle_rad)
    p_t = v_t * i_t

    # Average values
    P = np.mean(p_t)
    S = Vrms * Irms
    
    # Correct logic for 0°, 180°, and -180° angle to set reactive power to zero
    if angle == 0 or angle == 180 or angle == -180:
        Q = 0
        S = P  # Apparent Power equals Active Power
    else:
        Q = np.sqrt(S**2 - P**2)
    
    # Energy calculations with corrected logic
    kWh = P * time_interval / 1000
    kVAh = S * time_interval / 1000
    kVARh = Q * time_interval / 1000

    # If angle is 0°, 180°, or -180°, set kVARh to 0 and kVAh = kWh
    if angle == 0 or angle == 180 or angle == -180:
        kVARh = 0
        kVAh = kWh

    st.subheader("🔢 Results")
    st.markdown(f"**Instantaneous Active Power (kW):** {P / 1000:.2f}")
    st.markdown(f"**Apparent Power (kVA):** {S / 1000:.2f}")
    st.markdown(f"**Reactive Power (kVAR):** {Q / 1000:.2f}")
    st.markdown(f"**Energy - kWh:** {kWh:.2f}, kVAh: {kVAh:.2f}, kVARh: {kVARh:.2f}")
    
    quadrant = get_quadrant(angle)
    st.markdown(f"**Power Quadrant:** {quadrant}")

    plot_vectors(Vrms, Irms, angle)
    plot_waveforms(Vrms, Irms, angle_rad, t)
