import mido
import time

port_name = 'loopMIDI Port 2'

print(f"'{port_name}' 포트에서 미디 입력을 기다립니다...")
print("스크립트를 종료하려면 Ctrl+C를 누르세요.")

try:
    with mido.open_input(port_name) as inport:
        # 무한 루프를 돌면서 계속 확인합니다.
        while True:
            # 대기 중인 메시지가 있는지 확인하고, 있으면 처리합니다. (차단하지 않음)
            for msg in inport.iter_pending():
                if msg.type == 'note_on' and msg.velocity > 0:
                    note = msg.note
                    velocity = msg.velocity
                    print(f"음(Note): {note}, 벨로시티(Velocity): {velocity}")
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    note = msg.note
                    print(f"음(Note): {note} 꺼짐")
            
            # CPU 사용량이 100%가 되는 것을 방지하기 위해 아주 잠깐 대기합니다.
            time.sleep(0.01)

except KeyboardInterrupt:
    print("\n프로그램을 종료합니다.")
except (IOError, OSError) as e:
    print(f"\n오류: '{port_name}' 포트를 열 수 없습니다.")
    print("loopMIDI가 실행 중이고 포트 이름이 정확한지 확인하세요.")