from PIL import Image


def contains(arr, string):
    for s in arr:
        if s == string:
            return True
    return False


def truncate(string, max_lines):
    lines = str.splitlines(string)
    if len(lines) > max_lines:
        return lines[0] + '\n' + lines[1] + '\n' + lines[2] + '\n' + lines[3]
    else:
        return string


def removeColor(img_path, r, g, b, threshold=0):
    img = Image.open(img_path)
    img = img.convert("RGBA")
    data = img.getdata()

    new = []
    for item in data:
        if \
                r-threshold <= item[0] <= r+threshold and \
                g-threshold <= item[1] <= g+threshold and \
                b-threshold <= item[2] <= b+threshold:
            new.append((255, 255, 255, 0))
        else:
            new.append(item)

    img.putdata(new)
    img.save(img_path, "PNG")

