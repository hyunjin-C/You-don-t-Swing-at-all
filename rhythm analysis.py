import mido

def analyze_swing(filename):
    """
    MIDI 파일을 분석하여 각 노트의 절대 시작 시간, Velocity,
    그리고 연속된 노트 간의 시간 간격과 비율을 출력합니다.
    """
    try:
        mid = mido.MidiFile(filename)
        print(f"\n--- 분석 시작: {filename} ---")
    except FileNotFoundError:
        print(f"오류: '{filename}' 파일을 찾을 수 없습니다.")
        return

    ticks_per_beat = mid.ticks_per_beat or 480
    tempo = 500000  # 기본 템포 (120 BPM)

    notes = []
    absolute_time_ticks = 0
    for track in mid.tracks:
        for msg in track:
            absolute_time_ticks += msg.time
            if msg.is_meta and msg.type == 'set_tempo':
                tempo = msg.tempo
            if msg.type == 'note_on' and msg.velocity > 0:
                start_time_sec = mido.tick2second(absolute_time_ticks, ticks_per_beat, tempo)
                notes.append({
                    'start_time_ms': round(start_time_sec * 1000),
                    'velocity': msg.velocity
                })
    
    # 시간 순서대로 정렬
    notes.sort(key=lambda x: x['start_time_ms'])

    print(f"{'노트 #':<8} | {'시작 시간 (ms)':<15} | {'Velocity':<10} | {'이전 노트와의 간격 (ms)':<25} | {'타이밍 비율':<20}")
    print("-" * 90)

    previous_start_time_ms = 0

    for i, note in enumerate(notes):
        start_time_ms = note['start_time_ms']
        delta_ms = start_time_ms - previous_start_time_ms
        
        ratio_str = "-"
        if i > 1: # 세 번째 노트부터 비율을 계산해야 의미가 있음
            # 이전 두 노트 간의 간격을 계산
            prev_delta_ms = notes[i-1]['start_time_ms'] - notes[i-2]['start_time_ms']
            if prev_delta_ms > 0:
                ratio = delta_ms / prev_delta_ms
                ratio_str = f"{ratio:.2f} : 1"

        print(f"{i+1:<8} | {start_time_ms:<15} | {note['velocity']:<10} | {delta_ms:<25} | {ratio_str:<20}")
        
        previous_start_time_ms = start_time_ms


# --- 메인 실행 ---
analyze_swing("MIDI files/straight_rhythm.mid")
analyze_swing("MIDI files/swing_rhythm.mid")
analyze_swing("MIDI files/my_rhythm.mid")
