from chatbot import ChatBot
from connect_wifi import connect_wifi
    
    
connect_wifi()

bot  = ChatBot()
bot.chat("你好")

bot.set_prompt("你是一个刁蛮小辣椒，怼天怼地对空气。")
bot.chat("你好")

bot.reset()
bot.chat("你好")
