import os
import logging
import asyncio
from psycopg2 import connect
from aiogram import Bot, Dispatcher, executor, types
from io import BytesIO
from requests import get
from textwrap import wrap
from PIL import Image, ImageFont, ImageDraw

os.chdir(os.path.dirname(os.path.abspath(__file__)))
emt = b'BM:\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x04\x00\x00\x00\xc4\x0e\x00\x00\xc4\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00'

Token = '2077974561:AAGFIJXxEx6WZkAr5HGyWTWoNChgoAz90kc'
logging.basicConfig(level=logging.INFO)
bot = Bot(Token)
dp = Dispatcher(bot)
logs_id = -1001440234388
piclogs_id = -1001626784076

try:
    db = connect(
        host="fanny.db.elephantsql.com",
        database="haivqguu",
        user="haivqguu",
        port="5432",
        password="GMdfh5chLCA64FtvMTk29jWAvKseh07T"
    )
    sql = db.cursor()
except:
    get(f'https://api.telegram.org/bot{Token}/sendmessage?chat_id={logs_id}&text=[SQL]%20[Could\'t_Connect_To_BD]')

sql.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id Int
)""")
db.commit()
get(f'https://api.telegram.org/bot{Token}/sendmessage?chat_id={logs_id}&text=Rebooted%20{robot}')


def make_mq(pfp=emt, text='No text'):

    try:

        # with open('photo.jpg', 'rb') as f:
        #     pfp = f.read()
        
        text = '\n'.join(wrap(text, 30))
        text = f'“{text}„'
        with open('times.ttf', 'rb') as bff:
            bf = bff.read()
        font = ImageFont.truetype(BytesIO(bf), 50)
        im = Image.open(BytesIO(pfp))
        im = im.convert('L')
        im = im.convert('RGBA').resize((1024, 1024))
        w, h = im.size
        w_, h_ = 20 * (w // 100), 20 * (h // 100)
        im_ = Image.new('RGBA', (w - w_, h - h_), (0, 0, 0))
        im_.putalpha(150) 
        im.paste(im_, (w_ // 2, h_ // 2), im_)
        draw = ImageDraw.Draw(im)
        _w, _h = draw.textsize(text=text, font=font)
        x, y = (w - _w) // 2, (h - _h) // 2
        draw.text((x, y), text=text, font=font, fill='#fff', align='center')
        output = BytesIO()
        im.save(output, 'PNG')
        output.seek(0)

        return {'ok': True, 'pic': output}

    except Exception as e:
        print(e)
        return {'ok': False, 'exc': repr(e)}

@dp.message_handler(commands=['start'])
async def start_(message: types.Message):
    try:
        await bot.forward_message(logs_id, message.chat.id, message.message_id)
        if message.chat.type == 'private':
            await message.answer(f'Hi, [{message.from_user.first_name}](tg://user?id={message.from_user.id})\nI can make quotes, type me anything or send photo with caption', parse_mode='markdown')
        else:
            await message.answer(f'I can make quotes, reply /quote to any text', parse_mode='markdown')

        sql.execute(f"Select user_id from users where user_id = {message.chat.id}")
        if sql.fetchone() is None:
            sql.execute(f"INSERT INTO users (user_id) VALUES ({message.chat.id})")
            db.commit()

    except:
        await bot.send_message(logs_id, f'{repr(e)}')

@dp.message_handler(commands=['all'])
async def all_(message: types.Message):
    try:
        await bot.forward_message(logs_id, message.chat.id, message.message_id)

        sql.execute("SELECT * FROM users")
        allusers = sql.fetchall()
        with open(f'{len(allusers)}.txt', 'w') as f:
            f.write(str(allusers))
        await bot.send_document(message.chat.id, open(f'{len(allusers)}.txt', 'rb'))

    except Exception as e:
        await bot.send_message(logs_id, f'{repr(e)}')

@dp.message_handler(commands=['quote'])
async def quote_(message: types.Message):
    try:
        await bot.forward_message(logs_id, message.chat.id, message.message_id)

        try:
            text = message.reply_to_message.text
            if not text:
                raise
        except:
            await message.reply('Reply /quote to text')
            return

        ext = f"{message.reply_to_message['from'].id}"
        pic = await bot.get_user_profile_photos(ext)
        if pic['total_count']:
            pic = await pic['photos'][0][-1].download(ext)
            with open(ext, 'rb') as f:
                pfp = f.read()
        else:
            pfp = emt

        photo = make_mq(pfp, text)['pic']
        await message.reply_photo(photo)

    except Exception as e:
        await bot.send_message(logs_id, f'{repr(e)}')

@dp.message_handler(content_types=['text'])
async def text_(message: types.Message):
    try:
        if message.chat.type != 'private':
            return # Use filters you baka
        await bot.forward_message(logs_id, message.chat.id, message.message_id)

        ext = f'{message.from_user.id}'
        pic = await bot.get_user_profile_photos(ext)
        if pic['total_count']:
            pic = await pic['photos'][0][-1].download(ext)
            with open(ext, 'rb') as f:
                pfp = f.read()
        else:
            pfp = emt

        photo = make_mq(pfp, message.text)['pic']
        done = await message.reply_photo(photo)
        await bot.forward_message(piclogs_id, message.chat.id, done.message_id)

    except Exception as e:
        await bot.send_message(logs_id, f'{repr(e)}')

@dp.message_handler(content_types=['photo'])
async def photo_(message: types.Message):
    try:
        await bot.forward_message(logs_id, message.chat.id, message.message_id)

        ext = f'{message.from_user.id}'
        pic = await message.photo[-1].download(ext)
        with open(ext, 'rb') as f:
            pfp = f.read()

        photo = make_mq(pfp, message.caption if message.caption else 'Where\'s caption ?')['pic']
        done = await message.reply_photo(photo)
        await bot.forward_message(piclogs_id, message.chat.id, done.message_id)

    except Exception as e:
        await bot.send_message(logs_id, f'{repr(e)}')

if __name__ == '__main__':
    executor.start_polling(dp)
