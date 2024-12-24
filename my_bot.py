from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import asyncio
import plotly.graph_objects as go
from webserver import combine_weather_data
import pandas as pd
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Вставь сюда токен
API_TOKEN = '7592469504:AAFTdWw52d9pVroMWL1q7QRxukaa-nhcBUI'

# Создаём бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


STATE_START = 'STARTING'
STATE_DAYS = 'DAYS' #Состояния ввыбора количества дней в прогнозе
STATE_POINTS = 'POINT' #Состояние выборка количества промежуточных точек
STATE_СOORDS = 'COORDS' #Введение коориднат
STATE_FINISH = 'FINISH' #После введения всех коориднат 

# Словарь для хранения состояния пользователей
user_states = {}
df = {}
#Делаем сообщение для команды /help
help_message_content = ''
with open('My_project\help_message.txt', 'r', encoding='utf-8') as file:
    help_message_content = file.read()

#Делаем сообщение для команды /bot
about_coords = ''
with open('My_project\About_coords.txt', 'r', encoding='utf-8') as file:
    about_coords = file.read()

#Список для выбора погоды:
days_forecast = {
    '1_day': 1,
    '3_day': 3,
    '5_day': 5,
}

async def get_days_of_forecast():
    inline_buttons = []
    inline_buttons.append(InlineKeyboardButton(text = '1 день', callback_data=f'1_day'))
    inline_buttons.append(InlineKeyboardButton(text = '3 дня', callback_data=f'3_day'))
    inline_buttons.append(InlineKeyboardButton(text = '5 дней', callback_data=f'5_day'))
    inline_buttons.append(InlineKeyboardButton(text = '10 дней', callback_data=f'10_day'))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_buttons])
    return keyboard

extra_points = {
    '0extrapoint': 0,
    '1extrapoint': 1,
    '2extrapoint': 2,
    '3extrapoint': 3,
    '4extrapoint': 4,
    '5extrapoint': 5
}
async def get_extra_points():
    inline_buttons = []
    for i in range(0, 6):
        inline_buttons.append(InlineKeyboardButton(text=str(i), callback_data=f'{i}extrapoint'))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_buttons])
    return keyboard

async def validate_lanlon(latlon):
    lat, lon = latlon.split()
    answer = {'error': 0}
    try:
        lat = float(lat)
        if 90 > lat >= -90 and len(str(lat)) >= 7:
            answer['lat'] = lat
        else:
            answer['lat'] = 'Bad_format'
            answer['error'] += 1
    except ValueError:
        answer['lat'] = 'Not a number'
        answer['error'] += 1

    try:
        lon = float(lon)
        if 180 > lon >= -180 and len(str(lon)) >= 7:
            answer['lon'] = lon
        else:
            answer['lon'] = 'Bad_format'
            answer['error'] += 1
    except ValueError:
        answer['lon'] = 'Not a number'
        answer['error'] += 1
    
    return answer



@dp.message(F.text == '/start')
async def start_message(message: types.Message):
    user_states[message.from_user.id] = {'state': STATE_START, 'days': None, 'points': None, 'coords': [], 'df': {}}
    
    # Создаем кнопку "Начать работу"
    start_button = InlineKeyboardButton(text='Начать работу', callback_data='start_button')
    help_button = InlineKeyboardButton(text='Больше о функционале бота', callback_data='help')
    inline_buttons = [start_button, help_button]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_buttons], row_width=2)

    # Отправляем сообщение с кнопками
    await message.answer(
        '''Добро пожаловать в Weather_for_CU! Этот бот нужен, чтобы определять погоду в нужных тебе точках!
Чем я могу помочь тебе?''',
        reply_markup=keyboard
    )

    # Сразу вызываем обработчик нажатия кнопки "Начать работу"
    await start_working(message)


#Вывод для инлайн-кнопки начала работы
@dp.callback_query(F.data == 'start_button')
async def start_working(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.answer()
    await callback_query.message.answer('На сколько дней вам нужен прогноз?',
        reply_markup= await get_days_of_forecast())
    user_states[user_id]['state'] = STATE_DAYS


#Вывод для инлайн-кнопки помощи начала работы
@dp.callback_query(F.data == 'help')
async def help_message(callback_query: types.CallbackQuery):
    await callback_query.message.answer(help_message_content)
    await callback_query.answer()

@dp.message(F.text == '/coordinat')
async def coordinat_info(message: types.Message):
    await message.answer(about_coords)

@dp.callback_query(F.data.in_(days_forecast.keys()))
async def choose_days(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    if user_states[user_id]['state'] == STATE_DAYS:
        num_in = callback_query.data.find('_')
        days = int(callback_query.data[:num_in])
        user_states[user_id]['days'] = days
        print(user_states)

        await callback_query.answer()
        await callback_query.message.answer(
            f'Количество дней для вашего прогноза: {days}'
        )

        keyboard = await get_extra_points()
        await callback_query.message.answer(
            f'Сколько будет промежуточных точек в вашем маршруте?',
            reply_markup=keyboard
        )
        user_states[user_id]['state'] = STATE_POINTS
    
    else:
        await callback_query.answer()
        await callback_query.message.answer(
            f'''Вы уже выбрали количество дней в прогнозе, если хотите
сделать выбор снова, то используйте команду /start и пройдите процесс сначала'''
        )


@dp.callback_query(F.data.in_(extra_points.keys()))
async def write_extra_points(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_states[user_id]['state'] == STATE_POINTS:
        points = int(callback_query.data[0])
        user_states[user_id]['points'] = points + 2
        print(user_states)
        await callback_query.answer()
        await callback_query.message.answer(
            f'''Вы выбрали количество промежуточных точек: {points}
Итого точек в вашем маршруте: {points+2}.'''
        )

        await callback_query.message.answer('''
Теперь, отправьте сообщение, начинающееся с команды /set_coords, и затем в каждой новой строчке указывайте коориднаты каждой ваше точки
Сначала указывайте широту, затем долготу. Указывайте обе с коориднатами с точносью от 5 знаков''')

        user_states[user_id]['state'] = STATE_СOORDS

    
    else:
        await callback_query.answer()
        await callback_query.message.answer(
            f'''Вы уже выбрали количество дополнительных в прогнозе, если хотите сделать выбор снова, то используйте команду /start и пройдите процесс сначала'''
        )
    

async def get_set_coods_inline():
    inline_buttons = []
    inline_buttons.append(InlineKeyboardButton(text = 'Увидеть сводку', callback_data=f'Svodka'))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_buttons])
    return keyboard

@dp.message(F.text.startswith('/set_coords'))
async def set_coords(message: types.Message):
    user_id = message.from_user.id
    if user_states[user_id]['state'] == STATE_СOORDS:
        param = message.text.split('\n')

        if len(param) == user_states[user_id]['points'] + 1:
            await message.answer('Вы ввели нужное количество точек')
            errors = []
            for index, latlot in enumerate(param[1:]):
                answer = await validate_lanlon(latlon=latlot)
                if answer['error'] >= 1:
                    errors.append(index + 1)
                user_states[user_id]['coords'].append([answer['lat'], answer['lon']])


            if len(errors) >= 1:
                await message.answer(f'''Некоторые из ваших строх неккоректы.
    Проверьте эти строки {errors}''')
            
            else:
                user_states[user_id]['state'] = STATE_FINISH
                print(user_states[user_id]['coords'])
                await message.answer('Вы красавчик', reply_markup= await get_set_coods_inline())

        
        else:
            await message.answer(f'''Вы ввели не то количество коориднат, которое указывали
    Ожидалось {user_states[user_id]['points']}
    Вы ввели: {len(param) - 1} '''
            )
    else:
        await message.answer('Вы не находитесь на этапе записи координат. Используйте /start, чтобы пройти весь процесс занова и запсать коориднаты')

forecast = {
        'dates': 1,
        'min_temp_c': 1,
        'max_temp_c': 1,
        'humidity_day': 1, #Если самая низкая влажность выше порога, то точно выходить не стоит
        'wind_speed_day': 1, 
        'risk_of_rain': 1
    }
async def get_weather_features():
    inline_buttons = []
    inline_buttons.append(InlineKeyboardButton(text = 'Влажность', callback_data=f'humidity_day'))
    inline_buttons.append(InlineKeyboardButton(text = 'Вероятность дождя', callback_data=f'risk_of_rain'))
    inline_buttons.append(InlineKeyboardButton(text = 'Cкорость ветра', callback_data=f'wind_speed_day'))
    inline_buttons.append(InlineKeyboardButton(text = 'Минимальная температура', callback_data=f'min_temp_c'))
    inline_buttons.append(InlineKeyboardButton(text = 'Максимальная температура', callback_data=f'max_temp_c'))
    


    keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_buttons])
    return keyboard


@dp.callback_query(F.data == 'Svodka')
async def get_graphs(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_states[user_id]['df'] = combine_weather_data(user_states[user_id]['coords'], user_states[user_id]['days'])
    await callback_query.message.answer('Сводку по каким атрибутам вы хотите увидеть?',
    reply_markup= await get_weather_features())

@dp.callback_query(F.data.in_(forecast.keys()))
async def get_feature(callback_query: types.CallbackQuery):
    atribute = callback_query.data
    user_id = callback_query.from_user.id
    answer = ''

    for index, row in user_states[user_id]['df'].iterrows():
        answer += f"dates: {row['dates']}, {atribute}: {row[atribute]}, point_index: {row['point_index']} \n"

    await callback_query.message.answer(answer)

async def main():
        # Подключаем бота и диспетчера
        await dp.start_polling(bot)



# Запуск бота
if __name__ == '__main__':
    try:
    # Запускаем главный цикл
        asyncio.run(main())
    except Exception as e:
        logging.error(f'Ошибка при запуске бота: {e}')