# Sensor Analytics Agent

A professional-grade Data Analytics Agent capable of querying technical sensor data using natural language. Built with **LangChain**, **Google Gemini**, **FastAPI**, and **PostgreSQL**.

## Features

-   **Natural Language to SQL**: Converts engineering queries (e.g., "Show correlation between high temp and vibration") into optimized SQL.
-   **Direct Database Integration**: Connects directly to PostgreSQL using `psycopg2` for robust data handling.
-   **Interactive Dashboard**: A modern, glassmorphism-inspired web interface with a clean light theme.
-   **Smart Suggestions**: Provides 8 technical prompt suggestions to guide deep analysis.
-   **Chat History**: Persists conversation history in the database for context-aware responses.
-   **Transparency**: Displays the executed SQL query alongside the analysis for verification.

## Prerequisites

-   Python 3.10+
-   PostgreSQL Database
-   Google Gemini API Key

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd data_analytics_agent
    ```

2.  **Install dependencies**:
    Using `uv` (recommended):
    ```bash
    uv sync
    ```
    Or using standard pip:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure `psycopg2-binary`, `fastapi`, `uvicorn`, `langchain-google-genai`, `python-dotenv` are installed).*

3.  **Configure Environment**:
    Create a `.env` file in the root directory with the following variables:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key
    
    # Database Credentials
    user=your_db_user
    password=your_db_password
    host=localhost
    port=5432
    dbname=your_db_name
    
    # Legacy/Optional (if using Supabase REST)
    SUPABASE_URL=...
    SUPABASE_KEY=...
    ```

4.  **Database Setup**:
    Run the included SQL script to create the `sensor_data` and `chat_history` tables and populate them with dummy data (1500 rows).
    -   Execute `setup.sql` in your PostgreSQL client (e.g., pgAdmin, Supabase SQL Editor, or psql).

## Running the Application

Start the FastAPI server:

```bash
python main.py
```

The application will be available at **http://localhost:8000**.

## Usage

1.  Open the dashboard in your browser.
2.  Click on one of the **Technical Suggestions** (e.g., "Analyze pressure variance") or type your own query.
3.  The agent will:
    -   Generate a SQL query based on your request.
    -   Execute it against the `sensor_data` table.
    -   Display the **Executed SQL** for your review.
    -   Render the data in a styled HTML table.
    -   Provide a summary analysis.

## Tech Stack

-   **Backend**: Python, FastAPI
-   **AI/LLM**: LangChain, Google Gemini (gemini-1.5-flash)
-   **Database**: PostgreSQL (psycopg2)
-   **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript
