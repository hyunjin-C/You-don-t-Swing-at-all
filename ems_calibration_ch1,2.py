import serial
import time
import keyboard
import json

# --- 설정 ---
ARDUINO_PORT = 'COM6' 
CONFIG_FILENAME = 'calibration_advanced.json'

def get_intensity_from_user(arduino, channel_num, prompt_message, start_intensity=0):
    """사용자에게 특정 강도를 측정하도록 안내하고 값을 반환하는 헬퍼 함수"""
    print(f"\n{prompt_message}")
    print("[↑],[↓]로 조절 후 [스페이스 바]를 눌러 확정하세요.")
    
    # 이전 단계에서 확정한 값으로 강도 초기화
    intensity = start_intensity
    
    # 현재 강도로 자극을 시작하고 화면에 표시
    command_str = f"{channel_num}:{intensity},{'2' if channel_num == 1 else '1'}:0\n"
    arduino.write(command_str.encode())
    print(f"현재 강도: {intensity: <2}", end='\r')

    while True:
        event = keyboard.read_event(suppress=True)
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'up': intensity = min(intensity + 1, 99)
            elif event.name == 'down': intensity = max(intensity - 1, 0)
            elif event.name == '0':
                intensity = 0
                arduino.write(b"1:0,2:0\n")
            
            if event.name in ['up', 'down', '0']:
                command_str = f"{channel_num}:{intensity},{'2' if channel_num == 1 else '1'}:0\n"
                arduino.write(command_str.encode())
                print(f"현재 강도: {intensity: <2}", end='\r')
            
            elif event.name == 'space':
                print(f"\n>> 값 확정: {intensity}")
                return intensity

def calibrate_single_channel(arduino, channel_num):
    """하나의 채널에 대해 4단계 캘리브레이션을 진행"""
    print(f"\n{'='*10} 채널 {channel_num} 캘리브레이션 시작 {'='*10}")
    
    # 각 단계가 이전 단계의 값을 시작점으로 사용하도록 수정
    min_p = get_intensity_from_user(arduino, channel_num, "1/4: '최소 인지 강도'를 설정합니다 (겨우 느껴지는 지점).", start_intensity=0)
    comf_h = get_intensity_from_user(arduino, channel_num, "2/4: '확실한 햅틱 강도'를 설정합니다 (움직임 없는 최대 진동).", start_intensity=min_p)
    min_a = get_intensity_from_user(arduino, channel_num, "3/4: '최소 근육 수축 강도'를 설정합니다 (근육이 처음 움찔하는 지점).", start_intensity=comf_h)
    max_a = get_intensity_from_user(arduino, channel_num, "4/4: '편안한 최대 수축 강도'를 설정합니다 (아프지 않은 최대 움직임).", start_intensity=min_a)

    if not min_p <= comf_h <= min_a <= max_a:
        print("\n! 경고: 강도 값의 순서가 올바르지 않습니다 (최소인지 <= 햅틱 <= 최소수축 <= 최대수축).")
        print("해당 채널의 캘리브레이션을 다시 시작합니다.")
        return calibrate_single_channel(arduino, channel_num)

    return {"min_perception": min_p, "comfortable_haptic": comf_h, "min_actuation": min_a, "max_actuation": max_a}

# --- 메인 코드 ---
arduino = None
try:
    print(f"Arduino에 연결 중... ({ARDUINO_PORT})")
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
    time.sleep(2)
    arduino.write(b"1:0,2:0\n") 
    print("Arduino 연결 성공!")

    channel_1_data = calibrate_single_channel(arduino, 1)
    channel_2_data = calibrate_single_channel(arduino, 2)

    print("\n--- 모든 캘리브레이션 완료! ---")
    arduino.write(b"1:0,2:0\n") # 명시적인 안전 초기화
    print("모든 채널이 0으로 초기화되었습니다.")
    
    config_data = {
        "channel_1": channel_1_data,
        "channel_2": channel_2_data
    }
    with open(CONFIG_FILENAME, 'w') as f:
        json.dump(config_data, f, indent=4)
    print(f"측정된 값이 '{CONFIG_FILENAME}' 파일에 저장되었습니다.")

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