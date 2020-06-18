import telepot

"""classe para fazer comunicação com telegram
"""
class Telebot:
    def __init__(self, chat_id, token):
        self.bot = telepot.Bot(token)
        self.chat_id = chat_id

    """envia mensagem para chat pre definido
    """
    def sendMessage(self, msg: str)-> None:
        self.bot.sendMessage(self.chat_id, msg)

if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 3:
        Telebot(sys.argv[1], sys.argv[2]).sendMessage('[bot] say ~> teste de comunicação...')
    else:
        print('usage: ' + sys.argv[0] + ' chat_id token')
