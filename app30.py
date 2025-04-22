
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

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

def plot_vectors(v_rms, i_rms, angle_deg, phase):
    angle_rad = np.radians(angle_deg)
    Vx, Vy = v_rms, 0
    Ix = i_rms * np.cos(angle_rad)
    Iy = i_rms * np.sin(angle_rad)

    fig, ax = plt.subplots()
    ax.quiver(0, 0, Vx, Vy, angles='xy', scale_units='xy', scale=1, color='blue', label=f'{phase} Voltage')
    ax.quiver(0, 0, Ix, Iy, angles='xy', scale_units='xy', scale=1, color='red', label=f'{phase} Current')
    ax.set_xlim(-max(v_rms, i_rms)-10, max(v_rms, i_rms)+10)
    ax.set_ylim(-max(v_rms, i_rms)-10, max(v_rms, i_rms)+10)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title(f'{phase} Phase Voltage and Current Vectors')
    st.pyplot(fig)

def plot_waveform(Vrms, Irms, angle_rad, time_vector, phase):
    omega = 2 * np.pi * 50
    Vpeak = Vrms * np.sqrt(2)
    Ipeak = Irms * np.sqrt(2)
    v_t = Vpeak * np.sin(omega * time_vector)
    i_t = Ipeak * np.sin(omega * time_vector + angle_rad)
    p_t = v_t * i_t

    fig, ax = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    ax[0].plot(time_vector, v_t, color='blue')
    ax[0].set_ylabel('Voltage (V)')
    ax[0].set_title(f'{phase} Phase Voltage')
    ax[1].plot(time_vector, i_t, color='red')
    ax[1].set_ylabel('Current (A)')
    ax[1].set_title(f'{phase} Phase Current')
    ax[2].plot(time_vector, p_t, color='green')
    ax[2].set_ylabel('Power (W)')
    ax[2].set_xlabel('Time (s)')
    ax[2].set_title(f'{phase} Phase Instantaneous Power')
    st.pyplot(fig)

st.title("🔺 Three-Phase Voltage & Current Analyzer")

phases = ['R', 'Y', 'B']
Vrms = {}
Irms = {}
angles = {}
for phase in phases:
    Vrms[phase] = st.number_input(f"{phase}-Phase Voltage (RMS) [V]", min_value=0.0, value=230.0, key=f"V_{phase}")
    Irms[phase] = st.number_input(f"{phase}-Phase Current (RMS) [A]", min_value=0.0, value=10.0, key=f"I_{phase}")
    angles[phase] = st.slider(f"{phase}-Phase Angle between V and I (°)", -180, 180, 0, key=f"A_{phase}")

time_interval = st.number_input("Time Interval (Hours)", min_value=0.01, value=1.0)

if st.button("Calculate"):
    st.subheader("🔢 Per Phase Results")
    total_kw = total_kva = total_kvar = 0

    time_vector = np.linspace(0, 0.04, 1000)

    for phase in phases:
        angle_rad = np.radians(angles[phase])
        P = Vrms[phase] * Irms[phase] * np.cos(angle_rad)
        Q = Vrms[phase] * Irms[phase] * np.sin(angle_rad)
        S = Vrms[phase] * Irms[phase]

        total_kw += P
        total_kva += S
        total_kvar += Q

        kWh = P * time_interval / 1000
        kVAh = S * time_interval / 1000
        kVARh = Q * time_interval / 1000

        st.markdown(f"**{phase} Phase**")
        st.markdown(f"Active Power: {P/1000:.2f} kW")
        st.markdown(f"Reactive Power: {Q/1000:.2f} kVAR")
        st.markdown(f"Apparent Power: {S/1000:.2f} kVA")
        st.markdown(f"Energy: {kWh:.2f} kWh, {kVAh:.2f} kVAh, {kVARh:.2f} kVARh")
        st.markdown(f"Quadrant: {get_quadrant(angles[phase])}")

        plot_vectors(Vrms[phase], Irms[phase], angles[phase], phase)
        plot_waveform(Vrms[phase], Irms[phase], angle_rad, time_vector, phase)

    st.subheader("🔻 Total Power Summary")
    st.markdown(f"**Total Active Power:** {total_kw/1000:.2f} kW")
    st.markdown(f"**Total Reactive Power:** {total_kvar/1000:.2f} kVAR")
    st.markdown(f"**Total Apparent Power:** {total_kva/1000:.2f} kVA")
