import streamlit as st
import requests
import cohere

# 🔐 API keys hardcoded here
COHERE_API_KEY = "NqCDyPmfZHiXEDiyn0Xooutz67b0XHFPoeZ8qeYy"
ADZUNA_APP_ID = "a4a68e77"
ADZUNA_APP_KEY = "ce47a52bee49d0f4b9a33581a9d852e9"
ADZUNA_COUNTRY = "za"

career_map = {
    "technology": ["Coding", "AI", "Computers", "Gaming"],
    "healthcare": ["Biology", "Helping others", "Health", "Medicine"],
    "engineering": ["Math", "Design", "Building", "Physics"],
    "business": ["Economics", "Leadership", "Marketing", "Sales"],
    "arts": ["Creativity", "Drawing", "Writing", "Music"],
    "education": ["Teaching", "Learning", "Explaining", "Kids"]
}

def suggest_careers(interests):
    matches = []
    for field, keywords in career_map.items():
        if any(k.lower() in i.lower() or i.lower() in k.lower() for i in interests for k in keywords):
            matches.append(field)
    return matches if matches else ["general"]

def fetch_jobs(keyword):
    url = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 3,
        "what": keyword
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return [(job["title"], job["location"].get("display_name", "Unknown"), job["redirect_url"]) for job in results]
        else:
            return [("API Error", "N/A", "")]
    except Exception as e:
        return [(f"API Request Failed: {e}", "N/A", "")]

def get_ai_advice(prompt):
    try:
        co = cohere.Client(COHERE_API_KEY)
        response = co.generate(
            model="command",
            prompt=prompt,
            max_tokens=700,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Cohere API error: {e}"

# 🖼️ Page setup
st.set_page_config(page_title="Career Advisor", layout="centered")
st.title("🎓 AI Career Selection Chatbot")
st.markdown("Get career suggestions based on your interests and skills.")

# 🧠 Session state
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "interests" not in st.session_state:
    st.session_state.interests = []
if "dummy" not in st.session_state:
    st.session_state.dummy = False  # Dummy variable to force UI change

# 🎯 Input
if not st.session_state.show_results:
    name = st.text_input("Your Name", value=st.session_state.name)
    interests = st.multiselect(
        "Select your top 3 interests",
        options=sum(career_map.values(), []),
        default=st.session_state.interests,
        help="Pick things you enjoy or are good at"
    )
    if st.button("Suggest Careers"):
        if not name or not interests:
            st.warning("Please enter your name and select interests.")
        else:
            st.session_state.name = name
            st.session_state.interests = interests
            st.session_state.show_results = True
            st.session_state.dummy = not st.session_state.dummy  # Force UI update
else:
    name = st.session_state.name
    interests = st.session_state.interests

    st.subheader(f"Hi {name}, here are your suggestions:")

    matched_fields = suggest_careers(interests)
    st.markdown("**🔍 Recommended Career Fields:**")
    for field in matched_fields:
        st.success(f"✅ {field.capitalize()}")

    st.markdown("### 💼 Live Job Listings")
    job_found = False
    for field in matched_fields:
        jobs = fetch_jobs(field)
        for title, location, url in jobs:
            if "API" in title:
                continue
            st.markdown(f"- **{title}** in *{location}* [View Job]({url})")
            job_found = True
    if not job_found:
        st.error("No live jobs found or there was an API issue.")

    st.markdown("### 💡 AI Career Advice")
    prompt = f"I am interested in {', '.join(interests)}. What careers should I consider and why?"
    advice = get_ai_advice(prompt)
    st.text_area("AI Suggestions:", advice, height=600)

    if st.button("🔁 Try Again"):
        # Reset everything
        st.session_state.show_results = False
        st.session_state.name = ""
        st.session_state.interests = []
        st.session_state.dummy = not st.session_state.dummy  # Force refresh
