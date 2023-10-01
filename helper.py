import pandas as pd

def return_empty_string(value):
    return '' if pd.isnull(value) else value

def return_venue(row, roll):
    rolls = row["roll"].str.split(',').to_numpy()[0]
    if str(roll) in rolls:
        return row["venue"].item()
    else:
        return ""

def get_midsem_time(slot):
    if pd.isnull(slot):
        return ""
    else:
        if slot == "A":
            return "2023-09-18T09:00:00.000Z"
        elif slot == "A1":
            return "2023-09-18T14:00:00.000Z"
        if slot == "B":
            return "2023-09-19T09:00:00.000Z"
        elif slot == "B1":
            return "2023-09-19T14:00:00.000Z"
        if slot == "C":
            return "2023-09-20T09:00:00.000Z"
        elif slot == "C1":
            return "2023-09-20T14:00:00.000Z"
        if slot == "D":
            return "2023-09-21T09:00:00.000Z"
        elif slot == "D1":
            return "2023-09-21T14:00:00.000Z"
        if slot == "E":
            return "2023-09-22T09:00:00.000Z"
        elif slot == "E1":
            return "2023-09-22T14:00:00.000Z"
        if slot == "F":
            return "2023-09-23T09:00:00.000Z"
        elif slot == "F1":
            return "2023-09-23T14:00:00.000Z"
        if slot == "G":
            return "2023-09-24T09:00:00.000Z"
        elif slot == "G1":
            return "2023-09-24T14:00:00.000Z"

def get_endsem_time(slot):
    if pd.isnull(slot):
        return ""
    else:
        if slot == "A":
            return "2023-11-19T09:00:00.000Z"
        elif slot == "A1":
            return "2023-11-19T14:00:00.000Z"
        if slot == "B":
            return "2023-11-20T09:00:00.000Z"
        elif slot == "B1":
            return "2023-11-20T14:00:00.000Z"
        if slot == "C":
            return "2023-11-21T09:00:00.000Z"
        elif slot == "C1":
            return "2023-11-21T14:00:00.000Z"
        if slot == "D":
            return "2023-11-22T09:00:00.000Z"
        elif slot == "D1":
            return "2023-11-22T14:00:00.000Z"
        if slot == "E":
            return "2023-11-23T09:00:00.000Z"
        elif slot == "E1":
            return "2023-11-23T14:00:00.000Z"
        if slot == "F":
            return "2023-11-24T09:00:00.000Z"
        elif slot == "F1":
            return "2023-11-24T14:00:00.000Z"
        if slot == "G":
            return "2023-11-25T09:00:00.000Z"
        elif slot == "G1":
            return "2023-11-25T14:00:00.000Z"
