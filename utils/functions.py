from datetime import datetime

def split_columns_into_arrays(dataset):
    labels = []
    data = []
    for i in dataset:
        labels.append(i[0])
        data.append(i[1])
        
    return {
        "labels": labels,
        "data": data,
    }
    
def split_sales_data(dataset):
    units_sold = []
    daily_revenue = []
    dates = []
    for i in dataset:
        units_sold.append(i[2])
        daily_revenue.append(i[1])
        dates.append(datetime.strftime(i[0], "%d/%m/%y"))
        
    return {
        "dates": dates,
        "daily_revenue": daily_revenue,
        "units_sold": units_sold
    }