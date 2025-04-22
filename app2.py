
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Voltage-Current Waveform & Power Quadrant Analyzer")

Vm = st.number_input("Voltage Magnitude (V)", min_value=0.0, value=230.0)
Im = st.number_input("Current Magnitude (A)", min_value=0.0, value=10.0)
angle_deg = st.slider("Phase Angle (°) (positive: lagging, negative: leading)", -180, 180, 30)
duration = st.number_input("Time Duration (seconds)", min_value=0.01, value=0.1)

f = 50
w = 2 * np.pi * f
t = np.linspace(0, duration, 1000)
angle_rad = np.deg2rad(angle_deg)

v = Vm * np.sin(w * t)
i = Im * np.sin(w * t - angle_rad)

fig, ax = plt.subplots()
ax.plot(t, v, label='Voltage', color='blue')
ax.plot(t, i, label='Current', color='red')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
ax.legend()
st.pyplot(fig)

Vrms = Vm / np.sqrt(2)
Irms = Im / np.sqrt(2)
pf = np.cos(angle_rad)
S = Vrms * Irms
P = S * pf
Q = np.sqrt(S**2 - P**2)

if angle_deg > 0:
    Q_lag = Q
    Q_lead = 0
    quadrant = "Quadrant 1 (Import + Lagging)"
elif angle_deg < 0:
    Q_lag = 0
    Q_lead = Q
    quadrant = "Quadrant 4 (Import + Leading)"
else:
    Q_lag = Q_lead = 0
    quadrant = "Purely Active (No reactive component)"

kWh = P * (duration / 3600)
kVAh = S * (duration / 3600)
kVARh_lag = Q_lag * (duration / 3600)
kVARh_lead = Q_lead * (duration / 3600)

st.subheader("Power Parameters")
st.write(f"**Vrms**: {Vrms:.2f} V")
st.write(f"**Irms**: {Irms:.2f} A")
st.write(f"**Power Factor**: {pf:.3f}")
st.write(f"**Active Power (kW)**: {P:.3f}")
st.write(f"**Apparent Power (kVA)**: {S:.3f}")
st.write(f"**Reactive Power (kVAR)**: {Q:.3f}")
st.write(f"**Quadrant**: {quadrant}")

st.subheader("Energy Consumption Over Given Interval")
st.write(f"**kWh**: {kWh:.6f}")
st.write(f"**kVAh**: {kVAh:.6f}")
st.write(f"**kVARh Lagging**: {kVARh_lag:.6f}")
st.write(f"**kVARh Leading**: {kVARh_lead:.6f}")
