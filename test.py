import requests

url = "http://127.0.0.1:8000/create_dashboard"

payload = {
    "user_id": "Alex",
    "dashboard_id": "test_dashboard7",
    "description": """
Create a page showing 1 card and 2 charts.
The first card should say 'The Gapminder dataset is a detailed collection of global socioeconomic indicators over several decades. It includes data on GDP per capita, life expectancy, and population for numerous countries and regions.'
The first chart should show trend in average life expectancy with a line graph.
    """
    # Optionally, add "csv_path": "/absolute/path/to/your.csv"
}

response = requests.post(url, json=payload)
print(response.json())
