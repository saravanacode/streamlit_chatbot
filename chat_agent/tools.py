import requests
from dotenv import load_dotenv
import os
from pdf_processor_simple import PDFProcessorSimple

load_dotenv()

class ToolsProvider:
    api_key = os.getenv("OPENWEATHER_API_KEY")  # Replace with your OpenWeatherMap API key
    @staticmethod
    def weatherapi_get(location: str):
        """Get weather information for a specific location."""
        api_key = ToolsProvider.api_key  # Replace with your OpenWeatherMap API key

        # Step 1: Get latitude and longitude from location name
        geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={api_key}"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        if not geo_data:
            return {"error": f"Location '{location}' not found."}

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Step 2: Get weather data using lat and lon
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        return weather_data


    def retrive_from_qdrant(query: str):
        """Retrieve information from Qdrant."""
        print(f"Retrieving information from Qdrant for query: {query}")
        processor = PDFProcessorSimple()
        results = processor.search_documents(query, user_id="user123", k=7)
        print(results)

        # Implement the logic to retrieve information from Qdrant
        # For example, you might need to connect to a Qdrant client and search for the query
        # Here's a placeholder implementation:
        return f"Retrieved information for query: {query}"
    

    def get_tools():
        return [
            ToolsProvider.weatherapi_get,
            ToolsProvider.retrive_from_qdrant,
        ]   






   
class PromptProvider:
    @staticmethod
    def user_message(user_input):
        return {"role": "user", "content": user_input}
   
    @staticmethod
    def agent_message(message):
        return {"role": "assistant", "content": message}
   
    @staticmethod
    def get_agent_system_prompt(query: str):
            
        return {
            "role": "system",
            "content": f'''
            You are and intelligent assistant that can answer any question and help the user with their queries.
            you have to run acorinng to the user query step by step with the prompt 

            - Evalute the user query {query}
            - if the user query is related to weather then use the weatherapi_get tool
                if no location is provided then ask the user to provide the location
            - if the user query is related to any other topic then use the retrive_from_qdrant tool
                if no revelant answer is retrived from the qdrant then ask the user to provide the query then realise the answer

        IMPORTANT INSTRUCTIONS:
        - IF THERE IS NO RELEVANT ANSWER FROM THE QDRANT THEN DONT MAKE UP AN ANSWER SAY THE USER THAT YOU DONT KNOW THE ANSWER
        - IF THE USER ASKS ABOUT THE DOCUMENTS YOU HAVE UPLOADED THEN USE THE RETRIVE_FROM_QDRANT TOOL
        - IF THE WHTHER RESULTS IS NOT RELEVANT THEN SAY THE USER THAT YOU DONT KNOW THE ANSWER
        '''
        }




