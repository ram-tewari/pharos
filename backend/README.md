# Neo Alexandria 2.0 - Advanced Knowledge Management API

## Overview

Neo Alexandria 2.0 is a comprehensive knowledge management system that provides intelligent content processing, advanced search capabilities, and personalized recommendations through a RESTful API. The system combines traditional information retrieval with modern AI-powered features to deliver a complete solution for knowledge curation and discovery.

> **📚 Quick Navigation:**
> - [Product Vision & Goals](../.kiro/steering/product.md) - What we're building and why
> - [Tech Stack & Architecture](../.kiro/steering/tech.md) - How we're building it
> - [Repository Structure](../.kiro/steering/structure.md) - Where things are located
> - [Deployment Guide](docs/guides/deployment.md) - Cloud & edge deployment
> - [API Documentation](docs/index.md) - Complete API reference
> - [Architecture Guide](docs/architecture/overview.md) - System architecture details
> - [Developer Setup](docs/guides/setup.md) - Getting started guide

## Key Features

### Authentication and Security
- **JWT Authentication**: Secure token-based authentication with access and refresh tokens
- **OAuth2 Integration**: Social login via Google and GitHub
- **Tiered Rate Limiting**: Free (100/hr), Premium (1,000/hr), and Admin (10,000/hr) tiers
- **Token Revocation**: Redis-backed token blacklist for secure logout
- **Password Security**: Bcrypt password hashing with automatic salt generation
- **User Management**: User registration, authentication, and profile management

### Content Ingestion and Processing
- **Asynchronous URL Ingestion**: Submit web content for intelligent processing
- **AI-Powered Analysis**: Automatic summarization, tagging, and classification
- **Multi-Format Support**: HTML, PDF, and plain text content extraction
- **Quality Assessment**: Comprehensive content quality scoring and evaluation

### Advanced Search and Discovery
- **Hybrid Search**: Combines keyword and semantic search with configurable weighting
- **Vector Embeddings**: Semantic similarity search using state-of-the-art embedding models
- **Advanced RAG**: Parent-child chunking, GraphRAG retrieval, and question-based search
- **Faceted Search**: Advanced filtering by classification, language, quality, and subjects
- **Full-Text Search**: SQLite FTS5 integration with graceful fallbacks

### Advanced RAG Architecture
- **Parent-Child Chunking**: Split documents into searchable chunks while maintaining parent context
- **GraphRAG Retrieval**: Entity extraction, graph traversal, and chunk retrieval
- **Synthetic Questions**: Reverse HyDE retrieval using generated questions
- **Knowledge Graph**: Semantic triple storage with provenance tracking
- **Contradiction Discovery**: Identify conflicting information across resources
- **RAG Evaluation**: RAGAS metrics for faithfulness, relevance, and precision
- **Migration Tools**: Batch migration script for existing resources

### Code Intelligence Pipeline
- **Repository Ingestion**: Scan local directories or clone Git repositories (HTTPS/SSH)
- **AST-Based Chunking**: Parse code into logical units (functions, classes, methods) using Tree-Sitter
- **Multi-Language Support**: Python, JavaScript, TypeScript, Rust, Go, and Java
- **Static Analysis**: Extract imports, definitions, and function calls without code execution
- **Code Graph**: Build dependency graphs with IMPORTS, DEFINES, and CALLS relationships
- **Gitignore Support**: Automatically respect .gitignore patterns during ingestion
- **Binary Detection**: Exclude binary files from analysis
- **File Classification**: Automatic categorization (PRACTICE, THEORY, GOVERNANCE)
- **Performance**: <2s per file for AST parsing, <1s for static analysis (P95)

### Knowledge Graph and Relationships
- **Hybrid Graph Scoring**: Multi-signal relationship detection combining vector similarity, shared subjects, and classification matches
- **Mind-Map Visualization**: Resource-centric neighbor discovery for exploration
- **Global Overview**: System-wide relationship analysis and connection mapping

### Citation Network & Link Intelligence
- **Multi-Format Citation Extraction**: Automatically extract citations from HTML, PDF, and Markdown content
- **Internal Citation Resolution**: Link citations to existing resources in your library
- **PageRank Importance Scoring**: Compute citation importance using network analysis
- **Citation Graph Visualization**: Build and explore citation networks with configurable depth
- **Smart Citation Classification**: Automatically categorize citations as datasets, code, references, or general links

### Personalized Recommendations
- **Content-Based Filtering**: Learn user preferences from existing library content
- **Fresh Content Discovery**: Source and rank new content from external providers
- **Explainable Recommendations**: Provide reasoning for recommendation decisions

### Collection Management
- **Curated Collections**: Organize resources into named, thematic collections with descriptions
- **Hierarchical Organization**: Create nested collections for complex topic structures
- **Visibility Controls**: Set collections as private, shared, or public for flexible collaboration
- **Aggregate Embeddings**: Automatic semantic representation computed from member resources
- **Collection Recommendations**: Discover similar resources and collections based on semantic similarity
- **Batch Operations**: Add or remove up to 100 resources in a single request
- **Automatic Cleanup**: Collections update automatically when resources are deleted
- **Access Control**: Owner-based permissions with visibility-based read access

### Annotation & Active Reading System
- **Precise Text Highlighting**: Character-offset-based text selection with context preservation
- **Rich Note-Taking**: Add personal notes to highlights with automatic semantic embedding
- **Tag Organization**: Categorize annotations with custom tags and color-coding
- **Full-Text Search**: Search across all annotation notes and highlighted text (<100ms for 10K annotations)
- **Semantic Search**: Find conceptually related annotations using AI-powered similarity
- **Export Capabilities**: Export annotations to Markdown or JSON for external tools
- **Collection Integration**: Associate annotations with research collections
- **Privacy Controls**: Annotations are private by default with optional sharing

### Authority Control and Classification
- **Subject Normalization**: Intelligent tag standardization and canonical forms
- **Hierarchical Classification**: UDC-inspired classification system with automatic assignment
- **Usage Tracking**: Monitor and optimize metadata usage patterns

### ML-Powered Classification & Taxonomy
- **Transformer-Based Classification**: Fine-tuned BERT/DistilBERT models for accurate resource categorization
- **Hierarchical Taxonomy Management**: Create and manage multi-level category trees with parent-child relationships
- **Multi-Label Classification**: Resources can belong to multiple categories with confidence scores
- **Semi-Supervised Learning**: Train effective models with minimal labeled data (<500 examples)
- **Active Learning**: System identifies uncertain predictions for targeted human review
- **Confidence Scoring**: Every classification includes a confidence score (0.0-1.0) for transparency
- **Model Versioning**: Track and manage multiple model versions with rollback capability
- **GPU Acceleration**: Automatic GPU utilization with graceful CPU fallback
- **Continuous Improvement**: Models improve automatically through human feedback loops

## API-First Architecture

Neo Alexandria 2.0 is built with an API-first approach, enabling seamless integration with external systems and applications. The RESTful API provides comprehensive endpoints for all system functionality, making it suitable for both internal knowledge management and external service integration.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- SQLite (default) or PostgreSQL database
- Docker Desktop (for PostgreSQL and Redis)
- 4GB RAM minimum (8GB recommended for AI features)

### Option 1: Docker Development Setup (Recommended)

Use Docker for backing services (PostgreSQL and Redis) while running the application locally:

1. **Start backing services**
```bash
cd backend/deployment
docker-compose -f docker-compose.dev.yml up -d
```

2. **Create virtual environment and install dependencies**
```bash
cd ..
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r config/requirements.txt
```

3. **Configure environment**
```bash
# Copy template and edit
cp config/.env.example .env
# Edit .env with your settings
```

4. **Run database migrations**
```bash
alembic upgrade head -c config/alembic.ini
```

5. **Start the API server**
```bash
uvicorn app.main:app --reload
```

📖 **See [docs/guides/DOCKER_SETUP_GUIDE.md](docs/guides/DOCKER_SETUP_GUIDE.md) for detailed instructions**

### Option 2: SQLite Setup (Simple)

Use SQLite for a zero-configuration setup:

1. **Create a virtual environment**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r config/requirements.txt
```

3. **Configure environment**
```bash
cp config/.env.example .env
```

4. **Run database migrations**
```bash
alembic upgrade head -c config/alembic.ini
```

5. **Start the API server**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### First API Call

Test the API by ingesting your first resource:

```bash
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

## Documentation

For comprehensive documentation, see:

- **[API Reference](docs/index.md)** - Complete API endpoint documentation
- **[Architecture Guide](docs/architecture/overview.md)** - System design and patterns
- **[Developer Setup](docs/guides/setup.md)** - Detailed setup instructions
- **[Deployment Guide](docs/guides/deployment.md)** - Production deployment
- **[Testing Guide](docs/guides/testing.md)** - Testing strategies and patterns

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=sqlite:///backend.db
TEST_DATABASE_URL=sqlite:///:memory:

# Authentication and Security
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth2 Providers (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback

# Rate Limiting
REDIS_HOST=localhost
REDIS_PORT=6379
RATE_LIMIT_FREE_TIER=100
RATE_LIMIT_PREMIUM_TIER=1000
RATE_LIMIT_ADMIN_TIER=10000

# AI Model Configuration
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
SUMMARIZER_MODEL=facebook/bart-large-cnn

# Search Configuration
DEFAULT_HYBRID_SEARCH_WEIGHT=0.5
EMBEDDING_CACHE_SIZE=1000

# Graph Configuration
GRAPH_WEIGHT_VECTOR=0.6
GRAPH_WEIGHT_TAGS=0.3
GRAPH_WEIGHT_CLASSIFICATION=0.1
```

**Generate Secure JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Development

### Running Tests

```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=app --cov-report=html

# Run specific test module
pytest backend/tests/modules/test_resources_endpoints.py -v
```

### Code Quality

```bash
# Lint and format
ruff check .
ruff format .

# Type checking
mypy backend/app
```

## Contributing

We welcome contributions! Please see our contributing guidelines for details on:

- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## License

[Add your license information here]

## Support

For questions, issues, or feature requests:

- Open an issue on GitHub
- Check the documentation
- Review existing issues and discussions
