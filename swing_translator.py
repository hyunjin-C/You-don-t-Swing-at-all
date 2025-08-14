import mido
import serial
import time

# --- 설정 변수 ---
ARDUINO_PORT = 'COM6'
MIDI_PORT_NAME = 'loopMIDI Port 2'
PULSE_DURATION = 0.05 # 0.05 = 50ms

# --- 메인 코드 ---
try:
    print(f"Arduino에 연결 중... ({ARDUINO_PORT})")
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
    time.sleep(2)
    print("Arduino 연결 성공!")

    # EMS 초기화
    arduino.write(b"1:0,2:0\n")

    print(f"'{MIDI_PORT_NAME}' MIDI 포트 리스닝 시작...")
    with mido.open_input(MIDI_PORT_NAME) as port:
        print("Ableton Live에서 리듬을 재생하세요.")
        
        for msg in port:
            if msg.type == 'note_on':
                command = None
                
                if msg.note == 60: # C4 노트 (Swing Downbeat)
                    intensity = 30 
                    command = f"1:{intensity},2:0\n".encode()
                    print(f"Swing Downbeat 수신 -> 서보1 강도: {intensity}")

                elif msg.note == 62: # D4 노트 (Swing Offbeat)
                    intensity = int((msg.velocity / 127) * 99)
                    command = f"1:0,2:{intensity}\n".encode()
                    print(f" Swing Offbeat 수신 / Velocity: {msg.velocity} -> 서보2 강도: {intensity}")

                if command:
                    arduino.write(command)
                    time.sleep(PULSE_DURATION)
                    arduino.write(b"1:0,2:0\n")

except Exception as e:
    print(f"오류 발생: {e}")
    if 'arduino' in locals() and arduino.is_open:
        arduino.write(b"1:0,2:0\n")
        arduino.close()