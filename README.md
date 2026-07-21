# 🌍 Multi-Agent MCP Travel Planner ✈️

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![License](https://img.shields.io/badge/license-MIT-green)

> A powerful, real-world Multi-Agent AI System built with LangGraph that automates end-to-end travel planning. 

The **Multi-Agent MCP Travel Planner** leverages four specialized AI agents to autonomously handle flight searches, hotel bookings, weather forecasting, and complete itinerary generation. It incorporates persistent memory via PostgreSQL and communicates with real-world APIs through the Model Context Protocol (MCP).

---

## ✨ Key Features

- **✈️ Flight Search Agent**: Connects to the AviationStack API via MCP to find optimal routes and airlines.
- **🏨 Hotel Search Agent**: Utilizes the Tavily Search API via MCP to discover top-rated accommodations.
- **🌤️ Weather Agent**: Retrieves real-time weather and forecasts using a custom OpenWeather MCP server.
- **🗓️ Itinerary Planning Agent**: Synthesizes all gathered data into a personalized, coherent travel plan powered by LLaMA 3.3 70B (via Groq).
- **🧠 Persistent Memory**: Remembers user preferences and past interactions using PostgreSQL.
- **💻 Interactive Web UI**: Built with Streamlit for a sleek, user-friendly experience.

---

## 🛠️ Architecture & Workflow

<p align="center">
  <img src="assets/architecture.png" alt="Multi-Agent MCP Architecture Diagram" width="100%">
</p>

```mermaid
graph TD
    A[User Query] --> B(Flight Agent)
    B --> C(Hotel Agent)
    C --> D(Weather Agent)
    D --> E(Itinerary Agent)
    E --> F[Comprehensive Travel Plan]
    
    B -.->|AviationStack MCP| API1(Flights Data)
    C -.->|Tavily MCP| API2(Hotel Data)
    D -.->|OpenWeather MCP| API3(Weather Data)
    
    style A fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:white
    style F fill:#2196F3,stroke:#1976D2,stroke-width:2px,color:white
```

---

## ⚙️ Tech Stack

- **Framework**: LangGraph, LangChain
- **LLM Engine**: Groq (LLaMA 3.3 70B)
- **Database**: PostgreSQL
- **Frontend**: Streamlit
- **Protocols & Integrations**: Model Context Protocol (MCP) clients for Tavily, AviationStack, and OpenWeather

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.13+ installed and a running instance of PostgreSQL.

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# Alternatively, using uv:
# uv sync
```

### 3. Database Setup
Create a PostgreSQL database for the agent's memory:

```sql
CREATE DATABASE langgraph_memory_demo;
```

### 4. Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:

```ini
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/langgraph_memory_demo
```

> **API Key Resources:**
> - [Groq Console](https://console.groq.com)
> - [Tavily Search](https://tavily.com)
> - [AviationStack](https://aviationstack.com)
> - [OpenWeather](https://openweathermap.org/api)

---

## 💻 Usage

We recommend running the Streamlit web app for the best experience.

```bash
streamlit run frontend.py
```
*Navigate to `http://localhost:8501` in your browser.*

Alternatively, for a lightweight terminal interface:
```bash
python main.py
```

### How to Plan Your Trip:
1. **Enter User ID (Optional)**: Set a User ID in the sidebar to maintain your travel history across sessions.
2. **Describe Your Trip**: Enter your desired destination, budget, and timeline (e.g., *"Plan a 7-day trip to Japan under $2000"*).
3. **Generate**: Click the "🚀 Generate My Travel Plan" button.
4. **Watch the Agents Work**: The UI will display live progress as the Flight, Hotel, and Weather agents execute.
5. **Download**: Once your itinerary is ready, click **⬇️ Download Plan** to save it as a Markdown file.

---

## 📂 Project Structure

```text
multi-agent-mcp-travel-planner/
├── mcp_servers/
│   └── custom_weather_mcp_server.py   # Custom OpenWeather MCP server
├── frontend.py                         # Streamlit web interface
├── main.py                             # LangGraph multi-agent pipeline
├── mcp_client.py                       # MCP client & tool wrappers
├── requirements.txt                    # Project dependencies
├── pyproject.toml                      # Project metadata
└── README.md                           # Documentation
```

### 🧠 Core Architecture & Key Files

To understand how the project operates end-to-end, here is a breakdown of the most critical files and what they do in a systematic way:

| File Name | Role in the System | Description |
|-----------|-------------------|-------------|
| **`main.py`** | **The Brain (AI Logic)** | The core engine of the system. It builds the LangGraph workflow, configures the 4 travel agents (Flight, Hotel, Weather, Itinerary), and connects them to a PostgreSQL database for persistent memory. |
| **`mcp_client.py`** | **The Tool Provider** | Handles the Model Context Protocol (MCP) connections. Rather than the agents calling the internet directly, they ask this client. It wraps the external APIs (Tavily, AviationStack, OpenWeather) into tools for `main.py`. |
| **`frontend.py`** | **The Interface (UI)** | The interactive Streamlit dashboard. It takes user input, triggers the pipeline in `main.py`, displays live execution steps, and generates the final downloadable markdown itinerary. |
| **`custom_weather_mcp_server.py`** | **Custom Data Fetcher** | A locally-hosted custom MCP server located in `mcp_servers/`. It directly queries the OpenWeather API and exposes tools (`get_current_weather`, `get_forecast`) to the rest of the application. |
| **`.env`** | **Configuration** | *(User created)* Holds private API keys (Groq, Tavily, AviationStack, OpenWeather) and the PostgreSQL database URL crucial for the AI to authenticate and fetch real data. |
| **`requirements.txt` / `pyproject.toml`** | **Dependencies** | Lists all the Python packages (like `langgraph`, `streamlit`, `aviationstack-mcp`) required to build and run the project. |

---

## 📄 License
This project is licensed under the MIT License. See the `LICENSE` file for details.
