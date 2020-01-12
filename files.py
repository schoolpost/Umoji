import os


def getDictionary():

    dic = dict()
    path = "emoji"

    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            key = file.split(".")[0]
            dic[key] = os.path.join(r, file)

    return dic
