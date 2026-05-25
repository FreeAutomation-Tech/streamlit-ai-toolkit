import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

CUSTOM_CSS = """
<style>
:root {
    --primary-color: #FF4B4B;
    --secondary-color: #FF6B6B;
    --background-color: #0E1117;
    --secondary-background: #1A1C23;
    --text-color: #FAFAFA;
    --text-secondary: #B0B0B0;
    --border-color: #3A3C4E;
    --user-bubble: #FF4B4B;
    --assistant-bubble: #2D303E;
    --success-color: #00C853;
    --warning-color: #FFAB00;
    --error-color: #FF5252;
}

.stApp {
    background: linear-gradient(135deg, var(--background-color) 0%, #161823 100%);
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--secondary-background) 0%, #15171E 100%);
    border-right: 1px solid var(--border-color);
}

section[data-testid="stSidebar"] .stRadio label {
    padding: 0.5rem 0.75rem;
    border-radius: 0.5rem;
    margin-bottom: 0.25rem;
    transition: all 0.2s ease;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background-color: rgba(255, 75, 75, 0.1);
}

div[data-testid="stTextInput"] input,
div[data-testid="stPasswordInput"] input {
    background-color: var(--secondary-background);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    color: var(--text-color);
    padding: 0.75rem 1rem;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stPasswordInput"] input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.2);
}

div[data-testid="stSelectbox"] > div > div {
    background-color: var(--secondary-background);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    color: var(--text-color);
}

div[data-testid="stSlider"] > div > div > div {
    background-color: var(--primary-color);
}

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    border: none;
    border-radius: 0.5rem;
    color: white;
    font-weight: 500;
    padding: 0.5rem 1rem;
    transition: all 0.2s ease;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
}

div[data-testid="stFileUploader"] {
    background-color: var(--secondary-background);
    border: 2px dashed var(--border-color);
    border-radius: 0.75rem;
    padding: 1.5rem;
    transition: all 0.2s ease;
}

div[data-testid="stFileUploader"]:hover {
    border-color: var(--primary-color);
    background-color: rgba(255, 75, 75, 0.05);
}

.stChatMessage {
    border-radius: 1rem;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
}

.stChatMessage[data-testid="stChatMessage-user"] {
    background: linear-gradient(135deg, var(--user-bubble) 0%, #FF6B6B 100%);
    margin-left: 2rem;
}

.stChatMessage[data-testid="stChatMessage-assistant"] {
    background-color: var(--assistant-bubble);
    margin-right: 2rem;
    border: 1px solid var(--border-color);
}

div[data-testid="stExpander"] > div {
    background-color: var(--secondary-background);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
}

div[data-testid="stHeader"] {
    background: transparent;
}

footer {
    visibility: hidden;
}

.footer-custom {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--secondary-background);
    border-top: 1px solid var(--border-color);
    padding: 0.75rem;
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-secondary);
    z-index: 1000;
}

.footer-custom a {
    color: var(--primary-color);
    text-decoration: none;
}

h1, h2, h3, h4, h5, h6 {
    background: linear-gradient(90deg, #FFFFFF 0%, #B0B0B0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

div[data-testid="stTabs"] button[role="tab"] {
    background-color: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 0.75rem 1.5rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--primary-color);
    border-bottom: 2px solid var(--primary-color);
}

div[data-testid="stTabs"] button[role="tab"]:hover {
    color: var(--primary-color);
    background-color: rgba(255, 75, 75, 0.05);
}

div[data-testid="stMetric"] {
    background-color: var(--secondary-background);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    padding: 1rem;
}

div[data-testid="stMetric"] label {
    color: var(--text-secondary) !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--text-color) !important;
    font-size: 1.75rem !important;
}
</style>
"""

st.set_page_config(
    page_title="Streamlit AI Toolkit",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/anomalyco/streamlit-ai-toolkit/issues",
        "Report a bug": "https://github.com/anomalyco/streamlit-ai-toolkit/issues/new",
        "About": """
        ## Streamlit AI Toolkit
        
        Ready-to-run AI apps with Streamlit — chat, document Q&A, image analysis, and more.
        
        GitHub: https://github.com/anomalyco/streamlit-ai-toolkit
        """,
    },
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def init_session_state():
    if "provider" not in st.session_state:
        st.session_state.provider = "OpenAI"
    if "model" not in st.session_state:
        st.session_state.model = "gpt-4"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 2048
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if "anthropic_api_key" not in st.session_state:
        st.session_state.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if "ollama_base_url" not in st.session_state:
        st.session_state.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a helpful assistant. Be clear, concise, and friendly."
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "doc_chat_history" not in st.session_state:
        st.session_state.doc_chat_history = []
    if "images" not in st.session_state:
        st.session_state.images = []
    if "image_analysis_history" not in st.session_state:
        st.session_state.image_analysis_history = []

init_session_state()

with st.sidebar:
    st.markdown("# 🎨 AI Toolkit")
    st.markdown("---")
    
    st.markdown("### 🔌 AI Provider")
    
    provider = st.selectbox(
        "Select Provider",
        ["OpenAI", "Anthropic", "Ollama"],
        key="provider_selector",
        index=["OpenAI", "Anthropic", "Ollama"].index(st.session_state.provider),
    )
    st.session_state.provider = provider
    
    if provider == "OpenAI":
        st.text_input(
            "OpenAI API Key",
            type="password",
            key="openai_key_input",
            value=st.session_state.openai_api_key,
            on_change=lambda: setattr(st.session_state, "openai_api_key", st.session_state.openai_key_input),
            placeholder="sk-...",
        )
        if not st.session_state.openai_api_key:
            st.info("💡 Get your API key at [platform.openai.com](https://platform.openai.com)")
    
    elif provider == "Anthropic":
        st.text_input(
            "Anthropic API Key",
            type="password",
            key="anthropic_key_input",
            value=st.session_state.anthropic_api_key,
            on_change=lambda: setattr(st.session_state, "anthropic_api_key", st.session_state.anthropic_key_input),
            placeholder="sk-ant-...",
        )
        if not st.session_state.anthropic_api_key:
            st.info("💡 Get your API key at [console.anthropic.com](https://console.anthropic.com)")
    
    elif provider == "Ollama":
        st.text_input(
            "Ollama Base URL",
            key="ollama_url_input",
            value=st.session_state.ollama_base_url,
            on_change=lambda: setattr(st.session_state, "ollama_base_url", st.session_state.ollama_url_input),
            placeholder="http://localhost:11434",
        )
        st.info("💡 Ollama runs locally. Download at [ollama.com](https://ollama.com)")
    
    st.markdown("---")
    st.markdown("### 🚀 Quick Links")
    
    st.page_link("pages/1_Chat.py", label="💬 Chat", use_container_width=True)
    st.page_link("pages/2_Document_Q&A.py", label="📄 Document Q&A", use_container_width=True)
    st.page_link("pages/3_Image_Analysis.py", label="🖼️ Image Analysis", use_container_width=True)
    
    st.markdown("---")
    st.caption(f"Streamlit AI Toolkit v0.1.0 • 🐍 Python 3.9+")

st.markdown("# 🎨 Welcome to Streamlit AI Toolkit")
st.markdown("#### Ready-to-run AI apps with reusable components")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="💬 Chat Apps", value="1", delta="Interactive", delta_color="off")

with col2:
    st.metric(label="📄 Document Q&A", value="1", delta="RAG-like", delta_color="off")

with col3:
    st.metric(label="🖼️ Image Analysis", value="1", delta="Vision API", delta_color="off")

with col4:
    st.metric(label="🧩 Components", value="3+", delta="Reusable", delta_color="off")

st.markdown("---")

st.markdown("## ✨ Featured Apps")

app_col1, app_col2, app_col3 = st.columns(3)

with app_col1:
    st.markdown("### 💬 Chat")
    st.markdown("""
    **Multi-model chat interface**
    
    - OpenAI, Anthropic, Ollama support
    - Streaming responses
    - Custom system prompts
    - Export chat history
    """)
    if st.button("🚀 Open Chat", use_container_width=True, key="open_chat"):
        st.switch_page("pages/1_Chat.py")

with app_col2:
    st.markdown("### 📄 Document Q&A")
    st.markdown("""
    **Ask questions about your documents**
    
    - PDF, TXT, MD, CSV support
    - Drag & drop upload
    - Text extraction & preview
    - Context-aware responses
    """)
    if st.button("🚀 Open Doc Q&A", use_container_width=True, key="open_doc"):
        st.switch_page("pages/2_Document_Q&A.py")

with app_col3:
    st.markdown("### 🖼️ Image Analysis")
    st.markdown("""
    **Analyze images with AI**
    
    - PNG, JPG, GIF, WebP support
    - Vision models (GPT-4o, Claude-3)
    - Custom analysis prompts
    - Batch processing
    """)
    if st.button("🚀 Open Image Analysis", use_container_width=True, key="open_image"):
        st.switch_page("pages/3_Image_Analysis.py")

st.markdown("---")

st.markdown("## 🧩 Reusable Components")

st.markdown("""
The toolkit includes beautiful, reusable components you can use in your own Streamlit apps:

| Component | Description |
|-----------|-------------|
| `chat_ui.py` | Complete chat interface with message bubbles, streaming, and history management |
| `file_upload.py` | Drag-and-drop file upload with preview, extraction, and validation |
| `model_selector.py` | Provider-aware model selection with temperature and token sliders |
""")

st.code("""
# Example: Using components in your app
from streamlit_ai_toolkit.components.chat_ui import render_chat_interface
from streamlit_ai_toolkit.components.model_selector import render_model_selector

# Get model configuration
config = render_model_selector()

# Render chat interface
render_chat_interface(
    provider=config["provider"],
    model=config["model"],
    temperature=config["temperature"],
    max_tokens=config["max_tokens"]
)
""", language="python")

st.markdown("---")

st.markdown("## 🚀 Quick Start")

st.code("""
# Clone the repository
git clone https://github.com/anomalyco/streamlit-ai-toolkit.git
cd streamlit-ai-toolkit

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
""", language="bash")

st.markdown("---")

st.markdown("## 🎯 Why Streamlit AI Toolkit?")

feature_col1, feature_col2 = st.columns(2)

with feature_col1:
    st.markdown("""
    ### 🔌 Multi-Provider Support
    - **OpenAI** — GPT-4, GPT-4o, GPT-3.5-turbo
    - **Anthropic** — Claude-3 Opus, Sonnet, Haiku
    - **Ollama** — Llama 3, Mistral, CodeLlama, and more
    
    ### 🎨 Beautiful UI
    - Custom CSS styling
    - Dark theme by default
    - Responsive design
    - Smooth animations
    """)

with feature_col2:
    st.markdown("""
    ### 🧩 Reusable Components
    - Import components into your own apps
    - Well-documented API
    - Consistent styling
    - Session state management
    
    ### 💻 Developer Friendly
    - No heavy AI SDK dependencies
    - Uses urllib for API calls
    - Proper error handling
    - Extensible architecture
    """)

st.markdown("---")

st.markdown("""
<div class="footer-custom">
    Built with ❤️ using <a href="https://streamlit.io" target="_blank">Streamlit</a> | 
    <a href="https://github.com/anomalyco/streamlit-ai-toolkit" target="_blank">GitHub</a> | 
    Licensed under MIT
</div>
""", unsafe_allow_html=True)
