import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import requests

api_key = 'PEIFhlfzhSkbGxw5JHHYpmhf1on2gxTt'
api_url_location_key = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'
api_url_weather = 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/'


def get_location_key_by_coordinates(latitude, longitude):
    #Отправляем запрес для получение location_key
    print(f'{latitude},{longitude}')
    response = requests.get(api_url_location_key, params=dict(
        apikey=api_key,
        q=f'{latitude},{longitude}'
    ))

    #Проверяем корректность запроса

    if response.status_code == 200:
        data = response.json()
        if data:
            location_key = data['Key']
            print(f'Location Key для координат ({latitude}, {longitude}): {location_key}')
            return location_key
        else:
            print('Локация не найдена.')
            return None
        
    #Информируем, если произошла ошибка

    else:
        print(f'Ошибка: {response.status_code} - {response.text}')
        return None
    
def get_weather_by_coordinates(latitude, longitude):
    print('ВЫПОЛНЯЕМ КОД')

    #Получаем location_key для нашиш коориднат с помощью http-запроса
    location_key = get_location_key_by_coordinates(latitude, longitude)

    #Проверяем получили мы ключ
    if location_key is not None:
        response = requests.get(f'{api_url_weather}{location_key}', params=dict(
            apikey=api_key,
            details = True,
            metric = True
        ))

    #Проверяем корректность запроса
        if response.status_code == 200:
            data = response.json()
            return data
    
    #Информируем, если произошла ошибка
        else:
            print(f'Ошибка: {response.status_code} - {response.text}')


def get_weather_features(latitude, longitude, amount_of_days):
    #получаем информацию о погоде через http-запрос
    weather_data = get_weather_by_coordinates(latitude, longitude)
    daily_forecast = weather_data['DailyForecasts'][:amount_of_days]

    # Температура
    min_temp_c = [day['Temperature']['Minimum']['Value'] for day in daily_forecast]
    max_temp_c = [day['Temperature']['Maximum']['Value'] for day in daily_forecast]

    # Влажность (используем дневные данные)
    humidity_day = [day['Day']['RelativeHumidity']['Minimum'] for day in daily_forecast]

    # Скорость ветра (используем дневные данные)
    wind_speed_day = [day['Day']['Wind']['Speed']['Value'] for day in daily_forecast]

    # Вероятность дождя (используем дневные данные)
    precipitation_probability = [day['Day']['PrecipitationProbability'] for day in daily_forecast]

    dates = [day['Date'].split('T')[0] for day in daily_forecast]  

    forecast = {
        'dates': dates,
        'min_temp_c': min_temp_c,
        'max_temp_c': max_temp_c,
        'humidity_day': humidity_day, #Если самая низкая влажность выше порога, то точно выходить не стоит
        'wind_speed_day': wind_speed_day, 
        'risk_of_rain': precipitation_probability
    }

    return forecast

def combine_weather_data(coords, amount_of_days):
    weathers = []
    for point in coords:
        lat, lon = point[0], point[1]
        if lat != None and lon != None:
            forecast = get_weather_features(latitude=lat, longitude=lon, amount_of_days=amount_of_days)
            weathers.append(forecast) 

    combined_data = []
    
    for index, weather in enumerate(weathers):
        # Добавляем индекс точки к каждому словарю
        if index == 0:
            weather['point_index'] = f'Первая точка'
            combined_data.append(pd.DataFrame(weather))

        elif index == len(weathers)-1:
            weather['point_index'] = f'Последняя точка'
            combined_data.append(pd.DataFrame(weather))
        
        else:
            weather['point_index'] = f'Дополнительная {index}'
            combined_data.append(pd.DataFrame(weather))
    
    # Объединяем все DataFrame в один
    combined_df = pd.concat(combined_data, ignore_index=True)

    print(combined_df)
    return combined_df