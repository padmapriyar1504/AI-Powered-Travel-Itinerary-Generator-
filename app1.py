
import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image
from io import BytesIO
import subprocess
import sys

# Ensure required packages are installed
def install_dependencies():
    required_packages = ["google-generativeai", "requests", "pillow", "streamlit"]
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))  # Check if package is installed
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install missing dependencies before running the app
install_dependencies()
genai.configure(api_key="AIzaSyCFPQEgfqwyFRUQPcQElZX73zJ7kcITTxE")

model = genai.GenerativeModel("gemini-2.0-flash")

GOOGLE_API_KEY = "AIzaSyAVaLD8E9cn1nu9iO3SsFd2nFG91zl-mkA"  
CSE_ID = "35c77626f007c499f"  

def search_top_attractions(destination):
    search_query = f"Top attractions in {destination}"
    search_url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&cx={CSE_ID}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(search_url)
        results = response.json().get("items", [])
        return [{"title": item["title"], "link": item["link"]} for item in results[:5]]  # Get top 5 attractions
    except Exception:
        return []

def fetch_destination_image(destination):
    search_query = f"{destination} famous landmarks"
    search_url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&cx={CSE_ID}&searchType=image&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(search_url)
        image_url = response.json()["items"][0]["link"]
        return image_url
    except Exception:
        return None

def generate_itinerary(start_location, destination, budget, duration, preferences, accommodation, mobility, food_prefs):
    attractions = search_top_attractions(destination)
    prompt = f"""
    You are an AI travel assistant. Create a {duration}-day itinerary for a traveler from {start_location} to {destination}.
    Budget: {budget}
    Accommodation: {accommodation}
    Mobility: {mobility}
    Food Preferences: {food_prefs}
    Other Preferences: {preferences}
    Top Attractions: {', '.join([attr['title'] for attr in attractions])}
    
    ### Structure:
    - Morning Activity
    - Breakfast
    - Mid-Morning Activity
    - Lunch
    - Afternoon Activity
    - Evening Activity
    - Dinner
    - Optional Nightlife Spot

    ### Additional Information:
    - **Approximate Daily Expenses Breakdown** (Accommodation, Food, Transport, Activities)
    - **Total Estimated Budget for {duration} Days**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating itinerary: {e}"

st.title("🌍 AI-Powered Travel Planner")
st.write("Get a customized AI-generated itinerary for your next trip!")

col1, col2 = st.columns(2)
with col1:
    start_location = st.text_input("Enter your starting location:")
with col2:
    destination = st.text_input("Enter your travel destination:")

budget = st.selectbox("Select your budget:", ["Budget", "Moderate", "Luxury"])
duration = st.slider("Trip Duration (days):", 1, 14, 3)
preferences = st.text_area("Describe your preferences (e.g., adventure, food, nature):")
accommodation = st.selectbox("Accommodation Preference:", ["Budget-Friendly", "Mid-Range", "Luxury", "Unique Stays"])
mobility = st.selectbox("Mobility Concerns:", ["None", "Limited Walking", "Wheelchair Accessible"])
food_prefs = st.text_input("Food Preferences (e.g., vegetarian, vegan, halal, seafood):")

if st.button("Generate Itinerary"):
    if start_location and destination and budget and duration:
        with st.spinner("Generating your itinerary..."):
            # Fetch destination image
            # image_url = fetch_destination_image(destination)
            # if image_url:
            #     response = requests.get(image_url)
            #     img = Image.open(BytesIO(response.content))
            #     st.image(img, caption=f"{destination} Highlights", use_column_width=True)

            itinerary = generate_itinerary(start_location, destination, budget, duration, preferences, accommodation, mobility, food_prefs)
            st.subheader(f"Your {duration}-Day Travel Itinerary for {destination}")
            st.write(itinerary)

            # Show top attractions with clickable links
            attractions = search_top_attractions(destination)
            if attractions:
                st.subheader("Top Attractions You Might Like:")
                for attr in attractions:
                    st.markdown(f"✅ [{attr['title']}]({attr['link']})")
            else:
                st.write("No attractions found.")

    else:
        st.error("Please fill in all required details.")
