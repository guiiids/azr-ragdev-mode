# Technical Context: Azure Search RAG Assistant

## Technologies Used

### Backend
- **Python 3.x**: Core programming language
- **Flask**: Web framework for serving the application
- **Azure OpenAI**: For generating contextually relevant responses
- **Azure Search**: For vector search and document retrieval
- **Azure Identity**: For authentication with Azure services
- **Gunicorn**: WSGI HTTP Server for production deployment

### Frontend
- **HTML/CSS**: Structure and styling
- **JavaScript**: Client-side interactivity
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Fetch API**: For making API requests to the backend

### Data Processing
- **OpenAI Embeddings**: For vector representation of text
- **Vector Search**: For semantic similarity matching
- **JSON**: For data interchange between components
- **Streaming Responses**: For incremental response delivery

## Development Setup

### Environment Variables
The application requires the following environment variables:
- `OPENAI_ENDPOINT`: Azure OpenAI service endpoint
- `OPENAI_KEY`: API key for Azure OpenAI
- `OPENAI_API_VERSION`: API version for Azure OpenAI
- `EMBEDDING_DEPLOYMENT`: Deployment name for embeddings model
- `CHAT_DEPLOYMENT`: Deployment name for chat completion model
- `SEARCH_ENDPOINT`: Azure Search service endpoint
- `SEARCH_INDEX`: Name of the search index
- `SEARCH_KEY`: API key for Azure Search
- `VECTOR_FIELD`: Field name for vector embeddings

### Local Development
1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/macOS: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables (via .env file or directly)
6. Run the application: `python main.py`

### Production Deployment
- Deploy as a Flask application with Gunicorn
- Ensure environment variables are properly set
- Configure logging for production use
- Set up monitoring and alerting

## Technical Constraints

### Azure OpenAI Limitations
- Token limits for context and response
- Rate limits for API calls
- Deployment availability by region
- Model version constraints

### Azure Search Limitations
- Index size limits
- Query complexity constraints
- Vector dimension requirements
- Rate limits for search operations

### Performance Considerations
- Response time affected by:
  - Search latency
  - OpenAI API latency
  - Document size and complexity
  - Number of documents retrieved
- Memory usage affected by:
  - Concurrent users
  - Size of retrieved documents
  - Streaming buffer size

## Dependencies
Key Python packages and their purposes:

| Package | Purpose |
|---------|---------|
| Flask | Web framework |
| openai | Azure OpenAI API client |
| azure-search-documents | Azure Search client |
| azure-identity | Azure authentication |
| gunicorn | WSGI HTTP Server |
| python-dotenv | Environment variable management |
| logging | Application logging |
| json | JSON parsing and generation |
| re | Regular expression operations |
| traceback | Error tracking |

## Tool Usage Patterns

### Configuration Management
- Environment variables for sensitive information
- Config module for application settings
- Settings object for runtime configuration

### Error Handling
- Try-except blocks for API calls
- Logging for error tracking
- User-friendly error messages
- Fallback responses when services fail

### Logging
- Structured logging with timestamps
- Log levels for different severity
- File and console logging
- Debug logging for development

### API Design
- RESTful endpoints
- JSON request/response format
- Streaming responses for long-running operations
- Error codes and messages
