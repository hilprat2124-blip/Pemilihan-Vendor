import streamlit as st
import pandas as pd
import pulp
import matplotlib.pyplot as plt

st.set_page_config(page_title="Vendor Selection Dashboard", page_icon="🏗️", layout="wide")

st.title("🏗️ Vendor Selection Dashboard")
st.caption("Project A — Piping Installation | Sistem pendukung keputusan pemilihan vendor")

st.info(
    "Aplikasi demonstrasi menggunakan data vendor simulasi. "
    "Hasil optimasi adalah rekomendasi awal dan harus diverifikasi oleh tim Project, Engineering, HSE, dan Purchasing."
)

DEFAULT_VENDORS = pd.DataFrame([
    {"Vendor": "Vendor A", "Harga (juta Rp)": 120.0, "Kualitas (0-100)": 92, "Durasi (hari)": 25, "Skor K3 (0-100)": 90, "Lolos teknis": True},
    {"Vendor": "Vendor B", "Harga (juta Rp)": 105.0, "Kualitas (0-100)": 76, "Durasi (hari)": 20, "Skor K3 (0-100)": 88, "Lolos teknis": True},
    {"Vendor": "Vendor C", "Harga (juta Rp)": 115.0, "Kualitas (0-100)": 88, "Durasi (hari)": 28, "Skor K3 (0-100)": 91, "Lolos teknis": True},
    {"Vendor": "Vendor D", "Harga (juta Rp)": 98.0, "Kualitas (0-100)": 85, "Durasi (hari)": 35, "Skor K3 (0-100)": 86, "Lolos teknis": True},
    {"Vendor": "Vendor E", "Harga (juta Rp)": 145.0, "Kualitas (0-100)": 95, "Durasi (hari)": 22, "Skor K3 (0-100)": 94, "Lolos teknis": True},
])

with st.sidebar:
    st.header("Parameter Project")
    project_name = st.text_input("Nama proyek", "Project A — Piping Installation")
    min_quality = st.slider("Skor kualitas minimum", min_value=0, max_value=100, value=80)
    budget = st.number_input("Budget maksimum (juta Rp)", min_value=1.0, value=300.0, step=10.0)
    deadline = st.number_input("Deadline maksimum (hari)", min_value=1, value=30, step=1)
    min_hse = st.slider("Skor K3 minimum", min_value=0, max_value=100, value=80)
    require_technical = st.checkbox("Wajib lolos evaluasi teknis", value=True)

st.subheader("1. Data Vendor")
st.write("Edit data simulasi di tabel ini atau unggah file CSV dengan kolom yang sama.")
uploaded = st.file_uploader("Unggah data vendor CSV (opsional)", type=["csv"])

if uploaded:
    try:
        vendors = pd.read_csv(uploaded)
        required_cols = list(DEFAULT_VENDORS.columns)
        missing = [c for c in required_cols if c not in vendors.columns]
        if missing:
            st.error("Kolom berikut belum tersedia: " + ", ".join(missing))
            vendors = DEFAULT_VENDORS.copy()
    except Exception as e:
        st.error(f"File CSV tidak dapat dibaca: {e}")
        vendors = DEFAULT_VENDORS.copy()
else:
    vendors = DEFAULT_VENDORS.copy()

edited = st.data_editor(
    vendors,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    column_config={
        "Harga (juta Rp)": st.column_config.NumberColumn(min_value=0.0, format="%.2f"),
        "Kualitas (0-100)": st.column_config.NumberColumn(min_value=0, max_value=100, step=1),
        "Durasi (hari)": st.column_config.NumberColumn(min_value=1, step=1),
        "Skor K3 (0-100)": st.column_config.NumberColumn(min_value=0, max_value=100, step=1),
        "Lolos teknis": st.column_config.CheckboxColumn(),
    }
)

st.subheader("2. Filter Kelayakan")
if edited.empty:
    st.warning("Belum ada data vendor.")
    st.stop()

numeric_cols = ["Harga (juta Rp)", "Kualitas (0-100)", "Durasi (hari)", "Skor K3 (0-100)"]
for col in numeric_cols:
    edited[col] = pd.to_numeric(edited[col], errors="coerce")
edited = edited.dropna(subset=["Vendor"] + numeric_cols)
edited["Vendor"] = edited["Vendor"].astype(str)
edited["Lolos teknis"] = edited["Lolos teknis"].fillna(False).astype(bool)

eligible = (
    (edited["Kualitas (0-100)"] >= min_quality)
    & (edited["Durasi (hari)"] <= deadline)
    & (edited["Skor K3 (0-100)"] >= min_hse)
)
if require_technical:
    eligible &= edited["Lolos teknis"]

edited["Status Kelayakan"] = eligible.map({True: "Lolos", False: "Tidak lolos"})
edited["Alasan"] = ""
for idx, row in edited.iterrows():
    reasons = []
    if row["Kualitas (0-100)"] < min_quality:
        reasons.append("Kualitas di bawah minimum")
    if row["Durasi (hari)"] > deadline:
        reasons.append("Durasi melebihi deadline")
    if row["Skor K3 (0-100)"] < min_hse:
        reasons.append("Skor K3 di bawah minimum")
    if require_technical and not row["Lolos teknis"]:
        reasons.append("Tidak lolos teknis")
    edited.loc[idx, "Alasan"] = "; ".join(reasons) if reasons else "Memenuhi kriteria"

st.dataframe(
    edited[["Vendor", "Harga (juta Rp)", "Kualitas (0-100)", "Durasi (hari)", "Skor K3 (0-100)", "Status Kelayakan", "Alasan"]],
    use_container_width=True,
    hide_index=True
)

candidates = edited[edited["Status Kelayakan"] == "Lolos"].copy()
st.subheader("3. Optimasi dengan PuLP")
st.markdown(
    "Untuk satu paket pekerjaan yang harus diberikan kepada tepat satu vendor, "
    "model menggunakan variabel biner: **xᵢ = 1** jika vendor *i* dipilih, dan **0** jika tidak."
)

if len(candidates) == 0:
    st.error("Tidak ada vendor yang lolos. Coba tinjau kembali parameter atau data vendor.")
    st.stop()

# Binary Integer Linear Programming: select exactly one eligible vendor.
model = pulp.LpProblem("Vendor_Selection", pulp.LpMinimize)
vendor_vars = {
    idx: pulp.LpVariable(f"select_{idx}", cat=pulp.LpBinary)
    for idx in candidates.index
}
model += pulp.lpSum(candidates.loc[idx, "Harga (juta Rp)"] * vendor_vars[idx] for idx in candidates.index)
model += pulp.lpSum(vendor_vars[idx] for idx in candidates.index) == 1, "Select_exactly_one_vendor"
model += pulp.lpSum(candidates.loc[idx, "Harga (juta Rp)"] * vendor_vars[idx] for idx in candidates.index) <= budget, "Budget_limit"

status_code = model.solve(pulp.PULP_CBC_CMD(msg=False))
status = pulp.LpStatus[status_code]

if status != "Optimal":
    st.error(f"Solver tidak menemukan solusi optimal yang memenuhi kendala. Status: {status}")
    st.stop()

chosen_idx = next(idx for idx in candidates.index if pulp.value(vendor_vars[idx]) > 0.5)
chosen = candidates.loc[chosen_idx]
minimum_cost = float(chosen["Harga (juta Rp)"])
eligible_under_budget = candidates[candidates["Harga (juta Rp)"] <= budget]
if eligible_under_budget.empty:
    st.error("Tidak ada vendor yang lolos dengan harga dalam budget.")
    st.stop()

# Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Vendor direkomendasikan", chosen["Vendor"])
m2.metric("Estimasi biaya", f"Rp{minimum_cost:,.2f} jt".replace(",", "X").replace(".", ",").replace("X", "."))
m3.metric("Sisa budget", f"Rp{budget-minimum_cost:,.2f} jt".replace(",", "X").replace(".", ",").replace("X", "."))
m4.metric("Durasi vendor", f"{int(chosen['Durasi (hari)'])} hari")

st.success(
    f"Rekomendasi model: **{chosen['Vendor']}** untuk **{project_name}**, "
    f"dengan biaya simulasi Rp{minimum_cost:,.2f} juta, kualitas {int(chosen['Kualitas (0-100)'])}/100, "
    f"durasi {int(chosen['Durasi (hari)'])} hari, dan skor K3 {int(chosen['Skor K3 (0-100)'])}/100."
    .replace(",", "X").replace(".", ",").replace("X", ".")
)

st.subheader("4. Perbandingan Kandidat Lolos")
comparison = candidates.sort_values("Harga (juta Rp)").copy()
comparison["Terpilih"] = comparison.index == chosen_idx
st.dataframe(
    comparison[["Vendor", "Harga (juta Rp)", "Kualitas (0-100)", "Durasi (hari)", "Skor K3 (0-100)", "Terpilih"]],
    use_container_width=True,
    hide_index=True
)

fig, ax = plt.subplots()
colors = ["#2E8B57" if idx == chosen_idx else "#8CA6B8" for idx in comparison.index]
ax.bar(comparison["Vendor"], comparison["Harga (juta Rp)"], color=colors)
ax.set_ylabel("Harga penawaran (juta Rp)")
ax.set_title("Harga Vendor yang Lolos Kriteria")
ax.grid(axis="y", alpha=0.25)
st.pyplot(fig)
plt.close(fig)

# Baseline for savings: cheapest technically/quality/time/HSE eligible vendor's quoted price is the optimum itself.
st.caption(
    "Catatan metodologi: karena fungsi objektif meminimalkan harga dan semua kandidat sudah lolos ambang kualitas, "
    "K3, durasi, serta teknis, sistem memilih kandidat termurah yang memenuhi kendala. "
    "Skor kualitas yang lebih tinggi tidak otomatis dianggap lebih baik secara ekonomi kecuali bobot atau target kualitas "
    "tambahan didefinisikan dalam model."
)

export_cols = ["Vendor", "Harga (juta Rp)", "Kualitas (0-100)", "Durasi (hari)", "Skor K3 (0-100)", "Status Kelayakan", "Alasan"]
csv_data = edited[export_cols].to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ Unduh hasil evaluasi vendor (CSV)", data=csv_data,
                   file_name="hasil_evaluasi_vendor.csv", mime="text/csv")

with st.expander("Lihat formulasi model"):
    st.latex(r"\min Z = \sum_i c_i x_i")
    st.latex(r"\sum_i x_i = 1")
    st.latex(r"\sum_i c_i x_i \leq B")
    st.latex(r"x_i \in \{0,1\}")
    st.write(
        "Variabel hanya dibuat untuk vendor yang lolos filter kualitas, durasi, K3, dan evaluasi teknis. "
        "B adalah budget maksimum; cᵢ adalah harga penawaran vendor i."
    )
