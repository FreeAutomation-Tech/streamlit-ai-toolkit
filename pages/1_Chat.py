import streamlit as st
from streamlit_ai_toolkit.components.chat_ui import render_chat_interface
from streamlit_ai_toolkit.components.model_selector import render_model_selector

st.set_page_config(
    page_title="Chat - Streamlit AI Toolkit",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
.stApp {
    background: linear-gradient(135deg, #0E1117 0%, #161823 100%);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A1C23 0%, #15171E 100%);
    border-right: 1px solid #3A3C4E;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_chat_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_system_prompt" not in st.session_state:
        st.session_state.chat_system_prompt = "You are a helpful assistant. Be clear, concise, and friendly."


init_chat_session()


with st.sidebar:
    st.markdown("# 💬 Chat")
    st.markdown("---")
    
    config = render_model_selector(
        default_provider=st.session_state.get("provider", "OpenAI"),
        show_temperature=True,
        show_max_tokens=True,
        show_model_info=True,
        key_prefix="chat",
        sidebar=True,
    )
    
    st.session_state.provider = config["provider"]
    st.session_state.model = config["model"]
    st.session_state.temperature = config["temperature"]
    st.session_state.max_tokens = config["max_tokens"]
    
    st.markdown("---")
    st.markdown("### ⚙️ System Prompt")
    
    system_prompt = st.text_area(
        "Customize AI behavior",
        value=st.session_state.chat_system_prompt,
        height=150,
        key="chat_system_prompt_input",
        help="This prompt sets the behavior and personality of the AI assistant.",
    )
    
    st.session_state.chat_system_prompt = system_prompt
    
    st.markdown("---")
    
    preset_prompts = [
        "You are a helpful assistant.",
        "You are an expert programmer who writes clean, efficient code.",
        "You are a creative writing assistant.",
        "You are a technical writer who explains complex topics simply.",
        "You are a friendly and encouraging tutor.",
    ]
    
    st.markdown("#### 💡 Quick Presets")
    preset_cols = st.columns(1)
    for i, preset in enumerate(preset_prompts[:3]):
        if st.button(f"Preset {i+1}", key=f"preset_{i}", use_container_width=True):
            st.session_state.chat_system_prompt = preset
            st.rerun()
        st.caption(preset[:50] + "...")
    
    st.markdown("---")
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/2_Document_Q&A.py", label="📄 Doc Q&A", use_container_width=True)
    st.page_link("pages/3_Image_Analysis.py", label="🖼️ Image Analysis", use_container_width=True)


st.markdown("# 💬 AI Chat")
st.markdown(f"Chat with **{st.session_state.model}** ({st.session_state.provider})")

st.markdown("---")


def get_api_key_for_provider(provider: str) -> str:
    if provider == "OpenAI":
        return st.session_state.get("openai_api_key", "")
    elif provider == "Anthropic":
        return st.session_state.get("anthropic_api_key", "")
    elif provider == "Ollama":
        return "ollama-local"
    return ""


def get_base_url_for_provider(provider: str) -> str:
    if provider == "Ollama":
        return st.session_state.get("ollama_base_url", "http://localhost:11434")
    return None


api_key = get_api_key_for_provider(st.session_state.provider)
base_url = get_base_url_for_provider(st.session_state.provider)

needs_key = st.session_state.provider != "Ollama" and not api_key

if needs_key:
    st.warning(f"⚠️ Please configure your {st.session_state.provider} API key in the sidebar or home page.")
    st.info("💡 Click the home button and enter your API key in the sidebar.")
    st.stop()

if st.session_state.provider == "Ollama":
    try:
        import urllib.request
        req = urllib.request.Request(f"{base_url}/api/tags")
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Ollama at {base_url}")
        st.info(f"""
        💡 Make sure Ollama is running:
        1. Download Ollama from ollama.com
        2. Run `ollama serve` or start the Ollama app
        3. Pull a model: `ollama pull {st.session_state.model}`
        """)
        if st.button("Continue Anyway"):
            pass
        else:
            st.stop()


render_chat_interface(
    provider=st.session_state.provider,
    model=st.session_state.model,
    temperature=st.session_state.temperature,
    max_tokens=st.session_state.max_tokens,
    system_prompt=st.session_state.chat_system_prompt,
    chat_history_key="chat_history",
    api_key=api_key,
    base_url=base_url,
)


st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    message_count = len(st.session_state.chat_history)
    st.metric("Total Messages", message_count)

with col2:
    user_messages = sum(1 for msg in st.session_state.chat_history if msg["role"] == "user")
    st.metric("Your Messages", user_messages)

with col3:
    st.caption(f"""
    **Configuration:**
    - Provider: {st.session_state.provider}
    - Model: {st.session_state.model}
    - Temperature: {st.session_state.temperature}
    - Max Tokens: {st.session_state.max_tokens}
    """)
