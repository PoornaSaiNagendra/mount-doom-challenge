# Mount Doom Challenge 🌋🧠⚙️

This repository implements a scalable, resilient system for processing voice agent transcripts using LLMs. 🌐🔁📊 It demonstrates best practices in:

* **Asynchronous API Integration**: Authenticated streaming from an external transcripts API and submission of processed results.
* **Queue & Concurrency**: Back-pressure management with `asyncio.Queue` and a worker pool.
* **LLM Processing**: OpenAI integration for summarization and analysis with retries and prompt engineering.
* **Storage Layer**: Async persistence of raw transcripts and processed results in PostgreSQL via SQLAlchemy.
* **Testing & CI**: Comprehensive unit tests, integration tests using GitHub Actions, and code linting.
* **Containerization**: Dockerfile and Docker Compose for easy local deployment.

## Repository Structure 🗂️📁🔍

```
mount-doom-challenge/
│
├── README.md                 # Challenge overview and setup guide
├── CHALLENGE.md              # Detailed prompt description
├── docs/
│   ├── api-schema.md         # API documentation
│   └── system-diagram.svg    # Architecture diagram
│
├── src/
│   ├── api/
│   ├── processing/
│   ├── queue/
│   ├── storage/
│   └── app.py                # Main entrypoint
│
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
├── Dockerfile                # Container definition
├── docker-compose.yml        # Service orchestration
└── .github/workflows/ci.yml  # CI pipeline
```

## Prerequisites ✅🧰🔑

* Docker & Docker Compose
* Python 3.11
* An OpenAI API key (set `OPENAI_API_KEY`)

## Local Development 💻🔧🚀

1. **Clone the repo**

   ```bash
   git clone https://github.com/PoornaSaiNagendra/VOICE-AGENT.git
   cd VOICE-AGENT
   ```

2. **Environment Variables**
   Create a `.env` file or export:

   ```bash
   export API_KEY="<your-api-key>"
   export BASE_URL="https://<your-api>/api"
   export OPENAI_API_KEY="<your-openai-key>"
   ```

3. **Start Services**

   ```bash
   docker-compose up --build
   ```

4. **Run Tests**

   ```bash
   pytest
   ```

## Deployment 📦🚢🌍

* Build Docker image: `docker build -t mount-doom-challenge:latest .`
* Push to your registry and deploy with Kubernetes, ECS, or other container orchestrators.

## Extending the System 🧩🔄📈

* **LLM Models**: Swap `gpt-4o-mini` with other OpenAI models or integrate additional providers.
* **Scaling**: Adjust `CONCURRENCY` and queue parameters in `src/app.py`.
* **Observability**: Integrate Prometheus, Grafana, and distributed tracing.


