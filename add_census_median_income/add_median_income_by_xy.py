import pandas as pd
import numpy as np
import requests
from pprint import pprint
from datetime import datetime
from statistics import mean
from pyproj import CRS, Transformer

def add_census_median_hh_income(dataframe):
    '''
        Adds a column containing Census 2010 Median HH Income data for each land parcel to the dataframe.
        Process:
            - Converts parloc_id coordinates to longitude, latitude coordinates for each of the land parcels.
            - Utilizes these longitude, latitude coordinates to obtain census tract numbers.
            - Downloads median household income for all tracts in MA.
            - Matches tract numbers in both tables to combine median income data into the input dataframe.
        Outputs: dataframe object with added columns
            - longitude
            - latitude
            - census_tract
            - median_hh_income
        ** Note: intermediate .csv files are outputted to the current directory:
            - state_land_plus_long_lat.csv (input dataframe + longitude, latitude columns)
            - ma_med_income_tract.csv (table containing Census tract number and corresponding median household income)
            - state_land_plus_med_income.csv (input dataframe + longitude, latitude + median household income)
    '''

    ###########################################################################
    ###########################################################################
    #                        FUNCTION DEFINITIONS                             #
    ###########################################################################
    ###########################################################################
    def add_long_lat(dataframe):
        '''
        Uses parloc_id column in land parcel database (i.e. X, Y coordinates in NAD83 spatial reference)
        and transforms them into longitude, latitude coordinates (in ESPG:4326 = WGS84). Saves corresponding longitude, latitude
        coordinate information for each record in new columns appended to original dataframe.
        Note: parloc_id may start with 'F_' or 'M_' (designating feet or meters).
            For feet, initial spatial reference NAD83 is equivalent to ESPG:3586.
            For meters, initial spatial reference NAD83 is equivalent to ESPG:26986.
        '''
        # need to reset indices to account for removal of rows from filtering
        dataframe = dataframe.reset_index()

        # add columns to store longitude and latitude coordinates
        dataframe['longitude'] = np.nan
        dataframe['latitude'] = np.nan

        # convert parloc_id column to longitude, latitude coordinates
        crs_4326 = CRS.from_epsg(4326) # target spatial reference to transform to
        crs_26986 = CRS.from_epsg(26986) # for coordinates in meters
        crs_3586 = CRS.from_epsg(3586) # for coordinates in feet

        transformer_meters = Transformer.from_crs(crs_26986, crs_4326, always_xy=True)
        transformer_feet = Transformer.from_crs(crs_3586, crs_4326, always_xy=True)

        for i in range(len(dataframe)):
            # make sure there are no whitespaces
            parloc_id = str(dataframe.at[i, 'parloc_id']).replace(" ", "")
            dataframe.at[i, 'parloc_id'] = parloc_id
            
            if (parloc_id.startswith('F')):
                end_x_idx = parloc_id.find('_', 2)
                x = parloc_id[2:end_x_idx]
                y = parloc_id[end_x_idx+1:]
                longitude, latitude = transformer_feet.transform(x, y)
                dataframe.at[i, 'longitude'] = longitude
                dataframe.at[i, 'latitude'] = latitude
            elif (parloc_id.startswith('M')):
                end_x_idx = parloc_id.find('_', 2)
                x = parloc_id[2:end_x_idx]
                y = parloc_id[end_x_idx+1:]
                longitude, latitude = transformer_meters.transform(x, y)
                dataframe.at[i, 'longitude'] = longitude
                dataframe.at[i, 'latitude'] = latitude
            else:
                print('At index ', i, ' parloc_id does not start with M_ or F_')

        # outputs dataframe with addition of longitude, latitude columns to .csv file in current directory
        dataframe.to_csv('state_land_plus_long_lat.csv',index=False)

        return dataframe

    def add_tract_numbers(dataframe):
        '''
            Adds a 'census_tract' column to the input dataframe. 
            Uses helper method get_tract_number to populate the column with data. 
        '''

        def get_tract_number(longitude, latitude):
            '''
                Makes a REST API request to Census Geocoder API and returns a tract number for a given address.
                Inputs:
                    - longitude, latitude coordinates of the land parcel
            '''
            URL = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=" + str(longitude) \
                + "&y=" + str(latitude) \
                + "&benchmark=Public_AR_Census2010&vintage=Census2010_Census2010&layers=14&format=json"

            response = requests.get(url = URL)
            tract = np.nan
            
            if (response.status_code == 200):
                data = response.json()
                # pprint(data)
                if (len(data['result']['geographies']['Census Blocks']) > 0):
                    # if data['result']['addressMatches'][0]['geographies']['Census Blocks'][0]['TRACT']:
                    tract = data['result']['geographies']['Census Blocks'][0]['TRACT']
            
            return tract

        dataframe['census_tract'] = np.nan

        for i in range(len(dataframe)):
            x = dataframe.at[i, 'longitude'] 
            y = dataframe.at[i, 'latitude']

            if (i % 100 == 0):
                print('Step: ', i)
                print("Current Time =", datetime.now().strftime("%H:%M:%S"))

            # check for any blanks or nan values
            if not ((not x or x == np.nan or x == 'nan') \
                or (not y or y == np.nan or y == 'nan')):
                    try:
                        tract = get_tract_number(x,y)
                        dataframe.at[i, 'census_tract'] = tract
                    except:
                        print('Error at step: ', i)
        
        return dataframe

    def get_median_hh_income():
        '''
            Returns Pandas DataFrame representation Median Household Income Estimate by Census Tract for MA.
            American Community Survey (ACS) 2018 Census data used.
            Specific table: ACS 2018 5-year detailed table "B19013_001E"
        '''
        URL = "https://api.census.gov/data/2018/acs/acs5?get=B19013_001E&for=tract:*&in=state:25"
    
        response = requests.get(url = URL)
        data = response.json()

        # pprint(data)
        
        median_income_df = pd.DataFrame(data[1:len(data)-1], columns = data[0])
        median_income_df.to_csv('ma_med_income_tract.csv',index=False)
        
        return median_income_df

    ###########################################################################
    ###########################################################################
    #                                MAIN CODE                                #
    ###########################################################################
    ###########################################################################
    
    dataframe = add_long_lat(dataframe)
    dataframe = add_tract_numbers(dataframe)
    median_income_df = get_median_hh_income()
    
    # only check for land parcels that we were able to obtain tract numbers for
    for i in dataframe[dataframe['census_tract'].notna()].index:
        tract = dataframe.loc[i]['census_tract']
        median_hh_income = median_income_df[median_income_df['tract'] == str(int(tract))]['B19013_001E']
        
        # ACS data is broken down by state > county > tract
        # sometimes tract covered more than 1 county
        # averaged the median incomes
        # print(len(median_hh_income))
        if (len(median_hh_income) > 1):
            median_hh_income = mean([int(m) for m in median_income_df[median_income_df['tract'] == tract]['B19013_001E'].values])
        
        try:
            dataframe.at[i, 'median_hh_income'] = median_hh_income
        except:
            print('Error at index: ', i)

    # exports results to new .csv file in current directory
    dataframe.to_csv('state_land_plus_med_income.csv',index=False)

    return dataframe