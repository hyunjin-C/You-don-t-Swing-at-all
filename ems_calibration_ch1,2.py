import serial
import time
import keyboard
import json

# --- 설정 ---
ARDUINO_PORT = 'COM6' 
CONFIG_FILENAME = 'calibration_data.json'

def calibrate_channel(arduino, channel_num, ch1_max_intensity=None):
    """지정된 채널 번호의 최소/최대 강도를 측정하는 함수"""
    print(f"\n--- 채널 {channel_num} 캘리브레이션을 시작합니다 ---")
    print("키보드의 [↑]를 눌러 강도를 올리고, [↓]로 내립니다.")
    print("자극이 처음 느껴지면 [스페이스 바]를 누르세요.")
    print("🚨 안전 기능: 숫자 [0]을 누르면 즉시 모터가 초기화됩니다.")
    
    intensity = 0
    min_val = None
    
    while True:
        event = keyboard.read_event(suppress=True)
        
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'up':
                intensity = min(intensity + 1, 99)
            elif event.name == 'down':
                intensity = max(intensity - 1, 0)
            elif event.name == '0':
                intensity = 0
                arduino.write(b"1:0,2:0\n")
                print(f"모터 초기화됨. 현재 강도: {intensity: <2}", end='\r')
            
            if event.name in ['up', 'down']:  
                if channel_num == 1:
                    command_str_on = f"1:{intensity},2:0\n"
                else:
                    command_str_on = f"1:{ch1_max_intensity},2:{intensity}\n"

                arduino.write(command_str_on.encode())
                print(f"현재 강도: {intensity: <2}", end='\r')

            elif event.name == 'space':
                if min_val is None:
                    min_val = intensity
                    print(f"\n>> 채널 {channel_num}의 최소 인지 강도 저장됨: {min_val}")
                    print("\n--- '편안한 최대 강도'를 설정합니다 ---")
                    print("[↑], [↓]로 조절 후, 적절한 지점에서 [스페이스 바]를 다시 누르세요.")
                else:
                    max_val = intensity
                    if max_val < min_val:
                        print("! 경고: 최대 강도가 최소 강도보다 작습니다. 다시 시도하세요.")
                        min_val = None
                        print(f"\n--- 채널 {channel_num}의 최소 인지 강도를 다시 설정합니다 ---")
                    else:
                        print(f"\n>> 채널 {channel_num}의 편안한 최대 강도 저장됨: {max_val}")
                        return min_val, max_val

arduino = None
try:
    print(f"Arduino에 연결 중... ({ARDUINO_PORT})")
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
    time.sleep(2)
    print("Arduino 연결 성공!")
    arduino.write(b"1:0,2:0\n") 

    # --- 채널 1 캘리브레이션 실행 ---
    ch1_min, ch1_max = calibrate_channel(arduino, 1)

    # --- 채널 2 캘리브레이션 실행 ---
    ch2_min, ch2_max = calibrate_channel(arduino, 2, ch1_max_intensity=ch1_max)

    print("\n--- 모든 캘리브레이션 완료! ---")
    arduino.write(b"1:0,2:0\n")
    print("모든 채널이 0으로 초기화되었습니다.")

    
    config_data = {
        "channel_1": {
            "min_intensity": ch1_min,
            "max_intensity": ch1_max
        },
        "channel_2": {
            "min_intensity": ch2_min,
            "max_intensity": ch2_max
        }
    }
    with open(CONFIG_FILENAME, 'w') as f:
        json.dump(config_data, f, indent=4)
    print(f"측정된 값이 '{CONFIG_FILENAME}' 파일에 저장되었습니다.")

except KeyboardInterrupt:
    print("\n사용자에 의해 프로그램이 중단되었습니다. 서보모터를 초기화합니다.")
except Exception as e:
    print(f"오류 발생: {e}")
finally:
    if arduino and arduino.is_open:
        print("연결을 종료합니다.")
        try:
            arduino.write(b"1:0,2:0\n")
            arduino.close()
        except serial.serialutil.SerialException:
            print("포트가 정상적으로 닫혔습니다.")