def get_batches(dataset, batch_size):
    X = dataset
    n_samples = len(dataset)
    for start in range(0, n_samples, batch_size):
        end = min(start + batch_size, n_samples)
        yield X[start:end]
