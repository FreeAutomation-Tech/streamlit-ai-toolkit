import io
import re
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class UploadedFileData:
    name: str
    type: str
    size: int
    content: str
    raw_data: bytes
    num_pages: int = 1
    encoding: str = "utf-8"

TEXT_EXTENSIONS = [".txt", ".md", ".markdown", ".rst", ".log", ".csv", ".json", ".xml", ".html", ".htm", ".css", ".js", ".py", ".sh", ".bat", ".ps1", ".sql", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"]
PDF_EXTENSION = ".pdf"
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"]

def render_file_uploader(
    label: str = "📁 Upload Documents",
    allowed_types: Optional[List[str]] = None,
    max_size_mb: int = 50,
    multiple: bool = True,
    show_preview: bool = True,
    key: str = "file_uploader",
) -> List[UploadedFileData]:
    if allowed_types is None:
        allowed_types = ["txt", "md", "csv", "json", "pdf"]
    
    type_mapping = {
        "txt": ["txt"],
        "md": ["md", "markdown"],
        "csv": ["csv"],
        "json": ["json"],
        "pdf": ["pdf"],
        "xml": ["xml"],
        "html": ["html", "htm"],
        "py": ["py"],
        "yaml": ["yaml", "yml"],
        "toml": ["toml"],
    }
    
    extensions = []
    for t in allowed_types:
        extensions.extend(type_mapping.get(t, [t]))
    
    file_extensions = [f".{ext}" for ext in extensions]
    
    st.markdown(f"### {label}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Allowed: {', '.join([f'.{e}' for e in extensions])} | Max: {max_size_mb}MB per file")
    with col2:
        st.caption(f"Multiple: {'Yes' if multiple else 'No'}")
    
    uploaded_files = st.file_uploader(
        "Drag and drop files here, or click to browse",
        type=extensions,
        accept_multiple_files=multiple,
        key=key,
        label_visibility="collapsed",
    )
    
    results = []
    
    if uploaded_files:
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]
        
        for file in uploaded_files:
            max_size_bytes = max_size_mb * 1024 * 1024
            if file.size > max_size_bytes:
                st.error(f"❌ File '{file.name}' is too large. Max size is {max_size_mb}MB.")
                continue
            
            try:
                file_data = process_uploaded_file(file)
                results.append(file_data)
                
                if show_preview:
                    with st.expander(f"📄 Preview: {file.name} ({file.size / 1024:.1f} KB)", expanded=False):
                        col_meta, col_preview = st.columns([1, 3])
                        
                        with col_meta:
                            st.metric("File Type", file_data.type)
                            st.metric("File Size", f"{file_data.size / 1024:.1f} KB")
                            st.metric("Characters", len(file_data.content))
                            if file_data.num_pages > 1:
                                st.metric("Pages", file_data.num_pages)
                        
                        with col_preview:
                            if file_data.content:
                                preview_length = min(2000, len(file_data.content))
                                preview = file_data.content[:preview_length]
                                if len(file_data.content) > preview_length:
                                    preview += "\n\n... (content truncated)"
                                
                                if file_data.type == "json":
                                    try:
                                        import json
                                        parsed = json.loads(file_data.content)
                                        st.json(parsed, expanded=False)
                                    except Exception:
                                        st.code(preview, language="json")
                                elif file_data.type == "csv":
                                    st.code(preview, language="csv")
                                elif file_data.type in ["py", "js", "html", "css", "sql"]:
                                    st.code(preview, language=file_data.type)
                                else:
                                    st.text(preview)
                            else:
                                st.info("ℹ️ No text content could be extracted from this file.")
            
            except Exception as e:
                st.error(f"❌ Error processing '{file.name}': {str(e)}")
    
    return results


def process_uploaded_file(file) -> UploadedFileData:
    raw_data = file.read()
    file.seek(0)
    
    filename = file.name
    file_ext = get_file_extension(filename).lower()
    
    if file_ext == ".pdf":
        content, num_pages = extract_text_from_pdf(raw_data)
        return UploadedFileData(
            name=filename,
            type="pdf",
            size=file.size,
            content=content,
            raw_data=raw_data,
            num_pages=num_pages,
        )
    elif file_ext in IMAGE_EXTENSIONS:
        return UploadedFileData(
            name=filename,
            type=file_ext.lstrip("."),
            size=file.size,
            content=f"[Image file: {filename}]",
            raw_data=raw_data,
        )
    else:
        content, encoding = extract_text_from_text_file(raw_data, file_ext)
        return UploadedFileData(
            name=filename,
            type=file_ext.lstrip("."),
            size=file.size,
            content=content,
            raw_data=raw_data,
            encoding=encoding,
        )


def get_file_extension(filename: str) -> str:
    import os
    _, ext = os.path.splitext(filename)
    return ext.lower() if ext else ""


def extract_text_from_pdf(raw_data: bytes) -> Tuple[str, int]:
    try:
        import pdfplumber
        with io.BytesIO(raw_data) as pdf_buffer:
            with pdfplumber.open(pdf_buffer) as pdf:
                num_pages = len(pdf.pages)
                all_text = []
                
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        all_text.append(f"--- Page {i + 1} ---\n{text}\n")
                
                return "\n".join(all_text), num_pages
    except ImportError:
        return extract_text_from_pdf_fallback(raw_data)
    except Exception as e:
        return f"[PDF parsing error: {str(e)}]", 1


def extract_text_from_pdf_fallback(raw_data: bytes) -> Tuple[str, int]:
    try:
        text = ""
        raw_str = raw_data.decode("latin-1", errors="ignore")
        
        text_patterns = [
            r'\(([^)]*)\)\s*Tj',
            r'\[([^\]]*)\]\s*TJ',
        ]
        
        matches = []
        for pattern in text_patterns:
            for match in re.finditer(pattern, raw_str):
                text_content = match.group(1)
                text_content = re.sub(r'\\(\d{3})', lambda m: chr(int(m.group(1), 8)), text_content)
                text_content = text_content.replace('\\\\', '\\')
                text_content = text_content.replace('\\(', '(')
                text_content = text_content.replace('\\)', ')')
                text_content = text_content.replace('\\n', '\n')
                matches.append(text_content)
        
        text = " ".join(matches)
        
        page_count = raw_str.count("/Type /Page")
        if page_count == 0:
            page_count = 1
        
        if text.strip():
            return text, page_count
        else:
            return "[Note: This PDF appears to be scanned or contains no extractable text. Full text extraction requires pdfplumber library.]", page_count
            
    except Exception as e:
        return f"[PDF parsing error: {str(e)}]", 1


def extract_text_from_text_file(raw_data: bytes, file_ext: str) -> Tuple[str, str]:
    encodings_to_try = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    
    for encoding in encodings_to_try:
        try:
            content = raw_data.decode(encoding)
            return content, encoding
        except UnicodeDecodeError:
            continue
    
    content = raw_data.decode("utf-8", errors="replace")
    return content, "utf-8 (with replacements)"


def combine_files_content(files: List[UploadedFileData], separator: str = "\n\n" + "=" * 80 + "\n\n") -> str:
    combined = []
    for file in files:
        header = f"=== Document: {file.name} (Type: {file.type}, Size: {file.size} bytes) ==="
        combined.append(f"{header}\n{file.content}")
    
    return separator.join(combined)


def truncate_for_context(content: str, max_chars: int = 100000) -> str:
    if len(content) <= max_chars:
        return content
    
    truncation_msg = f"\n\n[Content truncated from {len(content)} to {max_chars} characters]"
    return content[:max_chars] + truncation_msg
