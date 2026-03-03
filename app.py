from PIL import Image
import streamlit as st
import pandas as pd
from sheet_loader import load_sheet
from scraper import scrape_product
from renderer import render_story
import io
from io import BytesIO
import requests
import copy

st.set_page_config(page_title="Digihaat Story Generator", layout="wide")

# ---------- HEADER ----------
st.markdown("""
<style>
.hero-title { font-size: 80px; font-weight: 800; margin-bottom: 1px; }
.hero-subtitle { font-size: 30px; font-weight: 400; color: #888; margin-bottom: 5px; }
.modified-badge { color:#f39c12; font-size:14px; font-weight:500; }
</style>

<div class="hero-title">Digihaat Story Generator</div>
<div class="hero-subtitle">Generate Instagram stories directly from Google Sheets</div>
""", unsafe_allow_html=True)

st.divider()

# ---------- LOAD DATA ----------
df = load_sheet()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
available_dates = sorted(df['Date'].dropna().unique())

selected_date = st.date_input(
    "Select Date",
    value=max(available_dates),
    format="DD/MM/YYYY"
)

selected_date = pd.to_datetime(selected_date)

if "generated_by_date" not in st.session_state:
    st.session_state.generated_by_date = {}

# ---------- GENERATE ----------
if st.button("✨ Generate Stories"):

    filtered = df[df['Date'] == selected_date]
    items = []

    for _, row in filtered.iterrows():
        data = scrape_product(row['LINK'])
        deal_price = int(row['Deal Price'])

        response = requests.get(data["image"], timeout=20)
        product_image = Image.open(BytesIO(response.content)).convert("RGBA")

        original_data = {
            "name": data["name"],
            "old_price": data["old_price"],
            "deal_price": deal_price
        }

        items.append({
            "original": copy.deepcopy(original_data),
            "current": copy.deepcopy(original_data),
            "draft": copy.deepcopy(original_data),
            "product_image": product_image,
            "link": row["LINK"] 
        })

    st.session_state.generated_by_date[selected_date] = items

# ---------- DISPLAY ----------
if selected_date in st.session_state.generated_by_date:

    items = st.session_state.generated_by_date[selected_date]

    # Fixed layout: Edit 1/4 | Preview 3/4
    edit_col, preview_col = st.columns([1, 3])

    # ---------------- EDIT PANEL ----------------
    with edit_col:
        st.markdown("## Edit Stories")

        for i, item in enumerate(items):

            with st.expander(f"Story {i+1}", expanded=True):

                draft = item["draft"]
                current = item["current"]
                original = item["original"]

                # Inputs update draft only
                draft_name = st.text_input(
                    "Product Name",
                    draft["name"],
                    key=f"name_{selected_date}_{i}"
                )

                draft_old = st.number_input(
                    "Old Price (₹)",
                    min_value=0,
                    value=draft["old_price"],
                    step=1,
                    key=f"old_{selected_date}_{i}"
                )

                draft_deal = st.number_input(
                    "Deal Price (₹)",
                    min_value=0,
                    value=draft["deal_price"],
                    step=1,
                    key=f"deal_{selected_date}_{i}"
                )

                if draft_deal > draft_old:
                    st.warning("⚠ Caution: Deal price is more than the old price")

                # Update draft state
                item["draft"] = {
                    "name": draft_name,
                    "old_price": draft_old,
                    "deal_price": draft_deal
                }

                # Show Save button ONLY if draft != current
                if item["draft"] != current:
                    if st.button("💾 Save Changes", key=f"save_{selected_date}_{i}"):
                        item["current"] = copy.deepcopy(item["draft"])
                        st.rerun()

                # Reset to original
                if st.button("Reset to Original", key=f"reset_{selected_date}_{i}"):
                    item["draft"] = copy.deepcopy(original)
                    item["current"] = copy.deepcopy(original)
                    st.rerun()

    # ---------------- PREVIEW AREA ----------------
    with preview_col:

        st.subheader(f"📸 Stories for {selected_date.strftime('%d %b %Y')}")

        cols = st.columns(len(items))

        for i, (col, item) in enumerate(zip(cols, items)):

            with col:

                current = item["current"]
                original = item["original"]

                is_modified = current != original

                if is_modified:
                    st.markdown(
                        "<span class='modified-badge'>● Modified</span>",
                        unsafe_allow_html=True
                    )

                rendered_image = render_story(
                    current["name"],
                    current["old_price"],
                    current["deal_price"],
                    item["product_image"]
                )

                st.image(rendered_image, use_container_width=True)

                buffer = io.BytesIO()
                rendered_image.save(buffer, format="PNG")

                st.download_button(
                    "⬇ Download",
                    buffer.getvalue(),
                    f"story_{i+1}.png",
                    mime="image/png",
                    key=f"download_{selected_date}_{i}"
                )

                caption = f"""Get this {current['name']}

At just ₹{current['deal_price']} 🔥

Link of the product:
{item['link']}"""

                st.code(caption)