from pdf_processor_simple import PDFProcessorSimple
import os
from chat_agent.chat_agent import stream_graph_updates

def test_pdf_processing():
    try:
        # Initialize processor
        print("Initializing PDF processor...")
        processor = PDFProcessorSimple()
        print("✅ Processor initialized")
        
        # Test with existing PDF
        pdf_path = "uploads/OFFER.pdf"
        print(f"📄 Testing with PDF: {pdf_path}")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            return
        
        print("🔄 Processing PDF...")
        response = stream_graph_updates("WHAT IS THE OFFER PROVIDE ADN THE SALARY STRCUTURE?", None)
        print(response)

        # # CORRECT - pass the file path directly
        # chunk_ids = processor.process_pdf_file(pdf_path, "user123", "research", "doc456")
        # print(f"✅ Successfully processed {len(chunk_ids)} chunks")
        
        # # Test search functionality
        # print("🔍 Testing search...")
        # results = processor.search_documents("WHAT IS THE OFFER PROVIDE ADN THE SALARY STRCUTURE?", user_id="user123", k=3)
        # print(f"✅ Found {len(results)} search results")
        
        # for i, result in enumerate(results):
        #     print(f"Result {i+1}: {result['content'][:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_processing()
