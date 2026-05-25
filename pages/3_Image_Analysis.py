import base64
import io
import streamlit as st
from streamlit_ai_toolkit.components.model_selector import render_model_selector, get_vision_models, is_vision_model
from streamlit_ai_toolkit.utils.ai import get_ai_provider, APIKeyError, APIError

st.set_page_config(
    page_title="Image Analysis - Streamlit AI Toolkit",
    page_icon="🖼️",
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


def init_image_session():
    if "image_analysis_history" not in st.session_state:
        st.session_state.image_analysis_history = []
    if "uploaded_images" not in st.session_state:
        st.session_state.uploaded_images = []


init_image_session()


IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "webp"]

ANALYSIS_PRESETS = {
    "Describe": "Describe this image in detail.",
    "Identify Objects": "List and describe all objects you see in this image.",
    "Extract Text": "Extract any text visible in this image. Format it clearly.",
    "Analyze Colors": "Analyze the color palette and mood of this image.",
    "Technical Review": "Analyze this image technically - lighting, composition, focus quality.",
    "Creative Ideas": "Suggest creative ways this image could be used or edited.",
}

with st.sidebar:
    st.markdown("# 🖼️ Image Analysis")
    st.markdown("---")
    
    st.markdown("### 👁️ Vision Model Selection")
    
    config = render_model_selector(
        default_provider=st.session_state.get("provider", "OpenAI"),
        show_temperature=True,
        show_max_tokens=True,
        show_model_info=True,
        key_prefix="image",
        sidebar=True,
    )
    
    st.session_state.provider = config["provider"]
    st.session_state.model = config["model"]
    st.session_state.temperature = config["temperature"]
    st.session_state.max_tokens = config["max_tokens"]
    
    model_has_vision = is_vision_model(st.session_state.provider, st.session_state.model)
    
    if not model_has_vision:
        st.error(f"⛔ {st.session_state.model} does not support image input.")
        st.info(f"💡 Switch to a vision model: GPT-4o, Claude-3 Opus/Sonnet, or LLaVA")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.uploaded_images = []
        st.session_state.image_analysis_history = []
        st.rerun()
    
    st.markdown("---")
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/1_Chat.py", label="💬 Chat", use_container_width=True)
    st.page_link("pages/2_Document_Q&A.py", label="📄 Doc Q&A", use_container_width=True)


st.markdown("# 🖼️ Image Analysis")
st.markdown(f"Analyze images using **{st.session_state.model}** ({st.session_state.provider})")

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


upload_col, config_col = st.columns([3, 2])

with upload_col:
    st.markdown("### 📷 Upload Images")
    
    uploaded_files = st.file_uploader(
        "Drag and drop images here",
        type=IMAGE_EXTENSIONS,
        accept_multiple_files=True,
        key="image_uploader",
    )
    
    if uploaded_files:
        for file in uploaded_files:
            existing = next((img for img in st.session_state.uploaded_images if img["name"] == file.name), None)
            if not existing:
                try:
                    from PIL import Image
                    image = Image.open(file)
                    
                    st.session_state.uploaded_images.append({
                        "name": file.name,
                        "type": file.type,
                        "size": file.size,
                        "width": image.width,
                        "height": image.height,
                        "mode": image.mode,
                        "raw_data": file.getvalue(),
                        "pil_image": image,
                    })
                except ImportError:
                    st.session_state.uploaded_images.append({
                        "name": file.name,
                        "type": file.type,
                        "size": file.size,
                        "width": "Unknown",
                        "height": "Unknown",
                        "mode": "Unknown",
                        "raw_data": file.getvalue(),
                        "pil_image": None,
                    })
                except Exception as e:
                    st.error(f"Error loading {file.name}: {str(e)}")
    
    if st.session_state.uploaded_images:
        st.markdown(f"### 🖼️ Loaded Images ({len(st.session_state.uploaded_images)})")
        
        cols_per_row = 3
        for i in range(0, len(st.session_state.uploaded_images), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(st.session_state.uploaded_images):
                    img = st.session_state.uploaded_images[i + j]
                    with cols[j]:
                        if img.get("pil_image"):
                            st.image(img["pil_image"], caption=img["name"], use_container_width=True)
                        else:
                            st.caption(f"📷 {img['name']}")
                        
                        st.caption(f"📏 {img['width']} x {img['height']} | 💾 {img['size'] / 1024:.1f} KB")
                        
                        if st.button("Remove", key=f"remove_img_{i}_{j}"):
                            st.session_state.uploaded_images.pop(i + j)
                            st.rerun()

with config_col:
    st.markdown("### ⚙️ Analysis Configuration")
    
    analysis_mode = st.radio(
        "Analysis Mode",
        ["Single Image", "Batch Analysis"],
        index=0,
        horizontal=True,
    )
    
    if analysis_mode == "Single Image":
        if st.session_state.uploaded_images:
            image_names = [img["name"] for img in st.session_state.uploaded_images]
            selected_image_name = st.selectbox(
                "Select Image to Analyze",
                options=image_names,
                index=0,
            )
            selected_image = next(
                (img for img in st.session_state.uploaded_images if img["name"] == selected_image_name),
                None
            )
        else:
            selected_image = None
            st.info("👈 Upload an image first")
    else:
        selected_image = None
    
    st.markdown("#### 📝 Analysis Prompt")
    
    preset = st.selectbox(
        "Quick Preset",
        options=["Custom"] + list(ANALYSIS_PRESETS.keys()),
        index=0,
    )
    
    if preset != "Custom":
        default_prompt = ANALYSIS_PRESETS[preset]
    else:
        default_prompt = "Describe this image in detail."
    
    prompt = st.text_area(
        "Custom Prompt",
        value=default_prompt,
        height=100,
        help="Tell the AI what you want it to do with the image.",
    )
    
    detail_level = st.radio(
        "Detail Level",
        ["Low", "Medium", "High"],
        index=1,
        horizontal=True,
        help="Controls the 'detail' parameter for vision API (OpenAI only).",
    )
    
    detail_map = {"Low": "low", "Medium": "auto", "High": "high"}
    
    analyze_button = st.button(
        "🔍 Analyze Image" if analysis_mode == "Single Image" else "🔍 Analyze All Images",
        type="primary",
        use_container_width=True,
        disabled=not model_has_vision,
    )


st.markdown("---")
st.markdown("### 📊 Analysis Results")

if analyze_button:
    if analysis_mode == "Single Image":
        if not selected_image:
            st.warning("⚠️ Please upload and select an image first.")
        else:
            try:
                ai_provider = get_ai_provider(
                    provider_name=st.session_state.provider,
                    api_key=api_key,
                    base_url=base_url,
                )
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if selected_image.get("pil_image"):
                        st.image(selected_image["pil_image"], caption=selected_image["name"], use_container_width=True)
                    st.caption(f"📏 {selected_image['width']} x {selected_image['height']} | Prompt: {prompt}")
                
                with col2:
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        if st.session_state.provider == "OpenAI":
                            base64_image = base64.b64encode(selected_image["raw_data"]).decode("utf-8")
                            
                            messages = [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}",
                                                "detail": detail_map[detail_level],
                                            },
                                        },
                                    ],
                                }
                            ]
                        elif st.session_state.provider == "Anthropic":
                            base64_image = base64.b64encode(selected_image["raw_data"]).decode("utf-8")
                            media_type = selected_image.get("type", "image/jpeg")
                            
                            messages = [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "image",
                                            "source": {
                                                "type": "base64",
                                                "media_type": media_type,
                                                "data": base64_image,
                                            },
                                        },
                                        {"type": "text", "text": prompt},
                                    ],
                                }
                            ]
                        else:
                            base64_image = base64.b64encode(selected_image["raw_data"]).decode("utf-8")
                            
                            messages = [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                                        },
                                    ],
                                }
                            ]
                        
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
                        
                        st.session_state.image_analysis_history.append({
                            "image_name": selected_image["name"],
                            "prompt": prompt,
                            "result": full_response,
                            "model": st.session_state.model,
                        })
                        
                        st.download_button(
                            "📥 Download Result",
                            data=f"# Image Analysis: {selected_image['name']}\n\n## Prompt:\n{prompt}\n\n## Result:\n{full_response}",
                            file_name=f"analysis_{selected_image['name']}.md",
                            mime="text/markdown",
                        )
                        
            except APIKeyError as e:
                st.error(f"🔑 API Key Error: {str(e)}")
            except APIError as e:
                st.error(f"⚠️ API Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    else:
        if not st.session_state.uploaded_images:
            st.warning("⚠️ Please upload images first.")
        else:
            for idx, img in enumerate(st.session_state.uploaded_images):
                try:
                    st.markdown(f"#### {idx + 1}. {img['name']}")
                    
                    ai_provider = get_ai_provider(
                        provider_name=st.session_state.provider,
                        api_key=api_key,
                        base_url=base_url,
                    )
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if img.get("pil_image"):
                            st.image(img["pil_image"], caption=img["name"], width=200)
                    
                    with col2:
                        with st.chat_message("assistant"):
                            message_placeholder = st.empty()
                            full_response = ""
                            
                            base64_image = base64.b64encode(img["raw_data"]).decode("utf-8")
                            
                            if st.session_state.provider == "OpenAI":
                                messages = [
                                    {
                                        "role": "user",
                                        "content": [
                                            {"type": "text", "text": prompt},
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                                    "detail": detail_map[detail_level],
                                                },
                                            },
                                        ],
                                    }
                                ]
                            elif st.session_state.provider == "Anthropic":
                                media_type = img.get("type", "image/jpeg")
                                messages = [
                                    {
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "image",
                                                "source": {
                                                    "type": "base64",
                                                    "media_type": media_type,
                                                    "data": base64_image,
                                                },
                                            },
                                            {"type": "text", "text": prompt},
                                        ],
                                    }
                                ]
                            else:
                                messages = [
                                    {
                                        "role": "user",
                                        "content": [
                                            {"type": "text", "text": prompt},
                                            {
                                                "type": "image_url",
                                                "image_url": f"data:image/jpeg;base64,{base64_image}",
                                            },
                                        ],
                                    }
                                ]
                            
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
                            
                            st.session_state.image_analysis_history.append({
                                "image_name": img["name"],
                                "prompt": prompt,
                                "result": full_response,
                                "model": st.session_state.model,
                            })
                    
                    st.markdown("---")
                    
                except Exception as e:
                    st.error(f"❌ Error analyzing {img['name']}: {str(e)}")


if st.session_state.image_analysis_history:
    with st.expander(f"📋 View History ({len(st.session_state.image_analysis_history)} analyses)", expanded=False):
        for idx, item in enumerate(reversed(st.session_state.image_analysis_history)):
            st.markdown(f"#### {idx + 1}. {item['image_name']}")
            st.caption(f"Model: {item['model']} | Prompt: {item['prompt'][:50]}...")
            st.markdown(item["result"])
            st.markdown("---")


st.markdown("---")

st.caption(f"""
💡 **Tips:**
- Use 'Describe' for general image understanding
- Use 'Extract Text' for OCR-like capabilities
- Use 'Technical Review' for photography feedback
- For best results, use vision-capable models like GPT-4o or Claude-3
""")
