import logging
import asyncio
import os

import requests
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.files import JSONStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from settings import API_TOKEN

storage = JSONStorage("states.json")

# bot = Bot(token=API_TOKEN)


if "https_proxy" in os.environ:
    proxy_url = os.environ["https_proxy"]
    bot = Bot(token=API_TOKEN, proxy=proxy_url)
    print(proxy_url)
else:
    bot = Bot(token=API_TOKEN)


dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)

prev_price = 0
n = 90  # timer sec
chat_id = -830090293


class StateMachine(StatesGroup):
    main_state = State()


async def parser():
    # print(proxy_url)
    response = requests.get('https://card.wb.ru/cards/detail?spp=0'
                            '&regions=80,64,83,4,38,33,70,82,69,68,86,30,40,48,1,22,66,31'
                            '&pricemarginCoeff=1.0'
                            '&reg=0'
                            '&appType=1'
                            '&emp=0'
                            '&locale=ru'
                            '&lang=ru'
                            '&curr=rub'
                            '&couponsGeo=12,7,3,6,18,22,21'
                            '&dest=-1075831,-79374,-367666,-2133462'
                            # '&nm=124415723', proxies=proxy_url)
                            '&nm=140524178')
    data = response.json()
    product = data['data']['products'][0]
    price = float(product['salePriceU'] / 100)
    # price = 33000
    # prev_price = float(product['priceU'] / 100)
    global prev_price

    if price < prev_price:
        text = (f"Цена понизилась!" + "\n" +
                "Товар: <b>" + product['name'] + "</b>\n" +
                "<b>Текущая цена: " + str(price) + "</b>" + "\n" +
                "Ссылка: " + "https://www.wildberries.ru/catalog/" + str(product['id']) + "/detail.aspx")
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="html")
        prev_price = price
    # else:
    #     await bot.send_message(chat_id=chat_id, text="test")

    # print(f"Товар: " + product['name'])
    # print(f"Ссылка: " + "https://www.wildberries.ru/catalog/" + str(product['id']) + "/detail.aspx")
    # print(f"Предыдущая цена: " + str(prev_price))
    # print(f"Текущая цена: " + str(price))


@dp.message_handler(commands=['begin'], state="*")
async def send_welcome(message: types.Message):
    if "https_proxy" in os.environ:
        proxy = os.environ["https_proxy"]
        print(f"proxy = " + proxy)
    else:
        print("no proxy :(")

    await StateMachine.main_state.set()
    await message.answer(f"Халлоу, запомиаю текущую цену и начну опрашивать каждые " + str(n) + " секунд. " +
            "Результат вывожу в нашу группу")

    response = requests.get('https://card.wb.ru/cards/detail?spp=0'
                            '&regions=80,64,83,4,38,33,70,82,69,68,86,30,40,48,1,22,66,31'
                            '&pricemarginCoeff=1.0'
                            '&reg=0'
                            '&appType=1'
                            '&emp=0'
                            '&locale=ru'
                            '&lang=ru'
                            '&curr=rub'
                            '&couponsGeo=12,7,3,6,18,22,21'
                            '&dest=-1075831,-79374,-367666,-2133462'
                            # '&nm=124415723', proxies=proxy)
                            '&nm=140524178')
    data = response.json()
    product = data['data']['products'][0]
    global prev_price
    prev_price = float(product['salePriceU'] / 100)

    text = (f"Товар: <b>" + product['name'] + "</b> \n" +
            "Текущая цена: <b>" + str(prev_price) + "</b>" + "\n" +
            "Ссылка: " + "https://www.wildberries.ru/catalog/" + str(product['id']) + "/detail.aspx")
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="html")


async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        await parser()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(n))
    executor.start_polling(dp, skip_updates=True)