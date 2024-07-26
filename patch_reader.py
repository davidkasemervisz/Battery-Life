import pandas as pd

def read_patch_data(filepath, columns):
    df = pd.read_csv(filepath)
    data = []
    for c in columns:
        data.append(df[c])
    return data

def get_time(time, program_start):
    local_time = []
    last_seconds = -1
    offset = 0
    for t in time:
        tokens = t.split(":")
        hours = int(tokens[0])
        minutes = int(tokens[1])
        seconds = int(tokens[2])
        local_time.append(hours * 60 * 60 + minutes * 60 + seconds - program_start + offset)
        if last_seconds == seconds:
            offset += 0.2
        else:
            last_seconds = seconds
            offset = 0

    return local_time
