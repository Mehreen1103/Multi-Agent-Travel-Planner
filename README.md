# Travel Planning Console

A Streamlit travel-planning app that combines flight search, hotel web search, and an LLM-generated itinerary and final trip plan. LangGraph orchestrates the workflow, and PostgreSQL stores checkpointed state for requests associated with a user ID.

## Features

- Generate a travel plan from a free-form trip description.
- Search flight information with AviationStack.
- Search for accommodation information with Tavily.
- Generate an itinerary and final plan with Groq.
- Optionally associate a request with a user ID to store LangGraph checkpoint state in PostgreSQL. Leave the ID blank for a request without checkpoint persistence.
- Download the generated plan as a Markdown file. Plans are also written to `travel_plans/`.

The app does not currently provide a separate screen for browsing saved conversations.

## Requirements

- Python 3.10 or newer
- PostgreSQL database and a connection URL
- API keys for Groq, Tavily, and AviationStack

## Setup

Open PowerShell in the project directory and create a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create your local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and provide your own credentials:

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

Replace every placeholder. The PostgreSQL database must exist and be accessible using the supplied connection URL. The application initializes the LangGraph checkpoint tables when it starts.

## Run the web app

From the project directory, with the virtual environment activated:

```powershell
python -m streamlit run .\frontend.py
```

Open the local URL Streamlit prints in the terminal (usually <http://localhost:8501>).

In the app's sidebar, leave **User ID** blank for a request without persisted checkpoint state. Enter an ID to associate checkpoints with that ID in PostgreSQL; enter the same ID again to continue using that checkpoint thread.

## Run the command-line version

The graph can also be run from the terminal:

```powershell
python .\main.py
```

This command prompts for a travel request and uses the checkpointed graph.

## Project layout

```text
.
├── frontend.py       # Streamlit interface
├── main.py           # LangGraph workflow and PostgreSQL checkpointing
├── requirements.txt  # Python dependencies
├── tools/
│   ├── flight_tool.py
│   └── tavily_tool.py
└── travel_plans/     # Generated plans (kept local, not committed)
```

## Keep credentials private

Do not commit `.env` or paste real API keys or database credentials into issues or public discussions. `.env.example` contains placeholders only. If a credential is accidentally exposed, revoke or rotate it with its provider.
