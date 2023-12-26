import pandas as pd
from collections import defaultdict
import ocr

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

def return_venue(code, roll, isMid):

    # Store venues in a DF
    venues = ocr.fetch_venues_DF("endsem")

    if isMid:
        venues = ocr.fetch_venues_DF("midsem")
        
    rows = venues[venues["code"]==code]

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
            return "2024-02-24T09:00:00.000Z"
        elif slot == "A1":
            return "2024-02-24T14:00:00.000Z"
        if slot == "B":
            return "2024-02-25T09:00:00.000Z"
        elif slot == "B1":
            return "2024-02-25T14:00:00.000Z"
        if slot == "C":
            return "2024-02-26T09:00:00.000Z"
        elif slot == "C1":
            return "2024-02-26T14:00:00.000Z"
        if slot == "D":
            return "2024-02-27T09:00:00.000Z"
        elif slot == "D1":
            return "2024-02-27T14:00:00.000Z"
        if slot == "E":
            return "2024-02-28T09:00:00.000Z"
        elif slot == "E1":
            return "2024-02-28T14:00:00.000Z"
        if slot == "F":
            return "2024-02-29T09:00:00.000Z"
        elif slot == "F1":
            return "2024-02-29T14:00:00.000Z"
        if slot == "G":
            return "2024-03-01T09:00:00.000Z"
        elif slot == "G1":
            return "2024-03-01T14:00:00.000Z"


def get_endsem_time(slot):
    if pd.isnull(slot):
        return ""
    else:
        if slot == "A":
            return "2024-04-29T09:00:00.000Z"
        elif slot == "A1":
            return "2024-04-29T14:00:00.000Z"
        if slot == "B":
            return "2024-04-30T09:00:00.000Z"
        elif slot == "B1":
            return "2024-04-30T14:00:00.000Z"
        if slot == "C":
            return "2024-05-01T09:00:00.000Z"
        elif slot == "C1":
            return "2024-05-01T14:00:00.000Z"
        if slot == "D":
            return "2024-05-02T09:00:00.000Z"
        elif slot == "D1":
            return "2024-05-02T14:00:00.000Z"
        if slot == "E":
            return "2024-05-03T09:00:00.000Z"
        elif slot == "E1":
            return "2024-05-03T14:00:00.000Z"
        if slot == "F":
            return "2024-05-04T09:00:00.000Z"
        elif slot == "F1":
            return "2024-05-04T14:00:00.000Z"
        if slot == "G":
            return "2024-05-05T09:00:00.000Z"
        elif slot == "G1":
            return "2024-05-05T14:00:00.000Z"
