import csv


def write_dict_to_csv(dictionary, filename):
    fieldnames = dictionary.keys()

    # 判断文件是否存在，如果不存在则创建新文件并写入表头
    file_exists = True
    try:
        with open(filename, 'r', encoding='ANSI') as file:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(filename, 'a', newline='', encoding='ANSI') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # 如果文件不存在，写入表头
        if not file_exists:
            writer.writeheader()

        writer.writerow(dictionary)


def test():
    data1 = {'Name': 'John', 'Age': 28, 'Country': 'USA'}
    data2 = {'Name': 'Alice', 'Age': 32, 'Country': 'Canada'}

    write_dict_to_csv(data1, 'data.csv')
    write_dict_to_csv(data2, 'data.csv')


if __name__ == "__main__":
    test()
