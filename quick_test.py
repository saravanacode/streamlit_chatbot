from chat_agent.chat_agent import stream_graph_updates

def quick_test():
    """Quick test of the chat agent"""
    
    # Test query
    query = "WHAT IS THE OFFER PROVIDE ADN THE SALARY STRCUTURE??"
    
    print(f"🤖 Testing: {query}")
    print("=" * 40)
    
    try:
        response = stream_graph_updates(query)
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()