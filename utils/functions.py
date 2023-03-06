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