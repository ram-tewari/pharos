# Repository Integration Plan

**Date**: 2026-04-17  
**Issue**: LangChain repository data is isolated in `repositories` table, not integrated with existing search/graph modules  
**Solution**: Convert repository data to resources/chunks format to work with existing modules

---

## Current State

### What We Have ✅
- **LangChain repository ingested**: 2,459 files, 342,280 lines, 11,027 functions, 1,766 classes
- **Embeddings generated**: 2,459 semantic embeddings
- **Data stored**: `repositories` table in NeonDB
- **Metadata**: File paths, imports, functions, classes, embeddings

### What's Missing ❌
- **No resources**: Repository files not in `resources` table (search module expects this)
- **No chunks**: File content not in `chunks` table (search module expects this)
- **No graph entities**: Functions/classes not in `graph_entities` table (graph module expects this)
- **No integration**: Existing search/graph endpoints return 0 results

---

## The Problem

Pharos has two data models that aren't connected:

### Model 1: Resources/Chunks (Existing)
```
resources (papers, docs)
  ↓
chunks (text segments)
  ↓
embeddings (semantic vectors)
  ↓
search module finds chunks
```

### Model 2: Repositories (New)
```
repositories (code repos)
  ↓
metadata (files, functions, classes)
  ↓
embeddings (semantic vectors)
  ↓
??? (no search integration)
```

---

## The Solution: Bridge the Models

Convert repository data to resources/chunks format so existing modules work:

### Step 1: Create Resources from Repository Files

For each file in the repository:
```python
# From repositories.metadata.files
file = {
    "path": "libs/langchain/auth.py",
    "size": 15602,
    "lines": 458,
    "imports": ["jwt", "hashlib"],
    "functions": ["authenticate", "verify_token"],
    "classes": ["AuthManager"]
}

# Create resource
resource = Resource(
    title=file["path"],
    url=f"{repo_url}/blob/main/{file['path']}",
    content_type="code/python",
    metadata={
        "repo_id": repo_id,
        "file_path": file["path"],
        "imports": file["imports"],
        "functions": file["functions"],
        "classes": file["classes"]
    }
)
```

### Step 2: Create Chunks from File Content

Fetch code from GitHub and create chunks:
```python
# Fetch code from GitHub
github_client = GitHubClient()
code = github_client.fetch_file_content(repo_url, file["path"])

# Create chunk (one per file for now)
chunk = Chunk(
    resource_id=resource.id,
    content=code,
    chunk_index=0,
    start_char=0,
    end_char=len(code),
    metadata={
        "file_path": file["path"],
        "lines": file["lines"],
        "language": "python"
    }
)
```

### Step 3: Link Embeddings

Use existing embeddings from repository ingestion:
```python
# Repository already has embeddings
embedding_vector = repo_metadata["embeddings"][file["path"]]

# Create embedding record
embedding = Embedding(
    chunk_id=chunk.id,
    vector=embedding_vector,
    model="nomic-embed-text-v1"
)
```

### Step 4: Create Graph Entities

Extract functions/classes to graph:
```python
# For each function
for func in file["functions"]:
    entity = GraphEntity(
        name=func,
        type="function",
        metadata={
            "file": file["path"],
            "repo_id": repo_id
        }
    )

# For each class
for cls in file["classes"]:
    entity = GraphEntity(
        name=cls,
        type="class",
        metadata={
            "file": file["path"],
            "repo_id": repo_id
        }
    )
```

---

## Implementation Plan

### Phase 1: Create Conversion Service

**File**: `backend/app/modules/resources/repository_converter.py`

```python
class RepositoryConverter:
    """Convert repository data to resources/chunks format"""
    
    async def convert_repository(self, repo_id: str):
        # 1. Get repository metadata
        repo = await get_repository(repo_id)
        
        # 2. For each file, create resource + chunk
        for file in repo.metadata["files"]:
            # Create resource
            resource = await self.create_resource_from_file(repo, file)
            
            # Fetch code from GitHub
            code = await github_client.fetch_file_content(
                repo.url, file["path"]
            )
            
            # Create chunk
            chunk = await self.create_chunk_from_code(resource, code, file)
            
            # Link embedding
            await self.link_embedding(chunk, repo, file)
            
            # Create graph entities
            await self.create_graph_entities(file, resource)
```

### Phase 2: Add GitHub Module

**File**: `backend/app/modules/github/service.py`

```python
class GitHubService:
    """Fetch code from GitHub with caching"""
    
    async def fetch_file_content(self, repo_url: str, file_path: str):
        # Check Redis cache
        cached = await redis.get(f"github:code:{repo_url}:{file_path}")
        if cached:
            return cached
        
        # Fetch from GitHub API
        code = await self._fetch_from_github(repo_url, file_path)
        
        # Cache for 1 hour
        await redis.setex(f"github:code:{repo_url}:{file_path}", 3600, code)
        
        return code
```

### Phase 3: Update Search Module

**No changes needed!** Once data is in resources/chunks, existing search works:

```python
# This will now work automatically
POST /api/search/search
{
  "query": "authentication",
  "limit": 10
}

# Returns LangChain files because they're now resources
```

### Phase 4: Update Graph Module

**No changes needed!** Once entities are created, existing graph works:

```python
# This will now work automatically
GET /api/graph/entities

# Returns LangChain functions/classes
```

---

## Event-Driven Flow

```
1. Repository ingested
   ↓
2. Emit: repository.ingested
   ↓
3. Converter subscribes → converts to resources/chunks
   ↓
4. Emit: resources.created (for each file)
   ↓
5. Search module subscribes → indexes for search
   ↓
6. Graph module subscribes → creates entities
   ↓
7. Everything works with existing endpoints!
```

---

## Benefits

✅ **No duplicate endpoints** - Use existing search/graph APIs  
✅ **No duplicate code** - Reuse existing modules  
✅ **Event-driven** - Follows Pharos architecture  
✅ **Backward compatible** - Existing resources still work  
✅ **Unified search** - Search papers AND code together  
✅ **Unified graph** - Graph connects papers AND code  

---

## API Usage After Integration

### Search for code
```python
POST /api/search/search
{
  "query": "authentication",
  "filters": {
    "content_type": "code/python"  # Filter to code only
  }
}

# Returns LangChain auth files
```

### Search everything
```python
POST /api/search/search
{
  "query": "authentication"
}

# Returns BOTH papers and code about authentication
```

### Graph entities
```python
GET /api/graph/entities?type=function

# Returns functions from LangChain
```

### Graph relationships
```python
GET /api/graph/entities/{entity_id}/relationships

# Shows which files import this function
```

---

## Implementation Steps

1. **Create GitHub module** - Fetch code from GitHub with caching
2. **Create converter service** - Convert repositories → resources/chunks
3. **Run conversion** - Convert LangChain repository
4. **Test search** - Verify search finds LangChain files
5. **Test graph** - Verify graph shows LangChain entities
6. **Update docs** - Document the integration

---

## Files to Create

1. `backend/app/modules/github/` - GitHub fetching module
   - `service.py` - GitHub API client + caching
   - `router.py` - Manual fetch endpoints
   - `handlers.py` - Event handlers

2. `backend/app/modules/resources/repository_converter.py` - Conversion service

3. `backend/convert_langchain.py` - Script to convert LangChain repository

4. `backend/test_integrated_search.py` - Test search after conversion

---

## Success Criteria

✅ LangChain files appear in search results  
✅ LangChain functions appear in graph entities  
✅ Can search code and papers together  
✅ Graph shows relationships between code files  
✅ No duplicate endpoints or modules  
✅ Event-driven architecture maintained  

---

**Status**: Ready to implement  
**Next**: Create GitHub module + converter service  
**ETA**: 2-3 hours of work
