# 🤖 AI Chatbot with Document Processing

An interactive Streamlit chatbot that processes documents (PDFs, DOCX, etc.) and answers user questions using AI-powered vector search with Qdrant and OpenAI/Gemini.

---

## ✨ Features

- 📄 **Document Upload**: PDF, Word, CSV, PPT, and TXT support  
- 🔍 **Smart Search**: Ask questions about your documents  
- 💬 **Natural Chat**: Human-like conversations  
- 🌤️ **Weather Info**: Ask for real-time weather  
- 🎨 **Clean UI**: Streamlit-based, responsive interface  

---

## 🚀 Quick Start

### 1. Install Requirements
```bash
pip install -r requirements.txt

Create a .env file in the root directory with the following:

OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
QDRANT_URL=https://your-qdrant-url
QDRANT_API_KEY=your_qdrant_api_key
VECTOR_NAME=your_collection_name
OPENWEATHER_API_KEY=your_weather_api_key


3. Run the app

streamlit run app.py


🎯 How to Use
Click 🚀 Start Chatbot

Upload your documents from the sidebar

Click 🔄 Process to index documents with Qdrant

Start chatting — ask anything about your files or weather