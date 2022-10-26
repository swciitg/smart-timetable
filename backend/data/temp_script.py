import camelot
import pandas as pd
import os

# tables = camelot.read_pdf(
#     "freshers.pdf", pages='1-end', strip_text='\n')
# table_dfs = [table.df.iloc[1:, :] for table in tables]
# final_df = pd.concat(table_dfs, ignore_index=True)
# final_df.to_csv('fresher_groups.csv', index=False)

df = pd.read_csv("fresher_groups.csv")
df.columns = df.iloc[0]
df = df.iloc[1:, :]
df = df.drop(['Name', 'IITG Email', 'PwD', 'Discipline/Branch Name'], axis=1)
df = df.set_index(['Roll no'])
print(df.loc(['220104001'], ))
