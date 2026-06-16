import streamlit as st
from sheet_loader import load_sheet
from scraper import scrape_product
from renderer import render_story
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import io
import copy


st.set_page_config(page_title="Digihaat Story Generator", layout="wide")

# ---------- GLOBAL STYLES ----------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">

<style>
/* ========== BASE & RESET ========== */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Main app background */
.stApp {
    background-color: #080c10 !important;
    color: #e8edf2 !important;
}

/* Hide default Streamlit top decoration */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #00253E; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #003d66; }

/* ========== MAIN CONTENT PADDING ========== */
.block-container {
    padding: 2.5rem 3rem 3rem 3rem !important;
    max-width: 100% !important;
}

/* ========== HERO HEADER ========== */
.hero-wrap {
    padding: 0.5rem 0 1.5rem 0;
}
.hero-eyebrow {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #4fa3d4;
    margin-bottom: 10px;
}
.hero-title {
    font-size: 58px;
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1.05;
    background: linear-gradient(135deg, #ffffff 0%, #a8c8e8 60%, #4fa3d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
}
.hero-subtitle {
    font-size: 15px;
    font-weight: 400;
    color: #5a7a95;
    letter-spacing: 0.2px;
    margin-bottom: 0;
}
.hero-divider {
    margin-top: 28px;
    height: 1px;
    background: linear-gradient(90deg, #00253E 0%, #003d66 40%, transparent 100%);
    border: none;
}

/* ========== DATE INPUT ========== */
.stDateInput label {
    color: #7a9ab5 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 1.8px !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}
.stDateInput input {
    background-color: #0d1822 !important;
    border: 1px solid #1a3348 !important;
    border-radius: 8px !important;
    color: #e8edf2 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s ease !important;
}
.stDateInput input:focus {
    border-color: #00253E !important;
    box-shadow: 0 0 0 3px rgba(0, 37, 62, 0.4) !important;
    outline: none !important;
}

/* ========== GENERATE BUTTON ========== */
.stButton > button[kind="secondary"], .stButton > button {
    background: linear-gradient(135deg, #00253E 0%, #003d66 100%) !important;
    color: #ffffff !important;
    border: 1px solid #004d7a !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    padding: 10px 22px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(0, 37, 62, 0.5) !important;
    min-height: 42px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #003357 0%, #005580 100%) !important;
    border-color: #0073aa !important;
    box-shadow: 0 4px 16px rgba(0, 37, 62, 0.8) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 4px rgba(0, 37, 62, 0.4) !important;
}

/* ========== SECTION HEADINGS ========== */
h2 {
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    color: #c8dcea !important;
    margin-bottom: 14px !important;
}
h3, .stSubheader {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #7a9ab5 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}

/* ========== EDIT PANEL — LEFT COLUMN ========== */
/* Sticky-style panel feel */
[data-testid="column"]:first-child {
    border-right: 1px solid #0f1f2e;
    padding-right: 1.5rem !important;
}

/* ========== EXPANDERS ========== */
.streamlit-expanderHeader {
    background-color: #0d1822 !important;
    border: 1px solid #1a3348 !important;
    border-radius: 8px !important;
    color: #a8c8e0 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.4px !important;
    padding: 10px 14px !important;
    transition: background-color 0.2s ease !important;
}
.streamlit-expanderHeader:hover {
    background-color: #10202e !important;
    border-color: #00253E !important;
}
.streamlit-expanderContent {
    background-color: #080c10 !important;
    border: 1px solid #1a3348 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 16px !important;
}
details[open] summary {
    border-radius: 8px 8px 0 0 !important;
}

/* ========== TEXT INPUTS ========== */
.stTextInput label, .stNumberInput label {
    color: #6a8fa8 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    margin-bottom: 5px !important;
}
.stTextInput input, .stNumberInput input {
    background-color: #0d1822 !important;
    border: 1px solid #1a3348 !important;
    border-radius: 7px !important;
    color: #dce8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    padding: 9px 12px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #00486e !important;
    box-shadow: 0 0 0 3px rgba(0, 72, 110, 0.25) !important;
    outline: none !important;
}
.stNumberInput [data-testid="stNumberInputContainer"] {
    background-color: #0d1822 !important;
    border: 1px solid #1a3348 !important;
    border-radius: 7px !important;
}
.stNumberInput button {
    background-color: #0f1e2b !important;
    border-color: #1e3a52 !important;
    color: #7ab2cc !important;
}
.stNumberInput button:hover {
    background-color: #172840 !important;
}

/* ========== WARNING ========== */
.stAlert {
    background-color: #1a1200 !important;
    border: 1px solid #3d2e00 !important;
    border-radius: 7px !important;
    color: #d4aa50 !important;
    font-size: 12px !important;
}
.stAlert .st-emotion-cache-1629p8f {
    color: #d4aa50 !important;
}

/* ========== DIVIDER ========== */
hr {
    border-color: #0f1f2e !important;
    margin: 18px 0 !important;
}

/* ========== PREVIEW AREA ========== */
/* Story image cards */
[data-testid="stImage"] img {
    border-radius: 10px !important;
    border: 1px solid #1a3348 !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
    transition: box-shadow 0.3s ease !important;
}
[data-testid="stImage"] img:hover {
    box-shadow: 0 12px 48px rgba(0, 37, 62, 0.8) !important;
}

/* ========== DOWNLOAD BUTTON ========== */
.stDownloadButton > button {
    background-color: #0d1822 !important;
    border: 1px solid #1a3348 !important;
    border-radius: 7px !important;
    color: #7ab2cc !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    padding: 8px 14px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background-color: #00253E !important;
    border-color: #0066a0 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(0, 37, 62, 0.5) !important;
    transform: translateY(-1px) !important;
}

/* ========== CODE / CAPTION BLOCK ========== */
.stCode, [data-testid="stCode"] {
    background-color: #060f17 !important;
    border: 1px solid #0f2030 !important;
    border-radius: 8px !important;
}
.stCode pre, [data-testid="stCode"] pre {
    background-color: #060f17 !important;
    color: #6fa8c8 !important;
    font-size: 11px !important;
    padding: 10px 12px !important;
}
[data-testid="stCodeCopyButton"] {
    color: #4a7a96 !important;
}

/* ========== MODIFIED BADGE ========== */
.modified-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(243, 156, 18, 0.12);
    border: 1px solid rgba(243, 156, 18, 0.3);
    border-radius: 20px;
    color: #f0b429 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    padding: 3px 10px;
    margin-bottom: 6px;
}

/* ========== COLUMN SEPARATOR ========== */
[data-testid="column"] + [data-testid="column"] {
    padding-left: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">✦ &nbsp; Digihaat Internal Tool</div>
    <div class="hero-title">Story Generator</div>
    <div class="hero-subtitle">Generate Instagram stories directly from Google Sheets</div>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

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

    total = len(filtered)

    progress_bar = st.progress(0)
    status_text = st.empty()

    with st.spinner("Generating stories..."):

        for idx, (_, row) in enumerate(filtered.iterrows()):

            status_text.write(f"Generating Story {idx+1} of {total}")

            try:

                data = scrape_product(row['LINK'])

                deal_raw = str(row['Deal Price']).strip()

                if deal_raw in ["", "nan", "None"]:
                    deal_price = "-"
                else:
                    try:
                        deal_price = int(float(deal_raw))
                    except (ValueError, TypeError):
                        deal_price = deal_raw

                img_url = str(data["image"])
                if img_url.startswith("data:"):
                    b64_data = img_url.split(",", 1)[1]
                    import base64
                    product_image = Image.open(BytesIO(base64.b64decode(b64_data))).convert("RGBA")
                else:
                    response = requests.get(img_url, timeout=20)
                    product_image = Image.open(BytesIO(response.content)).convert("RGBA")

                original_data = {
                    "name": data["name"],
                    "old_price": data["old_price"],
                    "deal_price": deal_price
                }

                items.append({
                    "original": original_data,
                    "current": original_data.copy(),
                    "draft": original_data.copy(),
                    "product_image": product_image,
                    "link": row["LINK"],
                    "error": None
                })

            except Exception as e:

                items.append({
                    "error": str(e),
                    "link": row["LINK"]
                })

            progress_bar.progress((idx + 1) / total)

    status_text.success("Stories generated successfully!")

    st.session_state.generated_by_date[selected_date] = items

# ---------- DISPLAY ----------
if selected_date in st.session_state.generated_by_date:

    items = st.session_state.generated_by_date[selected_date]

    st.markdown("<hr>", unsafe_allow_html=True)

    # Fixed layout: Edit 1/4 | Preview 3/4
    edit_col, preview_col = st.columns([1, 3])

    # ---------------- EDIT PANEL ----------------
    with edit_col:
        st.markdown("## Edit Stories")

        for i, item in enumerate(items):

            with st.expander(f"Story {i+1}", expanded=True):

                # ---------- ERROR CASE ----------
                if item.get("error"):

                    st.error("⚠ This story could not be generated")

                    st.code(item["error"])

                    st.caption(f"Link: {item['link']}")

                    continue

                # ---------- NORMAL CASE ----------
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

                if isinstance(draft["deal_price"], (int, float)):
                    draft_deal = st.number_input(
                        "Deal Price (₹)",
                        min_value=0,
                        value=draft["deal_price"],
                        step=1,
                        key=f"deal_{selected_date}_{i}"
                    )
                else:
                    raw_deal = st.text_input(
                        "Deal Price",
                        value=str(draft["deal_price"]),
                        key=f"deal_{selected_date}_{i}"
                    )
                    try:
                        draft_deal = int(float(raw_deal))
                    except (ValueError, TypeError):
                        draft_deal = raw_deal
                        st.error("⚠ Invalid format for Deal Price")

                if isinstance(draft_deal, (int, float)) and draft_deal > draft_old:
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
                if st.button("↺  Reset to Original", key=f"reset_{selected_date}_{i}"):
                    item["draft"] = copy.deepcopy(original)
                    item["current"] = copy.deepcopy(original)
                    st.rerun()

    # ---------------- PREVIEW AREA ----------------
    with preview_col:

        st.subheader(f"Stories · {selected_date.strftime('%d %b %Y')}")

        cols = st.columns(len(items))

        for i, (col, item) in enumerate(zip(cols, items)):

            with col:

                # ---------- ERROR CARD ----------
                if item.get("error"):

                    st.error("⚠ Story could not be generated")

                    st.code(item["error"])

                    st.caption(f"Link: {item['link']}")

                    continue

                # ---------- NORMAL STORY ----------
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

                st.image(rendered_image, width="stretch")

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
