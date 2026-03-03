from typing import List, Dict, Any

def get_chord_midi_notes(chord: Dict[str, Any]) -> List[int]:
    root_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    root = root_map.get(chord['r'], 0)
    acc = chord.get('ca', '')
    if acc == '#': root += 1
    elif acc == 'b': root -= 1
    base = 60 + root # C4 base

    intervals = [0] # Intervals relative to root

    # Quality
    quality = chord.get('q', '')
    if quality == 'm': intervals += [3, 7]
    elif quality == 'dim': intervals += [3, 6]
    elif quality == 'aug': intervals += [4, 8]
    elif quality == 'sus2': intervals += [2, 7]
    elif quality == 'sus4': intervals += [5, 7]
    else: intervals += [4, 7] # Default to Major

    # Extension
    ext = chord.get('ext', '')
    if ext == '7':
        intervals.append(9 if quality == 'dim' else 10)
    elif ext == '9':
        intervals += [9 if quality == 'dim' else 10, 14]
    elif ext == '11':
        intervals += [9 if quality == 'dim' else 10, 14, 17]
    elif ext == '13':
        intervals += [9 if quality == 'dim' else 10, 14, 17, 21]

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

    midi_notes = [base + n for n in intervals]

    # Bass
    bass_note = chord.get('b')
    if bass_note:
        b_root = root_map.get(bass_note, 0)
        b_acc = chord.get('ba', '')
        if b_acc == '#': b_root += 1
        elif b_acc == 'b': b_root -= 1
        midi_notes.append(48 + b_root) # C3 base for bass
    else:
        midi_notes.append(48 + root) # Add root as bass by default

    return sorted(list(set(midi_notes)))
