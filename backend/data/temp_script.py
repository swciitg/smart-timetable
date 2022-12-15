import camelot
import pandas as pd
import os


tables = camelot.read_pdf(
    "coursesjan.pdf", pages='1-end', strip_text='\n')
table_dfs = [table.df.iloc[:, :] for table in tables]
final_df = pd.concat(table_dfs, ignore_index=True)
final_df.to_csv('trycourses.csv', index=False)

# tables = camelot.read_pdf(
#     "freshers.pdf", pages='1-end', strip_text='\n')
# table_dfs = [table.df.iloc[:, :] for table in tables]
# final_df = pd.concat(table_dfs, ignore_index=True)
# final_df.to_csv('fresher_groups_new.csv', index=False)

# df = pd.read_csv("fresher_groups.csv")
# df.columns = df.iloc[0]
# df = df.iloc[1:, :]
# df = df.drop(['Name', 'IITG Email', 'PwD', 'Discipline/Branch Name'], axis=1)
# df.to_csv('freshers.csv',index=False)

# dfloc = pd.read_csv("location.csv",dtype=object)
# dfloc = dfloc.set_index('0')
# # print(df.loc['T1'][0])

# def get_location(row):
#     return dfloc.loc[row['Tutorial']][0]


# df = pd.read_csv("freshers.csv")
# df['Location'] = df.apply(lambda x: get_location(x),axis=1)
# print(df)
# df.to_csv('divisions.csv', index=False)
# # df.columns = df.iloc[0]
# # df = df.iloc[1:, :]
# # df = df.drop(['Name', 'IITG Email', 'PwD', 'Discipline/Branch Name'], axis=1)
# # df.to_csv('freshers.csv',index=False)

# # tables = camelot.read_pdf("tt.pdf", pages='3-end', strip_text='\n')
# # table_dfs = [table.df.iloc[1:, :] for table in tables]
# # final_df = pd.concat(table_dfs, ignore_index=True)
# # final_df.to_csv('location.csv', index=False)