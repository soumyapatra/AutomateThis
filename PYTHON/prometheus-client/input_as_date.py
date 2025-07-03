from datetime import datetime

start_date_entry = input('Enter a start date (i.e. 2017-7-1): ')
year, month, day = map(int, start_date_entry.split("-"))

start_date = datetime(year, month, day)

print(start_date)

end_date_entry = input('Enter a end date (i.e. 2017-7-1): ')
year, month, day = map(int, end_date_entry.split("-"))
end_date_entry = datetime(year, month, day)

no_of_days = end_date_entry - start_date_entry

