from datetime import datetime
import telegram

# test bot token
test_token = '1752082595:AAGNrv40yp-5RJVstxOXyPCCTRehfFf-X0I'

# ko_stock_manager_bot token
k_stock_token = '1734835630:AAFPw9UL89VfcGDn-hhzZh0xMaHqqEodDmg'
bot = telegram.Bot(token=k_stock_token)

system_log_bot_token = '1769031053:AAEUeiHVXhsHKq0lcNTj2BMZFCOlT5QXbgI'
log_bot = telegram.Bot(token=system_log_bot_token)

coin_log_bot_token = '1845524861:AAGv9tTHI08Ie1o7qTQkp-tu95lyBR41uLY'
coin_bot = telegram.Bot(token=coin_log_bot_token)

# messages = bot.getUpdates()
# print(messages)

# for message in messages:
# 	print(message)


def send_telegram_msg(msg: str, *args) -> None:
	now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	chat_id = '1736109154'
	text = f"[{now_str}] - {msg}"
	bot.send_message(chat_id=chat_id, text=text)


def system_log(msg: str, *args) -> None:
	""" 시스템 상 버그 발생시 메시지 전송 """
	now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	chat_id = '1736109154'
	txt = f'[{now_str}] {msg}'
	log_bot.send_message(chat_id=chat_id, text=txt)


def send_coin_bot(msg: str, *args) -> None:
	now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	chat_id = '1736109154'
	txt = f'[{now_str}] {msg}'
	coin_bot.send_message(chat_id=chat_id, text=txt)



if __name__ == '__main__':
	msg = 'hello world '
	# print(msg)
	# send_telegram_msg(msg)
	# system_log('hi world?')
	send_coin_bot('hi world?')