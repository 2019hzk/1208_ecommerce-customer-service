# coding=utf-8

import time
import json
import dashscope
from dashscope.audio.tts_v2 import *

from datetime import datetime


def get_timestamp():
    now = datetime.now()
    formatted_timestamp = now.strftime("[%Y-%m-%d %H:%M:%S.%f]")
    return formatted_timestamp


# 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
# 若没有配置环境变量，请用百炼API Key将下行替换为：dashscope.api_key = "sk-xxx"
dashscope.api_key = "sk-983bea5e73584a92950148b7df36a4b0"

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：wss://dashscope-intl.aliyuncs.com/api-ws/v1/inference
dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'

# 模型
model = "cosyvoice-v3-flash"
# 音色
voice = "longyingjing_v3"


# 定义回调接口
class Callback(ResultCallback):
    _player = None
    _stream = None

    def on_open(self):
        self.file = open("output.mp3", "wb")
        print("连接建立：" + get_timestamp())

    def on_complete(self):
        print("语音合成完成，所有合成结果已被接收：" + get_timestamp())
        # 当任务完成（on_complete 回调触发）后，才可调用 get_first_package_delay 获取延迟
        # 首次发送文本时需建立 WebSocket 连接，因此首包延迟会包含连接建立的耗时
        print('[Metric] requestId为：{}，首包延迟为：{}毫秒'.format(
            synthesizer.get_last_request_id(),
            synthesizer.get_first_package_delay()))

    def on_error(self, message: str):
        print(f"语音合成出现异常：{message}")

    def on_close(self):
        print("连接关闭：" + get_timestamp())
        self.file.close()

    def on_event(self, message):
        # 解析服务端事件，获取输出信息
        data = json.loads(message)
        output = data.get('payload', {}).get('output', {})
        event_type = output.get('type', '')
        original_text = output.get('original_text', '')
        if event_type:
            print(f"事件类型: {event_type}, 原始文本: {original_text}")

    def on_data(self, data: bytes) -> None:
        print(get_timestamp() + " 二进制音频长度为：" + str(len(data)))
        self.file.write(data)


callback = Callback()

# 实例化SpeechSynthesizer，并在构造方法中传入模型（model）、音色（voice）等请求参数
synthesizer = SpeechSynthesizer(
    model=model,
    voice=voice,
    callback=callback,
)

# 发送待合成文本，在回调接口的on_data方法中实时获取二进制音频


synthesizer.call("今天天气怎么样？")

time.sleep(5)
