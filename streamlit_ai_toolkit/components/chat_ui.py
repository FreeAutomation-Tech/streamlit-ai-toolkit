import json
import streamlit as st
from datetime import datetime
from typing import Optional, List, Dict, Any, Generator

def render_chat_interface(
    provider: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    system_prompt: Optional[str] = None,
    chat_history_key: str = "chat_history",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> List[Dict[str, Any]]:
    from streamlit_ai_toolkit.utils.ai import get_ai_provider, APIKeyError, APIError
    
    if chat_history_key not in st.session_state:
        st.session_state[chat_history_key] = []
    
    chat_history = st.session_state[chat_history_key]
    
    st.markdown(f"### 💬 Chat with {model}")
    
    if len(chat_history) == 0:
        st.info("👋 Start a conversation by typing a message below!")
    
    user_count = sum(1 for msg in chat_history if msg["role"] == "user")
    assistant_count = sum(1 for msg in chat_history if msg["role"] == "assistant")
    
    col1, col2, col3 = st.columns([2, 2, 4])
    with col1:
        st.metric("Your Messages", user_count)
    with col2:
        st.metric("AI Responses", assistant_count)
    with col3:
        clear_col, export_col = st.columns(2)
        with clear_col:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state[chat_history_key] = []
                st.rerun()
        with export_col:
            if st.button("📤 Export Chat", use_container_width=True) and chat_history:
                export_chat(chat_history, model)
    
    st.markdown("---")
    
    chat_container = st.container()
    
    with chat_container:
        for message in chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    if prompt := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        chat_history.append({"role": "user", "content": prompt})
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend([
            {"role": msg["role"], "content": msg["content"]}
            for msg in chat_history
        ])
        
        try:
            ai_provider = get_ai_provider(
                provider_name=provider,
                api_key=api_key or get_api_key_for_provider(provider),
                base_url=base_url or get_base_url_for_provider(provider),
            )
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                response_generator = ai_provider.stream_chat(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                
                for chunk in response_generator:
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
            
            chat_history.append({"role": "assistant", "content": full_response})
            
        except APIKeyError as e:
            st.error(f"🔑 API Key Error: {str(e)}")
            chat_history.pop()
        except APIError as e:
            st.error(f"⚠️ API Error: {str(e)}")
            chat_history.pop()
        except Exception as e:
            st.error(f"❌ Unexpected Error: {str(e)}")
            chat_history.pop()
    
    return chat_history


def export_chat(chat_history: List[Dict[str, Any]], model: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    chat_text = f"# Chat Export - {model}\n"
    chat_text += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    chat_text += f"# Total Messages: {len(chat_history)}\n\n"
    chat_text += "=" * 80 + "\n\n"
    
    for msg in chat_history:
        role = msg["role"].upper()
        chat_text += f"## [{role}]\n\n{msg['content']}\n\n"
        chat_text += "-" * 80 + "\n\n"
    
    chat_json = {
        "metadata": {
            "model": model,
            "exported_at": timestamp,
            "message_count": len(chat_history),
        },
        "messages": chat_history,
    }
    
    st.download_button(
        label="📄 Download as Markdown",
        data=chat_text,
        file_name=f"chat_export_{timestamp}.md",
        mime="text/markdown",
    )
    
    st.download_button(
        label="📋 Download as JSON",
        data=json.dumps(chat_json, indent=2),
        file_name=f"chat_export_{timestamp}.json",
        mime="application/json",
    )


def get_api_key_for_provider(provider: str) -> str:
    if provider == "OpenAI":
        return st.session_state.get("openai_api_key", "")
    elif provider == "Anthropic":
        return st.session_state.get("anthropic_api_key", "")
    elif provider == "Ollama":
        return "ollama-local"
    return ""


def get_base_url_for_provider(provider: str) -> Optional[str]:
    if provider == "Ollama":
        return st.session_state.get("ollama_base_url", "http://localhost:11434")
    return None


def render_message_bubble(role: str, content: str, timestamp: Optional[datetime] = None) -> None:
    bubble_style = {
        "user": {
            "bg": "linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 100%)",
            "margin": "0 0 0.75rem 2rem",
        },
        "assistant": {
            "bg": "#2D303E",
            "margin": "0 2rem 0.75rem 0",
            "border": "1px solid #3A3C4E",
        },
    }
    
    style = bubble_style.get(role, bubble_style["assistant"])
    
    css = f"""
    <div style="
        background: {style['bg']};
        border-radius: 1rem;
        padding: 0.75rem 1rem;
        margin: {style['margin']};
        color: #FAFAFA;
        {f'border: {style["border"]};' if 'border' in style else ''}
    ">
        <div style="font-size: 0.75rem; opacity: 0.7; margin-bottom: 0.25rem;">
            {role.upper()} {timestamp.strftime('%H:%M') if timestamp else ''}
        </div>
        <div style="white-space: pre-wrap; word-wrap: break-word;">
            {content}
        </div>
    </div>
    """
    
    st.markdown(css, unsafe_allow_html=True)
