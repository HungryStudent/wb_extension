from utils import schemas


def get_size(card):
    length = 1
    for option in card["options"]:
        if option["name"] == "Длина упаковки":
            try:
                length = int(option["value"].split(" ")[0])
            except ValueError:
                length = 1

    height = 1
    for option in card["options"]:
        if option["name"] == "Высота упаковки":
            try:
                height = int(option["value"].split(" ")[0])
            except ValueError:
                height = 1

    width = 1
    for option in card["options"]:
        if option["name"] == "Ширина упаковки":
            try:
                width = int(option["value"].split(" ")[0])
            except ValueError:
                width = 1

    weight = 1
    for option in card["options"]:
        if option["name"] == "Вес товара без упаковки (г)":
            try:
                weight = int(option["value"].split(" ")[0]) // 1000
            except ValueError:
                weight = 1

    is_kgt = False
    if max(length, width, height) > 120 or (length + width + height) > 200 or weight > 25:
        is_kgt = True

    return schemas.Size(length=length, width=width, height=height, weight=weight, is_kgt=is_kgt)


