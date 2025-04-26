import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

import base64

def get_image_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_image_base64("tata_logo.png")

st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{logo_base64}" width="100">
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    "<h1 style='text-align: center; color: #003366;'>⚡3 Phase Power and Energy Analyzer</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h4 style='text-align: center; color: gray;'>🔷 Designed by <span style='color: #0072C6;'>Tata Power - MMG</span></h4>",
    unsafe_allow_html=True
)
# --- Helper functions ---
# --- Helper functions ---
def get_quadrant(angle_deg):
    if 0 <= angle_deg <= 90:
        return "Quadrant I (Inductive Load)"
    elif 90 < angle_deg <= 180:
        return "Quadrant II (Generator - Leading)"
    elif -180 <= angle_deg < -90:
        return "Quadrant III (Generator - Lagging)"
    elif -90 <= angle_deg < 0:
        return "Quadrant IV (Capacitive Load)"
    else:
        return "Unknown"

def plot_vectors(Vrms_list, Irms_list, current_angles_deg):
    fig, ax = plt.subplots(figsize=(8,8))
    
    voltage_angles_deg = [0, -120, 120]  # Fixed voltage angles
    colors = ['red', 'gold', 'blue']
    labels = ['Phase R', 'Phase Y', 'Phase B']

    # Plot voltage vectors (solid line arrows)
    for i in range(3):
        Vx = Vrms_list[i] * np.cos(np.radians(voltage_angles_deg[i]))
        Vy = Vrms_list[i] * np.sin(np.radians(voltage_angles_deg[i]))
        ax.arrow(0, 0, Vx, Vy, head_width=15, head_length=15, fc=colors[i], ec=colors[i], label=f'Voltage {labels[i]}')

    # Plot current vectors (dashed line simulation)
    for i in range(3):
        angle = voltage_angles_deg[i] + current_angles_deg[i]
        Ix = Irms_list[i] * np.cos(np.radians(angle))
        Iy = Irms_list[i] * np.sin(np.radians(angle))
        # Dashed current arrow
        ax.plot([0, Ix], [0, Iy], color=colors[i], linestyle='dashed', label=f'Current {labels[i]}')

    ax.set_xlim(-300, 300)
    ax.set_ylim(-300, 300)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title('Voltage and Current Vectors')
    st.pyplot(fig)

def plot_waveforms(Vrms_list, Irms_list, current_angles_deg, time_vector):
    omega = 2 * np.pi * 50  # 50Hz
    voltage_angles_deg = [0, -120, 120]  # Voltage fixed
    
    colors = ['red', 'gold', 'blue']
    labels = ['R', 'Y', 'B']
    
    fig, ax = plt.subplots(figsize=(10,6))

    for i in range(3):
        Vpeak = Vrms_list[i] * np.sqrt(2)
        Ipeak = Irms_list[i] * np.sqrt(2)
        
        v_wave = Vpeak * np.sin(omega * time_vector + np.radians(voltage_angles_deg[i]))
        i_wave = Ipeak * np.sin(omega * time_vector + np.radians(voltage_angles_deg[i] - current_angles_deg[i]))
        
        ax.plot(time_vector, v_wave, color=colors[i], label=f'V{labels[i]}', linestyle='solid')
        ax.plot(time_vector, i_wave, color=colors[i], label=f'I{labels[i]}', linestyle='dashed')

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Voltage and Current Waveforms')
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

# --- Streamlit UI ---


st.subheader("Enter RMS Values and Angles:")

Vrms_R = st.number_input("Phase R Voltage (RMS) [V]", value=230.0)
Vrms_Y = st.number_input("Phase Y Voltage (RMS) [V]", value=230.0)
Vrms_B = st.number_input("Phase B Voltage (RMS) [V]", value=230.0)

Irms_R = st.number_input("Phase R Current (RMS) [A]", value=100.0)
Irms_Y = st.number_input("Phase Y Current (RMS) [A]", value=100.0)
Irms_B = st.number_input("Phase B Current (RMS) [A]", value=100.0)

angle_R = st.slider("Phase R Current Angle w.r.t Voltage (°)", -180, 180, 0)
angle_Y = st.slider("Phase Y Current Angle w.r.t Voltage (°)", -180, 180, 0)
angle_B = st.slider("Phase B Current Angle w.r.t Voltage (°)", -180, 180, 0)

time_interval = st.number_input("Time Interval (hours)", min_value=0.01, value=1.0)

if st.button("Calculate and Plot"):
    Vrms_list = [Vrms_R, Vrms_Y, Vrms_B]
    Irms_list = [Irms_R, Irms_Y, Irms_B]
    current_angles_deg = [angle_R, angle_Y, angle_B]
    current_angles_rad = np.radians(current_angles_deg)
    
    # --- Power Calculations ---
    P_list = [Vrms_list[i] * Irms_list[i] * np.cos(current_angles_rad[i]) for i in range(3)]  # Active Power (W)
    Q_list = [Vrms_list[i] * Irms_list[i] * np.sin(current_angles_rad[i]) for i in range(3)]  # Reactive Power (VAR)
    S_list = [Vrms_list[i] * Irms_list[i] for i in range(3)]                                # Apparent Power (VA)

    P_total = sum(P_list)
    Q_total = sum(Q_list)
    S_total = sum(S_list)

    # --- Energy Calculations ---
    kWh_list = [(P * time_interval) / 1000 for P in P_list]
    kVARh_list = [(Q * time_interval) / 1000 for Q in Q_list]
    kVAh_list = [(S * time_interval) / 1000 for S in S_list]

    kWh_total = sum(kWh_list)
    kVARh_total = sum(kVARh_list)
    kVAh_total = sum(kVAh_list)

    st.subheader("Results:")
    st.markdown(f"### Total Powers")
    st.write(f"**Total Active Power (kW):** {P_total/1000:.2f}")
    st.write(f"**Total Reactive Power (kVAR):** {Q_total/1000:.2f}")
    st.write(f"**Total Apparent Power (kVA):** {S_total/1000:.2f}")

    st.markdown(f"### Total Energies (for {time_interval} hr)")
    st.write(f"**Total kWh:** {kWh_total:.2f}")
    st.write(f"**Total kVARh:** {kVARh_total:.2f}")
    st.write(f"**Total kVAh:** {kVAh_total:.2f}")

    st.markdown("### Individual Phase Details")
    phase_names = ['R', 'Y', 'B']
    for i in range(3):
        st.write(f"**Phase {phase_names[i]}:**")
        st.write(f"  - Active Power (kW): {P_list[i]/1000:.2f}")
        st.write(f"  - Reactive Power (kVAR): {Q_list[i]/1000:.2f}")
        st.write(f"  - Apparent Power (kVA): {S_list[i]/1000:.2f}")
        st.write(f"  - Energy kWh: {kWh_list[i]:.2f}, kVARh: {kVARh_list[i]:.2f}, kVAh: {kVAh_list[i]:.2f}")

        quadrant = get_quadrant(current_angles_deg[i])
        st.write(f"  - Power Quadrant: {quadrant}")

    # --- Plots ---
    time_vector = np.linspace(0, 0.04, 1000)  # 2 cycles of 50Hz
    plot_vectors(Vrms_list, Irms_list, current_angles_deg)
    plot_waveforms(Vrms_list, Irms_list, current_angles_deg, time_vector)
