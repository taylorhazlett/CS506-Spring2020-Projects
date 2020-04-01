import pandas as pd
from clean_data import all_clean_processes


def main():
    std_name_df = all_clean_processes.all_clean_processes()
    std_name_df.to_csv('./data/std_name.csv', index=False)
    return


if __name__ == '__main__':
    main()



