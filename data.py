import pandas as pd


def fetch_courses_df():
    '''
    Fetches all the courses from a saved CSV file

    Since generation of CSV file takes time, this function
    is useful to immediately extract data from CSV and store
    in a pandas DataFrame

    Arguments:
        None
    Returns:
        A dataframe with all courses or an empty dataframe incase of an exception
    '''
    try:
        df = pd.read_csv(r'data/courses_csv.csv',dtype=str)
        # return df.drop_duplicates('code')
        return df  # Assume no duplicates
    except Exception:
        return pd.DataFrame()


def fetch_division_mapping(roll_number):
    '''
    Fetches all the fresher divisions from a saved CSV file
    Sample response:
        {'Division': 'III', 'Tutorial': 'T15', 'Lab': 'L6', 'Location': '5106'}
    Arguments:
        roll_number: a str 
    Returns:
        A dictionary of the students division mappings
    '''
    df = pd.read_csv(r'data/divisions.csv',dtype=object)
    df = df.set_index('Roll no')
    x=df.loc[roll_number]
    return x.to_dict()


def fetch_exam_venue_df(sem):
    '''
    Fetches all the exam venues from a saved CSV file

    Arguments:
        sem: a string, "midsem" or "endsem"
    Returns:
        A dataframe with all midsem/endsem venue data
    '''
    try:
        df = pd.read_csv(f'data/{sem}_venue.csv', dtype=str)
        return df  # Assume no duplicates
        # return df.drop_duplicates('code')
    except Exception:
        return pd.DataFrame(columns=["code", "venue", "roll"])
