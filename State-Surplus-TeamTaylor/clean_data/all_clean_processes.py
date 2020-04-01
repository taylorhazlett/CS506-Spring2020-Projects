import pandas as pd
from clean_data.clean_owner_names import *


# read the filtered state land data
def all_clean_processes():
    # read in raw data file and agency name file
    raw_df = pd.read_csv('./data/usable_state_land.csv')
    agency_name_df = pd.read_csv('./data/state_agency_addresses.csv')

    # get standard name list and change to upper case
    std_name_list = agency_name_df['Link'].str.upper()
    std_name_list = list(set(std_name_list))

    cleaned_df = pre_clean_user_names(raw_df, agency_name_df)
    similar_ratio_matrix = compare_owner_names(cleaned_df, std_name_list)
    name_dic = find_std_names(similar_ratio_matrix, std_name_list)
    std_owner_df = std_owner_names(cleaned_df, name_dic)

    return std_owner_df

