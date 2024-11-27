from MODULES.Camera.camera import Cam
from MODULES.Camera import calculate
from MODULES.Motion.robot import Bot

import logging
import time
import sys

startTime = time.time()

logger = logging.getLogger("[mainLogger]")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# log를 console에 출력
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


# log를 파일에 출력
file_handler = logging.FileHandler("./logs/my.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 상태 변수 정의
head_lefted = False
is_turning = 0
searched = False
walk_count = 3
head_left = 0
head_right = 0
flag_pass = False
hit = False
hit_right = True
checkIn = False
set90 = 0
par4 = False

logger.info("main intializing")
bot = Bot()
cam = Cam(True)
logger.info("bot True")

if __name__ == "__main__":
    print(sys.argv)
    if 'par4' in sys.argv:
        par4 = True
        print("par4 is True")
    if 'down' in sys.argv:
        # bot.head_down_65()
        bot.head_down_35()
        # time.sleep(.3)

### for test ###
bot.task2flag()
bot.hitting = 1
Cam.hsv_Upper_flag = (255, 105, 161)
###
while True:
    cam.read()
    if 1 in bot.waiting:
        break

while True:
    if bot.task == "flag":
        logger.info("flag is start")
        time.sleep(0.2)  # 안정화 대기 시간
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag(True, bot.hitting == 0)
        logger.debug(f"is_flag in flag: {is_flag}, {fc}")

        if is_flag:
            bot.head_center()
            time.sleep(1)
            logger.debug("turning 90")
            if searched:
                # 회전 동작 최적화
                if not head_lefted:
                    bot.body_right_90()
                searched = False
                head_left = False
            else:
                if (cam.flag_turnable(fc) and cam.flag_left(fc) ) or bot.hitting < 1:
                    head_left = False
                    bot.body_right_90()
            logger.info("test is done")
            break
        else:  # 깃발이 시야에 없을 때 탐색
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                # 머리 회전 각도를 단계적으로 증가
                if head_lefted:
                    bot.head_right_middle()  # 중간 각도로 추가 확인
                    time.sleep(0.2)
                    cam.read()
                    is_flag, fc = cam.detect_flag()
                    if not is_flag:
                        bot.head_right_max()
                else:
                    bot.head_left_middle()  # 중간 각도로 추가 확인
                    time.sleep(0.2)
                    cam.read()
                    is_flag, fc = cam.detect_flag()
                    if not is_flag:
                        bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
                searched = True
                time.sleep(.5)

while True:
    cam.read()
print((time.time() - startTime))