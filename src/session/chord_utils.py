from typing import List, Dict, Any

def get_chord_midi_notes(chord: Dict[str, Any]) -> List[int]:
    root_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    root = root_map.get(chord['r'], 0)
    acc = chord.get('ca', '')
    if acc == '#': root += 1
    elif acc == 'b': root -= 1

    # Base octave logic: Keep roots in G3-F#4 range (55-66)
    base = 60 + root
    if root >= 7:
        base -= 12

    intervals = [0] # Intervals relative to root

    # Quality
    quality = chord.get('q', '')
    if quality == 'm': intervals += [3, 7]
    elif quality == 'dim': intervals += [3, 6]
    elif quality == 'aug': intervals += [4, 8]
    elif quality == 'sus2': intervals += [2, 7]
    elif quality == 'sus4': intervals += [5, 7]
    elif quality == 'msus2': intervals += [2, 3, 7]
    elif quality == 'msus4': intervals += [3, 5, 7]
    else: intervals += [4, 7] # Default to Major

    # Extension
    ext = chord.get('ext', '')
    if ext:
        # Determine 7th/6th interval
        is_major_7 = any(m in ext for m in ['maj', 'M'])
        if is_major_7:
            intervals.append(11)
        elif ext == '6':
            intervals.append(9)
        elif any(x in ext for x in ['7', '9', '11', '13']):
            intervals.append(9 if quality == 'dim' else 10)

        # Add higher extensions
        if '9' in ext: intervals.append(14)
        if '11' in ext: intervals.append(17)
        if '13' in ext: intervals.append(21)

    # Alterations
    for alt_val in chord.get('alt', []):
        if alt_val == 'b5':
            if 7 in intervals: intervals[intervals.index(7)] = 6
            else: intervals.append(6)
        elif alt_val == '#5':
            if 7 in intervals: intervals[intervals.index(7)] = 8
            else: intervals.append(8)
        elif alt_val == 'b9': intervals.append(13)
        elif alt_val == '#9': intervals.append(15)
        elif alt_val == '#11': intervals.append(18)
        elif alt_val == 'b13': intervals.append(20)

    # Additions
    for add_val in chord.get('add', []):
        if add_val == 'add9': intervals.append(14)
        elif add_val == 'add11': intervals.append(17)
        elif add_val == 'add13': intervals.append(21)
        elif add_val == 'add2': intervals.append(2)
        elif add_val == 'add4': intervals.append(5)

    midi_notes = [base + n for n in intervals]

    # Bass
    bass_note = chord.get('b')
    if bass_note:
        b_root = root_map.get(bass_note, 0)
        b_acc = chord.get('ba', '')
        if b_acc == '#': b_root += 1
        elif b_acc == 'b': b_root -= 1
        midi_notes.append(36 + b_root) # C2 base for bass
    else:
        midi_notes.append(36 + root) # Add root as bass by default

    return sorted(list(set(midi_notes)))
