import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
from shapely import wkt

# Set Streamlit page config
st.set_page_config(page_title="Jordan Disease Map", layout="wide")

# Title
st.title("🗺️ Jordan District Disease Map - 2024")

# Load CSV data directly
try:
    df = pd.read_csv("data.csv")

    # Convert WKT geometry to shapely objects
    df["geometry"] = df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")


    # Sidebar for filtering
    st.sidebar.header("Filter")
    selected_gov = st.sidebar.selectbox("Select Governorate:", ["All"] + sorted(gdf["Governorate Name"].unique().tolist()))

    if selected_gov != "All":
        gdf = gdf[gdf["Governorate Name"] == selected_gov]

    # Metric selection
    metric = st.selectbox("Choose a disease metric to visualize:", [
        "Diarrheal Diseases per 100K",
        "Escherichia coli Infections per 100K",
        "Giardiasis per 100K",
        "Gonococcal Infections per 100K",
        "Salmonella Infections per 100K",
        "Scabies per 100K",
        "Typhoid and Paratyphoid Fevers per 100K"
    ])

    # Initialize map
    m = folium.Map(location=[31.24, 36.51], zoom_start=7)

    # Add choropleth layer
    folium.Choropleth(
        geo_data=gdf.to_json(),
        name='choropleth',
        data=gdf,
        columns=['District Name', metric],
        key_on='feature.properties.District Name',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color='gray',
        legend_name=f"{metric} (per 100K)"
    ).add_to(m)

    # Add hover tooltips
    folium.GeoJson(
        gdf,
        tooltip=folium.GeoJsonTooltip(fields=["District Name", metric])
    ).add_to(m)

    # Show map
    folium_static(m)

except Exception as e:
    st.error(f"Error loading or parsing data.csv: {e}")
