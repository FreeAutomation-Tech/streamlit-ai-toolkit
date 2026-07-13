<div align="center">

# 🎨 Streamlit AI Toolkit

**Ready-to-run AI apps with Streamlit — chat, document Q&A, image analysis, and more**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/FreeAutomation-Tech/streamlit-ai-toolkit?style=social)](https://github.com/FreeAutomation-Tech/streamlit-ai-toolkit/stargazers)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![CI](https://github.com/FreeAutomation-Tech/streamlit-ai-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/FreeAutomation-Tech/streamlit-ai-toolkit/actions)

[Features](#features) • [Quick Start](#quick-start) • [Apps](#apps-showcase) • [Components](#components) • [Deployment](#deployment)

</div>

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/FreeAutomation-Tech/streamlit-ai-toolkit.git
cd streamlit-ai-toolkit

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Then open your browser to `http://localhost:8501` and start exploring!

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Model Chat** | Chat with OpenAI, Anthropic, or Ollama models in a beautiful interface |
| 📄 **Document Q&A** | Upload PDFs, text files, and ask questions about their content (RAG-like) |
| 🖼️ **Image Analysis** | Analyze images using vision-capable models like GPT-4o and Claude-3 |
| 🧩 **Reusable Components** | Beautiful, configurable UI components you can use in your own apps |
| 🎨 **Beautiful UI** | Custom CSS styling with modern design principles |
| 🔌 **Multi-Provider** | Works with OpenAI, Anthropic Claude, and local Ollama models |
| 💾 **Session Persistence** | Chat history and settings persist across sessions |
| 📤 **Export Options** | Download chat history, extracted documents, and analysis results |

---

## 📺 Demo

![Streamlit AI Toolkit Demo](https://raw.githubusercontent.com/FreeAutomation-Tech/streamlit-ai-toolkit/main/assets/demo.gif)

*Terminal running `streamlit run app.py` + browser showing the toolkit in action*

---

## 📱 Apps Showcase

### 1. 💬 Chat Interface

A full-featured chat interface with:

- **Multiple AI providers** — Switch between OpenAI, Anthropic, and Ollama
- **Model selection** — Choose from GPT-4, Claude-3, Llama 3, Mistral, and more
- **System prompts** — Customize AI behavior with system prompts
- **Parameter tuning** — Adjust temperature and max tokens
- **Streaming output** — Watch responses appear in real-time
- **Chat management** — Clear, export, and track message counts

![Chat Interface](https://raw.githubusercontent.com/FreeAutomation-Tech/streamlit-ai-toolkit/main/assets/chat-screenshot.png)

---

### 2. 📄 Document Q&A

Upload documents and get answers based on their content:

- **Supported formats** — PDF, TXT, MD, CSV, JSON, and more
- **Drag & drop** — Easy file upload with preview
- **Text extraction** — Automatic text extraction from documents
- **Context-aware Q&A** — Ask questions about uploaded content
- **Multiple files** — Upload and reference multiple documents
- **Text preview** — View extracted text before asking questions

![Document Q&A](https://raw.githubusercontent.com/FreeAutomation-Tech/streamlit-ai-toolkit/main/assets/docqa-screenshot.png)

---

### 3. 🖼️ Image Analysis

Analyze images using state-of-the-art vision models:

- **Supported formats** — PNG, JPG, JPEG, GIF, WebP
- **Image preview** — View images with original dimensions
- **Custom prompts** — Ask anything about your images
- **Vision models** — Powered by GPT-4o, Claude-3 Opus/Sonnet
- **Batch analysis** — Analyze multiple images at once
- **Results export** — Download analysis results

![Image Analysis](https://raw.githubusercontent.com/FreeAutomation-Tech/streamlit-ai-toolkit/main/assets/image-screenshot.png)

---

## 🧩 Reusable Components

The toolkit includes beautiful, reusable components you can use in your own Streamlit apps:

### Chat UI Component

```python
from streamlit_ai_toolkit.components.chat_ui import render_chat_interface

# Render a complete chat interface
render_chat_interface(
    provider=st.session_state.provider,
    model=st.session_state.model,
    temperature=st.session_state.temperature,
    max_tokens=st.session_state.max_tokens,
    system_prompt="You are a helpful assistant."
)
```

**Features:**
- User/assistant message bubbles with styling
- Streaming text output
- Chat history in `st.session_state`
- Clear and export chat buttons
- Message counter display

---

### File Upload Component

```python
from streamlit_ai_toolkit.components.file_upload import render_file_uploader

# Render file upload with preview and extraction
uploaded_files = render_file_uploader(
    allowed_types=["pdf", "txt", "md", "csv"],
    max_size_mb=50,
    multiple=True,
    show_preview=True
)

# Access extracted content
for file in uploaded_files:
    st.write(f"Filename: {file['name']}")
    st.write(f"Content: {file['content'][:500]}...")
```

**Returns:** `List[Dict]` with `name`, `type`, `size`, `content`, and `raw_data` keys.

---

### Model Selector Component

```python
from streamlit_ai_toolkit.components.model_selector import render_model_selector

# Render model selector with parameters
config = render_model_selector(
    default_provider="OpenAI",
    show_temperature=True,
    show_max_tokens=True
)

# Access selected values
st.write(f"Provider: {config['provider']}")
st.write(f"Model: {config['model']}")
st.write(f"Temperature: {config['temperature']}")
st.write(f"Max Tokens: {config['max_tokens']}")
```

**Available Models by Provider:**

| Provider | Models |
|----------|--------|
| **OpenAI** | gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo |
| **Anthropic** | claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307 |
| **Ollama** | llama3, mistral, codellama, phi3, gemma |

---

## 🔧 AI Utilities

### Provider Architecture

```
AIProvider (base class)
├── OpenAIProvider      # OpenAI API compatible
├── AnthropicProvider   # Claude API
└── OllamaProvider      # Local models
```

### Usage Example

```python
from streamlit_ai_toolkit.utils.ai import get_ai_provider

# Get provider instance
provider = get_ai_provider(
    provider_name="OpenAI",
    api_key="sk-..."
)

# Chat completion (non-streaming)
response = provider.chat_completion(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=1000
)
print(response.content)

# Streaming response
for chunk in provider.stream_chat(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell me a story"}],
    temperature=0.8
):
    print(chunk, end="")
```

### Error Handling

All providers include user-friendly error handling for:

- `APIKeyError` — Missing or invalid API key
- `RateLimitError` — API rate limits exceeded
- `TimeoutError` — Request timeout
- `APIError` — General API errors with helpful messages

---

## 🎨 Customization Guide

### Environment Variables

Create a `.env` file to pre-configure API keys:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
```

### Custom CSS

The app uses a custom CSS theme. Modify `app.py` to customize colors:

```python
CUSTOM_CSS = """
<style>
:root {
    --primary-color: #FF4B4B;
    --background-color: #0E1117;
    --secondary-background-color: #262730;
    --text-color: #FAFAFA;
}
/* Your custom styles */
</style>
"""
```

### Adding New Providers

Extend the `AIProvider` base class:

```python
from streamlit_ai_toolkit.utils.ai import AIProvider

class MyProvider(AIProvider):
    def chat_completion(self, model, messages, **kwargs):
        # Implement your provider logic
        pass
    
    def stream_chat(self, model, messages, **kwargs):
        # Implement streaming
        yield "..."
```

---

## 🚢 Deployment Guide

### Streamlit Cloud (Recommended)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and select your fork
4. Set the main file path to `app.py`
5. Click "Advanced settings" to add environment variables:
   ```
   OPENAI_API_KEY=sk-...
   ```
6. Click "Deploy"

### Hugging Face Spaces

1. Create a new Space on [huggingface.co](https://huggingface.co)
2. Select "Streamlit" as the SDK
3. Push your code or use git to sync
4. Add secrets in the Space settings

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t streamlit-ai-toolkit .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... streamlit-ai-toolkit
```

---

## 🏗️ Architecture Overview

```
streamlit-ai-toolkit/
├── app.py                              # Main entry, page config, sidebar nav
├── pages/
│   ├── 1_Chat.py                       # Chat interface page
│   ├── 2_Document_Q&A.py               # Document Q&A page
│   └── 3_Image_Analysis.py             # Image analysis page
├── streamlit_ai_toolkit/
│   ├── components/
│   │   ├── chat_ui.py                  # Chat bubble, streaming, history
│   │   ├── file_upload.py              # Drag-drop, preview, extraction
│   │   └── model_selector.py           # Provider/model selection, params
│   └── utils/
│       └── ai.py                       # AI providers (OpenAI, Anthropic, Ollama)
├── requirements.txt
└── pyproject.toml
```

**Data Flow:**
1. User interacts with Streamlit UI components
2. Session state manages conversation history and settings
3. AI Provider classes handle API communication
4. Responses stream back to the chat interface

---

## 🛠️ Development Setup

```bash
# Clone the repo
git clone https://github.com/FreeAutomation-Tech/streamlit-ai-toolkit.git
cd streamlit-ai-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in dev mode
pip install -e .

# Run the app
streamlit run app.py
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-feature`
3. Make your changes and test them
4. Run any existing tests: `python -c "import streamlit_ai_toolkit"`
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature/my-new-feature`
7. Submit a Pull Request

### Ideas for Contributions:

- Add new AI providers (Google Gemini, Cohere, etc.)
- Add more document format support (DOCX, EPUB)
- Implement proper RAG with vector databases
- Add speech-to-text and text-to-speech
- Create more reusable components
- Write tests
- Improve documentation

---

## 📊 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=FreeAutomation-Tech/streamlit-ai-toolkit&type=Date)](https://star-history.com/#FreeAutomation-Tech/streamlit-ai-toolkit&Date)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io) 🎈
- Inspired by the amazing AI/ML community
- Thanks to all contributors!

---

<div align="center">

**If you find this project useful, please consider giving it a ⭐ star on GitHub!**

[![Follow on GitHub](https://img.shields.io/github/followers/FreeAutomation-Tech?style=social)](https://github.com/FreeAutomation-Tech)

</div>
---
*If you find this useful, please consider giving it a star ⭐ — it helps others discover it too!*

*Thank you for your support! 🙏*
