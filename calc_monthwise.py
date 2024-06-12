from pathlib import Path
import pandas as pd
import argparse
from dateutils import get_monthwise_date_ranges
import warnings

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', default='data', help='The directory containing the CSV file')
parser.add_argument('--csv_file', default='bills.csv', help='The CSV file to process')
args = parser.parse_args()

# Read the CSV file
data_dir = Path(args.data_dir)
csv_file = data_dir / args.csv_file
df = pd.read_csv(csv_file)

# Convert the 'Start' and 'End' columns to datetime format
df['Start'] = pd.to_datetime(df['Start'], format='%d/%m/%Y')
df['End'] = pd.to_datetime(df['End'], format='%d/%m/%Y')

df_split = pd.DataFrame(columns=['Bill', 'Start', 'End', 'Days', 'Month', 'Total'])
for index, row in df.iterrows():
    num_days = (row['End'] - row['Start']).days + 1
    date_start = row['Start']
    date_end = row['End']
    date_ranges = get_monthwise_date_ranges(date_start, date_end)
    for start, end in date_ranges:
        num_days_current = (end - start).days + 1
        total_current = row['Total'] * num_days_current / num_days
        month = start.strftime('%Y/%m')
        df_split.loc[len(df_split)] = {
            'Bill': row['Bill'],
            'Start': start,
            'End': end,
            'Days': num_days_current,
            'Month': month,
            'Total': f'{total_current:.2f}'
        }
    total_split = df_split[df_split['Bill'] == row['Bill']]['Total'].astype(float).sum()
    total_row = float(row['Total'])
    total_assert_str = f'For Bill {row["Bill"]}, Total Split: {total_split}, Total Row: {total_row}'
    assert abs(total_split - total_row) < 0.02, total_assert_str

# Write the new DataFrame to a new CSV file
out_file = data_dir / f'{csv_file.stem}_monthwise_split.csv'
df_split.to_csv(out_file, index=False)

# Calculate the total charges and days for each month
df_monthwise = df_split.groupby('Month')['Total'].apply(lambda x: x.astype(float).sum()).reset_index()
df_monthwise['Days'] = df_split.groupby('Month')['Days'].apply(lambda x: x.astype(int).sum()).reset_index()['Days']

# assert if number of days in a month is correct
for index, row in df_monthwise.iterrows():
    year, month = row['Month'].split('/')
    num_days = pd.Period(year=int(year), month=int(month), freq='M').days_in_month
    if row['Days'] != num_days:
        warn_msg = f'For {row["Month"]}, bills included for {row["Days"]}/{num_days} days only'
        warnings.warn(warn_msg)

# calc yearwise total
df_monthwise['Year'] = df_monthwise['Month'].apply(lambda x: x.split('/')[0])
df_yearwise = df_monthwise.groupby('Year')['Total'].apply(lambda x: x.astype(float).sum()).reset_index()
df_yearwise['Days'] = df_monthwise.groupby('Year')['Days'].apply(lambda x: x.astype(int).sum()).reset_index()['Days']
df_yearwise['Month'] = df_yearwise['Year']
df_monthwise = pd.concat([df_monthwise, df_yearwise], ignore_index=True)

# Write the new DataFrame to a new CSV file
df_monthwise.to_csv(data_dir / f'{csv_file.stem}_monthwise_total.csv', index=False, float_format='%.2f')
