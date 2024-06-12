from datetime import timedelta, datetime


def get_monthwise_date_ranges(start_date, end_date):
    date_ranges = []
    
    # Calculate the first month's end date
    first_month_end = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    if first_month_end > end_date:
        first_month_end = end_date

    # Add the first range
    date_ranges.append((start_date, first_month_end))

    # Move to the next month
    current_start = first_month_end + timedelta(days=1)
    
    while current_start < end_date:
        # Calculate the end of the current month
        current_end = (current_start.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        if current_end > end_date:
            current_end = end_date

        # Add the range
        date_ranges.append((current_start, current_end))

        # Move to the next month
        current_start = current_end + timedelta(days=1)
    
    return date_ranges


if __name__ == "__main__":
    # Test the function
    start_date = datetime(2023, 1, 15)
    end_date = datetime(2023, 4, 25)

    date_ranges = get_monthwise_date_ranges(start_date, end_date)
    for start, end in date_ranges:
        print(f"{start} - {end}")
