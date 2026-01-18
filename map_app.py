import geopandas as gpd
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import os

# Set Streamlit page config
st.set_page_config(page_title="Geo-Legend | Integrated Map", layout="wide")

# 1. Custom CSS for styling
st.markdown("""
    <style>
    /* 1. Force FULL WIDTH for map (Removes Streamlit side padding) */
    .stMainBlockContainer, [data-testid="stMainBlockContainer"], .block-container {
        padding: 0rem !important;
        max-width: 100vw !important;
        margin: 0 !important;
    }

    /* 2. Target the Unified Legend Card BUT NOT the map container */
    div[data-testid="stVerticalBlock"]:has(.legend-anchor):not(:has(iframe)) {
        position: fixed;
        top: 30px;
        right: 30px;
        width: 300px !important;
        background: rgba(255, 255, 255, 0.1); /* Glass: More transparent */
        backdrop-filter: blur(20px);           /* Glass: Stronger blur */
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.5); /* Crisper edge */
        border-radius: 12px;
        padding: 16px;
        z-index: 999999;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        opacity: 0.98;
    }

    .legend-handle {
        margin: -16px -16px 15px -16px;
        padding: 12px 16px;
        background: transparent; /* Transparent to show blur */
        border-bottom: 1px solid rgba(0,0,0,0.1);
        border-radius: 12px 12px 0 0;
        font-size: 13px;
        color: #1a1a1a;
        font-weight: 600;
        cursor: move;
        display: flex;
        align-items: center;
        justify-content: space-between;
        user-select: none;
    }
    
    .drag-dots {
        width: 12px;
        height: 12px;
        background-image: radial-gradient(#ccc 1px, transparent 1px);
        background-size: 3px 3px;
    }

    .color-bar {
        height: 14px;
        width: 100%;
        background: linear-gradient(90deg, #9b87db 0%, #fec84d 100%);
        border: 1px solid #333;
        border-radius: 2px;
        margin-bottom: 5px;
    }

    .range-txt {
        text-align: right;
        font-size: 11px;
        font-weight: bold;
        color: #d32f2f;
        margin-bottom: 5px;
    }

    .stSlider { margin-top: 10px !important; }
    div[data-baseweb="slider"] > div:first-child { background: transparent !important; }
    div[role="slider"] {
        background-color: #333 !important;
        width: 3px !important;
        height: 22px !important;
        border-radius: 0 !important;
    }
    div[data-testid="stThumbValue"] { display: none !important; }

    .tick-marks {
        display: flex;
        justify-content: space-between;
        font-size: 9px;
        color: #444;
        font-weight: bold;
        margin-top: -5px;
        margin-bottom: 15px;
    }

    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    .stButton button {
        background: #f0f0f0 !important;
        border: 1px solid #ccc !important;
        font-size: 11px !important;
        height: 30px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Ultra-Robust JavaScript for Draggability
DRAG_JS = """
<script>
    (function() {
        const doc = window.parent.document;
        
        const attachDrag = () => {
            const handle = doc.querySelector('.legend-handle');
            if (!handle || handle.dataset.dragListening === "true") return;

            // Find the card container (The vertical block that has the legend anchor)
            const box = handle.closest('div[data-testid="stVerticalBlock"]');
            if (!box) return;

            handle.dataset.dragListening = "true";
            
            // Critical Styles to decouple from Streamlit layout
            box.style.position = 'fixed';
            box.style.zIndex = '999999';
            box.style.width = '300px';

            let shield = doc.getElementById('drag-shield-global');
            if (!shield) {
                shield = doc.createElement('div');
                shield.id = 'drag-shield-global';
                shield.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:999998;display:none;cursor:grabbing;';
                doc.body.appendChild(shield);
            }

            let dragging = false;
            let sx, sy, bl, bt;

            handle.onmousedown = (e) => {
                dragging = true;
                shield.style.display = 'block';
                const r = box.getBoundingClientRect();
                bl = r.left;
                bt = r.top;
                
                // Switch to viewport coords
                box.style.right = 'auto';
                box.style.bottom = 'auto';
                box.style.left = bl + 'px';
                box.style.top = bt + 'px';
                box.style.margin = '0';

                sx = e.clientX;
                sy = e.clientY;
                handle.style.backgroundColor = '#f0f0f0';
                e.preventDefault();
            };

            const onMove = (e) => {
                if (!dragging) return;
                box.style.left = (bl + (e.clientX - sx)) + 'px';
                box.style.top = (bt + (e.clientY - sy)) + 'px';
            };

            const onUp = () => {
                if (dragging) {
                    dragging = false;
                    shield.style.display = 'none';
                    handle.style.backgroundColor = '#fdfdfd';
                }
            };

            doc.addEventListener('mousemove', onMove);
            doc.addEventListener('mouseup', onUp);
        };

        setInterval(attachDrag, 1000);
    })();
</script>
"""

@st.cache_data
def load_data():
    csv_path = "/Users/sangeeth/Documents/GitHub/geo-legend/Median age of population (2023).csv"
    if not os.path.exists(csv_path): return None
    df = pd.read_csv(csv_path)
    df['fips'] = df['Entity DCID'].str.split('/').str[1]
    df['median_age'] = df['Variable observation value']
    fl_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        gdf = gpd.read_file(fl_url)
        fl_gdf = gdf[gdf['id'].str.startswith('12')].copy()
        return fl_gdf.merge(df[['fips', 'median_age', 'Entity properties name']], left_on='id', right_on='fips')
    except: return None

def main():
    gdf = load_data()
    if gdf is None: return

    mina, maxa = float(gdf['median_age'].min()), float(gdf['median_age'].max())

    def reset_filter():
        st.session_state.age_filter = (mina, maxa)

    components.html(DRAG_JS, height=0)

    # --- THE LEGEND BOX ---
    with st.container():
        st.markdown('<div class="legend-anchor"></div>', unsafe_allow_html=True)
        st.markdown('<div class="legend-handle"><span>Median age in Florida</span><div class="drag-dots"></div></div>', unsafe_allow_html=True)
        
        if 'age_filter' not in st.session_state:
            st.session_state.age_filter = (mina, maxa)
            
        age_range = st.slider(
            "Age", mina, maxa, 
            key="age_filter",
            step=0.01, 
            label_visibility="collapsed"
        )
        
        st.markdown(f'<div class="range-txt">{age_range[0]:.2f} &nbsp;&nbsp;&nbsp; {age_range[1]:.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="color-bar"></div>', unsafe_allow_html=True)
        
        t = [mina, mina+(maxa-mina)*0.25, mina+(maxa-mina)*0.5, mina+(maxa-mina)*0.75, maxa]
        st.markdown(f'<div class="tick-marks"><span>{t[0]:.0f}</span><span>{t[1]:.0f}</span><span>{t[2]:.0f}</span><span>{t[3]:.0f}</span><span>{t[4]:.0f}</span></div>', unsafe_allow_html=True)
        
        st.button("Reset Filter", use_container_width=True, on_click=reset_filter)

    # --- THE MAP (FULL PAGE) ---
    filt = gdf[(gdf['median_age'] >= age_range[0]) & (gdf['median_age'] <= age_range[1])]
    m = filt.explore(column="median_age", cmap="YlOrRd", legend=False, tooltip=['Entity properties name', 'median_age'], tiles="cartodbpositron")
    st_folium(m, width=2048, height=1000, use_container_width=True)

if __name__ == "__main__":
    main()
