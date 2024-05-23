import pandas as pd
from collections import defaultdict
import ocr
from semester_constants import *

def readTT():
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


def ensureString(value):
    return '' if pd.isnull(value) else value

def examVenue(code, roll, isMid):

    # Store venues in a DF
    if isMid:
        venues = ocr.fetchVenuesDF("midsem")
    else:
        venues = ocr.fetchVenuesDF("endsem")
        
    rows = venues[venues["code"]==code]

    if len(rows) > 0:
        row = rows[rows["roll"].str.contains(roll)]
        if len(row) > 0:
            return row["venue"].item()
    return ""

def getMidsTime(slot):
    if pd.isnull(slot):
        return ""
    else:
        return MID_TIMINGS[slot]


def getEndsTime(slot):
    if pd.isnull(slot):
        return ""
    else:
        return END_TIMINGS[slot]
