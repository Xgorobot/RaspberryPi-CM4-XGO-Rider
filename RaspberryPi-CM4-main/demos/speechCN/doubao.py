import ast
from typing import List
from volcenginesdkarkruntime import Ark

# 常量定义
API_KEY = '67e1719b-fc92-43b7-979d-3692135428a4'
MODEL_NAME = "doubao-1.5-pro-32k-250115"

# 动作顺序定义
ACTION_ORDER = [
    "左右摇摆",  # LeftRight
    "高低起伏",  # UpDown
    "前进后退",  # GoBack
    "四方蛇形",  # Square
    "升降旋转",  # LiftRotate
    "圆周晃动"   # Swaying
]

def model_output(content: str) -> List[int]:
    """使用豆包大语言模型分析文本并返回动作列表
    
    Args:
        content: 待分析的文本内容
        
    Returns:
        包含6个动作状态的列表，1表示执行，0表示不执行
    """
    # 初始化客户端（单次初始化）
    client = Ark(api_key=API_KEY)
    
    # 构建系统提示词
    prompt = f"""
    请将以下描述转换为动作列表，格式为{ACTION_ORDER}，
    执行动作为1，否则为0。
    输入内容：{content}
    """
    
    # 创建对话请求
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    
    # 解析结果
    result = ast.literal_eval(completion.choices[0].message.content)
    print(f"模型返回结果: {result}, 类型: {type(result)}")
    
    # 验证结果长度
    if len(result) != len(ACTION_ORDER):
        raise ValueError(f"返回结果长度应为{len(ACTION_ORDER)}，实际为{len(result)}")
    
    return result