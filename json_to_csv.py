import pandas as pd

df = pd.read_json(r'Users/macbookpro/PycharmProjects/SwEng-group13/fetched_data/flutter_issues.json')
df.to_csv(r'Users/macbookpro/PycharmProjects/SwEng-group13/fetched_data/flutter_issues.csv', index = None)