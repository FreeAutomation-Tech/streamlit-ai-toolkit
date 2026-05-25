import streamlit as st
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    provider: str
    model: str
    temperature: float
    max_tokens: int
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None

MODEL_DEFAULTS = {
    "OpenAI": {
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o", "vision": True, "context": "128K"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "vision": True, "context": "128K"},
            {"id": "gpt-4", "name": "GPT-4", "vision": False, "context": "8K"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "vision": False, "context": "16K"},
        ],
        "default_model": "gpt-4",
        "default_temperature": 0.7,
        "default_max_tokens": 2048,
        "max_tokens_limit": 4096,
    },
    "Anthropic": {
        "models": [
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "vision": True, "context": "200K"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "vision": True, "context": "200K"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "vision": True, "context": "200K"},
        ],
        "default_model": "claude-3-sonnet-20240229",
        "default_temperature": 0.7,
        "default_max_tokens": 2048,
        "max_tokens_limit": 4096,
    },
    "Ollama": {
        "models": [
            {"id": "llama3", "name": "Llama 3", "vision": False, "context": "8K"},
            {"id": "llama3:70b", "name": "Llama 3 (70B)", "vision": False, "context": "8K"},
            {"id": "mistral", "name": "Mistral", "vision": False, "context": "8K"},
            {"id": "codellama", "name": "CodeLlama", "vision": False, "context": "100K"},
            {"id": "phi3", "name": "Phi 3", "vision": False, "context": "4K"},
            {"id": "gemma", "name": "Gemma", "vision": False, "context": "8K"},
            {"id": "llava", "name": "LLaVA (Vision)", "vision": True, "context": "4K"},
            {"id": "bakllava", "name": "BakLLaVA (Vision)", "vision": True, "context": "4K"},
        ],
        "default_model": "llama3",
        "default_temperature": 0.7,
        "default_max_tokens": 2048,
        "max_tokens_limit": 8192,
    },
}

def render_model_selector(
    default_provider: str = "OpenAI",
    show_temperature: bool = True,
    show_max_tokens: bool = True,
    show_model_info: bool = True,
    show_advanced: bool = False,
    key_prefix: str = "model_selector",
    sidebar: bool = False,
) -> Dict[str, Any]:
    container = st.sidebar if sidebar else st
    
    container.markdown("### 🤖 Model Configuration")
    
    provider_key = f"{key_prefix}_provider"
    model_key = f"{key_prefix}_model"
    temperature_key = f"{key_prefix}_temperature"
    max_tokens_key = f"{key_prefix}_max_tokens"
    top_p_key = f"{key_prefix}_top_p"
    frequency_penalty_key = f"{key_prefix}_frequency_penalty"
    presence_penalty_key = f"{key_prefix}_presence_penalty"
    
    if provider_key not in st.session_state:
        st.session_state[provider_key] = default_provider
    
    current_provider = st.session_state[provider_key]
    provider_config = MODEL_DEFAULTS.get(current_provider, MODEL_DEFAULTS["OpenAI"])
    
    provider = container.selectbox(
        "AI Provider",
        options=list(MODEL_DEFAULTS.keys()),
        key=provider_key,
        format_func=lambda x: f"🔌 {x}",
    )
    
    updated_provider_config = MODEL_DEFAULTS.get(provider, MODEL_DEFAULTS["OpenAI"])
    
    model_options = updated_provider_config["models"]
    
    model_display = {
        m["id"]: (
            f"{m['name']} "
            f"{('👁️' if m['vision'] else '')} "
            f"({m['context']})"
        )
        for m in model_options
    }
    
    default_model = updated_provider_config["default_model"]
    model_ids = [m["id"] for m in model_options]
    
    if model_key not in st.session_state or st.session_state.get(model_key) not in model_ids:
        st.session_state[model_key] = default_model
    
    model = container.selectbox(
        "Model",
        options=model_ids,
        format_func=lambda x: model_display.get(x, x),
        key=model_key,
    )
    
    if show_model_info:
        selected_model_info = next((m for m in model_options if m["id"] == model), None)
        if selected_model_info:
            info_cols = container.columns(2)
            with info_cols[0]:
                if selected_model_info["vision"]:
                    st.caption("✅ Vision-capable")
                else:
                    st.caption("❌ No vision support")
            with info_cols[1]:
                st.caption(f"📏 Context: {selected_model_info['context']}")
    
    if show_temperature:
        if temperature_key not in st.session_state:
            st.session_state[temperature_key] = updated_provider_config["default_temperature"]
        
        temperature = container.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state[temperature_key],
            step=0.1,
            key=temperature_key,
            help="Controls randomness. Lower = more deterministic, Higher = more creative.",
        )
        
        temp_help = container.container()
        with temp_help:
            col1, col2, col3 = container.columns(3)
            col1.caption("🔧 0.0-0.3: Precise")
            col2.caption("⚖️ 0.4-0.7: Balanced")
            col3.caption("🎨 0.8-2.0: Creative")
    
    if show_max_tokens:
        if max_tokens_key not in st.session_state:
            st.session_state[max_tokens_key] = updated_provider_config["default_max_tokens"]
        
        max_tokens_limit = updated_provider_config["max_tokens_limit"]
        
        max_tokens = container.slider(
            "Max Tokens",
            min_value=64,
            max_value=max_tokens_limit,
            value=min(st.session_state[max_tokens_key], max_tokens_limit),
            step=64,
            key=max_tokens_key,
            help="Maximum number of tokens in the response.",
        )
        
        container.caption(f"💡 Roughly ~{max_tokens // 4} words or ~{max_tokens // 3} sentences")
    
    top_p = None
    frequency_penalty = None
    presence_penalty = None
    
    if show_advanced:
        container.markdown("#### ⚙️ Advanced Parameters")
        
        if top_p_key not in st.session_state:
            st.session_state[top_p_key] = 1.0
        
        top_p = container.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state[top_p_key],
            step=0.05,
            key=top_p_key,
            help="Nucleus sampling probability.",
        )
        
        if frequency_penalty_key not in st.session_state:
            st.session_state[frequency_penalty_key] = 0.0
        
        frequency_penalty = container.slider(
            "Frequency Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=st.session_state[frequency_penalty_key],
            step=0.1,
            key=frequency_penalty_key,
            help="Reduces repetition by penalizing tokens based on frequency.",
        )
        
        if presence_penalty_key not in st.session_state:
            st.session_state[presence_penalty_key] = 0.0
        
        presence_penalty = container.slider(
            "Presence Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=st.session_state[presence_penalty_key],
            step=0.1,
            key=presence_penalty_key,
            help="Reduces repetition by penalizing new tokens that have appeared.",
        )
    
    return {
        "provider": provider,
        "model": model,
        "temperature": temperature if show_temperature else updated_provider_config["default_temperature"],
        "max_tokens": max_tokens if show_max_tokens else updated_provider_config["default_max_tokens"],
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
    }


def get_vision_models(provider: str) -> List[str]:
    provider_config = MODEL_DEFAULTS.get(provider)
    if not provider_config:
        return []
    
    return [m["id"] for m in provider_config["models"] if m.get("vision", False)]


def is_vision_model(provider: str, model: str) -> bool:
    provider_config = MODEL_DEFAULTS.get(provider)
    if not provider_config:
        return False
    
    model_info = next((m for m in provider_config["models"] if m["id"] == model), None)
    return model_info.get("vision", False) if model_info else False


def get_model_context_length(provider: str, model: str) -> str:
    provider_config = MODEL_DEFAULTS.get(provider)
    if not provider_config:
        return "Unknown"
    
    model_info = next((m for m in provider_config["models"] if m["id"] == model), None)
    return model_info.get("context", "Unknown") if model_info else "Unknown"
