#!/bin/bash
# Replace with your OpenWeatherMap API key and city ID
API_KEY="your_api_key"
CITY_ID="your_city_id"

weather=$(curl -s "http://api.openweathermap.org/data/2.5/weather?id=${CITY_ID}&appid=${API_KEY}&units=metric")
if [ $? -ne 0 ]; then
    echo "Error fetching weather"
    exit 1
fi

temp=$(echo $weather | jq -r '.main.temp')
description=$(echo $weather | jq -r '.weather[0].description')

if [[ -z "$temp" || -z "$description" ]]; then
    echo "Weather data not available"
else
    echo "${temp}°C, ${description}"
fi

