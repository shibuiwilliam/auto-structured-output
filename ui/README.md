# Auto Structured Output - Streamlit UI

A user-friendly web interface for the Auto Structured Output library that allows you to extract structured outputs from natural language prompts using OpenAI.

## Features

- **Interactive Prompt Input**: Enter natural language prompts to define output structures
- **Two-Mode Operation**:
  - Standard Mode (clear prompts)
  - High Reasoning Mode (vague prompts)
- **Schema Extraction**: Automatically extract and visualize JSON schemas
- **LLM Integration**: Test extracted structures with real OpenAI API calls
- **Model Configuration**: Choose different models for schema extraction and LLM requests
- **JSON Export**: Download extracted schemas and LLM responses

## Installation

1. Make sure you have the parent project installed:
```bash
cd ..
pip install -e .
```

2. Install UI dependencies:
```bash
cd ui
pip install -e .
```

Or using uv:
```bash
cd ui
uv pip install -e .
```

## Usage

1. Set your OpenAI API key (optional, can be entered in UI):
```bash
export OPENAI_API_KEY="your-api-key"
```

2. Run the Streamlit app:
```bash
streamlit run ui/main.py
```

Or from the ui directory:
```bash
cd ui
streamlit run ui/main.py
```

3. Open your browser to `http://localhost:8501`

## UI Components

### Sidebar Configuration
- **OpenAI API Key**: Enter your API key (or set via environment variable)
- **Basic Prediction Model**: Model for standard mode schema extraction
- **High Reasoning Model**: Model for high reasoning mode schema extraction
- **LLM Request Model**: Model for making structured output requests
- **Max Retries**: Number of retry attempts for schema extraction (1-10)
- **High Reasoning Mode**: Toggle for vague/implicit prompts

### Main Workflow

#### 1. Extract Structure from Prompt
- Enter a natural language prompt describing your desired output structure
- Click "Extract Structure" to generate the schema
- Example: "Extract user information with name (string), age (integer), and email (string with email format)"

#### 2. View Extracted Schema
- See the generated JSON schema
- Download the schema for reuse

#### 3. Request LLM with Structure
- Enter a prompt for the LLM to generate actual data
- Click "Request LLM" to get structured output
- Example: "Generate a sample user"

#### 4. View LLM Response
- See the structured JSON response
- Download the response

## Example Prompts

### Standard Mode (Clear Structure)
```
Extract user information with:
- name (string)
- age (integer, minimum 0)
- email (string with email format)
- status (enum: active, inactive, suspended)
```

### High Reasoning Mode (Vague Requirements)
```
Analyze customer feedback and extract actionable insights
```

### Complex Nested Structure
```
Extract course information with:
- course_id (string)
- title (string)
- instructor object containing:
  - name (string)
  - email (string with email format)
- students (list of student objects with name and grade)
```

## Model Options

Available models for selection:
- **gpt-4o** (default, recommended)
- **gpt-4o-mini**
- **gpt-4-turbo**
- **gpt-3.5-turbo**

## Tips

1. **Use Standard Mode** when your prompt clearly specifies field names and types
2. **Use High Reasoning Mode** when you need the LLM to infer structure from business requirements
3. **Adjust Max Retries** higher for complex schemas that may need correction
4. **Download Schemas** to reuse them across sessions
5. **Test Different Models** to find the best balance of cost and quality

## Troubleshooting

### Import Errors
If you get import errors, make sure:
1. The parent project is installed: `pip install -e ..` from the ui directory
2. You're in the correct directory when running the app

### API Errors
- Verify your OpenAI API key is correct
- Check you have sufficient API credits
- Ensure the selected models are available to your account

### Schema Extraction Failures
- Try increasing Max Retries
- Be more specific in your prompt description
- Try a different model

## Code Structure

The UI is organized into well-structured functions for maintainability:

### Main Functions (377 lines)
- `setup_page_config()` - Page configuration
- `render_header()` - Title and description
- `render_sidebar()` - Configuration panel (returns all settings)
- `initialize_session_state()` - Session state management
- `render_structure_extraction_section()` - Section 1: Prompt input and extraction
- `handle_structure_extraction()` - Business logic for extraction
- `render_schema_display_section()` - Section 2: Schema display
- `render_llm_request_section()` - Section 3: LLM request input
- `handle_llm_request()` - Business logic for LLM requests
- `render_llm_response_section()` - Section 4: Response display
- `render_footer()` - Footer
- `main()` - Main entry point orchestrating all functions

### Benefits
- ✅ Clean separation of UI rendering and business logic
- ✅ Easy to test individual functions
- ✅ Well-documented with type hints and docstrings
- ✅ Follows Python best practices

See `REFACTORING.md` for detailed documentation of the code structure.

## Development

To modify the UI:
1. Edit `ui/main.py`
2. Each section is in its own function for easy modification
3. Streamlit will auto-reload on save
4. Refresh your browser to see changes

### Key Files
- `ui/main.py` - Main Streamlit application (refactored, function-based)
- `README.md` - This file
- `USAGE_GUIDE.md` - Detailed usage instructions with examples
- `REFACTORING.md` - Code structure documentation
- `run.sh` - Quick launch script
- `pyproject.toml` - Dependencies

## License

Same as the parent Auto Structured Output library.
