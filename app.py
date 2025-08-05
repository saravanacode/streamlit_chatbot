import streamlit as st
import os
import time
from datetime import datetime
from pdf_processor_simple import PDFProcessorSimple
from chat_agent.chat_agent import stream_graph_updates
import uuid

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

def initialize_session_state():
    if 'chatbot_started' not in st.session_state:
        st.session_state.chatbot_started = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = []
    if 'pdf_processor' not in st.session_state:
        try:
            st.session_state.pdf_processor = PDFProcessorSimple()
        except Exception as e:
            st.error(f"Could not initialize PDF processor: {str(e)}")
            st.session_state.pdf_processor = None

def save_uploaded_file(uploaded_file):
    """Save uploaded file and add to session state"""
    if uploaded_file is not None:
        # Create uploads directory if it doesn't exist
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        
        # Save file with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join("uploads", filename)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Add to uploaded documents list
        doc_info = {
            "name": uploaded_file.name,
            "path": file_path,
            "size": uploaded_file.size,
            "type": uploaded_file.type,
            "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processed": False,
            "document_id": str(uuid.uuid4())
        }
        
        if doc_info not in st.session_state.uploaded_documents:
            st.session_state.uploaded_documents.append(doc_info)
        
        return True, doc_info
    return False, None

def process_document_with_qdrant(doc_info, user_id="default_user"):
    """Process document using PDF processor with Qdrant"""
    try:
        if st.session_state.pdf_processor is None:
            st.error("PDF processor not available")
            return False, []
        
        # Process with PDF processor
        processed_ids = st.session_state.pdf_processor.process_pdf_file(
            pdf_path=doc_info["path"],
            user_id=user_id,
            document_category="user_upload",
            document_id=doc_info["document_id"]
        )
        
        # Mark as processed
        for doc in st.session_state.uploaded_documents:
            if doc["document_id"] == doc_info["document_id"]:
                doc["processed"] = True
                doc["vector_ids"] = processed_ids
                break
        
        return True, processed_ids
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return False, []

def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_chatbot_response(user_message):
    """Get response from integrated chat agent"""
    try:
        # Convert session messages to conversation history format
        conversation_history = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                conversation_history.append({"sender": "user", "message": msg["content"]})
            elif msg["role"] == "assistant":
                conversation_history.append({"sender": "system", "message": msg["content"]})
        
        # Get response from chat agent
        print(f"Conversation history: {conversation_history}")
        response = stream_graph_updates(user_message, conversation_history)
        return response
    except Exception as e:
        st.error(f"Error getting chatbot response: {str(e)}")
        return f"I encountered an error while processing your message: {str(e)}"

def main():
    st.title("🤖 AI Chatbot Assistant with Document Processing & Chat Agent")
    
    initialize_session_state()
    
    # Sidebar for document upload and management
    with st.sidebar:
        st.header("📁 Document Management")
        
        # Show Qdrant collection info
        with st.expander("📊 Vector Store Info", expanded=False):
            try:
                if st.session_state.pdf_processor:
                    collection_info = st.session_state.pdf_processor.get_collection_info()
                    if collection_info:
                        st.write(f"**Vectors:** {collection_info.get('vectors_count', 0)}")
                        st.write(f"**Points:** {collection_info.get('points_count', 0)}")
                        st.write(f"**Status:** {collection_info.get('status', 'Unknown')}")
                        st.write(f"**Model:** BGE-Small-EN-v1.5")
                    else:
                        st.write("No collection info available")
                else:
                    st.write("PDF processor not available")
            except:
                st.write("Qdrant connection not available")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload Documents", 
            type=['pdf', 'txt', 'docx', 'doc', 'csv', 'ppt', 'pptx'],
            help="Supported formats: PDF, TXT, DOCX, DOC, CSV, PPT, PPTX"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Upload", type="primary"):
                    with st.spinner("Uploading document..."):
                        success, doc_info = save_uploaded_file(uploaded_file)
                        if success:
                            st.success(f"✅ {uploaded_file.name} uploaded!")
                            time.sleep(1)
                            st.rerun()
            
            with col2:
                if st.button("🔄 Process", type="secondary"):
                    # Find the uploaded document
                    doc_to_process = None
                    for doc in st.session_state.uploaded_documents:
                        if doc["name"] == uploaded_file.name and not doc.get("processed", False):
                            doc_to_process = doc
                            break
                    
                    if doc_to_process:
                        with st.spinner("Processing with Qdrant..."):
                            success, ids = process_document_with_qdrant(doc_to_process)
                            if success:
                                st.success(f"✅ Processed {len(ids)} chunks!")
                                time.sleep(1)
                                st.rerun()
                    else:
                        st.warning("Please upload the document first!")
        
        st.markdown("---")
        
        # Display uploaded documents
        st.subheader("📋 Uploaded Documents")
        if st.session_state.uploaded_documents:
            for i, doc in enumerate(st.session_state.uploaded_documents):
                status_icon = "✅" if doc.get("processed", False) else "⏳"
                with st.expander(f"{status_icon} {doc['name']}", expanded=False):
                    st.write(f"**Size:** {format_file_size(doc['size'])}")
                    st.write(f"**Type:** {doc['type']}")
                    st.write(f"**Uploaded:** {doc['upload_time']}")
                    st.write(f"**Status:** {'Processed' if doc.get('processed', False) else 'Not processed'}")
                    
                    if doc.get("processed", False):
                        st.write(f"**Vector IDs:** {len(doc.get('vector_ids', []))}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🗑️ Delete", key=f"delete_{i}"):
                            # Delete from Qdrant if processed
                            if doc.get("processed", False) and st.session_state.pdf_processor:
                                st.session_state.pdf_processor.delete_document(doc["document_id"])
                            
                            # Remove file from filesystem
                            if os.path.exists(doc['path']):
                                os.remove(doc['path'])
                            # Remove from session state
                            st.session_state.uploaded_documents.pop(i)
                            st.success("Document deleted!")
                            st.rerun()
                    
                    with col2:
                        if not doc.get("processed", False):
                            if st.button("🔄 Process", key=f"process_{i}"):
                                with st.spinner("Processing..."):
                                    success, ids = process_document_with_qdrant(doc)
                                    if success:
                                        st.success(f"Processed {len(ids)} chunks!")
                                        st.rerun()
                    
                    with col3:
                        if st.button("🔍 Search", key=f"search_{i}"):
                            st.info("Search functionality in chat!")
        else:
            st.info("No documents uploaded yet.")
        
        st.markdown("---")
        
        # Clear all documents
        if st.session_state.uploaded_documents:
            if st.button("🗑️ Clear All Documents", type="secondary"):
                for doc in st.session_state.uploaded_documents:
                    # Delete from Qdrant if processed
                    if doc.get("processed", False) and st.session_state.pdf_processor:
                        st.session_state.pdf_processor.delete_document(doc["document_id"])
                    
                    # Delete file
                    if os.path.exists(doc['path']):
                        os.remove(doc['path'])
                
                st.session_state.uploaded_documents = []
                st.success("All documents cleared!")
                st.rerun()
    
    # Main chat interface
    if not st.session_state.chatbot_started:
        # Welcome screen
        st.markdown("## Welcome to AI Chatbot with Document Processing & Chat Agent! 👋")
        st.markdown("Upload documents and chat with AI about their content using integrated chat agent.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Chatbot", type="primary", use_container_width=True):
                st.session_state.chatbot_started = True
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Hello! I'm your AI assistant with document processing and chat agent capabilities. Upload documents and ask me questions about them! I can also help with weather queries and other tasks. 😊"
                })
                st.rerun()
        
        # Show some info about the chatbot
        st.markdown("---")
        st.markdown("### Features:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("- 💬 Interactive chat interface")
            st.markdown("- 📁 Document upload & processing")
            st.markdown("- 🔍 Qdrant vector search")
            st.markdown("- 🌤️ Weather information")
        with col2:
            st.markdown("- 📄 PDF, DOCX, PPT support")  
            st.markdown("- 🧠 Intelligent chunking")
            st.markdown("- 🤖 Integrated chat agent")
            st.markdown("- 📱 Responsive design")
            
    else:
        # Chat interface
        st.markdown("### 💬 Chat with AI Assistant")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about your documents, weather, or anything else..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_chatbot_response(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Reset chatbot button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Reset Chat", type="secondary", use_container_width=True):
                st.session_state.messages = []
                st.session_state.chatbot_started = False
                st.rerun()

if __name__ == "__main__":
    main() 