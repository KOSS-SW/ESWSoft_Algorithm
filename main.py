# -*- coding: utf-8 -*-

from MODULES.Camera.camera import Cam
from MODULES.Camera import calculate
from MODULES.Motion.robot import Bot

import logging
import time

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

logger.info("main intializing")
cam = Cam(True)
bot = Bot()
logger.info("bot True")

# 상태 변수 정의
head_lefted = False
is_turning = 0
walk_count = 3
head_position = "up"  # 현재 머리 높이 위치 ("up", "center", "down")


while True:
    if bot.task == "ball":
        logger.info("ball is start")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()

        if is_ball:
            # 공이 중앙에 오도록 조정
            is_ball_center = cam.ball_is_center(bc)
            if not is_ball_center:
                if head_lefted:
                    bot.left_10()
                else:
                    bot.right_10()
                time.sleep(0.2)
            else:
                # 공이 중앙에 오면 전진하며 접근
                bot.go()
                time.sleep(0.2)
                
                # 공과의 거리 확인
                h, b, f = cam.read()
                is_ball, bc = cam.detect_ball()
                if is_ball:
                    is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
                    if is_hitable_X and is_hitable_Y:
                        bot.task2flag()  # 공에 충분히 가까워지면 깃발 탐색으로 전환
        else:
            # 체계적인 공 탐색 패턴
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_position == "up":
                    # 위쪽에서 좌우 탐색
                    if head_lefted:
                        bot.head_right_max()
                        head_lefted = False
                    else:
                        bot.head_left_max()
                        head_lefted = True
                        head_position = "center"  # 다음은 중앙 높이로
                elif head_position == "center":
                    # 중앙 높이에서 좌우 탐색
                    if head_lefted:
                        bot.head_right_max()
                        bot.head_center()
                        head_lefted = False
                    else:
                        bot.head_left_max()
                        bot.head_center()
                        head_lefted = True
                        head_position = "down"  # 다음은 아래쪽으로
                else:  # head_position == "down"
                    # 아래쪽에서 좌우 탐색
                    if head_lefted:
                        bot.head_right_max()
                        bot.head_down_75()
                        head_lefted = False
                    else:
                        bot.head_left_max()
                        bot.head_down_75()
                        head_lefted = True
                        head_position = "up"  # 다시 위쪽으로
                        bot.head_up()  # 다음 사이클을 위해 머리를 위로
                
                is_turning = time.time()
                time.sleep(0.3)  # 안정화 대기

    elif bot.task == "flag":
        logger.info("flag is start")
        # 고개를 들어 깃발 탐색
        bot.head_up()
        time.sleep(0.2)
        
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()

        if is_flag:
            # 깃발이 보이면 바로 준비 상태로 전환
            bot.head_center()
            time.sleep(0.2)
            bot.task2ready()
        else:
            # 깃발이 안 보이면 천천히 고개를 움직이며 탐색
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right()
                    time.sleep(0.3)
                else:
                    bot.head_left()
                    time.sleep(0.3)
                head_lefted = not head_lefted
                is_turning = time.time()

    elif bot.task == "ready":
        logger.info("ready is start")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()

        if not is_ball:
            bot.task2ball()
            continue

        # 공과 로봇의 위치 확인
        is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
        
        if is_hitable_X and is_hitable_Y:
            # 적절한 위치에 있으면 바로 퍼팅 준비
            bot.task2hit()
        else:
            # 위치 조정 필요
            if not is_hitable_X:
                bot.ready_x(x)
                time.sleep(0.2)
            if not is_hitable_Y:
                bot.ready_y(y)
                time.sleep(0.2)

    elif bot.task == "hit":
        logger.info("hit is start")
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()
        
        if is_flag:
            # 깃발까지의 거리를 계산하여 퍼팅
            distance = cam.flag_distance(bot.head_angle())
            time.sleep(0.3)

            # 거리에 따른 퍼팅
            bot.hit(True)  # 오른쪽으로 퍼팅
            time.sleep(1)
            bot.task2ball()  # 다음 공 찾기로 전환
        else:
            # 깃발이 안 보이면 재탐색
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right()
                else:
                    bot.head_left()
                head_lefted = not head_lefted
                is_turning = time.time()