# -*- coding: utf-8 -*-

from MODULES.Camera.camera import Cam
from MODULES.Camera import calculate
from MODULES.Motion.robot import Bot

import logging
import time

# 로깅 설정 부분은 동일하게 유지
logger = logging.getLogger("[mainLogger]")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler("./logs/my.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("main initializing")
cam = Cam(True)
bot = Bot()
logger.info("bot True")

# 상태 변수 정의
SEARCH_BALL = "search_ball"      # 공 찾기 상태
APPROACH_BALL = "approach_ball"  # 공에 접근하는 상태
SEARCH_FLAG = "search_flag"      # 깃발 찾기 상태
PUTTING = "putting"              # 퍼팅 상태

current_state = SEARCH_BALL
head_lefted = False
is_turning = 0

while True:
    if current_state == SEARCH_BALL:
        logger.info("Searching for ball")
        # 고개를 들어 공을 찾음
        bot.head_down_75()
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()

        if is_ball:
            logger.info("Ball found")
            current_state = APPROACH_BALL
            continue

        # 공이 보이지 않으면 좌우로 고개를 돌려가며 탐색
        if is_turning == 0 or abs(time.time() - is_turning) > 1:
            if head_lefted:
                bot.head_right_max()
            else:
                bot.head_left_max()
            head_lefted = not head_lefted
            is_turning = time.time()

    elif current_state == APPROACH_BALL:
        logger.info("Approaching ball")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()

        if not is_ball:
            current_state = SEARCH_BALL
            continue

        # 공이 중앙에 오도록 조정
        is_ball_center = cam.ball_is_center(bc)
        if not is_ball_center:
            if cam.ball_left(bc):
                bot.left_10()
            else:
                bot.right_10()
            time.sleep(0.1)
        else:
            # 공과의 거리 확인
            is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
            if is_hitable_X and is_hitable_Y:
                # 적절한 거리에 도달하면 깃발 탐색 시작
                current_state = SEARCH_FLAG
            else:
                # 아직 멀면 전진
                bot.go()
                time.sleep(0.2)

    elif current_state == SEARCH_FLAG:
        logger.info("Searching for flag")
        # 고개를 들어 깃발 탐색
        bot.head_up()
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()

        if is_flag:
            logger.info("Flag found")
            current_state = PUTTING
            continue

        # 깃발이 보이지 않으면 좌우로 고개를 돌려가며 탐색
        if is_turning == 0 or abs(time.time() - is_turning) > 1:
            if head_lefted:
                bot.head_right_max()
            else:
                bot.head_left_max()
            head_lefted = not head_lefted
            is_turning = time.time()

    elif current_state == PUTTING:
        logger.info("Preparing to putt")
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()
        
        if not is_flag:
            current_state = SEARCH_FLAG
            continue

        # 깃발까지의 거리 계산
        distance = cam.flag_distance(bot.head_angle())
        time.sleep(0.3)

        # 거리에 따른 퍼팅 파워 조절
        if 0 <= distance <= 50:
            power = 8
        elif 50 < distance <= 100:
            power = 15
        elif 100 < distance <= 150:
            power = 20
        elif 150 < distance <= 200:
            power = 25
        else:
            power = 30

        # 퍼팅 실행
        bot.hit(power)
        time.sleep(1)
        
        # 퍼팅 후 다시 공 찾기 상태로 전환
        current_state = SEARCH_BALL