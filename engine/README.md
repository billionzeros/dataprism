# Data Insights Engine

A powerful **Data Insights Engine** driven by semantic understanding, designed to extract meaningful patterns and insights from diverse data sources through advanced AI-powered analysis.

## 🎯 Overview

This engine leverages cutting-edge technologies including **DSPy**, **Neo4j Knowledge Graphs**, **Vector Embeddings**, and **Large Language Models** to create a comprehensive data intelligence platform that understands and analyzes data at a semantic level.

## ✨ Key Features

### 🧠 Semantic Understanding
- **MetricEncodingModule**: Transforms raw metrics into structured, semantic representations
- **Knowledge Graph Integration**: Stores relationships and patterns in a Neo4j graph database
- **Vector Embeddings**: Creates meaningful vector representations for similarity search and clustering

### 🔍 AI-Powered Analysis
- **DSPy Framework**: Utilizes advanced prompt engineering and optimization
- **MatrixModule**: Handles complex query execution with plan-reflect-synthesize patterns
- **Multi-Modal Processing**: Supports various data formats (CSV, Parquet, documents, etc.)

### 🛠 Advanced Tooling
- **Parquet File Analysis**: Schema extraction and querying capabilities
- **Similarity Search**: Find related data points across different sources
- **Code Generation**: Automatic code creation for data analysis tasks
- **MLflow Integration**: Experiment tracking and model management

### 📊 Data Pipeline
- **Learning Pipeline**: Automated data ingestion and pattern recognition
- **Execution Pipeline**: Real-time data processing and analysis
- **Model Context Protocol (MCP)**: Extensible tool integration framework

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Data Insights Engine                        │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend                                               │
│  ├── LLM Modules (DSPy)                                        │
│  │   ├── MetricEncodingModule                                  │
│  │   ├── MatrixModule                                          │
│  │   └── CodeGenerationModule                                  │
│  ├── Knowledge Graph (Neo4j)                                   │
│  ├── Vector Embeddings                                         │
│  ├── Learning Pipeline                                         │
│  └── MCP Tool Integration                                      │
├─────────────────────────────────────────────────────────────────┤
│  External Services                                              │
│  ├── MLflow (Experiment Tracking)                              │
│  ├── Neo4j Database                                            │
│  └── Cloud Storage (R2/S3)                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- **Python**: >= 3.12
- **Docker**: For Neo4j database
- **UV**: Python package manager
- **MLflow**: For experiment tracking
- **API Keys**: Gemini API key for LLM operations

### System Setup

Before installing the project dependencies, you need to set up the required tools:

#### 1. Install UV (Python Package Manager)

Follow the official UV installation guide: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

**Verify installation:**
```bash
uv --version
```

#### 2. Install MLflow

Follow the official MLflow installation guide: [https://mlflow.org/docs/latest/getting-started/intro-quickstart/index.html](https://mlflow.org/docs/latest/getting-started/intro-quickstart/index.html)

**Quick install:**
```bash
pip install mlflow
# or
uv tool install mlflow
```

**Verify installation:**
```bash
mlflow --version
```

#### 3. Install Docker

Follow the official Docker installation guide for your operating system:
- **macOS**: Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
- **Linux**: Use your package manager or follow [Docker's Linux installation guide](https://docs.docker.com/engine/install/)
- **Windows**: Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)

**Verify installation:**
```bash
docker --version
docker-compose --version
```

#### 4. Create Virtual Environment (Optional but Recommended)

While UV manages environments automatically, you can also create a traditional virtual environment:

**Using UV (Recommended):**
```bash
# UV automatically manages virtual environments
# No manual setup required - UV handles this when you run commands
```

**Using Python venv (Alternative):**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Deactivate when done
deactivate
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/billionzeros/dataprism.git
   cd dataprism/engine
   ```

2. **Install dependencies**
   ```bash
   make install
   ```
   
   **Note:** UV automatically creates and manages a virtual environment for this project. The `make install` command uses `uv pip sync pyproject.toml` which:
   - Creates a virtual environment if one doesn't exist
   - Installs all dependencies specified in `pyproject.toml`
   - Ensures reproducible dependency resolution

   **Alternative manual UV commands:**
   ```bash
   # Create virtual environment explicitly
   uv venv
   
   # Install dependencies manually
   uv pip install -e .
   
   # Or sync from pyproject.toml
   uv pip sync pyproject.toml
   ```

3. **Set up environment variables**
   Create a `.env` file with:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   ```

### Running the Application

The application requires three main services to run properly:

#### 1. Start MLflow Server
```bash
make mlflow
```
This starts the MLflow tracking server on `http://127.0.0.1:3080` for experiment logging and DSPy run tracking.

#### 2. Start Neo4j Knowledge Graph Database
```bash
make kg-up
```
This launches a Neo4j database in Docker for storing the knowledge graph.

#### 3. Run the Main Application
```bash
make run
```
This starts the FastAPI server with all the AI modules and pipelines.

### Complete Setup Script
```bash
# Start all services
make mlflow &     # Start MLflow in background
make kg-up        # Start Neo4j database
make run          # Start the main application
```

## 🛠 Available Commands

### Development Commands
```bash
make install      # Install dependencies using uv
make run          # Run the main application
make lint         # Lint code using Ruff
make format       # Format code using Ruff
make check        # Check formatting and linting
make clean        # Remove cache files
```

### Infrastructure Commands
```bash
make mlflow       # Start MLflow server
make kg-up        # Start Neo4j database
make kg-down      # Stop Neo4j database
```

### Database Migration Commands
```bash
make migrate-up           # Run database migrations
make migrate-down         # Rollback last migration
make migrate-down-all     # Rollback all migrations
make migrate-create name="migration_name"        # Create new migration
make migrate-create-empty name="migration_name"  # Create empty migration
```

### Utility Commands
```bash
make requirements # Generate requirements.txt with hashes
```

## 📚 Core Components

### 🔄 Learning Pipeline
The Learning Pipeline is responsible for:
- Ingesting raw metrics data
- Encoding data using LLM capabilities
- Storing encoded data with embeddings as Metric Nodes in the Knowledge Graph
- Identifying patterns and correlations between metrics

### 🧠 MetricEncodingModule
Transforms raw metrics into structured formats:
- Converts unstructured data into clean, human-friendly representations
- Generates descriptions and metadata for each metric
- Ensures consistency across different data sources

### 🌐 Knowledge Graph
Powered by Neo4j for:
- Storing semantic relationships between data points
- Enabling complex graph queries
- Maintaining data lineage and provenance
- Supporting pattern recognition and similarity search

### 🔍 MatrixModule
Advanced query processing engine that:
- Plans query execution strategies
- Reflects on intermediate results
- Synthesizes comprehensive responses
- Handles multi-step reasoning tasks

## 📦 Dependencies

### Core Dependencies
- **FastAPI**: Web framework for API development
- **DSPy**: Framework for composing language model pipelines
- **Neo4j**: Graph database for knowledge storage
- **MLflow**: Experiment tracking and model management
- **Pandas**: Data manipulation and analysis
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation and settings management

### AI/ML Dependencies
- **Google GenAI**: Large language model integration
- **PgVector**: Vector similarity search
- **PyArrow**: Columnar data processing
- **DuckDB**: In-process analytical database

### Infrastructure Dependencies
- **Uvicorn**: ASGI server
- **Alembic**: Database migration tool
- **Boto3**: AWS SDK for cloud storage
- **AsyncPG**: Async PostgreSQL driver

## 🔧 Configuration

The application uses environment-based configuration through `app/settings/config.py`. Key settings include:

- **Database connections** (PostgreSQL, Neo4j)
- **API keys** (Gemini, cloud services)
- **Server configuration** (host, port, workers)
- **Logging levels** and formats
- **Thread pool settings**

## 📊 Monitoring and Logging

- **MLflow Integration**: Track experiments, models, and DSPy runs
- **Structured Logging**: Comprehensive application logging
- **Health Checks**: Built-in service monitoring
- **Error Tracking**: Detailed error reporting and handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**
   - Ensure Docker is running
   - Check if port 7687 is available
   - Verify Neo4j container is healthy: `docker ps`

2. **MLflow Server Not Starting**
   - Check if port 3080 is available
   - Ensure MLflow is installed: `uv run mlflow --version`

3. **Missing API Keys**
   - Verify `.env` file exists with required keys
   - Check GEMINI_API_KEY is valid

### Debug Commands
```bash
# Check service status
docker-compose -f docker/neo4j_service/docker-compose.yml ps

# View application logs
uv run python run.py --log-level debug

# Test Neo4j connection
curl http://localhost:7474
```

## 🔮 Future Roadmap

- [ ] Multi-tenant support
- [ ] Real-time streaming data processing
- [ ] Advanced visualization components
- [ ] Custom model fine-tuning
- [ ] Extended data connector library
- [ ] GraphQL API support
- [ ] Distributed processing capabilities

---

**Built ❤️ by Billionzeros**

