# === Pilot 1 ===
# EMS 시스템 지연 시간 계산을 위한 테스트입니다.


import mido
import serial
import time
import json
import os

# --- 설정 ---
ARDUINO_PORT = 'COM6' 
MIDI_PORT_NAME = 'loopMIDI Port 0'
CONFIG_FILENAME = 'calibration_advanced.json'

# --- 헬퍼 함수 ---
def calculate_intensity(min_val, max_val, ratio):
    """주어진 최소/최대 범위 내에서 비율에 맞는 강도를 계산"""
    return int(min_val + (max_val - min_val) * ratio)

# --- 메인 코드 ---
arduino = None
try:
    # 1. 캘리브레이션 파일 불러오기
    if not os.path.exists(CONFIG_FILENAME):
        print(f"'{CONFIG_FILENAME}' 파일이 없습니다. 'calibration_advanced.py'를 먼저 실행해주세요.")
        exit()

    with open(CONFIG_FILENAME, 'r') as f:
        config = json.load(f)
        ch1_config = config['channel_1']
        ch1_min_act = ch1_config['min_actuation']
        ch1_max_act = ch1_config['max_actuation']
    
    print("서스테인 모드(단일 채널)로 실행합니다.")
    print(f"설정 값 로드 완료: 손등({ch1_min_act}-{ch1_max_act})")

    # 2. 장치 연결
    print(f"Arduino에 연결 중... ({ARDUINO_PORT})")
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
    time.sleep(2)
    print("Arduino 연결 성공!")
    arduino.write(b"1:0,2:0\n") 

    print(f"'{MIDI_PORT_NAME}' MIDI 포트 리스닝 시작...")
    with mido.open_input(MIDI_PORT_NAME) as port:
        print("Ableton Live에서 리듬을 재생하거나 건반을 눌러보세요. (중단하려면 Ctrl+C)")
        
        for msg in port:
            # --- note_on: 건반을 눌렀을 때 ---
            # Velocity가 0보다 큰 note_on 메시지는 실제 건반을 누른 것으로 간주
            if msg.type == 'note_on' and msg.velocity > 0 and msg.note in [64]:
                velocity_ratio = msg.velocity / 127.0
                intensity = calculate_intensity(ch1_min_act, ch1_max_act, velocity_ratio)
                
                note_name = "F4"
                print(f"Note ON ({note_name}, V:{msg.velocity}) -> 손등 강도:{intensity}")

                # 계산된 강도로 자극 '시작'
                command = f"1:{intensity},2:0\n".encode()
                arduino.write(command)

            # --- note_off: 건반을 뗐을 때---
            # type이 note_off이거나, velocity가 0인 note_on 메시지는 건반을 뗀 것으로 간주
            elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)) and msg.note in [64]:
                note_name = "F4"
                print(f"Note OFF ({note_name}) -> 자극 종료")
                
                # 자극 '종료'
                arduino.write(b"1:0,2:0\n")

except KeyboardInterrupt:
    print("\n사용자에 의해 프로그램이 중단되었습니다.")
except Exception as e:
    print(f"오류 발생: {e}")
finally:
    if arduino and arduino.is_open:
        print("서보모터를 초기화하고 연결을 종료합니다.")
        try:
            arduino.write(b"1:0,2:0\n")
            arduino.close()
        except serial.serialutil.SerialException:
            print("포트가 정상적으로 닫혔습니다.")