import telebot
import requests
import logging
from bot_sec import BOT_TOKEN
from yacloud_sec import FOLDER_ID, API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
HEADER = {
    'Content-Type': "application/json",
    'Authorization': f"Api-Key {API_KEY}"
}

bot = telebot.TeleBot(BOT_TOKEN)

prompt = {
    'modelUri': f"gpt://{FOLDER_ID}/yandexgpt-lite",
    'completionOptions': {
        'stream': False,
        'temperature': 0.6,
        'maxTokens': "2000"
    }
}


def getText(respText):
    res = respText['result']['alternatives'][0]['message']['text']
    return res


@bot.message_handler(commands=['start'])
def start_message(message):
    userText = " ".join(message.text.split()[1:])
    
    logger.info(f"Запрос: {userText}")

    prompt['messages'] = [
        {
            'role': "user",
            'text': userText
        }
    ]
    
    response = requests.post(MODEL_URL, headers=HEADER, json=prompt).json()
    bot.send_message(message.chat.id, getText(response))


bot.polling()
