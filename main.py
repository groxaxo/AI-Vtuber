import os
import threading
import schedule
import random
import asyncio, aiohttp
import traceback
import copy
import json, re

from functools import partial

from typing import *

# Keyboard listening voice chat section
import keyboard
import pyaudio
import wave
import numpy as np
import speech_recognition as sr
from aip import AipSpeech
import signal
import time

import http.server
import socketserver

from utils.my_log import logger
from utils.common import Common
from utils.config import Config
from utils.my_handle import My_handle
import utils.my_global as my_global

"""
	___ _                       
	|_ _| | ____ _ _ __ ___  ___ 
	 | || |/ / _` | '__/ _ \/ __|
	 | ||   < (_| | | | (_) \__ \
	|___|_|\_\__,_|_|  \___/|___/

"""

config = None
common = None
my_handle = None


# Configuration file path
config_path = "config.json"


# Web service thread
async def web_server_thread(web_server_port):
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", web_server_port), Handler) as httpd:
        logger.info(f"Web running on port: {web_server_port}")
        logger.info(
            f"Access Live2D page directly: http://127.0.0.1:{web_server_port}/Live2D/"
        )
        httpd.serve_forever()


"""
                       _oo0oo_
                       o8888888o
                       88" . "88
                       (| -_- |)
                       0\  =  /0
                     ___/`---'\___
                   .' \\|     |// '.
                  / \\|||  :  |||// \
                 / _||||| -:- |||||- \
                |   | \\\  - /// |   |
                | \_|  ''\---/''  |_/ |
                \  .-\__  '-'  ___/-. /
              ___'. .'  /--.--\  `. .'___
           ."" '<  `.___\_<|>_/___.' >' "".
          | | :  `- \`.;`\ _ /`;.`/ - ` : | |
          \  \ `_.   \_ __\ /__ _/   .-` /  /
      =====`-.____`.___ \_____/___.-`___.-'=====
                        `=---='


      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

          Buddha bless       Never crash     No bugs
"""


# Ignition and takeoff
def start_server():
    global config, common, my_handle, config_path
    global do_listen_and_comment_thread, stop_do_listen_and_comment_thread_event
    global faster_whisper_model, sense_voice_model, is_recording, is_talk_awake

    # Keyboard listening related
    do_listen_and_comment_thread = None
    stop_do_listen_and_comment_thread_event = threading.Event()
    # Cooldown 0.5 seconds
    cooldown = 0.5
    last_pressed = 0
    # Recording flag
    is_recording = False
    # Chat wakeup status
    is_talk_awake = False

    # Pending play audio count (used for external players like metahuman-stream)
    my_global.wait_play_audio_num = 0
    my_global.wait_synthesis_msg_num = 0

    # Get loggers for external libraries
    # httpx_logger = logging.getLogger("httpx")
    # httpx_logger.setLevel(logging.WARNING)

    # Latest live room data
    my_global.last_liveroom_data = {
        "OnlineUserCount": 0,
        "TotalUserCount": 0,
        "TotalUserCountStr": "0",
        "OnlineUserCountStr": "0",
        "MsgId": 0,
        "User": None,
        "Content": "Current online: 0, Total: 0",
        "RoomId": 0,
    }
    # Latest entering user list
    my_global.last_username_list = [""]

    my_handle = My_handle(config_path)
    if my_handle is None:
        logger.error("Program initialization failed!")
        os._exit(0)

    # Live2D thread
    try:
        if config.get("live2d", "enable"):
            web_server_port = int(config.get("live2d", "port"))
            threading.Thread(
                target=lambda: asyncio.run(web_server_thread(web_server_port))
            ).start()
    except Exception as e:
        logger.error(traceback.format_exc())
        os._exit(0)

    if platform != "wxlive":
        """

                  /@@@@@@@@          @@@@@@@@@@@@@@@].      =@@@@@@@       
                 =@@@@@@@@@^         @@@@@@@@@@@@@@@@@@`    =@@@@@@@       
                ,@@@@@@@@@@@`        @@@@@@@@@@@@@@@@@@@^   =@@@@@@@       
               .@@@@@@\@@@@@@.       @@@@@@@^   .\@@@@@@\   =@@@@@@@       
               /@@@@@/ \@@@@@\       @@@@@@@^    =@@@@@@@   =@@@@@@@       
              =@@@@@@. .@@@@@@^      @@@@@@@\]]]@@@@@@@@^   =@@@@@@@       
             ,@@@@@@^   =@@@@@@`     @@@@@@@@@@@@@@@@@@/    =@@@@@@@       
            .@@@@@@@@@@@@@@@@@@@.    @@@@@@@@@@@@@@@@/`     =@@@@@@@       
            /@@@@@@@@@@@@@@@@@@@\    @@@@@@@^               =@@@@@@@       
           =@@@@@@@@@@@@@@@@@@@@@^   @@@@@@@^               =@@@@@@@       
          ,@@@@@@@.       ,@@@@@@@`  @@@@@@@^               =@@@@@@@       
          @@@@@@@^         =@@@@@@@. @@@@@@@^               =@@@@@@@   

        """

        # HTTP API thread
        def http_api_thread():
            import uvicorn
            from fastapi import FastAPI
            from fastapi.middleware.cors import CORSMiddleware
            from utils.models import (
                SendMessage,
                LLMMessage,
                CallbackMessage,
                CommonResult,
            )

            # Define FastAPI app
            app = FastAPI()

            # Allow CORS
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            # Define POST routes and handlers
            @app.post("/send")
            async def send(msg: SendMessage):
                global my_handle, config

                try:
                    tmp_json = msg.dict()
                    logger.info(f"Internal HTTP API send received data: {tmp_json}")
                    data_json = tmp_json["data"]
                    if "type" not in data_json:
                        data_json["type"] = tmp_json["type"]

                    if data_json["type"] in ["reread", "reread_top_priority"]:
                        my_handle.reread_handle(data_json, type=data_json["type"])
                    elif data_json["type"] == "comment":
                        my_handle.process_data(data_json, "comment")
                    elif data_json["type"] == "tuning":
                        my_handle.tuning_handle(data_json)
                    elif data_json["type"] == "gift":
                        my_handle.gift_handle(data_json)
                    elif data_json["type"] == "entrance":
                        my_handle.entrance_handle(data_json)

                    return CommonResult(code=200, message="Success")
                except Exception as e:
                    logger.error(f"Failed to send data! {e}")
                    return CommonResult(code=-1, message=f"Failed to send data! {e}")

            @app.post("/llm")
            async def llm(msg: LLMMessage):
                global my_handle, config

                try:
                    data_json = msg.dict()
                    logger.info(f"API received data: {data_json}")

                    resp_content = my_handle.llm_handle(
                        data_json["type"], data_json, webui_show=False
                    )

                    return CommonResult(
                        code=200, message="Success", data={"content": resp_content}
                    )
                except Exception as e:
                    logger.error(f"LLM call failed! {e}")
                    return CommonResult(code=-1, message=f"LLM call failed! {e}")

            from starlette.requests import Request

            @app.post("/tts")
            async def tts(request: Request):
                try:
                    data_json = await request.json()
                    logger.info(f"API received data: {data_json}")

                    resp_json = await My_handle.audio.tts_handle(data_json)

                    return {"code": 200, "message": "Success", "data": resp_json}
                except Exception as e:
                    logger.error(traceback.format_exc())
                    return CommonResult(code=-1, message=f"Failed! {e}")

            @app.post("/callback")
            async def callback(msg: CallbackMessage):
                global my_handle, config

                try:
                    data_json = msg.dict()

                    # Special callback handling
                    if data_json["type"] == "audio_playback_completed":
                        my_global.wait_play_audio_num = int(
                            data_json["data"]["wait_play_audio_num"]
                        )
                        my_global.wait_synthesis_msg_num = int(
                            data_json["data"]["wait_synthesis_msg_num"]
                        )
                        logger.info(
                            f"Internal HTTP API callback Audio Playback Completed, Pending: {my_global.wait_play_audio_num}, Synthetic: {my_global.wait_synthesis_msg_num}"
                        )
                    else:
                        logger.info(
                            f"Internal HTTP API callback received data: {data_json}"
                        )

                    # Audio playback completed
                    if data_json["type"] in ["audio_playback_completed"]:
                        my_global.wait_play_audio_num = int(
                            data_json["data"]["wait_play_audio_num"]
                        )

                        # If pending audio count > threshold
                        if data_json["data"]["wait_play_audio_num"] > int(
                            config.get(
                                "idle_time_task", "wait_play_audio_num_threshold"
                            )
                        ):
                            logger.info(
                                f"Pending audio count exceeds limit, reset idle timer: {my_global.global_idle_time} -> {int(config.get('idle_time_task', 'idle_time_reduce_to'))}s"
                            )
                            # Reset idle timer
                            my_global.global_idle_time = int(
                                config.get("idle_time_task", "idle_time_reduce_to")
                            )

                    return CommonResult(code=200, message="callback success!")
                except Exception as e:
                    logger.error(f"callback failed! {e}")
                    return CommonResult(code=-1, message=f"callback failed! {e}")

            # Get system info API
            @app.get("/get_sys_info")
            async def get_sys_info():
                global my_handle, config

                try:
                    data = {
                        "audio": my_handle.get_audio_info(),
                        "metahuman-stream": {
                            "wait_play_audio_num": my_global.wait_play_audio_num,
                            "wait_synthesis_msg_num": my_global.wait_synthesis_msg_num,
                        },
                    }

                    return CommonResult(
                        code=200, data=data, message="get_sys_info success!"
                    )
                except Exception as e:
                    logger.error(f"get_sys_info failed! {e}")
                    return CommonResult(code=-1, message=f"get_sys_info failed! {e}")

            logger.info("HTTP API thread started!")

            # Expose static files in local directory
            if config.get("webui", "local_dir_to_endpoint", "enable"):
                for tmp in config.get("webui", "local_dir_to_endpoint", "config"):
                    from fastapi.staticfiles import StaticFiles

                    app.mount(
                        tmp["url_path"],
                        StaticFiles(directory=tmp["local_dir"]),
                        name=tmp["local_dir"],
                    )

            uvicorn.run(app, host="0.0.0.0", port=config.get("api_port"))

        # Start HTTP API thread
        inside_http_api_thread = threading.Thread(target=http_api_thread)
        inside_http_api_thread.start()

    """
    Keyboard listening section
    """

    # Audio recording (OpenAI STT will error if recording is too short)
    def record_audio():
        pressdown_num = 0
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        WAVE_OUTPUT_FILENAME = "out/record.wav"
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        frames = []
        logger.info("Recording...")
        flag = 0
        while 1:
            while keyboard.is_pressed("RIGHT_SHIFT"):
                flag = 1
                data = stream.read(CHUNK)
                frames.append(data)
                pressdown_num = pressdown_num + 1
            if flag:
                break
        logger.info("Stopped recording.")
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()
        if pressdown_num >= 5:  # Rough handling
            return 1
        else:
            logger.info("Too short! (Press Right Shift to record again)")
            return 0

    # THRESHOLD sets volume threshold, default 800.0. silence_threshold sets silence threshold.
    def audio_listen(volume_threshold=800.0, silence_threshold=15):
        audio = pyaudio.PyAudio()

        # Set audio parameters
        FORMAT = pyaudio.paInt16
        CHANNELS = config.get("talk", "CHANNELS")
        RATE = config.get("talk", "RATE")
        CHUNK = 1024

        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=int(config.get("talk", "device_index")),
        )

        frames = []  # Stores recorded frames

        is_speaking = False
        silent_count = 0
        speaking_flag = False

        logger.info("[Recording starts soon...]")

        while True:
            # Don't record during playback
            if config.get("talk", "no_recording_during_playback"):
                # If there are pending/synthesis/playback tasks
                if (
                    my_handle.is_audio_queue_empty() != 15
                    or my_handle.is_handle_empty() == 1
                    or my_global.wait_play_audio_num > 0
                ):
                    time.sleep(
                        float(
                            config.get(
                                "talk", "no_recording_during_playback_sleep_interval"
                            )
                        )
                    )
                    continue

            # Read audio data
            data = stream.read(CHUNK)
            audio_data = np.frombuffer(data, dtype=np.short)
            max_dB = np.max(audio_data)

            if max_dB > volume_threshold:
                is_speaking = True
                silent_count = 0
            elif is_speaking is True:
                silent_count += 1

            if is_speaking is True:
                frames.append(data)
                if speaking_flag is False:
                    logger.info("[Recording...]")
                    speaking_flag = True

            if silent_count >= silence_threshold:
                break

        logger.info("[Recording complete]")

        return frames

    # Handle chat logic with ASR text
    def talk_handle(content: str):
        global is_talk_awake

        def clear_queue_and_stop_audio_play(
            message_queue: bool = True,
            voice_tmp_path_queue: bool = True,
            stop_audio_play: bool = True,
        ):
            """
            Clear queue or stop audio playback
            """
            if message_queue:
                ret = my_handle.clear_queue("message_queue")
                if ret:
                    logger.info("Cleared pending message queue!")
                else:
                    logger.error("Failed to clear pending message queue!")
            if voice_tmp_path_queue:
                ret = my_handle.clear_queue("voice_tmp_path_queue")
                if ret:
                    logger.info("Cleared pending audio queue!")
                else:
                    logger.error("Failed to clear pending audio queue!")
            if stop_audio_play:
                ret = my_handle.stop_audio("pygame", True, True)

        try:
            # Check and switch chat wakeup status
            def check_talk_awake(content: str):
                """Check and switch chat wakeup status

                Args:
                    content (str): Chat content

                Returns:
                    dict:
                        ret Whether to trigger
                        is_talk_awake Current wakeup status
                        first Whether it's the first trigger (wakeup/sleep) for special prompts
                """
                global is_talk_awake

                # Check if wakeup word feature is enabled
                if config.get("talk", "wakeup_sleep", "enable"):
                    if config.get("talk", "wakeup_sleep", "mode") == "Long-term wakeup":
                        # If currently asleep
                        if is_talk_awake is False:
                            # Check for wakeup word
                            trigger_word = common.find_substring_in_list(
                                content,
                                config.get("talk", "wakeup_sleep", "wakeup_word"),
                            )
                            if trigger_word:
                                is_talk_awake = True
                                logger.info("[Chat wake up success]")
                                return {
                                    "ret": 0,
                                    "is_talk_awake": is_talk_awake,
                                    "first": True,
                                    "trigger_word": trigger_word,
                                }
                            return {
                                "ret": -1,
                                "is_talk_awake": is_talk_awake,
                                "first": False,
                            }
                        else:
                            # Check for sleep word
                            trigger_word = common.find_substring_in_list(
                                content,
                                config.get("talk", "wakeup_sleep", "sleep_word"),
                            )
                            if trigger_word:
                                is_talk_awake = False
                                logger.info("[Chat sleep success]")
                                return {
                                    "ret": 0,
                                    "is_talk_awake": is_talk_awake,
                                    "first": True,
                                    "trigger_word": trigger_word,
                                }
                            return {
                                "ret": 0,
                                "is_talk_awake": is_talk_awake,
                                "first": False,
                            }
                    elif config.get("talk", "wakeup_sleep", "mode") == "Single wakeup":
                        # No need to check current status
                        trigger_word = common.find_substring_in_list(
                            content, config.get("talk", "wakeup_sleep", "wakeup_word")
                        )
                        if trigger_word:
                            is_talk_awake = True
                            logger.info("[Chat wake up success]")
                            return {
                                "ret": 0,
                                "is_talk_awake": is_talk_awake,
                                "first": False,
                                "trigger_word": trigger_word,
                            }
                        return {
                            "ret": -1,
                            "is_talk_awake": is_talk_awake,
                            "first": False,
                        }

                return {
                    "ret": 0,
                    "is_talk_awake": True,
                    "trigger_word": "",
                    "first": False,
                }

            # Recognition result
            logger.info("Recognition Result: " + content)

            # Filter empty content
            if content == "":
                return

            username = config.get("talk", "username")

            data = {"platform": "Local Chat", "username": username, "content": content}

            # Check wakeup status
            check_resp = check_talk_awake(content)
            if check_resp["ret"] == 0:
                # If awake
                if check_resp["is_talk_awake"]:
                    # Long-term wakeup, not first trigger: don't strip trigger words from subsequent messages
                    if (
                        config.get("talk", "wakeup_sleep", "mode") == "Long-term wakeup"
                        and not check_resp["first"]
                    ):
                        pass
                    else:
                        # Strip trigger word
                        content = content.replace(
                            check_resp["trigger_word"], ""
                        ).strip()

                    # Handle case where content becomes empty after stripping trigger word
                    if content == "" and not check_resp["first"]:
                        return

                    data["content"] = content

                    # First trigger: play wakeup prompt
                    if check_resp["first"]:
                        resp_json = common.get_random_str_in_list_and_format(
                            ori_list=config.get(
                                "talk", "wakeup_sleep", "wakeup_copywriting"
                            )
                        )
                        if resp_json["ret"] == 0:
                            data["content"] = resp_json["content"]
                            data["insert_index"] = -1
                            my_handle.reread_handle(data)
                    else:
                        # "Interrupt chat" feature
                        if config.get("talk", "interrupt_talk", "enable"):
                            interrupt_word = common.find_substring_in_list(
                                data["content"],
                                config.get("talk", "interrupt_talk", "keywords"),
                            )
                            if interrupt_word:
                                logger.info(
                                    f"[Chat Interrupt] Keyword hit: {interrupt_word}"
                                )
                                clean_type = config.get(
                                    "talk", "interrupt_talk", "clean_type"
                                )
                                message_queue = "message_queue" in clean_type
                                voice_tmp_path_queue = (
                                    "voice_tmp_path_queue" in clean_type
                                )
                                stop_audio_play = "stop_audio_play" in clean_type

                                clear_queue_and_stop_audio_play(
                                    message_queue, voice_tmp_path_queue, stop_audio_play
                                )
                                return False

                        # Handle data
                        my_handle.process_data(data, "talk")

                        # Reset status for single wakeup
                        if (
                            config.get("talk", "wakeup_sleep", "mode")
                            == "Single wakeup"
                        ):
                            is_talk_awake = False
                # If asleep
                else:
                    # First entering sleep: play sleep prompt
                    if check_resp["first"]:
                        resp_json = common.get_random_str_in_list_and_format(
                            ori_list=config.get(
                                "talk", "wakeup_sleep", "sleep_copywriting"
                            )
                        )
                        if resp_json["ret"] == 0:
                            data["content"] = resp_json["content"]
                            data["insert_index"] = -1
                            my_handle.reread_handle(data)
        except Exception as e:
            logger.error(traceback.format_exc())

    # Execute recording, recognition & submission
    def do_listen_and_comment(status=True):
        global \
            stop_do_listen_and_comment_thread_event, \
            faster_whisper_model, \
            sense_voice_model, \
            is_recording, \
            is_talk_awake

        try:
            is_recording = True

            config = Config(config_path)
            # Check if key listener or direct talk is enabled
            if not config.get("talk", "key_listener_enable") and not config.get(
                "talk", "direct_run_talk"
            ):
                is_recording = False
                return

            # For faster_whisper, load model once
            if "faster_whisper" == config.get("talk", "type"):
                from faster_whisper import WhisperModel

                if faster_whisper_model is None:
                    logger.info("faster_whisper model loading, please wait...")
                    faster_whisper_model = WhisperModel(
                        model_size_or_path=config.get(
                            "talk", "faster_whisper", "model_size"
                        ),
                        device=config.get("talk", "faster_whisper", "device"),
                        compute_type=config.get(
                            "talk", "faster_whisper", "compute_type"
                        ),
                        download_root=config.get(
                            "talk", "faster_whisper", "download_root"
                        ),
                    )
                    logger.info("faster_whisper model loaded, start speaking meow~")
            elif "sensevoice" == config.get("talk", "type"):
                from funasr import AutoModel

                logger.info("sensevoice model loading, please wait...")
                asr_model_path = config.get("talk", "sensevoice", "asr_model_path")
                vad_model_path = config.get("talk", "sensevoice", "vad_model_path")
                if sense_voice_model is None:
                    sense_voice_model = AutoModel(
                        model=asr_model_path,
                        vad_model=vad_model_path,
                        vad_kwargs={
                            "max_single_segment_time": int(
                                config.get(
                                    "talk", "sensevoice", "vad_max_single_segment_time"
                                )
                            )
                        },
                        trust_remote_code=True,
                        device=config.get("talk", "sensevoice", "device"),
                        remote_code="./sensevoice/model.py",
                    )

                    logger.info("sensevoice model loaded, start speaking meow~")

            while True:
                try:
                    # Check for stop event
                    if stop_do_listen_and_comment_thread_event.is_set():
                        logger.info("Stop recording~")
                        is_recording = False
                        break

                    config = Config(config_path)

                    # Execute based on STT type
                    if config.get("talk", "type") in [
                        "baidu",
                        "faster_whisper",
                        "sensevoice",
                    ]:
                        FORMAT = pyaudio.paInt16
                        CHANNELS = config.get("talk", "CHANNELS")
                        RATE = config.get("talk", "RATE")

                        audio_out_path = config.get("play_audio", "out_path")

                        if not os.path.isabs(audio_out_path):
                            if not audio_out_path.startswith("./"):
                                audio_out_path = "./" + audio_out_path
                        file_name = "asr_" + common.get_bj_time(4) + ".wav"
                        WAVE_OUTPUT_FILENAME = common.get_new_audio_path(
                            audio_out_path, file_name
                        )

                        frames = audio_listen(
                            config.get("talk", "volume_threshold"),
                            config.get("talk", "silence_threshold"),
                        )

                        # Save audio to WAV
                        with wave.open(WAVE_OUTPUT_FILENAME, "wb") as wf:
                            wf.setnchannels(CHANNELS)
                            wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
                            wf.setframerate(RATE)
                            wf.writeframes(b"".join(frames))

                        if config.get("talk", "type") == "baidu":
                            with open(WAVE_OUTPUT_FILENAME, "rb") as fp:
                                audio = fp.read()

                            baidu_client = AipSpeech(
                                config.get("talk", "baidu", "app_id"),
                                config.get("talk", "baidu", "api_key"),
                                config.get("talk", "baidu", "secret_key"),
                            )

                            res = baidu_client.asr(
                                audio,
                                "wav",
                                16000,
                                {
                                    "dev_pid": 1536,
                                },
                            )
                            if res["err_no"] == 0:
                                content = res["result"][0]
                                talk_handle(content)
                            else:
                                logger.error(f"Baidu API error: {res}")
                        elif config.get("talk", "type") == "faster_whisper":
                            logger.debug("faster_whisper model loading...")

                            language = config.get("talk", "faster_whisper", "language")
                            if language == "auto":
                                language = None

                            segments, info = faster_whisper_model.transcribe(
                                WAVE_OUTPUT_FILENAME,
                                language=language,
                                beam_size=config.get(
                                    "talk", "faster_whisper", "beam_size"
                                ),
                            )

                            logger.debug(
                                "Detected language: '%s', Prob: %f"
                                % (info.language, info.language_probability)
                            )

                            content = ""
                            for segment in segments:
                                logger.info(
                                    "[%.2fs -> %.2fs] %s"
                                    % (segment.start, segment.end, segment.text)
                                )
                                content += segment.text + "。"

                            if content == "":
                                is_recording = False
                                return

                            talk_handle(content)
                        elif config.get("talk", "type") == "sensevoice":
                            res = sense_voice_model.generate(
                                input=WAVE_OUTPUT_FILENAME,
                                cache={},
                                language=config.get("talk", "sensevoice", "language"),
                                text_norm=config.get("talk", "sensevoice", "text_norm"),
                                batch_size_s=int(
                                    config.get("talk", "sensevoice", "batch_size_s")
                                ),
                                batch_size=int(
                                    config.get("talk", "sensevoice", "batch_size")
                                ),
                            )

                            def remove_angle_brackets_content(input_string: str):
                                return re.sub(r"<.*?>", "", input_string)

                            content = remove_angle_brackets_content(res[0]["text"])
                            talk_handle(content)
                    elif "google" == config.get("talk", "type"):
                        r = sr.Recognizer()

                        try:
                            with sr.Microphone() as source:
                                logger.info("Recording...")
                                audio = r.listen(source)
                                logger.info("Successfully recorded")

                                content = r.recognize_google(
                                    audio,
                                    language=config.get("talk", "google", "tgt_lang"),
                                )

                                talk_handle(content)
                        except sr.UnknownValueError:
                            logger.warning("Could not recognize input speech")
                        except sr.RequestError as e:
                            logger.error("Request error: " + str(e))

                    is_recording = False

                    if not status:
                        return
                except Exception as e:
                    logger.error(traceback.format_exc())
                    is_recording = False
                    return
        except Exception as e:
            logger.error(traceback.format_exc())
            is_recording = False
            return

    def on_key_press(event):
        global \
            do_listen_and_comment_thread, \
            stop_do_listen_and_comment_thread_event, \
            is_recording

        # Check if key listener is enabled
        if not config.get("talk", "key_listener_enable"):
            return

        # Key cooldown
        current_time = time.time()
        if current_time - last_pressed < cooldown:
            return

        """
        Trigger key logic
        """
        trigger_key_lower = None
        stop_trigger_key_lower = None

        if trigger_key.isalpha():
            trigger_key_lower = trigger_key.lower()

        if stop_trigger_key.isalpha():
            stop_trigger_key_lower = stop_trigger_key.lower()

        if trigger_key_lower:
            if event.name == trigger_key or event.name == trigger_key_lower:
                logger.info(f"Keyboard {event.name} clicked, start recording soon~")
            elif event.name == stop_trigger_key or event.name == stop_trigger_key_lower:
                logger.info(f"Keyboard {event.name} clicked, stop recording soon~")
                stop_do_listen_and_comment_thread_event.set()
                return
            else:
                return
        else:
            if event.name == trigger_key:
                logger.info(f"Keyboard {event.name} clicked, start recording soon~")
            elif event.name == stop_trigger_key:
                logger.info(f"Keyboard {event.name} clicked, stop recording soon~")
                stop_do_listen_and_comment_thread_event.set()
                return
            else:
                return

        if not is_recording:
            # Continuous talk mode
            if config.get("talk", "continuous_talk"):
                stop_do_listen_and_comment_thread_event.clear()
                do_listen_and_comment_thread = threading.Thread(
                    target=do_listen_and_comment, args=(True,)
                )
                do_listen_and_comment_thread.start()
            else:
                stop_do_listen_and_comment_thread_event.clear()
                do_listen_and_comment_thread = threading.Thread(
                    target=do_listen_and_comment, args=(False,)
                )
                do_listen_and_comment_thread.start()
        else:
            logger.warning("Recording in progress... please don't click again!")

    # Key listener
    def key_listener():
        keyboard.on_press(on_key_press)

        try:
            keyboard.wait()
        except KeyboardInterrupt:
            os._exit(0)

    # Directly run voice chat
    def direct_run_talk():
        global \
            do_listen_and_comment_thread, \
            stop_do_listen_and_comment_thread_event, \
            is_recording

        if not is_recording:
            if config.get("talk", "continuous_talk"):
                stop_do_listen_and_comment_thread_event.clear()
                do_listen_and_comment_thread = threading.Thread(
                    target=do_listen_and_comment, args=(True,)
                )
                do_listen_and_comment_thread.start()
            else:
                stop_do_listen_and_comment_thread_event.clear()
                do_listen_and_comment_thread = threading.Thread(
                    target=do_listen_and_comment, args=(False,)
                )
                do_listen_and_comment_thread.start()

    # Read trigger keys from config
    trigger_key = config.get("talk", "trigger_key")
    stop_trigger_key = config.get("talk", "stop_trigger_key")

    if config.get("talk", "key_listener_enable"):
        logger.info(
            f"Press {trigger_key} to record meow~ If no response, wait for models to load."
        )

    # Direct run talk mode
    if config.get("talk", "direct_run_talk"):
        logger.info("Direct talk mode, start recognition on run.")
        direct_run_talk()

    # Start keyboard listener thread
    thread = threading.Thread(target=key_listener)
    thread.start()

    # Scheduled task
    def schedule_task(index):
        global config, common, my_handle

        logger.debug("Scheduled task executing...")
        hour, min = common.get_bj_time(6)

        if 0 <= hour and hour < 6:
            time = f"early morning {hour}:{min}"
        elif 6 <= hour and hour < 9:
            time = f"morning {hour}:{min}"
        elif 9 <= hour and hour < 12:
            time = f"forenoon {hour}:{min}"
        elif hour == 12:
            time = f"noon {hour}:{min}"
        elif 13 <= hour and hour < 18:
            time = f"afternoon {hour - 12}:{min}"
        elif 18 <= hour and hour < 20:
            time = f"evening {hour - 12}:{min}"
        elif 20 <= hour and hour < 24:
            time = f"night {hour - 12}:{min}"

        if len(config.get("schedule")[index]["copy"]) <= 0:
            return None

        random_copy = random.choice(config.get("schedule")[index]["copy"])

        variables = {
            "time": time,
            "user_num": "N",
            "last_username": my_global.last_username_list[-1],
        }

        if platform in ["dy", "tiktok"]:
            variables["user_num"] = my_global.last_liveroom_data["OnlineUserCount"]

        if any(var in random_copy for var in variables):
            content = random_copy.format(
                **{var: value for var, value in variables.items() if var in random_copy}
            )
        else:
            content = random_copy

        content = common.brackets_text_randomize(content)

        data = {"platform": platform, "username": "Scheduled Task", "content": content}

        logger.info(f"Scheduled Task: {content}")

        my_handle.process_data(data, "schedule")

    # Run scheduler
    def run_schedule():
        global config

        try:
            for index, task in enumerate(config.get("schedule")):
                if task["enable"]:
                    min_seconds = int(task["time_min"])
                    max_seconds = int(task["time_max"])

                    def schedule_random_task(index, min_seconds, max_seconds):
                        schedule.clear(index)
                        next_time = random.randint(min_seconds, max_seconds)
                        schedule_task(index)
                        schedule.every(next_time).seconds.do(
                            schedule_random_task, index, min_seconds, max_seconds
                        ).tag(index)

                    schedule_random_task(index, min_seconds, max_seconds)
        except Exception as e:
            logger.error(traceback.format_exc())

        while True:
            schedule.run_pending()

    if any(item["enable"] for item in config.get("schedule")) or platform == "dy":
        schedule_thread = threading.Thread(target=run_schedule)
        schedule_thread.start()

    # Dynamic copywriting
    async def run_trends_copywriting():
        global config

        try:
            if not config.get("trends_copywriting", "enable"):
                return

            logger.info("Dynamic copywriting thread running...")

            while True:
                copywriting_file_path_list = []

                for copywriting in config.get("trends_copywriting", "copywriting"):
                    for tmp in common.get_all_file_paths(copywriting["folder_path"]):
                        copywriting_file_path_list.append(tmp)

                    if config.get("trends_copywriting", "random_play"):
                        random.shuffle(copywriting_file_path_list)

                    logger.debug(
                        f"copywriting_file_path_list={copywriting_file_path_list}"
                    )

                    for copywriting_file_path in copywriting_file_path_list:
                        copywriting_file_content = common.read_file_return_content(
                            copywriting_file_path
                        )
                        if copywriting["prompt_change_enable"]:
                            data_json = {
                                "username": "trends_copywriting",
                                "content": copywriting["prompt_change_content"]
                                + copywriting_file_content,
                            }

                            data_json["content"] = my_handle.llm_handle(
                                config.get("trends_copywriting", "llm_type"), data_json
                            )
                        else:
                            copywriting_file_content = common.brackets_text_randomize(
                                copywriting_file_content
                            )

                            data_json = {
                                "username": "trends_copywriting",
                                "content": copywriting_file_content,
                            }

                        logger.debug(
                            f"copywriting_file_content={copywriting_file_content},content={data_json['content']}"
                        )

                        if (
                            data_json["content"] is not None
                            and data_json["content"] != ""
                        ):
                            my_handle.reread_handle(
                                data_json, filter=True, type="trends_copywriting"
                            )

                            await asyncio.sleep(
                                config.get("trends_copywriting", "play_interval")
                            )
        except Exception as e:
            logger.error(traceback.format_exc())

    if config.get("trends_copywriting", "enable"):
        threading.Thread(target=lambda: asyncio.run(run_trends_copywriting())).start()

    # Idle time task
    async def idle_time_task():
        global config, common

        try:
            if not config.get("idle_time_task", "enable"):
                return

            logger.info("Idle time task thread running...")

            last_mode = 0
            copywriting_copy_list = None
            comment_copy_list = None
            local_audio_path_list = None

            overflow_time_min = int(config.get("idle_time_task", "idle_time_min"))
            overflow_time_max = int(config.get("idle_time_task", "idle_time_max"))
            overflow_time = random.randint(overflow_time_min, overflow_time_max)

            logger.info(f"Next idle task in {overflow_time}s")

            def load_data_list(type):
                if type == "copywriting":
                    tmp = config.get("idle_time_task", "copywriting", "copy")
                elif type == "comment":
                    tmp = config.get("idle_time_task", "comment", "copy")
                elif type == "local_audio":
                    tmp = config.get("idle_time_task", "local_audio", "path")

                logger.debug(f"type={type}, tmp={tmp}")
                tmp2 = copy.copy(tmp)
                return tmp2

            copywriting_copy_list = load_data_list("copywriting")
            comment_copy_list = load_data_list("comment")
            local_audio_path_list = load_data_list("local_audio")

            logger.debug(f"copywriting_copy_list={copywriting_copy_list}")
            logger.debug(f"comment_copy_list={comment_copy_list}")
            logger.debug(f"local_audio_path_list={local_audio_path_list}")

            def do_task(
                last_mode,
                copywriting_copy_list,
                comment_copy_list,
                local_audio_path_list,
            ):
                my_global.global_idle_time = 0

                if config.get("idle_time_task", "copywriting", "enable"):
                    if last_mode == 0:
                        if config.get("idle_time_task", "copywriting", "random"):
                            logger.debug("Switch to copywriting mode")
                            if copywriting_copy_list != []:
                                random.shuffle(copywriting_copy_list)
                                copywriting_copy = copywriting_copy_list.pop(0)
                            else:
                                # 刷新list数据
                                copywriting_copy_list = load_data_list("copywriting")
                                # 随机打乱列表中的元素
                                random.shuffle(copywriting_copy_list)
                                if copywriting_copy_list != []:
                                    copywriting_copy = copywriting_copy_list.pop(0)
                                else:
                                    return (
                                        last_mode,
                                        copywriting_copy_list,
                                        comment_copy_list,
                                        local_audio_path_list,
                                    )
                        else:
                            logger.debug(copywriting_copy_list)
                            if copywriting_copy_list != []:
                                copywriting_copy = copywriting_copy_list.pop(0)
                            else:
                                # 刷新list数据
                                copywriting_copy_list = load_data_list("copywriting")
                                if copywriting_copy_list != []:
                                    copywriting_copy = copywriting_copy_list.pop(0)
                                else:
                                    return (
                                        last_mode,
                                        copywriting_copy_list,
                                        comment_copy_list,
                                        local_audio_path_list,
                                    )

                        hour, min = common.get_bj_time(6)

                        if 0 <= hour and hour < 6:
                            time = f"凌晨{hour}点{min}分"
                        elif 6 <= hour and hour < 9:
                            time = f"早晨{hour}点{min}分"
                        elif 9 <= hour and hour < 12:
                            time = f"上午{hour}点{min}分"
                        elif hour == 12:
                            time = f"中午{hour}点{min}分"
                        elif 13 <= hour and hour < 18:
                            time = f"下午{hour - 12}点{min}分"
                        elif 18 <= hour and hour < 20:
                            time = f"傍晚{hour - 12}点{min}分"
                        elif 20 <= hour and hour < 24:
                            time = f"晚上{hour - 12}点{min}分"

                        # Dynamic variable substitution
                        variables = {
                            "time": time,
                            "user_num": "N",
                            "last_username": my_global.last_username_list[-1],
                        }

                        if platform in ["dy", "tiktok"]:
                            variables["user_num"] = my_global.last_liveroom_data[
                                "OnlineUserCount"
                            ]

                        if any(var in copywriting_copy for var in variables):
                            copywriting_copy = copywriting_copy.format(
                                **{
                                    var: value
                                    for var, value in variables.items()
                                    if var in copywriting_copy
                                }
                            )

                        copywriting_copy = common.brackets_text_randomize(
                            copywriting_copy
                        )

                        data = {
                            "platform": platform,
                            "username": "Idle Task - Copywriting Mode",
                            "type": "reread",
                            "content": copywriting_copy,
                        }

                        my_handle.process_data(data, "idle_time_task")

                        # Mode switch
                        last_mode = 1

                        overflow_time = random.randint(
                            overflow_time_min, overflow_time_max
                        )
                        logger.info(f"Next idle task in {overflow_time}s")

                        return (
                            last_mode,
                            copywriting_copy_list,
                            comment_copy_list,
                            local_audio_path_list,
                        )
                else:
                    last_mode = 1

                if config.get("idle_time_task", "comment", "enable"):
                    if last_mode == 1:
                        if config.get("idle_time_task", "comment", "random"):
                            logger.debug("Switch to comment trigger LLM mode")
                            if comment_copy_list != []:
                                random.shuffle(comment_copy_list)
                                comment_copy = comment_copy_list.pop(0)
                            else:
                                comment_copy_list = load_data_list("comment")
                                random.shuffle(comment_copy_list)
                                comment_copy = comment_copy_list.pop(0)
                        else:
                            if comment_copy_list != []:
                                comment_copy = comment_copy_list.pop(0)
                            else:
                                comment_copy_list = load_data_list("comment")
                                comment_copy = comment_copy_list.pop(0)

                        hour, min = common.get_bj_time(6)

                        if 0 <= hour and hour < 6:
                            time = f"early morning {hour}:{min}"
                        elif 6 <= hour and hour < 9:
                            time = f"morning {hour}:{min}"
                        elif 9 <= hour and hour < 12:
                            time = f"forenoon {hour}:{min}"
                        elif hour == 12:
                            time = f"noon {hour}:{min}"
                        elif 13 <= hour and hour < 18:
                            time = f"afternoon {hour - 12}:{min}"
                        elif 18 <= hour and hour < 20:
                            time = f"evening {hour - 12}:{min}"
                        elif 20 <= hour and hour < 24:
                            time = f"night {hour - 12}:{min}"

                        variables = {
                            "time": time,
                            "user_num": "N",
                            "last_username": my_global.last_username_list[-1],
                        }

                        if platform in ["dy", "tiktok"]:
                            variables["user_num"] = my_global.last_liveroom_data[
                                "OnlineUserCount"
                            ]

                        if any(var in comment_copy for var in variables):
                            comment_copy = comment_copy.format(
                                **{
                                    var: value
                                    for var, value in variables.items()
                                    if var in comment_copy
                                }
                            )

                        comment_copy = common.brackets_text_randomize(comment_copy)

                        data = {
                            "platform": platform,
                            "username": "Idle Task - Comment Trigger LLM Mode",
                            "type": "comment",
                            "content": comment_copy,
                        }

                        my_handle.process_data(data, "idle_time_task")

                        # Mode switch
                        last_mode = 2

                        overflow_time = random.randint(
                            overflow_time_min, overflow_time_max
                        )
                        logger.info(f"Next idle task in {overflow_time}s")

                        return (
                            last_mode,
                            copywriting_copy_list,
                            comment_copy_list,
                            local_audio_path_list,
                        )
                else:
                    last_mode = 2

                if config.get("idle_time_task", "local_audio", "enable"):
                    if last_mode == 2:
                        logger.debug("Switch to local audio mode")

                        if config.get("idle_time_task", "local_audio", "random"):
                            if local_audio_path_list != []:
                                random.shuffle(local_audio_path_list)
                                local_audio_path = local_audio_path_list.pop(0)
                            else:
                                local_audio_path_list = load_data_list("local_audio")
                                random.shuffle(local_audio_path_list)
                                local_audio_path = local_audio_path_list.pop(0)
                        else:
                            if local_audio_path_list != []:
                                local_audio_path = local_audio_path_list.pop(0)
                            else:
                                local_audio_path_list = load_data_list("local_audio")
                                local_audio_path = local_audio_path_list.pop(0)

                        local_audio_path = common.brackets_text_randomize(
                            local_audio_path
                        )

                        logger.debug(f"local_audio_path={local_audio_path}")

                        data = {
                            "platform": platform,
                            "username": "Idle Task - Local Audio Mode",
                            "type": "local_audio",
                            "content": common.extract_filename(local_audio_path, False),
                            "file_path": local_audio_path,
                        }

                        my_handle.process_data(data, "idle_time_task")

                        # Mode switch
                        last_mode = 0

                        overflow_time = random.randint(
                            overflow_time_min, overflow_time_max
                        )
                        logger.info(f"Next idle task in {overflow_time}s")

                        return (
                            last_mode,
                            copywriting_copy_list,
                            comment_copy_list,
                            local_audio_path_list,
                        )
                else:
                    last_mode = 0

                return (
                    last_mode,
                    copywriting_copy_list,
                    comment_copy_list,
                    local_audio_path_list,
                )

            while True:
                if overflow_time_min > 0 and overflow_time_max > 0:
                    # Every 1s sleep for idle count
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0.1)
                my_global.global_idle_time = my_global.global_idle_time + 1

                if (
                    config.get("idle_time_task", "type")
                    == "Idle time when no messages in stream"
                ):
                    # Trigger idle task when idle count reaches threshold
                    if my_global.global_idle_time >= overflow_time:
                        (
                            last_mode,
                            copywriting_copy_list,
                            comment_copy_list,
                            local_audio_path_list,
                        ) = do_task(
                            last_mode,
                            copywriting_copy_list,
                            comment_copy_list,
                            local_audio_path_list,
                        )
                elif (
                    config.get("idle_time_task", "type")
                    == "Pending message queue update idle"
                ):
                    if my_handle.is_queue_less_or_greater_than(
                        type="message_queue",
                        less=int(
                            config.get("idle_time_task", "min_msg_queue_len_to_trigger")
                        ),
                    ):
                        (
                            last_mode,
                            copywriting_copy_list,
                            comment_copy_list,
                            local_audio_path_list,
                        ) = do_task(
                            last_mode,
                            copywriting_copy_list,
                            comment_copy_list,
                            local_audio_path_list,
                        )
                elif (
                    config.get("idle_time_task", "type")
                    == "Pending audio queue update idle"
                ):
                    logger.debug(
                        f"Pending audio count: {my_global.wait_play_audio_num}"
                    )
                    # Special for metahuman_stream
                    if config.get("visual_body") == "metahuman_stream":
                        if my_global.wait_play_audio_num < config.get(
                            "idle_time_task", "min_audio_queue_len_to_trigger"
                        ):
                            (
                                last_mode,
                                copywriting_copy_list,
                                comment_copy_list,
                                local_audio_path_list,
                            ) = do_task(
                                last_mode,
                                copywriting_copy_list,
                                comment_copy_list,
                                local_audio_path_list,
                            )
                    else:
                        if my_handle.is_queue_less_or_greater_than(
                            type="voice_tmp_path_queue",
                            less=int(
                                config.get(
                                    "idle_time_task", "min_audio_queue_len_to_trigger"
                                )
                            ),
                        ):
                            (
                                last_mode,
                                copywriting_copy_list,
                                comment_copy_list,
                                local_audio_path_list,
                            ) = do_task(
                                last_mode,
                                copywriting_copy_list,
                                comment_copy_list,
                                local_audio_path_list,
                            )

        except Exception as e:
            logger.error(traceback.format_exc())

    if config.get("idle_time_task", "enable"):
        # Start idle task thread
        threading.Thread(target=lambda: asyncio.run(idle_time_task())).start()

    # Image recognition scheduled task
    def image_recognition_schedule_task(type: str):
        global config, common, my_handle

        logger.debug(f"Image recognition-{type} scheduled task executing...")

        data = {"platform": platform, "username": None, "content": "", "type": type}

        logger.info(f"Image recognition-{type} scheduled task triggered")

        my_handle.process_data(data, "image_recognition_schedule")

    # Start image recognition scheduler
    def run_image_recognition_schedule(interval: int, type: str):
        global config

        try:
            schedule.every(interval).seconds.do(
                partial(image_recognition_schedule_task, type)
            )
        except Exception as e:
            logger.error(traceback.format_exc())

        while True:
            schedule.run_pending()

    if config.get("image_recognition", "loop_screenshot_enable"):
        image_recognition_schedule_thread = threading.Thread(
            target=lambda: run_image_recognition_schedule(
                config.get("image_recognition", "loop_screenshot_delay"),
                "Window Screenshot",
            )
        )
        image_recognition_schedule_thread.start()

    if config.get("image_recognition", "loop_cam_screenshot_enable"):
        image_recognition_cam_schedule_thread = threading.Thread(
            target=lambda: run_image_recognition_schedule(
                config.get("image_recognition", "loop_cam_screenshot_delay"),
                "Camera Screenshot",
            )
        )
        image_recognition_cam_schedule_thread.start()

    # Special handling for metahuman-stream (LiveTalking)
    if config.get("visual_body") == "metahuman_stream":

        def metahuman_stream_is_speaking():

            try:
                from urllib.parse import urljoin

                url = urljoin(
                    config.get("metahuman_stream", "api_ip_port"), "is_speaking"
                )
                resp_json = common.send_request(
                    url, "POST", {"sessionid": 0}, timeout=5
                )
                if resp_json and resp_json["code"] == 0:
                    if resp_json["data"]:
                        logger.debug("LiveTalking is playing audio")
                        my_global.wait_play_audio_num = 1
                    else:
                        logger.debug("LiveTalking is not playing audio")
                        my_global.wait_play_audio_num = 0

            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error("Failed to request LiveTalking is_speaking interface")

        # Periodically check if LiveTalking is speaking
        def run_metahuman_stream_is_speaking_schedule():
            interval = 3
            try:
                schedule.every(interval).seconds.do(
                    partial(metahuman_stream_is_speaking)
                )
            except Exception as e:
                logger.error(traceback.format_exc())

            while True:
                schedule.run_pending()

        run_metahuman_stream_is_speaking_schedule_thread = threading.Thread(
            target=lambda: run_metahuman_stream_is_speaking_schedule()
        )
        run_metahuman_stream_is_speaking_schedule_thread.start()

    logger.info(f"Current platform: {platform}")

    if platform == "bilibili":
        from utils.platforms.bilibili import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform == "bilibili2":
        from utils.platforms.bilibili2 import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform == "dy":
        from utils.platforms.dy import start_listen

        start_listen(config, common, my_handle, platform, schedule_thread)
    elif platform == "dy2":
        from utils.platforms.dy2 import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform == "ks":
        from utils.platforms.ks import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform in ["ks2", "pdd", "douyu", "1688", "taobao"]:
        from utils.platforms.lx_live_monitor_assistant import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform == "tiktok":
        from utils.platforms.tiktok import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform == "twitch":
        from utils.platforms.twitch import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform == "wxlive":
        from utils.platforms.wxlive import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform == "youtube":
        from utils.platforms.youtube import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform == "hntv":
        from utils.platforms.hntv import start_listen

        start_listen(config, common, my_handle, platform)
    elif platform == "ordinaryroad_barrage_fly":
        from utils.platforms.ordinaryroad_barrage_fly import start_listen

        start_listen(config, common, my_handle, platform)

    elif platform == "talk":
        thread.join()


# Exit program
def exit_handler(signum, frame):
    logger.info("Signal received:", signum)


if __name__ == "__main__":
    common = Common()
    config = Config(config_path)
    # Log file path
    log_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    # Configure_logger(log_path)

    platform = config.get("platform")

    # Keyboard listening related
    do_listen_and_comment_thread = None
    stop_do_listen_and_comment_thread_event = None
    # Store loaded model objects
    faster_whisper_model = None
    sense_voice_model = None
    # Recording flag
    is_recording = False
    # Chat wakeup status
    is_talk_awake = False

    # Special signal handling
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    start_server()
