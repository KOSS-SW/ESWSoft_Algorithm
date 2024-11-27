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
    if 18 in bot.recived:
        bot.recived.remove(31)
    else:
        continue

    while True:
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag(True, bot.hitting == 0)
        logger.debug(f"is_flag in flag: {is_flag}, {fc}")
        if (cam.flag_turnable(fc) or not cam.flag_left(fc)) or bot.hitting < 1:
            head_left = False
            logger.info("test is done")
            logger.info("test is done")
            logger.info("test is done")
            logger.info("test is done")
            logger.info("test is done")
            logger.info("test is done")
            logger.info("test is done")
            logger.info("test is done")
            logger.info("test is done")
            logger.info("test is done")
            logger.info("test is done")
            break
    
print((time.time() - startTime))