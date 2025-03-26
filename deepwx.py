# coding=utf-8

from wxauto import *
import time
from openai import OpenAI
import re


URL = input("Base URL:")
apikey = input("密钥(sk-xxxx):")
Modelname = input("模型名称: ")
chatgroup = input("监听的群聊:")

systemprot = input("角色(系统提示词):")

try:
    convorounds = int(input("保留对话轮数:"))
except:
    convorounds = 1
    print(convorounds)
try:
    TEMP = float(input("对话温度:"))
except:
    TEMP = 0.7
    print(TEMP)
try: 
    MAX = int(input("最大答复tokens:"))
except:
    MAX = 0
    print(MAX)



client = OpenAI(api_key=apikey, base_url=URL)

wx = WeChat()

agentname = "@"+wx.nickname

def summarize_history(messages):
    # 将 messages 拼接成文本，发送给AI生成摘要
    summary = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[{"role": "user", "content": f"总结对话历史(字数不要太多)：\n{messages}"}]
    )
    return summary.choices[0].message.content

def remove_extra_newlines(text):
  """删除文本中多余的换行符，只保留一个。"""
  return re.sub(r"\n{2,}", "\n", text)

messages = [
        {"role": "system", "content": systemprot}
    ]
wx.AddListenChat(who=chatgroup)

wait = 1  # 设置1秒查看一次是否有新消息


while True:
    msgs = wx.GetListenMessage()
    for msg in msgs:
        for msgall in msgs[msg]:

            if msgall[0] != "查看更多消息" and msgall[0] != "SYS" and msgall[0] != "Self":
                if agentname in msgall[1]:
                    match = re.search(r"for (.*)>", str(msg))



                    try:
                        messagea =  msgall[0] +" 向你提问:" + msgall[1].replace(agentname, "")
                        print("提问:" + messagea)

                        messages.append({"role": "user", "content": messagea})

                        response = client.chat.completions.create(
                            model=Modelname,  # 也可以使用 "gpt-4"
                            messages=messages,
                            temperature=TEMP,
                            max_tokens=MAX
                        )

                        assistant_reply = response.choices[0].message.content
                        concat_reply = remove_extra_newlines(assistant_reply)
                        # total_tokens_used = response.usage.total_tokens #联网应用bot无法使用此表达式
                        named_reply = msgall[0] + ", " + concat_reply
                        wx.SendMsg(named_reply, who=match.group(1))
                        print(agentname + "回复完成！")

                        messages.append({"role": "assistant", "content": concat_reply})

                        max_history = convorounds  # 保留最近n轮对话（用户和助手交替）
                        system_messages = [msg for msg in messages if msg["role"] == "system"]  # 提取所有系统消息
                        other_messages = [msg for msg in messages if msg["role"] != "system"]  # 非系统消息

                        # 截断非系统消息，保留最近的n轮（每轮2条，共2n条）
                        truncated_other = other_messages[-max_history * 2:]

                        # 合并：系统消息 + 截断后的对话历史
                        messages = system_messages + truncated_other

                        # recent_messages = messages[-10:]  # 最近2轮（用户+助手各2条）
                        # summary = summarize_history(messages[:-4])
                        # messages = [
                        #     {"role": "system", "content": sysprot + "历史摘要：" + summary},
                        #     *recent_messages
                        # ]
                    except:
                        print("ERRPR!!!!!!!")

                        wx.SendMsg("服务器错误..", who=match.group(1))

                    else:
                        a = 0
                    finally:
                        a = 0









    time.sleep(wait)
