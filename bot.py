#https://t.me/xbotsmakerx make a order for the bot
from bs4 import BeautifulSoup
import random
import aiogram
import requests
import logging
import asyncio
from aiogram import Bot, Dispatcher, html, types, md
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto

TOKEN = 'your_token_botfather'
dp = Dispatcher()
max_pages = 100
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
base_url = 'https://thehentaiworld.com/page/{}/?new'
user_image_queues = defaultdict(deque)

async def main() -> None:
    global bot
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await db_start()
    # And the run events dispatching
    await dp.start_polling(bot)

@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🖼️ Генератор случайной картинки", callback_data='hgen')]
    ])
    await message.answer("Нажмите кнопку ниже, чтобы получить случайную картинку.", reply_markup=inline_kb)

def get_page_links(pages=3):
    page_links = []
    for page in range(1, pages + 1):
        url = base_url.format(page)
        response = requests.get(url, headers=headers)
        logging.info(f"Fetching URL: {url}")
        soup = BeautifulSoup(response.text, 'html.parser')

        content = soup.find('div', id='content')
        if content:
            grid = content.find('div', id='grid')
            if grid:
                thumb_container = grid.find('div', id='thumbContainer')
                if thumb_container:
                    thumbs = thumb_container.find_all('div', class_='thumb')
                    for thumb in thumbs:
                        link = thumb.find('a', href=True)
                        if link and 'videos' not in link['href']:
                            page_links.append(link['href'])
                else:
                    logging.warning(f"No thumb container found on page {page}")
            else:
                logging.warning(f"No grid found in content on page {page}")
        else:
            logging.warning(f"No content found on page {page}")
    return page_links

def get_image_links(page):
    image_links = []
    url = base_url.format(page)
    response = requests.get(url, headers=headers)
    logging.info(f"Fetching URL: {url}")
    soup = BeautifulSoup(response.text, 'html.parser')

    content = soup.find('div', id='content')
    if content:
        grid = content.find('div', id='grid')
        if grid:
            thumb_container = grid.find('div', id='thumbContainer')
            if thumb_container:
                thumbs = thumb_container.find_all('div', class_='thumb')
                for thumb in thumbs:
                    link = thumb.find('a', href=True)
                    if link and 'videos' not in link['href']:
                        image_links.append(link['href'])
            else:
                logging.warning(f"No thumb container found on page {page}")
        else:
            logging.warning(f"No grid found in content on page {page}")
    else:
        logging.warning(f"No content found on page {page}")
    return image_links

# Функция для получения ссылки на полное изображение
def get_image_url(page_url):
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find('div', id='content')
    if content:
        grid = content.find('div', id='grid')
        if grid:
            image = grid.find('div', id='image', itemtype="http://schema.org/ImageObject")
            if image:
                link = image.find('a', href=True)
                if link:
                    image_url = link['href']
                    return image_url
                else:
                    logging.warning(f"No link found in image on page {page_url}")
            else:
                logging.warning(f"No image found in grid on page {page_url}")
        else:
            logging.warning(f"No grid found in content on page {page_url}")
    else:
        logging.warning(f"No content found on page {page_url}")
    return None

# Функция для проверки, является ли URL ссылкой на изображение
def is_image_url(url):
    try:
        response = requests.head(url, headers=headers)
        content_type = response.headers.get('content-type')
        return content_type and 'image' in content_type
    except requests.RequestException as e:
        logging.error(f"Error checking URL {url}: {e}")
        return False

@dp.callback_query(lambda c: c.data == 'hgen')
async def process_callback_hgen(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    current_page = random.randint(1, max_pages)

    while True:
        if not user_image_queues[user_id]:
            image_links = get_image_links(current_page)
            if image_links:
                user_image_queues[user_id].extend(image_links)
                current_page = random.randint(1, max_pages)
            else:
                await bot.send_message(user_id, "Не удалось найти страницы с картинками на сайте.")
                break

        if user_image_queues[user_id]:
            page_url = user_image_queues[user_id].popleft()
            image_url = get_image_url(page_url)
            if image_url and is_image_url(image_url):
                try:
                    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=[
                        [types.InlineKeyboardButton(text="🖼️ Еще", callback_data='hgen')]
                    ])
                    await bot.send_photo(user_id, photo=image_url, reply_markup=inline_kb)
                    break
                except Exception as e:
                    logging.error(f"Error sending photo: {e}")
        else:
            await bot.send_message(user_id, "Не удалось найти страницы с картинками на сайте.")
            break

    await bot.answer_callback_query(callback_query.id)

if __name__ == "__main__":
    asyncio.run(main())


#https://t.me/xbotsmakerx make a order for the bot
#https://t.me/xbotsmakerx make a order for the bot
#https://t.me/xbotsmakerx make a order for the bot
