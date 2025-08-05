
# import requests

# api_key = "51d3f47362c2d66c4e0ddae91918f184"
# # Example coordinates (Chennai, India)
# lat = 13.0827
# lon = 80.2707
# # url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=hourly,daily&appid={api_key}"
# url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
# response = requests.get(url)
# data = response.json()

# print(data)


from chat_agent.tools import ToolsProvider

print(ToolsProvider.weatherapi_get("Chennai"))
