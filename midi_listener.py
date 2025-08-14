import mido
import time

port_name = 'loopMIDI Port 2'

print(f"'{port_name}' 포트에서 미디 입력을 기다립니다...")
print("스크립트를 종료하려면 Ctrl+C를 누르세요.")

try:
    with mido.open_input(port_name) as inport:
        while True:
            for msg in inport.iter_pending():
                if msg.type == 'note_on' and msg.velocity > 0:
                    note = msg.note
                    velocity = msg.velocity
                    print(f"음(Note): {note}, 벨로시티(Velocity): {velocity}")
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    note = msg.note
                    print(f"음(Note): {note} 꺼짐")
            
            time.sleep(0.01)

except KeyboardInterrupt:
    print("\n프로그램을 종료합니다.")
except (IOError, OSError) as e:
    print(f"\n오류: '{port_name}' 포트를 열 수 없습니다.")
    print("loopMIDI가 실행 중이고 포트 이름이 정확한지 확인하세요.")