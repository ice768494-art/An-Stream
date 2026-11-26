def humanbytes(size):
    if not size:
        return "0 B"
    power = 1024
    n = 0
    labels = ["B", "KiB", "MiB", "GiB", "TiB"]
    size = float(size)
    while size >= power and n < len(labels) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {labels[n]}"
