import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Function to detect power quadrant
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

# Function to plot vectors
def plot_vectors(v_mag, i_mag, angle_deg):
    angle_rad = np.radians(angle_deg)
    Vx, Vy = v_mag, 0
    Ix = i_mag * np.cos(angle_rad)
    Iy = i_mag * np.sin(angle_rad)

    fig, ax = plt.subplots()
    ax.quiver(0, 0, Vx, Vy, angles='xy', scale_units='xy', scale=1, color='blue', label='Voltage')
    ax.quiver(0, 0, Ix, Iy, angles='xy', scale_units='xy', scale=1, color='red', label='Current')
    ax.set_xlim(-max(v_mag, i_mag)-1, max(v_mag, i_mag)+1)
    ax.set_ylim(-max(v_mag, i_mag)-1, max(v_mag, i_mag)+1)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.legend()
    ax.set_title('Voltage and Current Vectors')
    st.pyplot(fig)

# Streamlit UI
st.title("Voltage & Current Vector and Power Parameters")

voltage_mag = st.number_input("Voltage Magnitude (V)", min_value=0.0, value=230.0)
current_mag = st.number_input("Current Magnitude (A)", min_value=0.0, value=10.0)
angle = st.slider("Phase Angle between Voltage and Current (°)", -180, 180, 30)
time_interval = st.number_input("Time Interval (Hours)", min_value=0.0, value=1.0)

if st.button("Calculate"):
    angle_rad = np.radians(angle)
    V = voltage_mag
    I = current_mag
    P = V * I * np.cos(angle_rad)
    Q = V * I * np.sin(angle_rad)
    S = V * I

    kWh = P * time_interval / 1000
    kVAh = S * time_interval / 1000
    kVARh = Q * time_interval / 1000

    quadrant = get_quadrant(angle)

    st.subheader("Results:")
    st.markdown(f"**Active Power (kWh):** {kWh:.2f}")
    st.markdown(f"**Apparent Power (kVAh):** {kVAh:.2f}")
    st.markdown(f"**Reactive Power (kVARh):** {abs(kVARh):.2f} {'Lagging' if Q >= 0 else 'Leading'}")
    st.markdown(f"**Power Quadrant:** {quadrant}")

    plot_vectors(V, I, angle)