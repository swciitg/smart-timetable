import camelot
import pandas as pd


def generate_all_courses_CSV(url):
    '''
    Generate CSV file corresponding to the PDF file

    This function generates a CSV file, given the URl of a PDF file. 
    It makes use of camelot-py (https://pypi.org/project/camelot-py/)

    Arguments:
        url: a string
    Returns:
        A dictionary message or None incase of an exception
    '''
    try:
        tables = camelot.read_pdf(url, pages='1-end', strip_text='\n')
        table_dfs = [table.df.iloc[1:, :] for table in tables]
        final_df = pd.concat(table_dfs, ignore_index=True)
        final_df.to_csv('data/courses_csv.csv', index=False)
        return {'message': 'Successfully converted and saved CSV file'}
    except Exception:
        return None


def fetch_all_courses_DF():
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
        df = pd.read_csv(r'data/courses_csv.csv')
        return df.drop_duplicates('1')
    except Exception:
        return pd.DataFrame()


def get_fresher_DF(roll_number):
    df = pd.read_csv(r'data/divisions.csv',dtype=object)
    df = df.set_index('Roll no')
    x=df.loc[roll_number]
    return x.to_dict()