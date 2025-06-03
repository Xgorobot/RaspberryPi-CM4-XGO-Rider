import time
from src.iot.thing import Thing, Parameter, ValueType
from xgolib import XGO


class Rider(Thing):
    def __init__(self):
        # 调用父类初始化方法，设置设备名称和描述
        # 第一个参数是设备ID(全局唯一)，第二个参数是对设备的描述文本
        super().__init__("MychanicalRider", "双轮足rider")

        # 双轮足状态变量定义
        self.rider = XGO("xgorider")

        self.direction = 'stop'  # 定义双轮足的移动方向，初始为停止
        self.speed = 0  # 定义双轮足的移动速度，初始为0
        self.move_time = 0  # 移动时间


        self.action = False   #xgo的自定义动作,初始为无动作
        self.perform = False  #xgo的表演模式


        self.turn_direction = 'stop'
        self.turn_time = 0 #转动时间
        self.turn_speed = 0 #转动速度


        self.last_update_time = 0  # 记录最后一次状态更新的时间戳

        self.height = 0

        self.is_balance = 1

        self.is_led_1 = False
        self.is_led_2 = False
        self.is_led_3 = False
        self.is_led_4 = False
        self.led_color_1_R = 0
        self.led_color_1_G = 0
        self.led_color_1_B = 0
        self.led_color_1 = [0,0,0]
        self.led_color_2_R = 0
        self.led_color_2_G = 0
        self.led_color_2_B = 0
        self.led_color_2 = [0, 0, 0]
        self.led_color_3_R = 0
        self.led_color_3_G = 0
        self.led_color_3_B = 0
        self.led_color_3 = [0, 0, 0]
        self.led_color_4_R = 0
        self.led_color_4_G = 0
        self.led_color_4_B = 0
        self.led_color_4 = [0, 0, 0]


        self.roll = 0

        self.periodic_z = 0
        self.periodic_z_time = 0

        self.periodic_roll = 0
        self.periodic_roll_time = 0

        self.reset = False

        # =========================
        # 注册设备属性（状态值）
        # =========================
        self.add_property("direction", "双轮足的移动方向(forward, backward)",
                          lambda: self.direction)
        self.add_property("speed", "双轮足的移动速度,向前移动为正，向后移动为负，取值范围为[-1.5,1.5]",
                          lambda: self.speed)
        self.add_property("move_time", "双轮足的移动时间",
                          lambda: self.move_time)

        self.add_property("last_update_time", "最后一次状态更新时间",
                          lambda: self.last_update_time)

        self.add_property("turn_speed", "双轮足的转动速度,向左转为正，向右转为负，取值范围是[-360,360]",
                          lambda: self.turn_speed)
        self.add_property("turn_direction", "双轮足的转动方向(left, right)",
                          lambda: self.turn_direction)
        self.add_property("turn_time", "双轮足的转动时间",
                          lambda: self.turn_time)

        self.add_property("action", "双轮足的预设动作包括'左右摇摆','高低起伏','前进后退','四方蛇形','升降旋转','圆周晃动'",
                          lambda: self.action)

   
        self.add_property("perform", "双轮足的表演模式是否开启",
                          lambda: self.perform)


        self.add_property("led_index_1", "双轮足背面的左上灯是否打开",
                          lambda: self.is_led_1)
        self.add_property("led_index_2", "双轮足背面的左下灯是否打开",
                          lambda: self.is_led_2)
        self.add_property("led_index_3", "双轮足背面的右下灯是否打开",
                          lambda: self.is_led_3)
        self.add_property("led_index_4", "双轮足背面的右上灯是否打开",
                          lambda: self.is_led_4)
        self.add_property("led_color_1_R", "双轮足的左上灯光颜色，代表RGB的亮度中的R，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_1_R)
        self.add_property("led_color_1_G", "双轮足的左上灯光颜色，代表RGB的亮度中的G，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_1_G)
        self.add_property("led_color_1_B", "双轮足的左上灯光颜色，代表RGB的亮度中的B，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_1_B)
        self.add_property("led_color_2_R", "双轮足的左下灯光颜色，代表RGB的亮度中的R，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_2_R)
        self.add_property("led_color_2_G", "双轮足的左下灯光颜色，代表RGB的亮度中的G，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_2_G)
        self.add_property("led_color_2_B", "双轮足的左下灯光颜色，代表RGB的亮度中的B，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_2_B)
        self.add_property("led_color_3_R", "双轮足的右下灯光颜色，代表RGB的亮度中的R，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_3_R)
        self.add_property("led_color_3_G", "双轮足的右下灯光颜色，代表RGB的亮度中的G，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_3_G)
        self.add_property("led_color_3_B", "双轮足的右下灯光颜色，代表RGB的亮度中的B，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_3_B)
        self.add_property("led_color_4_R", "双轮足的右上灯光颜色，代表RGB的亮度中的R，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_4_R)
        self.add_property("led_color_4_G", "双轮足的右上灯光颜色，代表RGB的亮度中的G，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_4_G)
        self.add_property("led_color_4_B", "双轮足的右上灯光颜色，代表RGB的亮度中的B，RGB为[0,0,0]代表灭，[255,255,255]代表最亮的白光",
                          lambda: self.led_color_4_B)


        self.add_property("height", "双轮足的高度取值范围是[60,120]",
                          lambda: self.height)

        self.add_property("roll", "双轮足的机身姿态调节幅度,单位为°,取值范围为[-17,17]",
                          lambda: self.roll)


        self.add_property("periodic_z", "双轮足的机身周期蹲起的周期（反映了周期蹲起的速率），单位s,取值范围[2,4];输入0代表停止运动",
                          lambda: self.periodic_z)
        self.add_property("periodic_z_time", "双轮足的机身周期蹲起的持续时间",
                          lambda: self.periodic_z_time)

        self.add_property("periodic_roll", "双轮足的机身周期晃动周期（反映了周期晃动的速率），单位s,取值范围[2,4];输入0代表停止运动",
                          lambda: self.periodic_roll)
        self.add_property("periodic_roll_time", "双轮足的机身周期晃动的持续时间",
                          lambda: self.periodic_roll_time)

        self.add_property("reset", "双轮足停止所有运动，所有状态全部恢复到初始状态，如果是倒地状态，调用该方法后会站起",
                          lambda: self.reset)

        self.add_property("is_balance", "是否开启双轮足平衡模式，自稳状态下，轮足将自动调节Roll以保持背部处于水平位置。",
                          lambda: self.is_balance)

        # =========================
        # 注册设备方法（可执行的操作）
        # =========================

        self.add_method(
            "MoveForward",
            "让双轮足向前移动",
            [
                Parameter("speed", "移动速度(0-1.5之间的数字)", ValueType.NUMBER, True),
                Parameter("move_time", "移动时间单位秒", ValueType.NUMBER, True)
            ],
            lambda params: self._move_forward(params["speed"].get_value(), params['move_time'].get_value())
        )

        self.add_method(
            "MoveBackward",
            "让双轮足向后移动",
            [
                Parameter("speed", "移动速度(0-1.5之间的数字)", ValueType.NUMBER, True),
                Parameter("move_time", "移动时间单位秒", ValueType.NUMBER, True)
            ],
            lambda params: self._move_backward(params["speed"].get_value(), params['move_time'].get_value())
        )

        self.add_method(
            "Turnright",
            "让双轮足右转",
            [
                Parameter('turn_speed', "转动速度(0-360之间的数字)单位度/秒", ValueType.NUMBER, True),
                Parameter("turn_time", "移动时间单位秒", ValueType.NUMBER, True)
            ],
            lambda params: self._turn_right(params["turn_speed"].get_value(), params["turn_time"].get_value())
        )

        self.add_method(
            "Turnleft",
            "让双轮足左转",
            [
                Parameter('turn_speed', "转动速度(0-360之间的数字)单位度/秒", ValueType.NUMBER, True),
                Parameter("turn_time", "移动时间单位秒", ValueType.NUMBER, True)
            ],
            lambda params: self._turn_left(params["turn_speed"].get_value(), params["turn_time"].get_value())
        )

        self.add_method(
            "action",
            "双轮足执行预设动作",
            [
                Parameter('action',
             '取值范围为1-6,分别对应[左右摇摆, 高低起伏, 前进后退, 四方蛇形, 升降旋转, 圆周晃动 ]。',
             ValueType.NUMBER,
             True)
            ],
            lambda params: self._action(params["action"].get_value())
        )

        self.add_method(
            "perform",
            "双轮足的表演模式",
            [
                Parameter('perform', '0代表关闭、1代表开启', ValueType.NUMBER, True)
            ],
            lambda params: self._perform(params["perform"].get_value())
        )

        self.add_method(
            "led_1",
            "双轮足机器人的左上灯颜色",
            [
                Parameter('R', 'RGB颜色中R的亮度取值为[0，255]', ValueType.NUMBER, True),
                Parameter('G', 'RGB颜色中G的亮度取值为[0，255]', ValueType.NUMBER, True),
                Parameter('B', 'RGB颜色中B的亮度取值为[0，255]', ValueType.NUMBER, True)
            ],
            lambda params: self._led_1(params["R"].get_value(), params["G"].get_value(), params["B"].get_value())
        )

        self.add_method(
            "led_2",
            "双轮足机器人的左下灯颜色",
            [
                Parameter('R', 'RGB颜色中R的亮度取值为[0，255]', ValueType.NUMBER, True),
                Parameter('G', 'RGB颜色中G的亮度取值为[0，255]', ValueType.NUMBER, True),
                Parameter('B', 'RGB颜色中B的亮度取值为[0，255]', ValueType.NUMBER, True)
            ],
            lambda params: self._led_2(params["R"].get_value(), params["G"].get_value(), params["B"].get_value())
        )

        self.add_method(
            "led_3",
            "双轮足机器人的右下灯颜色",
            [
                Parameter('R', 'RGB颜色中R的亮度取值为[0，255]', ValueType.NUMBER, True),
                Parameter('G', 'RGB颜色中G的亮度取值为[0，255]', ValueType.NUMBER, True),
                Parameter('B', 'RGB颜色中B的亮度取值为[0，255]', ValueType.NUMBER, True)
            ],
            lambda params: self._led_3(params["R"].get_value(), params["G"].get_value(), params["B"].get_value())
        )

        self.add_method(
            "led_4",
            "双轮足机器人的右上灯颜色",
            [
                Parameter('R', 'RGB颜色中R的亮度取值为[0，255]', ValueType.NUMBER, True),
                Parameter('G', 'RGB颜色中G的亮度取值为[0，255]', ValueType.NUMBER, True),
                Parameter('B', 'RGB颜色中B的亮度取值为[0，255]', ValueType.NUMBER, True)
            ],
            lambda params: self._led_4(params["R"].get_value(), params["G"].get_value(), params["B"].get_value())
        )

        self.add_method(
            "balance",
            "双轮足平衡模式是否开启，自稳状态下，轮足将自动调节Roll以保持背部处于水平位置",
            [
                Parameter('mode', '取值为0或1, 1表示开启, 0表示关闭', ValueType.NUMBER, True)
            ],
            lambda params: self._balance(params["mode"].get_value())
        )

        self.add_method(
            "height",
            "表示双轮足的高度",
            [
                Parameter('data', '表示双轮足的高度，取值范围是[60,120]', ValueType.NUMBER, True)
            ],
            lambda params: self._height(params["data"].get_value())
        )

        self.add_method(
            "roll",
            "表示机身姿态调整",
            [
                Parameter('data', '代表机身姿态调节幅度，单位为°,取值范围为[-17,17]', ValueType.NUMBER, True)
            ],
            lambda params: self._roll(params["data"].get_value())
        )

        self.add_method(
            "periodic_z",
            "表示机身周期蹲起",
            [
                Parameter('data', '双轮足的机身周期蹲起的周期（反映了周期蹲起的速率），单位s,取值范围[2,4];输入0代表停止运动', ValueType.NUMBER, True),
                Parameter('time','双轮足的机身周期蹲起的持续时间',ValueType.NUMBER, True)
            ],
            lambda params: self._periodic_z(params["data"].get_value(), params["time"].get_value())
        )

        self.add_method(
            "periodic_roll",
            "表示机身周期晃动",
            [
                Parameter('data', '双轮足的机身周期晃动的周期（反映了周期晃动的速率），单位s,取值范围[2,4];输入0代表停止运动', ValueType.NUMBER, True),
                Parameter('time', '双轮足的机身周期晃动的持续时间', ValueType.NUMBER, True)
            ],
            lambda params: self._periodic_roll(params["data"].get_value(), params["time"].get_value())
        )

        self.add_method(
            "reset",
            "表示停止所有运动，所有状态全部恢复到初始状态，如果是倒地状态，调用该方法后会站起",
            [],
            lambda params: self._reset()
        )

    # =========================
    # 内部方法实现（实际功能）
    # =========================

    def _move_forward(self, speed, move_time):
        self.speed = speed
        self.last_update_time = int(time.time())
        self.direction = 'forward'
        self.move_time = move_time
        self.rider.rider_move_x(self.speed, self.move_time)
        return {
            "status": "success",
            "message": f"双轮足机器人以速度{self.speed}向前移动了{self.move_time}秒"
        }
    def _move_backward(self, speed, move_time):
        self.speed = speed
        self.last_update_time = int(time.time())
        self.direction = 'backward'
        self.move_time = move_time
        self.move_time = move_time
        self.rider.rider_move_x(-self.speed, self.move_time)
        return {
            "status": "success",
            "message": f"双轮足机器人以速度 {self.speed} 向后移动{self.move_time}秒"
        }
    def _turn_right(self, turn_speed, turn_time):
        self.turn = 'right'
        self.turn_speed = turn_speed
        self.turn_time = turn_time
        self.last_update_time = int(time.time())
        self.rider.rider_turn(-self.turn_speed, self.turn_time)
        return {
            "status": "success",
            "message": f"双轮足机器人以速度{self.turn_speed}向右转{self.turn_time}秒"
        }
    def _turn_left(self, turn_speed, turn_time):
        self.is_turn = True
        self.turn = 'left'
        self.turn_speed = turn_speed
        self.last_update_time = int(time.time())
        self.turn_time = turn_time
        self.rider.rider_turn(self.turn_speed, self.turn_time)
        return {
            "status": "success",
            "message": f"双轮足机器人以速度 {self.turn_speed} 向左转{self.turn_time}秒"
        }
    def _action(self, action):
        self.last_update_time = int(time.time())
        time_list = [3, 4, 3, 4, 6, 5]
        action_list = ['左右摇摆', '高低起伏', '前进后退', '四方蛇形', '升降旋转', '圆周晃动']
        self.action = action_list[action-1]
        self.rider.rider_action(action)
        time.sleep(time_list[action-1])
        self.rider.rider_reset()

        return {
            "status": "success",
            "message": f"双轮足机器人已经完成预设动作{self.action}"
        }

    def _perform(self, perform):
        perform_list = [False, True]
        self.perform = perform_list[perform]
        self.rider.rider_perform(perform)
        time.sleep(10)
        self.rider.rider_reset()
        return {
            "status": "success",
            "message": "双轮足机器人已经表演完成"
        }

    def _led_1(self, R, G, B):
        self.is_lcd_1 = True
        self.led_color_1_R = R
        self.led_color_1_G = G
        self.led_color_1_B = B
        self.led_color_1 = [R, G, B]

        if self.led_color_1 == [0, 0, 0]:
            self.is_lcd_1 = False
        self.rider.rider_led(1,self.led_color_1)

        return {
            "status": "success",
            "message":f"双轮足机器人的左上灯的颜色已经调整为{self.led_color_1}"
        }

    def _led_2(self, R, G, B):
        self.is_lcd_2 = True
        self.led_color_2_R = R
        self.led_color_2_G = G
        self.led_color_2_B = B
        self.led_color_2 = [R, G, B]
        if self.led_color_2 == [0, 0, 0]:
            self.is_lcd_2 = False
        self.rider.rider_led(2,self.led_color_2)

        return {
            "status": "success",
            "message":f"双轮足机器人的左下灯的颜色已经调整为{self.led_color_2}"
        }
    def _led_3(self, R, G, B):
        self.is_lcd_3 = True
        self.led_color_3_R = R
        self.led_color_3_G = G
        self.led_color_3_B = B
        self.led_color_3 = [R, G, B]
        if self.led_color_3 == [0, 0, 0]:
            self.is_lcd_3 = False
        self.rider.rider_led(3,self.led_color_3)

        return {
            "status": "success",
            "message":f"双轮足机器人的右下灯的颜色已经调整为{self.led_color_3}"
        }
    def _led_4(self, R, G, B):
        self.is_lcd_4 = True
        self.led_color_4_R = R
        self.led_color_4_G = G
        self.led_color_4_B = B
        self.led_color_4 = [R, G, B]
        if self.led_color_4 == [0, 0, 0]:
            self.is_lcd_4 = False
        self.rider.rider_led(4,self.led_color_4)

        return {
            "status": "success",
            "message":f"双轮足机器人的右上灯的颜色已经调整为{self.led_color_4}"
        }

    def _balance(self, mode):
        if mode == 1:
            self.is_balance = True
        else:
            self.is_balance = False
        self.rider.rider_balance_roll(mode)

        return {
            "status": "success",
            "message": f"双轮足机器人是否开启平衡模式：{self.is_balance}"
        }

    def _height(self, data):
        self.height = data
        self.rider.rider_height(self.height)

        return {
            "status": "success",
            "message": f"双轮足机器人的高度{self.height}"
        }

    def _roll(self, data):
        self.roll = data
        self.rider.rider_roll(self.roll)

        return {
            "status": "success",
            "message": f"双轮足机器人的机身姿态幅度{self.roll}"
        }

    def _periodic_z(self, data, time):
        self.periodic_z = data
        self.periodic_z_time = time
        self.rider.rider_periodic_z(self.periodic_z)
        time.sleep(self.periodic_z_time)
        self.rider.rider_periodic_z(0)

        return {
            "status": "success",
            "message": f"双轮足机器人以蹲起周期{self.periodic_z}持续{self.periodic_z_time}"
        }

    def _periodic_roll(self, data, time):
        self.periodic_roll = data
        self.periodic_roll_time = time
        self.rider.rider_periodic_roll(self.periodic_roll)
        time.sleep(self.periodic_roll_time)
        self.rider.rider_periodic_roll(0)

        return {
            "status": "success",
            "message": f"双轮足机器人以晃动周期{self.periodic_z}持续{self.periodic_z_time}"
        }


    def _reset(self):
        self.rider.rider_reset()
        return {
            "status": "success",
            "message": f"双轮足机器人已完成初始化"
        }