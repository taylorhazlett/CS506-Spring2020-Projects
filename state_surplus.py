import pandas as pd 

accepted_codes = ['910','911','912','913','914','915','916','917','918','919','920','921','922',
				 '923','924','925','926','927','928','929','970','971','972','973','974','975']

#df = pd.read_pickle('mapc.pkl'), pickle used on pc
df = pd.read_csv('mapc.ma_parcels_metrofuture.csv',dtype=object)

def filter_luc(dataframe):
  """filters by land use codes affiliated with MA state agencies
  """
	return df[df['luc_1'].isin(accepted_codes) | df['luc_2'].isin(accepted_codes) | 
		      df['luc_adj_1'].isin(accepted_codes)|
		      df['luc_adj_2'].isin(accepted_codes)]

def filter_bldg(dataframe):
    '''
    Filter on related columns that indicate whether building(s) are present on the land parcel.
    Removes rows that correspond to land parcels that do not contain buildings.
    Ziba specified: 
        bldg_value - for condos, generally includes land value
        bldg_area - may include garages, stairwells, basements, and other uninhabitable areas.
        bldgv_psf - building value $ per sq foot
    Additional: 
        sqm_bldg - parcel area estimated to be covered by a building (sq meters)
        pct_bldg - % parcel area estimated to be covered by a building 
    '''
    
    return dataframe.query('bldg_value > 0 | \
                           bldg_area > 0 | \
                           bldgv_psf > 0 | \
                           sqm_bldg > 0 | \
                           pct_bldg > 0')

land_parcel_df = filter_luc(df)
land_parcel_df = filter_bldg(df)[['bldg_value', 'bldg_area', 'bldgv_psf', 'sqm_bldg', 'pct_bldg']]
