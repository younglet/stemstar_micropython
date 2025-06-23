import requests

def escape_unicode(s):
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in s)


class ChatBot:
    """
    基于 DeepSeek 的聊天机器人实现
    """
    def __init__(self,  api_key="sk-9c7380369ed8496490c93942cfcdf2ad", 
                        prompt="reply in Chinese, within 20 words",
                        ready_message='我准备好了， 一起来聊天吧！',
                        bot_avatar='🤖',
                        user_avatar='🤔'):
        self.bot_avatar = bot_avatar
        self.user_avatar = user_avatar
        self.ready_message = ready_message or "聊天机器人已就绪，请输入您的问题。"
        self.api_key = api_key
        self.url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.messages = [{"role": "system", "content": escape_unicode(prompt)}]
        
        # 验证 API Key 是否有效
        print(f"{self.bot_avatar}: 聊天机器人创建成功，正在验证 API Key...")
        self.is_valid = self.validate()
        
    def validate(self):
        payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content":"hello, reply shortly"}]}
        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            
            if response.status_code == 200:
                print(f"{self.bot_avatar}: {self.ready_message}")
                return True
            elif response.status_code == 401:
                print(f"{self.bot_avatar}: 401 - API 密钥无效，请检查密钥是否正确。")
                return False
            elif response.status_code == 402:
                print(f"{self.bot_avatar}: 402 - 账户余额不足，请充值后再试。")
                return False
            elif response.status_code == 429:
                print(f"{self.bot_avatar}: 429 - 您的请求速率已达到上限，请稍后再试。")
                return False
            elif response.status_code == 500:
                print(f"{self.bot_avatar}: 500 - 服务器内部错误，请稍后再试。")
                return False
            elif response.status_code == 503:
                print(f"{self.bot_avatar}: 503 - 服务器繁忙，请稍后再试。")
                return False
            else:
                print(f"{self.bot_avatar}: 请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"{self.bot_avatar}: 请求失败，网络未连接。")
            return False
        except requests.exceptions.RequestException as e:
            print(f"{self.bot_avatar}: API Key 验证失败: {e}")
            return False

    def chat(self, message):
        if not self.is_valid:
            answer  = f"{self.bot_avatar}: 请检查网络是否正常连接、 API 密钥是否正确、账户余额是否充足。"
            print(answer)
            return answer
        
        print(f"{self.user_avatar}: {message}")
        message = escape_unicode(message) # 针对micropython的josn模块兼容性的特殊处理
        self.messages.append({"role": "user", "content": message})
        
        
        payload = {"model": "deepseek-chat", "messages": self.messages}
        response = requests.post(self.url, json=payload, headers=self.headers)
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            answer = response_json["choices"][0]["message"]["content"]
            self.messages.append({"role": "assistant", "content": answer})
            print(f"{self.bot_avatar}: {answer}")
            return answer

    def reset(self):
        self.messages = [{"role": "system", "content": "reply in Chinese, within 20 words"}]
        print(f"{self.bot_avatar}: 已重置聊天记录和提示词。")

    def set_prompt(self, prompt):
        prompt = escape_unicode(prompt) # 针对micropython的josn模块兼容性的特殊处理
        self.messages = [{"role": "system", "content": prompt}]
        print(f"{self.bot_avatar}: 已成功修提示词。")


if __name__ == "__main__":
    from connect_wifi import connect_wifi
    
    
    connect_wifi()
    
    bot  = ChatBot()
    bot.chat("你好")
    
    bot.set_prompt("你是一个刁蛮小辣椒，怼天怼地对空气。")
    bot.chat("你好")

    bot.reset()
    bot.chat("你好")
