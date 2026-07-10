import os
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app

st.set_page_config(page_title="AI Travel Booking System", page_icon="✈️", layout="wide")

###################################
# CSS
###################################
st.markdown("""
<style>
/* Refined Primary Button */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 2rem !important;
    transition: all 0.2s ease;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    transform: translateY(-1px) !important;
}

/* Cleaner Text Area */
.stTextArea textarea {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

###################################
# Sidebar
###################################
with st.sidebar:
    st.title("🌍 AI Travel Planner")
    st.markdown("---")
    
    thread_id = st.text_input(
        "👤 User ID",
        value="default_user",
        help="Your session ID — keeps travel history across queries",
    )

    st.subheader("Powered by")
    st.markdown("- 🔗 LangGraph\n- 🧠 Groq · LLaMA 3.3 70B\n- 🐘 PostgreSQL\n- 🔍 Tavily Search\n- ✈️ AviationStack\n- 🌤️ OpenWeather")

    st.subheader("Agent Pipeline")
    st.markdown("1. ✈️ Flight Agent\n2. 🏨 Hotel Agent\n3. 🌤️ Weather Agent\n4. 🗓️ Itinerary Agent")

###################################
# Main Interface
###################################
st.title("✈️ AI Travel Booking System")
st.markdown("Four specialized agents work together — searching flights, hotels, weather, building an itinerary, and delivering your perfect trip plan.")
st.markdown("---")

st.subheader("🗺️ Describe your trip")

# Quick Destinations
QUICK = [
    "6-day serene Kerala (South India) trip",
    "10-day Euro trip (Italy & Switzerland)",
    "7-day Japan cultural tour under ₹2L",
    "4-day Maldives relaxing getaway",
]

# Use a clean selectbox for quick templates instead of blocky buttons
template_choice = st.selectbox(
    "Or choose a quick template:", 
    ["(Write my own)"] + QUICK,
    index=0
)

quick_fill = template_choice if template_choice != "(Write my own)" else ""

user_query = st.text_area(
    "Trip Description",
    value=quick_fill,
    placeholder="e.g. Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs",
    height=100,
    label_visibility="collapsed"
)

generate = st.button("🚀 Generate My Travel Plan", type="primary", use_container_width=True)

###################################
# Agent Pipeline Execution
###################################
AGENT_META = {
    "flight_agent": ("✈️", "Flight Agent"),
    "hotel_agent": ("🏨", "Hotel Agent"),
    "weather_agent": ("🌤️", "Weather Agent"),
    "itinerary_agent": ("🗓️", "Itinerary Agent"),
}

if generate:
    if not user_query.strip():
        st.warning("Please describe your trip first.")
    else:
        config = {"configurable": {"thread_id": thread_id}}
        collected = {
            "flight_results": "",
            "hotel_results": "",
            "weather_results": "",
            "itinerary": "",
            "llm_calls": 0,
        }

        st.markdown("---")
        st.subheader("🤖 Agent Pipeline — Live")

        for chunk in app.stream(
            {
                "messages": [HumanMessage(content=user_query)],
                "user_query": user_query,
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",
                "llm_calls": 0,
            },
            config=config,
            stream_mode="updates",
        ):
            for node_name, state_update in chunk.items():
                icon, label = AGENT_META.get(node_name, ("🔧", node_name))

                with st.expander(f"{icon} {label}", expanded=True):
                    if node_name == "flight_agent":
                        text = state_update.get("flight_results", "")
                        collected["flight_results"] = text
                        st.markdown(text or "_No flight data returned._")

                    elif node_name == "hotel_agent":
                        text = state_update.get("hotel_results", "")
                        collected["hotel_results"] = text
                        st.markdown(text or "_No hotel data returned._")

                    elif node_name == "weather_agent":
                        text = state_update.get("weather_results", "")
                        collected["weather_results"] = text
                        st.markdown(text or "_No weather data returned._")

                    elif node_name == "itinerary_agent":
                        text = state_update.get("itinerary", "")
                        collected["itinerary"] = text
                        st.markdown(text or "_No itinerary generated._")

                    collected["llm_calls"] = state_update.get(
                        "llm_calls", collected["llm_calls"]
                    )

        ###################################
        # Metrics Display
        ###################################
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Agents Run", 4)
        m2.metric("LLM Calls", collected["llm_calls"])
        m3.metric("Status", "✅ Complete")

        ###################################
        # Final Plan Card
        ###################################
        if collected["itinerary"]:
            st.markdown("---")
            st.subheader("🗓️ Complete Travel Plan")
            st.info(collected["itinerary"])

        ###################################
        # Save & Download
        ###################################
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.md"
        save_dir = os.path.join(os.path.dirname(__file__), "travel_plans")
        os.makedirs(save_dir, exist_ok=True)

        file_content = f"""# Travel Plan
**Query:** {user_query}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**User ID:** {thread_id}

---

## ✈️ Flight Information
{collected['flight_results'] or 'N/A'}

---

## 🏨 Hotel Information
{collected['hotel_results'] or 'N/A'}

---

## 🌤️ Weather Information
{collected['weather_results'] or 'N/A'}

---

## 🗓️ Itinerary
{collected['itinerary'] or 'N/A'}

---
*LLM Calls: {collected['llm_calls']}*
"""
        with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
            f.write(file_content)

        st.markdown("---")
        st.download_button(
            "⬇️ Download Plan",
            data=file_content,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True,
        )
        st.success(f"📁 Auto-saved → `travel_plans/{filename}`")
