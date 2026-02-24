import streamlit as st
import pandas as pd
from sheet_loader import load_sheet
from scraper import scrape_product
from renderer import render_story
import zipfile
import io

st.set_page_config(page_title="Digihaat Story Generator", layout="wide")

# ---------- HEADER ----------
st.markdown("""
<style>
.hero-title { font-size: 80px; font-weight: 800; margin-bottom: 1px; }
.hero-subtitle { font-size: 30px; font-weight: 400; color: #888; margin-bottom: 5px; }
</style>

<div class="hero-title">Digihaat Story Generator</div>
<div class="hero-subtitle">Generate Instagram stories directly from Google Sheets</div>
""", unsafe_allow_html=True)

st.divider()

# ---------- LOAD DATA ----------
df = load_sheet()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
available_dates = sorted(df['Date'].dropna().unique())

if not available_dates:
    st.error("No valid dates found in sheet.")
    st.stop()

selected_date = st.date_input(
    "Select Date",
    value=max(available_dates),
    format="DD/MM/YYYY"
)

selected_date = pd.to_datetime(selected_date)

# ---------- SESSION STATE ----------
if "generated_by_date" not in st.session_state:
    st.session_state.generated_by_date = {}

# ---------- GENERATE BUTTON ----------
if st.button("✨ Generate Stories"):

    filtered = df[df['Date'] == selected_date]

    if filtered.empty:
        st.warning("No products found for selected date.")
    else:
        images = []

        with st.spinner("Generating stories..."):
            for _, row in filtered.iterrows():
                data = scrape_product(row['LINK'])

                img = render_story(
                    data["name"],
                    data["old_price"],
                    int(row['Deal Price']),
                    data["image"]
                )

                images.append(img)

        # store by date
        st.session_state.generated_by_date[selected_date] = images
        st.success(f"✅ Generated {len(images)} stories for {selected_date.strftime('%d %b %Y')}")

# ---------- SHOW STORIES (persist per date) ----------
if selected_date in st.session_state.generated_by_date:

    images = st.session_state.generated_by_date[selected_date]

    st.divider()
    st.subheader(f"📸 Stories for {selected_date.strftime('%d %b %Y')}")

    cols = st.columns(len(images))

    for i, (col, img) in enumerate(zip(cols, images)):

        with col:
            st.image(img, use_container_width=True)

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")

            st.download_button(
                label="⬇ Download",
                data=buffer.getvalue(),
                file_name=f"story_{i+1}.png",
                mime="image/png",
                key=f"download_{selected_date}_{i}"
            )

    # ---------- ZIP DOWNLOAD ----------
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for i, img in enumerate(images):
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            zf.writestr(f"story_{i+1}.png", img_bytes.getvalue())

    st.divider()
    st.download_button(
        label="📦 Download All Stories (ZIP)",
        data=zip_buffer.getvalue(),
        file_name=f"digihaat_{selected_date.strftime('%d_%m_%Y')}.zip",
        mime="application/zip",
        key=f"zip_{selected_date}"
    )