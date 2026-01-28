# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 12:05:53 2024

@author: mcustado
"""

import pandas as pd
import matplotlib.pyplot as plt

# INSTRUCTIONS: Save data summary tabs in separate CSV files from the dataset linked in: https://doi.org/10.5281/zenodo.15724097 

# import datasets
df_author = pd.read_csv('...\\author_data_clean.csv') # modifiy file directory path of input file
df_author['name'] = df_author['name'].str.lower()

df_funding = pd.read_csv('...\\funding_statement_data_clean.csv') # modify file directory path of input file
df_pub = pd.read_csv('...\\publication_data_clean.csv') # modify file directory path of input file

df_pub = df_pub[df_pub['article_id'] != 367]
df_pub = df_pub[df_pub['article_id'] != 617]
df_pub = df_pub[df_pub['article_id'] != 732]

df_pub['# of SEA inst'] = df_pub['# of SEA inst'].astype(int)
df_pub['# of unique author + country'] = df_pub['# of unique author + country'].astype(int)

# import auxiliary dataset (region.csv is included as a supplemental file)
df_region = pd.read_csv('...\\region.csv') # modify file directory path of input file

#%% unique author+country 
df_author_ = df_author.drop(['article_id'], axis=1)
df_author_ = df_author_.drop_duplicates()
df_author_ = pd.merge(df_author_, df_region)

# count number of authors with multiple country affiliations
df_authors_list = df_author_.pivot_table(index=['name'], aggfunc='size')
df_bool = (df_authors_list > 1)

# count of SEA authors with multiple country affiliations
df_authors_list_sea = df_author.pivot_table(index=['name'], columns=['SEA?'], aggfunc='size')
df_temp = df_authors_list_sea.loc[df_authors_list[df_bool].index] # extract authors with multiple affiliations
dup_authors_sea = len(df_temp['Yes'].dropna())

print("Total number of unique author+country pairs:\t", len(df_author_),
      "\nTotal number of unique authors:\t", df_author['name'].nunique(),
      "\nTotal number of authors with multiple country affiliations:\t", df_bool.sum(),
      "\nTotal number of authors with multiple country affiliations that include at least one SEA:\t", dup_authors_sea,
      "\nTotal number of unique countries:\t", df_author['country'].nunique())

#%% per publication

print("Total number of manuscripts with at least one SEA:\t", df_pub[df_pub['# of SEA inst'].astype('int64') > 0].count()['article_id']) 

#%% unique article_id + funding country

nan_count = df_funding[df_funding['countries'] =='-']['article_id'].count()
df_funding_ = df_funding[df_funding['countries'] != '-'].drop_duplicates()

# count number of articles with multiple country funders
df_funding_list = df_funding_.pivot_table(index=['article_id'], aggfunc='size')
df_bool2 = (df_funding_list > 1)

# count number of articles with multiple country funders that include at least one SEA
df_funding_list_reg = df_funding_.pivot_table(index=['article_id'], columns=['region'], aggfunc='size')
df_temp = df_funding_list_reg.loc[df_funding_list[df_bool2].index]['Southeast Asia'] # extract authors with multiple affiliations
dup_funding_sea = len(df_temp.dropna())

print("Total number of articles without info:\t", nan_count,
      "\nTotal number of articles with multiple country funders:\t", df_bool2.sum(),
      "\nTotal number of articles with multiple country funders that include at least one SEA:\t", dup_funding_sea,
      "\nTotal number of unique countries:\t", df_funding_['countries'].nunique())

# count regional funders and save in separate variables
region_count_fund = df_funding_.groupby(['region']).count() # funders per region
fund_country_count = df_funding_.groupby(['countries']).count() # funders per country

#%% unique article_id + author_country  for count and citations

id_country = df_author[['article_id','country']].drop_duplicates()
id_country_pub = pd.merge(id_country, df_pub, on='article_id')
id_country_pub = pd.merge(id_country_pub, df_region)

# citation count
id_country_cite = id_country_pub.groupby(['country'])['times_cited'].sum()
id_region_cite = id_country_pub.groupby(['region'])['times_cited'].sum()
id_country_pub[['region','article_id']].drop_duplicates()

id_country_count = id_country.groupby(['country'])['article_id'].count() # article count per country
id_region_count = id_country_pub[['region','article_id']].drop_duplicates().groupby(['region'])['article_id'].count() # article count per region
#%% per year plots

# group authorship data per year 
year_all_auth = df_pub.groupby(['year'])['# of unique author + country'].sum()
year_all_articles = df_pub.groupby(['year'])['article_id'].count()

year_sea_auth = df_pub.groupby(['year'])['# of SEA inst'].sum()
perc_sea_auth = 100*year_sea_auth/year_all_auth
sea_manus = df_pub[df_pub['# of SEA inst']!=0]

year_sea_manus = sea_manus.groupby(['year'])['# of SEA inst'].count()
perc_sea_manus = 100*year_sea_manus/year_all_articles

# % SEA share of citations per year
cite_year_all_count = id_country_pub.groupby(['year'])['times_cited'].sum()
cite_year_sea_count = id_country_pub.pivot_table(index=['year'], columns=['region'], values=['times_cited'], aggfunc='sum')[('times_cited','Southeast Asia')]
cite_year_sea_perc = 100*cite_year_sea_count/cite_year_all_count

# % SEA author per publication
df_pub['perc_sea_authors'] = 100*df_pub['# of SEA inst']/df_pub['# of unique author + country']

sea_manus_0 = df_pub[df_pub['perc_sea_authors']==0]
sea_manus_100 = df_pub[df_pub['perc_sea_authors']==100]
sea_manus_bet = df_pub[(df_pub['perc_sea_authors'] > 0) & (df_pub['perc_sea_authors'] < 100)]

year_sea_manus_0 = sea_manus_0.groupby(['year'])['article_id'].count()
year_sea_manus_100 = sea_manus_100.groupby(['year'])['article_id'].count()
year_sea_manus_bet = sea_manus_bet.groupby(['year'])['article_id'].count()

plt.rcParams.update({'font.size': 10})

fig, (ax1, ax3) = plt.subplots(2,figsize=(10,10))

ax1.grid(visible=True, axis='y')
ax1.bar(year_all_auth.index, year_all_auth, hatch='////', color = 'white', edgecolor='black', label = "Authors", zorder=5)
ax1.bar(year_all_auth.index, year_sea_auth, color='#440154', edgecolor='black', label = "SEA-affiliated authors",  zorder=6)
ax1.set_ylabel("Country-affiliated author count")
ax1.set_xticks(year_all_auth.index)

axb = ax1.twinx()
axb.plot(year_all_auth.index, perc_sea_auth, color='#21918c', lw = 2, label = "% SEA-affiliated authors",  zorder=6)
axb.set_ylabel("Percent, %", rotation=270, labelpad=14)
axb.set_ylim(0,100)

h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = axb.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, loc=2)

ax3.grid(visible=True, axis='y')
# First layer (bottom of stack)
ax3.bar(year_all_articles.index, year_sea_manus_100, 
        color='#5ec962', edgecolor='black', label="Only SEA-affiliated authors", zorder=5)

# Second layer (stacked on top of the first)
ax3.bar(year_all_articles.index, year_sea_manus_bet, 
        bottom=year_sea_manus_100, color='#440154', edgecolor='black', label="Mixed SEA and non-SEA-affiliated authors", zorder=5)

# Third layer (stacked on top of the second)
ax3.bar(year_all_articles.index, year_sea_manus_0, 
        bottom=year_sea_manus_100 + year_sea_manus_bet, hatch='\\\\', color = 'white', edgecolor='black', label="No SEA-affiliated authors", zorder=5)


ax3.set_ylabel("Article count")
ax3.set_xticks(year_all_articles.index)


axc = ax3.twinx()
axc.plot(year_all_auth.index, perc_sea_manus, color='#21918c', lw = 2, label = "% of SEA-affiliated articles (≥1 SEA-affiliated author)",  zorder=6)
axc.set_ylabel("Percent, %", rotation=270, labelpad=14)
axc.set_ylim(0,100)

h1, l1 = ax3.get_legend_handles_labels()
h2, l2 = axc.get_legend_handles_labels()
ax3.legend(h1+h2, l1+l2, loc=2)
ax3.set_xlabel("Year")

plt.savefig('...\\fig_6.png', bbox_inches="tight", dpi=600) # modifiy file directory path of output file