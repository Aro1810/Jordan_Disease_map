# --- IMPORTS ---
import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
from shapely import wkt
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- LOAD ENV VARIABLES ---
load_dotenv()  # Load environment variables from .env file

# --- SETUP ---
st.set_page_config(page_title="Jordan Disease Map", layout="wide")
st.title("🗺️ Jordan District Disease Map - 2024")

# --- GEMINI SETUP ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Load the key from the .env file
model = genai.GenerativeModel("gemini-1.5-flash")

# --- MAIN CODE ---
try:
    df = pd.read_csv("data.csv", encoding="utf-8")
    df["geometry"] = df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter")
    selected_gov = st.sidebar.selectbox(
        "Select Governorate:", 
        ["All"] + sorted(gdf["Governorate Name"].unique().tolist())
    )
    if selected_gov != "All":
        gdf = gdf[gdf["Governorate Name"] == selected_gov]

    # --- METRIC SELECTION ---
    metric = st.selectbox(
        "Choose a disease metric to visualize:",
        [
            "Diarrheal Diseases per 100K",
            "Escherichia coli Infections per 100K",
            "Giardiasis per 100K",
            "Gonococcal Infections per 100K",
            "Salmonella Infections per 100K",
            "Scabies per 100K",
            "Typhoid and Paratyphoid Fevers per 100K"
        ]
    )

    # --- FOLIUM MAP ---
    m = folium.Map(location=[31.24, 36.51], zoom_start=7)
    folium.Choropleth(
        geo_data=gdf.to_json(),
        name='choropleth',
        data=gdf,
        columns=['District Name', metric],
        key_on='feature.properties.District Name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color='gray',
        legend_name=f"{metric} (per 100K)"
    ).add_to(m)
    folium.GeoJson(
        gdf,
        tooltip=folium.GeoJsonTooltip(
            fields=["District Name", metric],
            aliases=["District:", f"{metric}:"]
        )
    ).add_to(m)
    folium_static(m)

    # --- DATA TABLE ---
    st.subheader("📊 District-Level Data Table")
    st.dataframe(gdf.drop(columns=["geometry"]))

    # --- DOWNLOAD BUTTON ---
    csv = gdf.to_csv(index=False)
    proposed_name = (
        "jordan_disease_data.csv"
        if selected_gov == "All"
        else selected_gov + "_Governorate_disease_data.csv"
    )
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name=proposed_name,
        mime="text/csv"
    )

    # --- GEMINI LLM SECTION ---
    st.subheader("🤖 Ask a Question About This Data")
    user_question = st.text_input(
        "Example: 'What is the population of Amman?', or 'Which district has the highest Typhoid rate?'"
    )

    if user_question:
        with st.spinner("Thinking..."):
            # Convert selected columns into a text block for Gemini
            short_df = gdf.drop(columns=["geometry", "href", "Wikidata", "img", "name"])
            context = short_df.to_csv(index=False)

            prompt = f"""You are a helpful data analyst. Based on the following CSV data, answer the user's question accurately. CSV Data: {context}
            User's Question: {user_question}"""

            try:
                response = model.generate_content(prompt)
                st.success(response.text)
            except Exception as e:
                st.error(f"LLM Error: {e}")

# --- ERROR HANDLING ---
except Exception as e:
    st.error(f"Error loading or parsing data.csv: {e}")
