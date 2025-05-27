'''
此api可能会过期，如果过期可以去coze.com注册智能体继续体验功能，具体操作可以查看文档
'''

import sys
import ast
vosk_path = '/home/pi/.local/lib/python3.9/site-packages'
if vosk_path not in sys.path:
    sys.path.append(vosk_path)
from cozepy import Coze, TokenAuth, BotPromptInfo, Message, ChatEventType, MessageContentType, \
    COZE_CN_BASE_URL  # 忽略代码检查工具对该行import的警告
def model_output(content):
    coze_api_token = 'pat_rdTYS4U5jVUlnNfEWVPFl7TwmrWtw3Im9IBEzZedR6hVPp5bHfV41e9ewjsk7Xw3'
    # 初始化Coze客户端
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)
    bot_id = '7501211586074509339'
    user_id = '123'
    # 调用coze.chat.stream方法创建一个聊天会话。此创建方法是流式聊天，会返回一个聊天迭代器。
    # 开发者应迭代该迭代器以获取聊天事件并进行处理
    chat_poll = coze.chat.create_and_poll(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            # 构建用户提问消息
            Message.build_user_question_text(content)
        ],
    )
    result = chat_poll.messages[0].content
    result = ast.literal_eval(result)
    return result