# Pharos - Product Overview

## Purpose

Pharos is your second brain for code - an AI-powered knowledge management system designed specifically for developers, researchers, and technical teams. It combines intelligent code analysis with research paper management to help you understand, organize, and discover connections across your technical knowledge base.

## Target Users

1. **Software Developers** - Engineers managing codebases, libraries, and technical documentation
2. **Researchers** - Academic and industry researchers working with code and papers
3. **Technical Writers** - Documentation specialists organizing API docs and guides
4. **Engineering Teams** - Collaborative knowledge management for development organizations
5. **Students** - Computer science students learning from code and research papers

## Core Value Propositions

### Code Intelligence
- AST-based code analysis that understands structure, not just text
- Multi-language support (Python, JavaScript, TypeScript, Rust, Go, Java)
- Dependency graph extraction (imports, definitions, calls)
- Semantic code search - find by concept, not just keywords
- Repository-wide understanding with sub-2s per file parsing

### Research Integration
- Manage research papers alongside code
- Automatic citation extraction and resolution
- Scholarly metadata parsing (equations, tables, references)
- Quality assessment for papers and documentation
- Link papers to relevant code implementations

### Knowledge Graph
- Connect code, papers, and concepts through relationships
- Citation networks showing influence and dependencies
- Code dependency graphs visualizing architecture
- Contradiction detection across documentation
- PageRank scoring for importance

### Semantic Search and Discovery
- Hybrid search combining keyword and semantic approaches
- Advanced RAG with parent-child chunking
- GraphRAG retrieval using entity relationships
- Sub-500ms search latency
- Faceted filtering by language, quality, classification

### Active Reading and Annotation
- Precise text highlighting in code and papers
- Rich notes with semantic embeddings
- Tag organization with color-coding
- Semantic search across all annotations
- Export to Markdown and JSON

### Organization and Curation
- Flexible collection management
- Hierarchical taxonomy
- Quality-based filtering
- Batch operations
- Private, shared, or public visibility

## Non-Goals

### What We Are NOT Building

❌ **General-Purpose Note-Taking** - Focused on code and technical content, not general notes
❌ **Social Network** - No user profiles, followers, or social features
❌ **Content Creation Platform** - No authoring tools or publishing workflows (use your IDE/editor)
❌ **File Storage Service** - No general-purpose file hosting
❌ **Real-time Collaboration** - No simultaneous editing or live cursors
❌ **Mobile Apps** - Web-first, responsive design only (API-first for IDE integration)
❌ **Enterprise SSO** - Simple authentication only
❌ **Multi-tenancy** - Single-user or small team focus
❌ **Blockchain/Web3** - Traditional database architecture
❌ **Video/Audio Processing** - Code and text focus only
❌ **Code Execution** - Static analysis only, no code running or sandboxing

## Product Principles

1. **Code-First** - Optimized for understanding and navigating code repositories
2. **API-First** - All features accessible via RESTful API for IDE/editor integration
3. **Privacy-Focused** - Your code and knowledge stays local or self-hosted
4. **Open Source** - Transparent, extensible, community-driven
5. **Performance** - Fast response times (<200ms for most operations, <2s for code parsing)
6. **Simplicity** - Clean interfaces, minimal configuration
7. **Extensibility** - Plugin architecture for custom features and language support

## Success Metrics

- **Code Analysis Speed**: <2s per file for AST parsing (P95)
- **Search Quality**: nDCG > 0.7 for hybrid search
- **Response Time**: P95 < 200ms for API endpoints
- **Classification Accuracy**: >85% for ML taxonomy
- **Repository Scale**: Handle 10K+ files per repository
- **User Satisfaction**: Qualitative feedback from developers
- **System Reliability**: 99.9% uptime for self-hosted deployments

## Roadmap Themes

### Current Status (Phase 19 - COMPLETE ✅)
- **Hybrid Edge-Cloud Architecture**: Deployed production system with cloud API and edge worker
- **Cloud API**: Lightweight control plane on Render (512MB RAM, 0.1 CPU)
- **Edge Worker**: GPU-accelerated compute for ML-intensive tasks
- **Production Deployment**: Live at https://pharos.onrender.com with 88.9% endpoint coverage
- **Repository Cleanup**: Consolidated documentation, removed 110+ temporary files
- **Frontend Integration**: Phase 2 Discovery & Search feature complete

### Completed Phases
- ✅ Phase 17: Production hardening with authentication and rate limiting
- ✅ Phase 17.5: Advanced RAG architecture with parent-child chunking
- ✅ Phase 18: Code repository analysis and AST-based chunking
- ✅ Phase 19: Hybrid edge-cloud orchestration and deployment

### Near-term (Phase 20+)
- IDE/Editor plugins (VS Code, JetBrains, Vim)
- Enhanced code navigation and "jump to definition" across repos
- Advanced graph intelligence features
- Improved recommendation algorithms for related code
- Performance optimization for large monorepos
- Frontend-backend integration completion

### Long-term Vision
- Multi-language support expansion (C++, C#, Ruby, PHP)
- Advanced code visualization tools (call graphs, dependency maps)
- Plugin ecosystem for custom analyzers
- Community-contributed language parsers
- Distributed knowledge graph federation
- AI-powered code explanation and documentation generation
