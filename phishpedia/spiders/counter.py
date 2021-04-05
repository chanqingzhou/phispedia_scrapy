import pandas as pd
counter = 0
df = pd.read_csv('D:/junyang/phispedia/phispedia_scrapy/phishpedia/spiders/retry.csv')
for i in range(len(df)):
	row = df.iloc[i]
	if (row['yes'] > 0 or row['unsure'] > 0 ) and row['no'] == 0:
		url = row['url']
		counter +=1
		continue
print(counter)