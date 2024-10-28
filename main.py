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

head_lefted = False  # 탐지 과정에서 머리가 왼쪽으로
is_turning = 0  # 가장 최근 머리 회전 시간
searched = False  # 화면에 탐지 대상이 없어 회전한 적이 있는가
walk_count = 3  # 걷기 횟수
head_left = 0  # 탐지 과정에서 머리를 왼쪽으로 돌린 횟수
head_right = 0  # 탐지 과정에서 머리를 오른쪽으로 돌린 횟수
flag_pass = False  # 깃발 탐지 과정을 건너 뛸 것인가
hit = False  # 치기 과정으로 넘어갈 것인가
hit_right = True  # 오른쪽으로 치는가

while True:
    if bot.task == "ball":
        logger.info("ball is start")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        if is_ball:
            bot.head_center()
            if searched:
                if head_lefted:
                    bot.body_left_30()
                else:
                    bot.body_right_30()
                searched = False
            is_ball_center = cam.ball_is_center(bc)
            if not is_ball_center:
                if cam.ball_left(bc):
                    bot.left_10()
                else:
                    bot.right_10()
            else:
                bot.task2walk()
                pass
        else:  # 공이 시야에 없을 때
            # print("no ball is on cam")
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()  # 도리도리 방지 코드
                searched = True
            else:
                pass
    elif bot.task == "walk":  # 공이 중앙에 왔다는 가정 하
        logger.info("walk is start")
        # time.sleep(3)
        h, b, f = cam.read()
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        
        if is_ball:
            is_hitable, (x, y) = cam.ball_hitable(bc)
            if cam.ball_is_center_h(bc):
                # 세부 조정
                if is_hitable:
                    bot.task2flag()
                else:
                    bot.ready_x(x)
                    bot.ready_y(y)
                    time.sleep(0.1)
                    continue
            else:
                bot.go()
        else:
            bot.go()
        continue
    elif bot.task == "flag":
        logger.info("flag is start")
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()
        # 깃발 찾기
        if is_flag:
            bot.head_center()
            if searched:
                if not head_lefted:
                    bot.left_70()  # 공 안차도록 옆으로 간 뒤 회전
                    bot.left_70()
                    bot.left_70()
                    bot.left_70()
                    time.sleep(0.1)
                    bot.body_right_45()
                    bot.body_right_45()
                    bot.left_70()
                    bot.left_70()
                    bot.left_70()
                    bot.left_70()
                else:
                    bot.right_70()  # 공 안차도록 옆으로 간 뒤 회전
                    bot.right_70()
                    bot.right_70()
                    bot.right_70()
                    time.sleep(0.1)
                    bot.body_left_45()
                    bot.body_left_45()
                    bot.right_70()
                    bot.right_70()
                    bot.right_70()
                    bot.right_70()
                searched = False
                head_left = False
            is_flag_center = cam.flag_is_center(fc)
            if not is_flag_center:
                if not cam.flag_left(fc):
                    bot.body_right_20()
                    bot.left_20() # 공 안차도록 옆으로 간 뒤 회전
                    bot.left_20() # 공 안차도록 옆으로 간 뒤 회전
                    bot.left_20() # 공 안차도록 옆으로 간 뒤 회전
                    bot.left_10() # 공 안차도록 옆으로 간 뒤 회전
                    # bot.body_right_10()
                else:
                    bot.body_left_20()
                    bot.right_20() # 공 안차도록 옆으로 간 뒤 회전
                    bot.right_20() # 공 안차도록 옆으로 간 뒤 회전
                    bot.right_20() # 공 안차도록 옆으로 간 뒤 회전
                    bot.right_10() # 공 안차도록 옆으로 간 뒤 회전
                    # bot.body_left_10()
            else:
                bot.task2ready()
                pass
        else:  # 공이 시야에 없을 때
            # print("no ball is on cam")
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
                searched = True
            else:
                pass
    elif bot.task == "ready":
        logger.info("ready is start")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        if not is_ball:
            bot.task2ball()
            continue
        is_hitable, (x, y) = cam.ball_hitable(bc)
        if is_hitable:
            if hit:
                bot.task2hit()
            else:
                if hit_right:
                    bot.left_20()  # 11cm
                    bot.left_10()  # 11cm
                    bot.left_10()  # 11cm
                    bot.body_right_45()  # 90도
                    bot.body_right_45()  # 90도
                    bot.left_20()  # 11cm
                    bot.left_10()  # 11cm
                    bot.left_10()  # 11cm
                else:
                    bot.right_20()
                    bot.right_10()
                    bot.right_10()
                    bot.body_left_45()
                    bot.body_left_45()
                    bot.right_20()
                    bot.right_10()
                    bot.right_10()
                hit = True
        else:
            bot.ready_x(x)
            # y좌표 조정
            bot.ready_y(y)
            # 90도 회전

        pass
    elif bot.task == "hit":
        logger.info("hit is start")
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()
        if is_flag:
            distance = cam.flag_distance(bot.head_angle())

            # 퍼팅
            if (distance >= 0) and (distance <= 100):
                # 약
                bot.hit()
                power = 10
            elif (distance >= 100) and (distance <= 200):
                # 중
                bot.hit()
                power = 20
            else:
                # 강
                bot.hit()
                power = 30
            bot.task2ball()
        else:
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
            else:
                pass
        pass
