import pandas as pd
import string
from string import digits
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


# pre-clean the owner names in the raw data:

# replace abbreviation, change user_name to uppercase, remove punctuation, sort in alphabet order
def pre_clean_user_names(raw_df, agency_name_df):
    # replace abbreviation with full name
    index = 0
    std_name_list = agency_name_df['Link'].str.upper()
    for abb_name in agency_name_df['Abbreviation']:
        if abb_name == '':
            index += 1
            continue
        raw_df.loc[raw_df['owner_name'] == abb_name] = std_name_list[index]
        index += 1

    # make all owner names uppercase
    raw_df['owner_name'] = raw_df['owner_name'].str.upper()

    # remove the spaces in the front and end of each agency name
    for owner_name in raw_df['owner_name']:
        owner_name.strip()

    # remove punctuations
    punct = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{}~'  # `|` is not present here
    transtab = str.maketrans(dict.fromkeys(punct, ''))
    # remove digits
    remove_digits = str.maketrans('', '', digits)
    raw_df['owner_name'] = '|'.join(raw_df['owner_name'].tolist()).translate(remove_digits).split('|')
    raw_df['owner_name'] = '|'.join(raw_df['owner_name'].tolist()).translate(transtab).split('|')

    # sort in alphabet order
    cleaned_df = raw_df.sort_values(by=['owner_name'])

    return cleaned_df


# receive the pre-cleaned data table and the accurate owner name list
def compare_owner_names(cleaned_df, std_name_list):
    # get a list of user names from the data table and standard agency name table and remove duplicates
    raw_name_list = cleaned_df['owner_name']
    unique_raw_name_ist = list(set(raw_name_list))

    ratio_list = []
    cmp_dic = {}
    # calculate the similarity ratio between each unique raw owner name and the standard owner name
    for name in unique_raw_name_ist:
        for std_name in std_name_list:
            ratio_list.append(fuzz.token_sort_ratio(name, std_name))
        cmp_dic[name] = ratio_list
        ratio_list = []

    similar_ratio_matrix = pd.DataFrame(cmp_dic)

    return similar_ratio_matrix


# find the most similar owner names to the raw name data
def find_std_names(similar_ratio_matrix, std_name_list):
    name_dic = {}
    # Get the index of the largest ratio in the matrix
    # The name associated with such index in the std_name_list is the most likely one
    for index in similar_ratio_matrix.columns:
        std_name_index = similar_ratio_matrix[index].idxmax()
        name_dic[index] = std_name_list[std_name_index]
    return name_dic


# replace the owner name list in the raw data table with std names
def std_owner_names(cleaned_df, name_dic):
    std_owner_df = pd.DataFrame(cleaned_df)
    # add a new column for all the std names to the original table
    std_owner_df['std_owner_name'] = std_owner_df['owner_name']

    # for each name in the original table, go through the std name list searching for the name
    # then add the corresponding std name in the std name list to the newly added column
    for key in name_dic:
        std_owner_df['std_owner_name'].loc[std_owner_df['std_owner_name'] == key] = name_dic[key]

    return std_owner_df




