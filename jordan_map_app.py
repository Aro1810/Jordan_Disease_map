import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
from shapely import wkt

# Set up the Streamlit app layout and title
st.set_page_config(page_title="Jordan Disease Map", layout="wide")
st.title("🗺️ Jordan District Disease Map - 2024")

# Try loading and processing the data
try:
    # Read the CSV file that contains both data and WKT geometries
    df = pd.read_csv("data.csv")

    # Convert the WKT strings in the 'geometry' column to actual shapely geometries
    df["geometry"] = df["geometry"].apply(wkt.loads)

    # Create a GeoDataFrame with the specified coordinate reference system (WGS84 = EPSG:4326)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    # --- SIDEBAR FILTERS ---

    # Governorate dropdown filter in the sidebar
    st.sidebar.header("Filter")
    selected_gov = st.sidebar.selectbox(
        "Select Governorate:", 
        ["All"] + sorted(gdf["Governorate Name"].unique().tolist())
    )

    # Apply the governorate filter if one is selected
    if selected_gov != "All":
        gdf = gdf[gdf["Governorate Name"] == selected_gov]

    # Disease metric selection for the choropleth map
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

    # --- MAP GENERATION ---

    # Initialize the base folium map centered around Jordan
    m = folium.Map(location=[31.24, 36.51], zoom_start=7)

    # Create a choropleth layer to show the selected disease metric
    folium.Choropleth(
        geo_data=gdf.to_json(),             # Convert GeoDataFrame to GeoJSON
        name='choropleth',
        data=gdf,                           # Data for coloring
        columns=['District Name', metric],  # Data columns: district and metric
        key_on='feature.properties.District Name',  # How to link GeoJSON to data
        fill_color='YlOrRd',                # Color scheme (light to dark red)
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color='gray',              # Color for missing values
        legend_name=f"{metric} (per 100K)"  # Title for the legend
    ).add_to(m)

    # Add a layer with interactive tooltips on hover
    folium.GeoJson(
        gdf,
        tooltip=folium.GeoJsonTooltip(
            fields=["District Name", metric],  # Fields to display on hover
            aliases=["District:", f"{metric}:"]
        )
    ).add_to(m)

    # Display the folium map inside the Streamlit app
    folium_static(m)

    # --- DOWNLOAD BUTTON ---

    # Convert the GeoDataFrame to CSV (without index column)
    csv = gdf.to_csv(index=False)

    # genearete the file name
    if selected_gov == "All":
        file_name = "jordan_disease_data.csv"
    else:
        file_name = selected_gov + "_Governorate_disease_data.csv"
    # Add a download button to allow the user to download the data as CSV
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name= file_name,
        mime="text/csv"
    )

# If anything goes wrong, show an error message
except Exception as e:
    st.error(f"Error loading or parsing data.csv: {e}")
