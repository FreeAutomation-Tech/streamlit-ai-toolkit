import streamlit as st
from streamlit_ai_toolkit.components.file_upload import render_file_uploader, combine_files_content, truncate_for_context
from streamlit_ai_toolkit.components.model_selector import render_model_selector, get_vision_models
from streamlit_ai_toolkit.utils.ai import get_ai_provider, APIKeyError, APIError

st.set_page_config(
    page_title="Document Q&A - Streamlit AI Toolkit",
    page_icon="📄",
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


def init_doc_session():
    if "doc_chat_history" not in st.session_state:
        st.session_state.doc_chat_history = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "doc_system_prompt" not in st.session_state:
        st.session_state.doc_system_prompt = """You are a helpful document assistant. Answer questions based on the provided document content.

If the answer is not in the documents, say "I don't find information about that in the provided documents."

Be thorough but concise. Reference specific parts of the documents when answering."""


init_doc_session()


with st.sidebar:
    st.markdown("# 📄 Document Q&A")
    st.markdown("---")
    
    config = render_model_selector(
        default_provider=st.session_state.get("provider", "OpenAI"),
        show_temperature=True,
        show_max_tokens=True,
        show_model_info=True,
        key_prefix="docqa",
        sidebar=True,
    )
    
    st.session_state.provider = config["provider"]
    st.session_state.model = config["model"]
    st.session_state.temperature = config["temperature"]
    st.session_state.max_tokens = config["max_tokens"]
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Documents", use_container_width=True):
        st.session_state.uploaded_files = []
        st.session_state.doc_chat_history = []
        st.rerun()
    
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.doc_chat_history = []
        st.rerun()
    
    st.markdown("---")
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/1_Chat.py", label="💬 Chat", use_container_width=True)
    st.page_link("pages/3_Image_Analysis.py", label="🖼️ Image Analysis", use_container_width=True)


st.markdown("# 📄 Document Q&A")
st.markdown("Upload documents and ask questions about their content")

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
    st.stop()


upload_tab, chat_tab = st.tabs(["📁 Upload Documents", "💬 Ask Questions"])

with upload_tab:
    uploaded = render_file_uploader(
        label="Upload Documents for Q&A",
        allowed_types=["txt", "md", "csv", "json", "pdf", "py"],
        max_size_mb=50,
        multiple=True,
        show_preview=True,
        key="doc_uploader",
    )
    
    if uploaded:
        for file in uploaded:
            existing = next((f for f in st.session_state.uploaded_files if f.name == file.name), None)
            if not existing:
                st.session_state.uploaded_files.append(file)
                st.success(f"✅ Added: {file.name}")
    
    if st.session_state.uploaded_files:
        st.markdown("---")
        st.markdown("### 📚 Uploaded Documents")
        
        total_chars = 0
        for file in st.session_state.uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**📄 {file.name}**")
                st.caption(f"Type: {file.type} | Size: {file.size / 1024:.1f} KB")
            with col2:
                char_count = len(file.content)
                total_chars += char_count
                st.metric("Characters", f"{char_count:,}")
            with col3:
                if st.button("Remove", key=f"remove_{file.name}"):
                    st.session_state.uploaded_files = [
                        f for f in st.session_state.uploaded_files if f.name != file.name
                    ]
                    st.rerun()
        
        st.markdown("---")
        st.metric("Total Characters Across All Documents", f"{total_chars:,}")
        
        if total_chars > 80000:
            st.warning("⚠️ Large document context. Consider using a model with larger context window or splitting documents.")
    else:
        st.info("👆 Upload documents above to get started with Q&A.")

with chat_tab:
    if not st.session_state.uploaded_files:
        st.info("📁 Please upload documents first in the 'Upload Documents' tab.")
        st.stop()
    
    doc_count = len(st.session_state.uploaded_files)
    doc_names = ", ".join([f.name for f in st.session_state.uploaded_files])
    
    st.info(f"📚 {doc_count} document(s) loaded: {doc_names}")
    
    st.markdown("---")
    
    for message in st.session_state.doc_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask a question about your documents..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.doc_chat_history.append({"role": "user", "content": prompt})
        
        combined_content = combine_files_content(st.session_state.uploaded_files)
        truncated_content = truncate_for_context(combined_content, max_chars=80000)
        
        context_message = f"""Here are the documents to reference:

{truncated_content}

---

Please answer the following question based only on the document content above. If the answer is not in the documents, say "I don't find information about that in the provided documents."

Question: {prompt}"""
        
        messages = []
        if st.session_state.doc_system_prompt:
            messages.append({"role": "system", "content": st.session_state.doc_system_prompt})
        
        messages.append({"role": "user", "content": context_message})
        
        try:
            ai_provider = get_ai_provider(
                provider_name=st.session_state.provider,
                api_key=api_key,
                base_url=base_url,
            )
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                response_generator = ai_provider.stream_chat(
                    model=st.session_state.model,
                    messages=messages,
                    temperature=st.session_state.temperature,
                    max_tokens=st.session_state.max_tokens,
                )
                
                for chunk in response_generator:
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
            
            st.session_state.doc_chat_history.append({"role": "assistant", "content": full_response})
            
        except APIKeyError as e:
            st.error(f"🔑 API Key Error: {str(e)}")
        except APIError as e:
            st.error(f"⚠️ API Error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


st.markdown("---")

st.caption(f"""
💡 **Tips:**
- Ask specific questions about the content
- The AI only knows what's in your uploaded documents
- For best results with PDFs, install `pdfplumber`: `pip install pdfplumber`
""")
