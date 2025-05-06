# Jordan Disease Map - 2024

This is a Streamlit app that visualizes disease data across Jordan's districts using geographic data and the Gemini AI model for answering questions.

## Setup Instructions

### 1. Clone the repository

### 2. Create a virtual environment (optional but recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

### 3. Install the required dependencies
pip install -r requirements.txt

### 4. Set up environment variables
Create a `.env` file in the root directory of the project. Add your **Gemini API key** in the following format:
GEMINI_API_KEY=<your-gemini-api-key>

### 5. Running the app
streamlit run jordan_map_app.py

This will start the app, and it will be accessible at `http://localhost:8501` in your browser.

## Usage
- **Filter**: Use the sidebar to filter the data by governorate.
- **Disease Metrics**: Choose from a variety of disease metrics to visualize on the map.
- **Interactive Map**: Explore the disease rates across different districts of Jordan with a choropleth map.
- **Ask Questions**: Use the LLM-powered question box to ask questions about the displayed data.



## Troubleshooting
If you encounter issues with the Gemini API or dependencies, please ensure that your API key is correctly set in the `.env` file and that all required dependencies are installed.
