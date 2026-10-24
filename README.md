# Multi-Agent Travel Planner

An AI travel-planning application that combines flight information, hotel search, and weather data, then uses an LLM to produce a travel itinerary. The agents are run as a sequential [LangGraph](https://www.langchain.com/langgraph) workflow, with conversation checkpoints stored in PostgreSQL.

## What it does

For a natural-language travel request, the workflow:

1. Retrieves airport and airline information from AviationStack.
2. Searches for hotel recommendations with Tavily.
3. Looks up current weather and a short forecast with OpenWeatherMap.
4. Combines the results into a travel itinerary using Groq.

The current application entry point is a command-line prompt in `main.py`.

## Technology stack

| Area | Technologies |
| --- | --- |
| Language and runtime | Python 3.13+ |
| Agent orchestration and state | LangGraph, LangChain |
| Language model | Groq via `langchain-groq` (`openai/gpt-oss-120b`) |
| Tool integration | Model Context Protocol (MCP), `langchain-mcp-adapters` |
| Flight data | AviationStack API via [`aviationstack-mcp`](https://github.com/Pradumnasaraf/aviationstack-mcp) |
| Hotel and web search | Tavily MCP service |
| Weather | OpenWeatherMap API via the included FastMCP server |
| Checkpoint persistence | PostgreSQL, `psycopg`, `langgraph-checkpoint-postgres` |
| Configuration and HTTP | `python-dotenv`, `requests` |

`requirements.txt` also includes Streamlit and other LangChain integrations, but this repository currently has no Streamlit app or UI entry point.

## Requirements

- Python 3.13 or newer. The AviationStack MCP server currently requires Python 3.13+.
- PostgreSQL 14 or newer, running locally or reachable over the network.
- API keys for Groq, Tavily, AviationStack, and OpenWeatherMap.
- Git and an internet connection to install the AviationStack MCP server and access the APIs.

Create accounts and obtain API keys from [Groq](https://console.groq.com/keys), [Tavily](https://app.tavily.com/home), [AviationStack](https://aviationstack.com/), and [OpenWeatherMap](https://openweathermap.org/api).

## Install

### 1. Clone the project and create a virtual environment

```powershell
git clone https://github.com/Mehreen1103/Multi-Agent-Travel-Planner.git
cd Multi-Agent-Travel-Planner
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow scripts for the current terminal session, then activate:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, create and activate the environment with:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### 2. Install Python dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install "git+https://github.com/pradumnasaraf/aviationstack-mcp.git"
```

The AviationStack MCP server used by this project is sourced from [Pradumnasaraf/aviationstack-mcp](https://github.com/Pradumnasaraf/aviationstack-mcp). It is a separate upstream project rather than code maintained in this repository; installing it makes the `aviationstack_mcp` module available to the travel planner.

### 3. Start PostgreSQL

Use an existing PostgreSQL server, or start one with Docker:

```powershell
docker run --name travel-planner-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=travel_planner -p 5432:5432 -d postgres:16
```

### 4. Configure API keys and database access

Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/travel_planner
```

Use your own credentials and database connection details. Do not commit `.env` or publish API keys. `DATABASE_URL` must point to an existing PostgreSQL database; the application initializes LangGraph's checkpoint tables when it starts.

## Run

With PostgreSQL running, the virtual environment active, and `.env` configured:

```bash
python main.py
```

Enter a request when prompted, for example:

```text
Plan a 5-day trip from New York to Paris in June
```

The workflow calls external services and the configured LLM, so valid API keys and internet access are required.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Defines and runs the travel-agent graph, and initializes PostgreSQL checkpointing. |
| `mcp_client.py` | Configures Tavily, AviationStack, and weather MCP clients and their tool wrappers. |
| `custom-mcp-server.py` | Exposes current weather and forecast tools using OpenWeatherMap. |
| `requirements.txt` | Python dependencies for the application. |
| `test-as.py` | Small diagnostic script that lists the AviationStack MCP tools. |

## Troubleshooting

- **Missing API key:** Check that the key is spelled correctly in the root `.env` file and that the variable name matches the configuration above.
- **PostgreSQL connection error:** Confirm PostgreSQL is running, the database exists, and `DATABASE_URL` has the correct host, port, database, username, and password.
- **`aviationstack_mcp` not found:** Activate the project's virtual environment and rerun the AviationStack MCP installation command.
- **No weather or search results:** Confirm the corresponding API key is valid and that the provider account/API plan allows the requested endpoint.

## License

No license file is currently included in this repository. Check with the project maintainers before redistributing or reusing the project.
