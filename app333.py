import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import base64

# --- Helper functions ---
def get_image_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_quadrant(angle_deg):
    if 0 <= angle_deg <= 90:
        return "Quadrant I (Inductive Load)"
    elif 90 < angle_deg <= 180:
        return "Quadrant II (Generator - Lead)"
    elif -180 <= angle_deg < -90:
        return "Quadrant III (Generator - lag)"
    elif -90 <= angle_deg < 0:
        return "Quadrant IV (Capacitive Load)"
    else:
        return "Unknown"

def plot_vectors(v_rms, i_rms, angles_deg):
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ['blue', 'green', 'red']
    labels = ['Phase R', 'Phase Y', 'Phase B']
    
    # Plot each phase vector
    for i, angle_deg in enumerate(angles_deg):
        angle_rad = np.radians(angle_deg)
        Vx, Vy = v_rms[i], 0  # Voltage vectors are along X-axis
        Ix = i_rms[i] * np.cos(angle_rad)  # Current vector along X-axis
        Iy = i_rms[i] * np.sin(angle_rad)  # Current vector along Y-axis
        
        # Plot voltage and current vectors for each phase
        ax.quiver(0, 0, Vx, Vy, angles='xy', scale_units='xy', scale=1, color=colors[i], label=f'Voltage {labels[i]}', width=0.005)
        ax.quiver(0, 0, Ix, Iy, angles='xy', scale_units='xy', scale=1, color=colors[i], label=f'Current {labels[i]}', width=0.005)

    # Setting limits for the plot
    ax.set_xlim(-max(v_rms)-10, max(v_rms)+10)
    ax.set_ylim(-max(i_rms)-10, max(i_rms)+10)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title('Voltage and Current Vectors for 3 Phases')
    
    # Display the plot
    st.pyplot(fig)

def plot_waveforms(Vrms, Irms, angles_rad, time_vector):
    omega = 2 * np.pi * 50  # 50 Hz means angular frequency
    Vpeak = [Vrms[i] * np.sqrt(2) for i in range(3)]  # Voltage peak values
    Ipeak = [Irms[i] * np.sqrt(2) for i in range(3)]  # Current peak values
    
    # Create waveforms using peak values for each phase
    v_t = [Vpeak[i] * np.sin(omega * time_vector + np.radians(i * 120)) for i in range(3)]  # Voltage waveform (using peak value)
    i_t = [Ipeak[i] * np.sin(omega * time_vector + np.radians(i * 120) - angles_rad[i]) for i in range(3)]  # Current waveform (using peak value)
    p_t = [v_t[i] * i_t[i] for i in range(3)]  # Instantaneous power
    
    fig, ax = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    
    # Plot voltage, current, and power for all phases
    for i in range(3):
        ax[0].plot(time_vector, v_t[i], label=f'Voltage {["R", "Y", "B"][i]}', color=['blue', 'green', 'red'][i])
        ax[1].plot(time_vector, i_t[i], label=f'Current {["R", "Y", "B"][i]}', color=['blue', 'green', 'red'][i])
        ax[2].plot(time_vector, p_t[i], label=f'Power {["R", "Y", "B"][i]}', color=['blue', 'green', 'red'][i])

    ax[0].set_ylabel('Voltage (V)')
    ax[1].set_ylabel('Current (A)')
    ax[2].set_ylabel('Power (W)')
    ax[2].set_xlabel('Time (s)')
    
    ax[0].legend()
    ax[1].legend()
    ax[2].legend()

    st.pyplot(fig)

# --- Streamlit UI ---
st.title("⚡ Three-Phase Power and Energy Analyzer")
st.markdown(
    "<h4 style='text-align: center; color: gray;'>🔷 Designed by <span style='color: #0072C6;'>Tata Power - MMG</span></h4>",
    unsafe_allow_html=True
)

Vrms_R = st.number_input("Phase R Voltage (RMS) [V]", min_value=0.0, value=230.0)
Vrms_Y = st.number_input("Phase Y Voltage (RMS) [V]", min_value=0.0, value=230.0)
Vrms_B = st.number_input("Phase B Voltage (RMS) [V]", min_value=0.0, value=230.0)

Irms_R = st.number_input("Phase R Current (RMS) [A]", min_value=0.0, value=10.0)
Irms_Y = st.number_input("Phase Y Current (RMS) [A]", min_value=0.0, value=10.0)
Irms_B = st.number_input("Phase B Current (RMS) [A]", min_value=0.0, value=10.0)

angle_R = st.slider("Phase R Angle (°)", -180, 180, 0)
angle_Y = st.slider("Phase Y Angle (°)", -180, 180, -120)
angle_B = st.slider("Phase B Angle (°)", -180, 180, 120)

time_interval = st.number_input("Time Interval (Hours)", min_value=0.01, value=1.0)

if st.button("Calculate"):
    angles_rad = np.radians([angle_R, angle_Y, angle_B])

    # Active Power (kW) for each phase
    P_R = Vrms_R * Irms_R * np.cos(angles_rad[0])
    P_Y = Vrms_Y * Irms_Y * np.cos(angles_rad[1])
    P_B = Vrms_B * Irms_B * np.cos(angles_rad[2])

    # Total Active Power (kW)
    P_total = P_R + P_Y + P_B
    
    # Reactive Power (kVAR) for each phase
    Q_R = Vrms_R * Irms_R * np.sin(angles_rad[0])
    Q_Y = Vrms_Y * Irms_Y * np.sin(angles_rad[1])
    Q_B = Vrms_B * Irms_B * np.sin(angles_rad[2])

    # Total Reactive Power (kVAR)
    Q_total = Q_R + Q_Y + Q_B
    
    # Apparent Power (kVA) for each phase
    S_R = Vrms_R * Irms_R
    S_Y = Vrms_Y * Irms_Y
    S_B = Vrms_B * Irms_B

    # Total Apparent Power (kVA)
    S_total = S_R + S_Y + S_B

    # Energy calculations (in kWh, kVAh, kVARh)
    kWh_R = P_R * time_interval / 1000
    kWh_Y = P_Y * time_interval / 1000
    kWh_B = P_B * time_interval / 1000
    kWh_total = P_total * time_interval / 1000
    
    kVAh_R = S_R * time_interval / 1000
    kVAh_Y = S_Y * time_interval / 1000
    kVAh_B = S_B * time_interval / 1000
    kVAh_total = S_total * time_interval / 1000
    
    kVARh_R = Q_R * time_interval / 1000
    kVARh_Y = Q_Y * time_interval / 1000
    kVARh_B = Q_B * time_interval / 1000
    kVARh_total = Q_total * time_interval / 1000
    
    st.subheader("🔢 Results")
    st.markdown(f"**Total Active Power (kW):** {P_total / 1000:.2f}")
    st.markdown(f"**Total Apparent Power (kVA):** {S_total / 1000:.2f}")
    st.markdown(f"**Total Reactive Power (kVAR):** {Q_total / 1000:.2f}")
    st.markdown(f"**Energy - kWh Total:** {kWh_total:.2f}, kVAh Total: {kVAh_total:.2f}, kVARh Total: {kVARh_total:.2f}")
    
    # Individual Phase Power and Energy Results
    st.markdown(f"**Phase R Active Power (kW):** {P_R / 1000:.2f}, Apparent Power (kVA): {S_R / 1000:.2f}, Reactive Power (kVAR): {Q_R / 1000:.2f}")
    st.markdown(f"**Phase R Energy - kWh:** {kWh_R:.2f}, kVAh: {kVAh_R:.2f}, kVARh: {kVARh_R:.2f}")
    
    st.markdown(f"**Phase Y Active Power (kW):** {P_Y / 1000:.2f}, Apparent Power (kVA): {S_Y / 1000:.2f}, Reactive Power (kVAR): {Q_Y / 1000:.2f}")
    st.markdown(f"**Phase Y Energy - kWh:** {kWh_Y:.2f}, kVAh: {kVAh_Y:.2f}, kVARh: {kVARh_Y:.2f}")
    
    st.markdown(f"**Phase B Active Power (kW):** {P_B / 1000:.2f}, Apparent Power (kVA): {S_B / 1000:.2f}, Reactive Power (kVAR): {Q_B / 1000:.2f}")
    st.markdown(f"**Phase B Energy - kWh:** {kWh_B:.2f}, kVAh: {kVAh_B:.2f}, kVARh: {kVARh_B:.2f}")

    quadrant_R = get_quadrant(angle_R)
    quadrant_Y = get_quadrant(angle_Y)
    quadrant_B = get_quadrant(angle_B)
    st.markdown(f"**Phase R Power Quadrant:** {quadrant_R}")
    st.markdown(f"**Phase Y Power Quadrant:** {quadrant_Y}")
    st.markdown(f"**Phase B Power Quadrant:** {quadrant_B}")

    # Plot vectors and waveforms
    plot_vectors([Vrms_R, Vrms_Y, Vrms_B], [Irms_R, Irms_Y, Irms_B], [angle_R, angle_Y, angle_B])
    
    time_vector = np.linspace(0, time_interval * 3600, 1000)  # Time vector for plotting waveforms (in seconds)
    plot_waveforms([Vrms_R, Vrms_Y, Vr
