def contains(arr, string):
    for s in arr:
        if s == string:
            return True
    return False


def truncate(string, max_lines):
    lines = string.split('\n', 1)
    if len(lines) > max_lines:
        return lines[0] + '\n' + lines[1] + '\n' + lines[2] + '\n' + lines[3]
    else:
        return string
