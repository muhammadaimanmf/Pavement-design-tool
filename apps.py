import streamlit as st
import math
import matplotlib.pyplot as plt
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Pavement Design Tool", layout="wide")

st.title("🏗️ Pavement Design Tool (ATJ vs AASHTO)")
st.write("Compare pavement thickness design using ATJ method and simplified AASHTO method.")

# -----------------------------
# INPUT
# -----------------------------
st.sidebar.header("Input Parameters")

aadt = st.sidebar.number_input("AADT (vehicles/day)", min_value=0.0, value=1000.0)
growth = st.sidebar.number_input("Growth Rate (%)", min_value=0.0, value=3.0)
years = st.sidebar.number_input("Design Life (years)", min_value=1.0, value=20.0)
hv = st.sidebar.number_input("Heavy Vehicle (%)", min_value=0.0, max_value=100.0, value=20.0)
cbr = st.sidebar.number_input("CBR (%)", min_value=0.1, value=5.0)

run = st.sidebar.button("Run Design")

# -----------------------------
# FUNCTIONS
# -----------------------------
def calculate_esal(aadt, growth, years, hv):
    r = growth / 100
    total = 0

    for i in range(int(years)):
        total += aadt * ((1 + r) ** i) * 365

    return total * (hv / 100)


def traffic_class(esal):
    if esal < 1e5:
        return "T1"
    elif esal < 3e5:
        return "T2"
    elif esal < 1e6:
        return "T3"
    elif esal < 3e6:
        return "T4"
    elif esal < 1e7:
        return "T5"
    elif esal < 3e7:
        return "T6"
    else:
        return "T7"


def cbr_class(cbr):
    if cbr < 5:
        return "S1"
    elif cbr < 10:
        return "S2"
    elif cbr < 15:
        return "S3"
    else:
        return "S4"


# -----------------------------
# ATJ TABLE
# -----------------------------
ATJ = {
    "T1": {"S1": (80, 200, 180), "S2": (60, 150, 120), "S3": (50, 130, 100), "S4": (40, 120, 80)},
    "T2": {"S1": (100, 230, 200), "S2": (80, 180, 150), "S3": (60, 150, 120), "S4": (50, 130, 100)},
    "T3": {"S1": (120, 280, 250), "S2": (100, 250, 200), "S3": (80, 200, 150), "S4": (60, 180, 120)},
    "T4": {"S1": (140, 320, 300), "S2": (120, 300, 250), "S3": (100, 240, 180), "S4": (80, 200, 150)},
    "T5": {"S1": (160, 380, 350), "S2": (140, 350, 300), "S3": (120, 280, 220), "S4": (100, 240, 180)},
    "T6": {"S1": (180, 420, 380), "S2": (160, 400, 350), "S3": (140, 320, 260), "S4": (120, 280, 220)},
    "T7": {"S1": (200, 450, 400), "S2": (180, 450, 400), "S3": (160, 360, 300), "S4": (140, 300, 250)}
}


def cbr_to_mr(cbr):
    return 1500 * cbr


def solve_sn(esal, mr):
    SN = 1.0

    for _ in range(300):
        term = 9.36 * math.log10(SN + 1) + 2.32 * math.log10(mr) - 8.07
        error = math.log10(esal) - term
        SN += error * 0.01

        if abs(error) < 0.001:
            break

    return SN


def sn_to_layers(sn):
    a1, a2, a3 = 0.44, 0.14, 0.11
    surface = sn * 0.5 / a1
    base = sn * 0.3 / a2
    subbase = sn * 0.2 / a3
    return surface, base, subbase


# -----------------------------
# MAIN OUTPUT
# -----------------------------
if run:

    esal = calculate_esal(aadt, growth, years, hv)

    t_class = traffic_class(esal)
    s_class = cbr_class(cbr)

    premix, base, subbase = ATJ[t_class][s_class]

    mr = cbr_to_mr(cbr)
    sn = solve_sn(esal, mr)
    a1, a2, a3 = sn_to_layers(sn)

    # -----------------------------
    # TABLE
    # -----------------------------
    st.subheader("📊 ATJ vs AASHTO Comparison Table")

    df = pd.DataFrame({
        "Layer": ["Surface", "Base", "Subbase", "Total"],
        "ATJ (mm)": [premix, base, subbase, premix + base + subbase],
        "AASHTO (mm)": [a1, a2, a3, a1 + a2 + a3]
    })

    st.dataframe(df, use_container_width=True)

    # -----------------------------
    # BAR CHART (LAYER COMPARISON)
    # -----------------------------
    st.subheader("📈 Pavement Layer Thickness Comparison")

    layers = ["Surface", "Base", "Subbase"]

    atj_values = [premix, base, subbase]
    aashto_values = [a1, a2, a3]

    fig, ax = plt.subplots()

    x = range(len(layers))

    ax.bar([i - 0.2 for i in x], atj_values, width=0.4, label="ATJ")
    ax.bar([i + 0.2 for i in x], aashto_values, width=0.4, label="AASHTO")

    ax.set_xticks(x)
    ax.set_xticklabels(layers)
    ax.set_ylabel("Thickness (mm)")
    ax.set_title("Pavement Layer Thickness Comparison")
    ax.legend()

    st.pyplot(fig)