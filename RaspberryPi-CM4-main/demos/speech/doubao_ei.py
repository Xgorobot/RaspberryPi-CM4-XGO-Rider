import os
import ast
from typing import List
from volcenginesdkarkruntime import Ark

API_KEY = '67e1719b-fc92-43b7-979d-3692135428a4'
MODEL_NAME = "doubao-1.5-pro-32k-250115"


def get_model_response(client: Ark, prompt: str) -> List[int]:
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    result = ast.literal_eval(completion.choices[0].message.content)
    print(f"模型返回结果: {result}, 类型: {type(result)}")
    return result

def model_output(content: str) -> List[int]:
    system_prompt = """
    我接下来会给你一段话，如果有退出，停止等意思，请返回字符'退出'，如果指令存在不符合下面要求或无法理解请返回'重试',请根据以下规则对其进行处理，并以列表形式返回结果。列表格式为：  
        `[['move', [step, time]], ['turn', [yaw, time]], ...]`，同一列表中元素必须成对出现的，即运动名字和运动参数同时必须出现，各元素的含义如下：  
        1. name:'move'：表示前后移动。  
           - [speed,time] speed为正时，表示向前移动的速度,为负时，表示向后移动的速度，speed的取值范围是[-1.5,1.5]。time表示移动的时间
        2. name:'turn'：表示旋转。  
           - [speed,time] speed为正时表示逆时针旋转的速度,为负时表示顺时针旋转的速度，speed的取值范围是[-360,360]。time表示移动的时间
        3. name:'balance'：表示双轮足平衡模式，自稳状态下，轮足将自动调节Roll以保持背部处于水平位置。
           - id, 取值为0或1, 1表示开启, 0表示关闭。
        4. name:'led':表示双轮足四个灯光的显示
           - [index,uint8, uint8, uint8]:index的取值为1-4，分别表示左上，左下，右下，右上的四个灯, [uint8, uint8, uint8], 需要三个数据，代表RGB的亮度，[0,0,0]代表灭，[255,255,255]代表最亮的白光
        5. name:'height':表示双轮足的高度
           - data, 表示双轮足的高度，取值范围是[60,120]
        6. name:'roll':表示机身姿态调整
           - data, 该参数代表机身姿态调节幅度，单位为°,取值范围为[-17,17]
        7. name:'periodic_z':表示机身周期蹲起
           - [data, time] data代表运动频率，取值范围为[2,4];输入0代表停止运动。time表示持续时间
        8. name:'periodic_roll':表示机身周期晃动
           - [data, time], 该参数代表运动频率，取值范围为[2,4];输入0代表停止运动。time表示持续时间
        9. name:'reset'
           - mode,取值为0,表示停止所有运动，所有状态全部恢复到初始状态，如果是倒地状态，调用该方法后会站起。。          
        10. name:'action':执行预设动作
           - id,'左右摇摆','高低起伏','前进后退','四方蛇形','升降旋转','圆周晃动'。        
        11. name:'perform':表演模式，机器狗将循环执行预设的动作。
           - mode, 取值为0或者1，0代表关闭表演模式，1表示打开表演模式。         
       **默认值规则**：  
        - 如果未指定移动速度，默认移动速度为 `1`或'-1'。  
        - 如果未指定转动速度，默认转动速度为 `30`或'-30'。
        - 如果未指定移动或转动时间，默认时间为 3
        - 如有谐音的命令可自行理解
       name是指方法名字，后面是需要传入的参数以及参数规则,多个参数时需要以列表形式给出,两者必须同时出现，如果参数未明确给出，可使用默认值或者其他值,如果只需要传入一个参数，参数不需要以列表形式给出
       返回结果以'['作为开始，以']'作为结束,下面我将给出几个例子
       蹲起3秒，晃动2秒，然后将左下灯调为红色，然后退出，应返回[['periodic_z',[2, 3]],['periodic_roll',[2, 2]],['lcd', [2, 255, 0, 0]],['退出']]
       左转90度 应返回[['turn',[30,3]]]
       表演，应返回[['perform', 1]]
       请严格按照上述规则处理输入内容，并返回结果列表。
          """
    client = Ark(api_key=API_KEY)
    
    result = get_model_response(client, system_prompt + content)

    return result
