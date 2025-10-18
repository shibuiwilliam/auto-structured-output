"""Streamlit UI for Auto Structured Output Library."""

import json
import os
from datetime import date, datetime, time
from enum import Enum
from typing import Any

import streamlit as st
from openai import OpenAI

from auto_structured_output.extractor import StructureExtractor


class GPTModel(Enum):
    """Available GPT models for the UI."""

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"

    @staticmethod
    def list_str() -> list[str]:
        """Return list of model values as strings."""
        return [model.value for model in GPTModel]


def json_serial(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json code.

    Handles datetime, date, and time objects by converting them to ISO format strings.

    Args:
        obj: Object to serialize

    Returns:
        String representation of the object

    Raises:
        TypeError: If object type is not supported
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def setup_page_config() -> None:
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Auto Structured Output",
        page_icon="🤖",
        layout="wide",
    )


def render_header() -> None:
    """Render the main header and description."""
    st.title("🤖 Auto Structured Output")
    st.markdown("Automatically extract structured outputs from natural language prompts using OpenAI")


def render_sidebar() -> tuple[str, str, str, str, int, bool]:
    """Render the sidebar configuration panel.

    Returns:
        Tuple containing: api_key, basic_model, high_reasoning_model,
        llm_model, max_retries, use_high_reasoning
    """
    st.sidebar.header("⚙️ Model Configuration")

    # API Key input
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key",
    )

    # Model selection
    basic_model = st.sidebar.selectbox(
        "Basic Prediction Model",
        options=GPTModel.list_str(),
        index=0,
        help="Model used for standard mode (clear prompts)",
    )

    high_reasoning_model = st.sidebar.selectbox(
        "High Reasoning Model",
        options=GPTModel.list_str(),
        index=0,
        help="Model used for high reasoning mode (vague prompts)",
    )

    llm_model = st.sidebar.selectbox(
        "LLM Request Model",
        options=GPTModel.list_str(),
        index=0,
        help="Model used for final LLM requests with extracted structure",
    )

    # Max retries configuration
    max_retries = st.sidebar.slider(
        "Max Retries",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of retry attempts for schema extraction",
    )

    # High reasoning mode toggle
    use_high_reasoning = st.sidebar.checkbox(
        "Use High Reasoning Mode",
        value=False,
        help="Enable for vague prompts that need structure inference",
    )

    # About section
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
### About
This tool helps you:
1. Extract structure from natural language prompts
2. Generate Pydantic models automatically
3. Use them with OpenAI API for structured outputs
"""
    )

    return api_key, basic_model, high_reasoning_model, llm_model, max_retries, use_high_reasoning


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "extracted_model" not in st.session_state:
        st.session_state.extracted_model = None
    if "extracted_schema" not in st.session_state:
        st.session_state.extracted_schema = None
    if "llm_response" not in st.session_state:
        st.session_state.llm_response = None
    if "num_prompts" not in st.session_state:
        st.session_state.num_prompts = 1


def render_structure_extraction_section(api_key: str, max_retries: int, use_high_reasoning: bool) -> None:
    """Render the structure extraction section.

    Args:
        api_key: OpenAI API key
        max_retries: Number of retry attempts
        use_high_reasoning: Whether to use high reasoning mode
    """
    st.header("1️⃣ Extract Structure from Prompt(s)")

    # Info message about multi-prompt feature
    if st.session_state.num_prompts > 1:
        st.info(
            f"📝 Multi-prompt mode: {st.session_state.num_prompts} prompts. "
            "The system will generate a unified schema that accommodates all prompts."
        )

    # Collect prompts
    prompts = []
    for i in range(st.session_state.num_prompts):
        if i == 0:
            label = "Enter your prompt"
            placeholder = "Example: Extract user information with name (string), age (integer), and email (string with email format)"
        else:
            label = f"Prompt {i + 1}"
            placeholder = f"Enter additional prompt {i + 1} for unified schema generation"

        prompt = st.text_area(
            label,
            height=120,
            placeholder=placeholder,
            help="Describe the structure you want to extract",
            key=f"prompt_{i}",
        )
        prompts.append(prompt)

    # Add/Remove prompt buttons
    col_add, col_remove = st.columns(2)
    with col_add:
        if st.button("➕ Add Prompt", use_container_width=True):
            st.session_state.num_prompts += 1
            st.rerun()
    with col_remove:
        if st.session_state.num_prompts > 1:
            if st.button("➖ Remove Last Prompt", use_container_width=True):
                st.session_state.num_prompts -= 1
                st.rerun()

    st.markdown("---")

    # Extract structure button
    col1, col2 = st.columns([1, 4])
    with col1:
        extract_button = st.button("🔍 Extract Structure", type="primary", use_container_width=True)
    with col2:
        if st.session_state.extracted_model:
            st.success("✅ Structure extracted successfully!")

    if extract_button:
        handle_structure_extraction(prompts, api_key, max_retries, use_high_reasoning)


def handle_structure_extraction(prompts: list[str], api_key: str, max_retries: int, use_high_reasoning: bool) -> None:
    """Handle the structure extraction process.

    Args:
        prompts: List of user's structure definition prompts
        api_key: OpenAI API key
        max_retries: Number of retry attempts
        use_high_reasoning: Whether to use high reasoning mode
    """
    # Filter out empty prompts
    non_empty_prompts = [p.strip() for p in prompts if p.strip()]

    if not non_empty_prompts:
        st.error("❌ Please enter at least one prompt.")
        return

    try:
        with st.spinner(f"Extracting structure from {len(non_empty_prompts)} prompt(s)..."):
            # Initialize OpenAI client and extractor
            client = OpenAI(api_key=api_key)
            extractor = StructureExtractor(client, max_retries=max_retries)

            # Extract structure with list of prompts
            model = extractor.extract_structure(non_empty_prompts, use_high_reasoning=use_high_reasoning)

            # Store in session state
            st.session_state.extracted_model = model
            st.session_state.extracted_schema = model.model_json_schema()
            st.session_state.llm_response = None  # Reset LLM response

            if len(non_empty_prompts) > 1:
                st.success(
                    f"✅ Structure extracted successfully from {len(non_empty_prompts)} prompts! "
                    "The schema accommodates all provided use cases."
                )
            else:
                st.success("✅ Structure extracted successfully!")
            st.rerun()

    except Exception as e:
        st.error(f"❌ Error extracting structure: {str(e)}")
        st.session_state.extracted_model = None
        st.session_state.extracted_schema = None


def render_schema_display_section() -> None:
    """Render the extracted schema display section."""
    if not st.session_state.extracted_schema:
        return

    st.header("2️⃣ Extracted Schema (JSON)")

    # Display schema in JSON format
    st.json(st.session_state.extracted_schema)

    # Download button for schema
    schema_json = json.dumps(st.session_state.extracted_schema, indent=2)
    st.download_button(
        label="⬇️ Download Schema JSON",
        data=schema_json,
        file_name="extracted_schema.json",
        mime="application/json",
    )

    st.markdown("---")


def render_llm_request_section(api_key: str, llm_model: str) -> None:
    """Render the LLM request section.

    Args:
        api_key: OpenAI API key
        llm_model: Model to use for LLM requests
    """
    if not st.session_state.extracted_schema:
        return

    st.header("3️⃣ Request LLM with Extracted Structure")

    llm_prompt = st.text_area(
        "Enter your request prompt",
        height=100,
        placeholder="Example: Generate a sample user",
        help="This prompt will be sent to the LLM with the extracted structure",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        llm_button = st.button("🚀 Request LLM", type="primary", use_container_width=True)
    with col2:
        if st.session_state.llm_response:
            st.success("✅ LLM response received!")

    if llm_button:
        handle_llm_request(llm_prompt, api_key, llm_model)


def handle_llm_request(llm_prompt: str, api_key: str, llm_model: str) -> None:
    """Handle the LLM request process.

    Args:
        llm_prompt: User's request prompt for the LLM
        api_key: OpenAI API key
        llm_model: Model to use for LLM requests
    """
    if not llm_prompt.strip():
        st.error("❌ Please enter a request prompt first.")
        return

    try:
        with st.spinner("Requesting LLM..."):
            # Initialize OpenAI client
            client = OpenAI(api_key=api_key)

            # Make API request with extracted structure
            response = client.chat.completions.parse(
                model=llm_model,
                messages=[{"role": "user", "content": llm_prompt}],
                response_format=st.session_state.extracted_model,
            )

            # Parse response
            parsed_response = response.choices[0].message.parsed

            # Convert to dict for display
            if parsed_response is None:
                raise ValueError("LLM response could not be parsed into the expected structure.")
            if hasattr(parsed_response, "model_dump"):
                response_dict = parsed_response.model_dump()
            else:
                response_dict = dict(parsed_response)

            st.session_state.llm_response = response_dict
            st.success("✅ LLM response received!")
            st.rerun()

    except Exception as e:
        st.error(f"❌ Error requesting LLM: {str(e)}")
        st.session_state.llm_response = None


def render_llm_response_section() -> None:
    """Render the LLM response display section."""
    if not st.session_state.llm_response:
        return

    st.header("4️⃣ LLM Response (JSON)")

    # Display response in JSON format
    st.json(st.session_state.llm_response)

    # Download button for response with datetime serialization support
    response_json = json.dumps(st.session_state.llm_response, indent=2, default=json_serial)
    st.download_button(
        label="⬇️ Download Response JSON",
        data=response_json,
        file_name="llm_response.json",
        mime="application/json",
    )


def render_footer() -> None:
    """Render the footer section."""
    st.markdown("---")
    st.markdown(
        """
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ using Auto Structured Output Library |
    <a href='https://github.com/shibuiwilliam/auto-structured-output' target='_blank'>GitHub</a>
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


def main() -> None:
    """Main application entry point."""
    # Setup page configuration
    setup_page_config()

    # Render header
    render_header()

    # Render sidebar and get configuration
    (
        api_key,
        basic_model,
        high_reasoning_model,
        llm_model,
        max_retries,
        use_high_reasoning,
    ) = render_sidebar()

    # Check API key
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to continue.")
        st.stop()

    # Set environment variables for model configuration
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["BASIC_PREDICTION_MODEL"] = basic_model
    os.environ["HIGH_PREDICTION_MODEL"] = high_reasoning_model

    # Initialize session state
    initialize_session_state()

    # Render main sections
    render_structure_extraction_section(api_key, max_retries, use_high_reasoning)
    render_schema_display_section()
    render_llm_request_section(api_key, llm_model)
    render_llm_response_section()

    # Render footer
    render_footer()


if __name__ == "__main__":
    main()
