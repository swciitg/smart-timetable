import pandas as pd
from collections import defaultdict


def read_tt():
    '''
    gets the tt json from tt_slot csv
    '''
    ml_lab = "9:00 - 11:55 AM"
    al_lab = "2:00 - 4:55 PM"
    week_map = {"1": "Monday", "2": "Tuesday",
                "3": "Wednesday", "4": "Thursday", "5": "Friday"}
    lab_codes = ["ML1", "ML2", "ML3", "ML4",
                 "ML5", "AL1", "AL2", "AL3", "AL4", "AL5"]
    tt_json = defaultdict(dict)
    for lab in lab_codes:  # Get the codes for lab
        if lab.startswith("ML") or lab.startswith("AL"):
            if lab[0] == "M":
                tt_json[lab] = {week_map[lab[2]]: ml_lab}  # eg: ML'x'
            else:
                tt_json[lab] = {week_map[lab[2]]: al_lab}
    df = pd.read_csv("data/tt_slots.csv")
    num_days, num_times = df.shape
    for time in range(1,num_times):
        for day in range(num_days):
            slot = df.iloc[day, time]
            tt_json[slot][week_map[str(day+1)]] = df.columns[time] # this will give the time slot
    return tt_json


def return_empty_string(value):
    return '' if pd.isnull(value) else value

def return_venue(rows, roll):
    if len(rows) > 0:
        row = rows[rows["roll"].str.contains(roll)]
        if len(row) > 0:
            return row["venue"].item()
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
