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


#log를 파일에 출력
file_handler = logging.FileHandler("my.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("main intializing")
cam = Cam(True)
bot = Bot()
logger.info("bot True")

head_lefted = False
is_turning = 0
searched = False
walk_count = 3
turning_time = 0
head_left = 0
head_right = 0
flag_pass = False
hit = False

while True:
    if bot.task == "ball":
        logging.info("ball is start")
        h,b,f = cam.read()
        is_ball, bc = cam.detect_ball()
        if is_ball:
            bot.head_center()
            if searched:
                if head_lefted:
                    bot.body_left_45()
                else:
                    bot.body_right_45()
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
        else: # 공이 시야에 없을 때
            # print("no ball is on cam")
            if is_turning == 0 or abs(time.time()-is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
                searched = True
            else:
                pass
    elif bot.task == "walk": # 공이 중앙에 왔다는 가정 하
        logging.info("walk is start")
        bot.go()
        # time.sleep(3)
        h,b,f = cam.read()
        is_ball, bc = cam.detect_ball()
        if is_ball:
            if cam.ball_is_center_h(bc):
                bot.stop()
                bot.task2flag()
            elif walk_count == 0:
                bot.task2ball()
                walk_count = 3
            else:
                walk_count -= 1
        else:
            if walk_count == 0:
                bot.task2ball()
                walk_count = 3
            else:
                walk_count -= 1
            # print(walk_count)
        continue
    elif bot.task == "flag":
        logging.info("flag is start")
        h,b,f = cam.read()
        is_flag, fc = cam.detect_flag()
        # 깃발 찾기
        if is_flag:
            bot.head_center()
            if searched:
                if head_lefted:
                    bot.left_10()
                    bot.left_10()
                    bot.body_left_45()
                else:
                    bot.right_10()
                    bot.right_10()
                    bot.body_right_45()
                searched = False
            is_flag_center = cam.flag_is_center(bc)
            if not is_flag_center:
                if cam.flag_left(bc):
                    bot.left_10()
                    bot.body_left_10()
                else:
                    bot.right_10()
                    bot.body_right_10()
            else:
                bot.task2ready()
                pass
        else: # 공이 시야에 없을 때
            # print("no ball is on cam")
            if is_turning == 0 or abs(time.time()-is_turning) > 1:
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
        logging.info("ready is start")
        h,b,f = cam.read()
        is_ball, bc = cam.detect_ball()
        if not is_ball:
            bot.task2ball()
            continue
        is_hitable, [x, y] = cam.ball_hitable(bc)
        if is_hitable:
            if hit:
                bot.task2hit()
            else:
                bot.move_left() # 11cm
                bot.body_left_45() # 90도
                bot.move_left() # 11cm
                hit = True
        else:
            # x좌표 조정
            if x < 0:
                bot.move_left()
            else:
                bot.move_right()
            # y좌표 조정
            if y < 0:
                bot.go()
            else:
                bot.back()
            # 90도 회전
            
        pass
    elif bot.task == "hit":
        logging.info("hit is start")
        h,b,f = cam.read()
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

        else:
            if is_turning == 0 or abs(time.time()-is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
            else:
                pass
        pass
