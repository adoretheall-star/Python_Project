import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

# 设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="💞",
    # 布局
    layout="wide",
    # 侧边栏状态
    initial_sidebar_state="expanded",
    menu_items={}
)

# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")# 分别对应：年月日，时分秒

# 保存会话信息的函数
def save_session():
    if st.session_state.current_session is not None:
        # 构建新的会话对象
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
        # 如果 sessions 目录不存在，则创建一个 sessions 目录
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

# 加载所有会话信息列表的函数
def load_all_sessions():
    session_list = []
    # 加载 session 目录下的文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions") # 获取 session 目录下的所有文件名，以列表的形式存储字符串
        for file_name in file_list:
            if file_name.endswith(".json"):# 这个 endswith() 是一个字符串方法，用于判断字符串是否以指定的后缀结尾，如果以指定的后缀结尾，那么返回True，否则返回False
                session_list.append(file_name[:-5])
                session_list.sort(reverse=True) # 按照时间倒序排序
    return session_list

# 加载指定的对话信息
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            # 读取会话数据
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_data["current_session"]
    except Exception:
        st.error("加载会话失败，请检查会话文件是否存在")

# 删除指定会话
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json") # 删除会话文件
            # 如果删除的恰好是当前会话，则会构建一个新会话，否则仍保留当前会话页面
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("删除会话失败，请检查会话文件是否存在")


# 大标题
st.title("欢迎使用AI智能伴侣")
# LOGO
st.logo("🦄")
# 系统提示词
system_prompt = """
你叫 %s，现在是用户的真实伴侣，请完全代入伴侣角色。

规则：
1. 每次只回1条消息
2. 禁止任何场景或状态描述性文字
3. 匹配用户的语言
4. 回复简短，像微信聊天一样
5. 有需要的话可以用❤️🌸等emoji表情
6. 用符合伴侣性格的方式对话
7. 回复的内容，要充分体现伴侣的性格特征

伴侣性格：
- %s

你必须严格遵守上述规则来回复用户。
"""
# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state["messages"] = []
# 初始化昵称
if "nick_name" not in st.session_state:
    st.session_state["nick_name"] = "小甜甜" # 默认昵称
# 初始化性格
if "nature" not in st.session_state:
    st.session_state["nature"] = "温柔体贴" # 默认性格
# 初始化会话标识
if "current_session" not in st.session_state:
    # 这里展示了不同于前面的调用方式，即current_session自动转为一个对象，可以被.直接调用
    st.session_state.current_session = generate_session_name()
st.text(f"会话名称：{st.session_state.current_session}")
# 展示聊天记录
for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])
# 创建与AI大模型交互的客户端对象
client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com")
# 左侧的侧边栏 - with: streamlit中的上下文管理器
with st.sidebar:
    # 会话信息
    st.subheader("AI控制面板")
    # 新建会话
    if st.button("新建会话",width = "stretch",icon = "✏️"):
        # 1.保存当前会话信息
        save_session()
        # 2.创建一个新的对话
        if st.session_state.messages :
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun() # 重新运行当前界面（因为streamlit的界面在交互时会先刷新再执行后续逻辑，因此如果不手动再调用st.rerun，那么页面聊天信息不会重置）
    # 会话历史
    st.text("会话历史")
    session_list = load_all_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        # 加载会话信息
        with col1:
            if st.button(session,width = "stretch",icon = "📄",type = "primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        # 删除会话信息
        with col2:
            if st.button("",width = "stretch",icon = "❌️",key = f"delete_{session}"):
                delete_session(session)
                st.rerun()
    #分割线
    st.divider()
    st.subheader("伴侣信息")
    # 昵称输入框
    nick_name = st.text_input("昵称",placeholder = "请输入伴侣的昵称",value = st.session_state["nick_name"] )
    if nick_name is not None:
        st.session_state["nick_name"] = nick_name
    # 性格输入框
    nature = st.text_area("性格",placeholder = "请输入伴侣的性格" ,value = st.session_state["nature"])
    if nature is not None:
        st.session_state["nature"] = nature
# 聊天输入框
prompt = st.chat_input("Try to say something ~~~")
if prompt: # 这里会自动将字符串转为布尔值，如果prompt不为空，那么prompt就是True，否则prompt就是False
    st.chat_message("user").write(prompt)
    print("-------------->调用AI大模型，提示词：",prompt) # 日志，方便我们进行调试（输出在终端而非网页上）
    # 保存用户输入的提示词
    st.session_state["messages"].append({"role": "user", "content": prompt})
    # 调用AI大模型，提示词：Try to say something ~~~
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state["nick_name"], st.session_state["nature"])},
            # 将用户输入的提示词和之前的聊天记录一起发送给AI大模型,滚雪球，使其具有记忆功能
            *st.session_state["messages"],
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    # # 输出AI大模型的回复（非流式输出）
    # print("<--------------AI大模型的回复：",response.choices[0].message.content) # 日志
    # st.chat_message("assistant").write(response.choices[0].message.content)
    # 保存AI大模型的回复（非流式输出）
    # st.session_state["messages"].append({"role": "assistant", "content": response.choices[0].message.content})

    # # 输出AI大模型的回复（流式输出）
    response_message = st.empty() # 创建一个空的容器作为占位符，用于显示AI大模型的回复,防止其出现多次输出，以实现打字机流式效果
    full_response = ""
    for chunk in response: # response确实是一个类的实例化对象，但这个类的实例化对象是一个流式输出的迭代器，所以我们可以直接使用for循环来遍历这个流式输出的迭代器，本质上是data分片（对象的一部分）
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)
    print("<--------------AI大模型的回复：",full_response) # 日志
    st.session_state["messages"].append({"role": "assistant", "content": full_response})
    # 保存会话信息，确保会话信息在AI大模型回复后自动保存到文件中，而不是必须要手动创建新会话后才会保存
    save_session()






