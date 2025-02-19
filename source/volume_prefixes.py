prefixes = {
    1000000000: "B",
    1000000: "M",
    1000: "K",
}

def format_numbers(number):
    for limit, prefix in prefixes.items():
        if number >= limit:
            return f"{number / limit:.2f}{prefix}"
    return number