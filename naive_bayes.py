import pandas as pd


def test(trained, p_y_0, p_y_1, test_data, dem):
    y_hat = []
    y_actual = []
    file = open(test_data)
    next(file)
    for line in file:
        line = line.strip()
        line = line.split(',')
        y_actual.append(int(line[len(line) - 1]))
        y1 = p_y_1
        y0 = p_y_0
        for i in range(len(line) - 1):
            if dem and i == len(line) - 2:
                break
            y1 *= trained[i][1][int(line[i])]
            y0 *= trained[i][0][int(line[i])]
        if y0 > y1:
            y_hat.append(0)
        else:
            y_hat.append(1)

    correct_y1 = 0
    correct_y0 = 0
    correct_total = 0
    num_y1 = 0
    num_y0 = 0
    for i in range(len(y_hat)):
        if y_actual[i] == 1:
            num_y1 += 1
            if y_hat[i] == 1:
                correct_total += 1
                correct_y1 += 1
        else:
            num_y0 += 1
            if y_hat[i] == 0:
                correct_total += 1
                correct_y0 += 1
    print("Class 0: tested", num_y0, "     correctly classified:", correct_y0)
    print("Class 1: tested", num_y1, "     correctly classified:", correct_y1)
    print("Overall: tested", len(y_hat), "     correctly classified:", correct_total)
    print("Accuracy:", correct_total/len(y_hat))


def train_mle(train_data, dem):
    p_x_y = []
    df = pd.read_csv(train_data)

    if dem:
        num_of_datapoints = len(df.columns) - 2
    else:
        num_of_datapoints = len(df.columns) - 1

    num_y_0 = df['Label'].value_counts()[0]
    num_y_1 = df['Label'].value_counts()[1]
    p_y_0 = num_y_0/(num_y_0 + num_y_1)
    p_y_1 = num_y_1 / (num_y_0 + num_y_1)

    for i in range(num_of_datapoints):
        num_x_0_y_0 = df[(df.iloc[:, i] == 0) & (df.Label == 0)].shape[0]
        num_x_1_y_0 = df[(df.iloc[:, i] == 1) & (df.Label == 0)].shape[0]
        num_x_0_y_1 = df[(df.iloc[:, i] == 0) & (df.Label == 1)].shape[0]
        num_x_1_y_1 = df[(df.iloc[:, i] == 1) & (df.Label == 1)].shape[0]
        p_x_0_y_0 = num_x_0_y_0 / num_y_0
        p_x_1_y_0 = num_x_1_y_0 / num_y_0
        p_x_0_y_1 = num_x_0_y_1 / num_y_1
        p_x_1_y_1 = num_x_1_y_1 / num_y_1
        p_x_y.append([[p_x_0_y_0, p_x_1_y_0], [p_x_0_y_1, p_x_1_y_1]])

    return p_x_y, p_y_0, p_y_1


def train_map(train_data, dem):
    p_x_y = []
    df = pd.read_csv(train_data)

    if dem:
        num_of_datapoints = len(df.columns) - 2
    else:
        num_of_datapoints = len(df.columns) - 1

    num_y_0 = df['Label'].value_counts()[0]
    num_y_1 = df['Label'].value_counts()[1]
    p_y_0 = num_y_0/(num_y_0 + num_y_1)
    p_y_1 = num_y_1 / (num_y_0 + num_y_1)

    for i in range(num_of_datapoints):
        num_x_0_y_0 = df[(df.iloc[:, i] == 0) & (df.Label == 0)].shape[0]
        num_x_1_y_0 = df[(df.iloc[:, i] == 1) & (df.Label == 0)].shape[0]
        num_x_0_y_1 = df[(df.iloc[:, i] == 0) & (df.Label == 1)].shape[0]
        num_x_1_y_1 = df[(df.iloc[:, i] == 1) & (df.Label == 1)].shape[0]
        p_x_0_y_0 = (num_x_0_y_0 + 1) / (num_y_0 + 2)
        p_x_1_y_0 = (num_x_1_y_0 + 1)/ (num_y_0 + 2)
        p_x_0_y_1 = (num_x_0_y_1 + 1) / (num_y_1 + 2)
        p_x_1_y_1 = (num_x_1_y_1 + 1) / (num_y_1 + 2)
        p_x_y.append([[p_x_0_y_0, p_x_1_y_0], [p_x_0_y_1, p_x_1_y_1]])

    return p_x_y, p_y_0, p_y_1


def main():
    data = input("1 for simple, 2 for netflix, 3 for heart, 4 for ancestry: ")
    demographic = input("exclude demographic? y/n ")
    dem = True
    if demographic == 'y':
        dem = True
    elif demographic == 'n':
        dem = False
    else:
        print("invalid input")
        return
    train_data = ""
    test_data = ""
    if data == '1':
        train_data = "data/simple-train.csv"
        test_data = "data/simple-test.csv"
    elif data == '2':
        train_data = "data/netflix-train.csv"
        test_data = "data/netflix-test.csv"
    elif data == '3':
        train_data = "data/heart-train.csv"
        test_data = "data/heart-test.csv"
    elif data == '4':
        train_data = "data/ancestry-train.csv"
        test_data = "data/ancestry-test.csv"
    else:
        print("invalid input")
        return

    param = input("1 for MAP, 2 for MLE: ")
    if param == '1':
        (trained, p_y_0, p_y_1) = train_map(train_data, dem)
        #print(p_y_1)
        test(trained, p_y_0, p_y_1, test_data, dem)
    elif param == '2':
        (trained, p_y_0, p_y_1) = train_mle(train_data, dem)
        #print(p_y_1)
        test(trained, p_y_0, p_y_1, test_data, dem)
    else:
        print("invalid input")
        return


if __name__ == '__main__':
    main()