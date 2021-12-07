
import numpy as np


def sigmoid(theta, x):
    return 1.0 / (1.0 + np.exp(-(theta @ x)))


def test(test_data, theta, dem):
    data = np.loadtxt(test_data, delimiter=',', skiprows=1, dtype=float)
    test_x = data[:, :-1]
    test_x = np.insert(test_x, 0, 1, axis=1)
    if dem:
        test_x = np.delete(test_x, -1, axis=1)
    y_actual = data[:, -1]
    test_y = []
    for x in test_x:
        y = sigmoid(theta, x)
        if y > 0.5:
            y = 1
        else:
            y = 0
        test_y.append(y)

    correct_y1 = 0
    correct_y0 = 0
    correct_total = 0
    num_y1 = 0
    num_y0 = 0
    for i in range(len(test_y)):
        if y_actual[i] == 1:
            num_y1 += 1
            if test_y[i] == 1:
                correct_total += 1
                correct_y1 += 1
        else:
            num_y0 += 1
            if test_y[i] == 0:
                correct_total += 1
                correct_y0 += 1
    print("Class 0: tested", num_y0, "     correctly classified:", correct_y0)
    print("Class 1: tested", num_y1, "      correctly classified:", correct_y1)
    print("Overall: tested", len(test_y), "     correctly classified:", correct_total)
    print("Accuracy:", correct_total / len(test_y))


def train(filename, rate, steps, dem):
    # data = np.genfromtxt(filename, delimiter=',', names=True, dtype=float)
    data = np.loadtxt(filename, delimiter=',', skiprows=1, dtype=float)
    train_x = data[:, :-1]
    train_x = np.insert(train_x, 0, 1, axis=1)
    if dem:
        train_x = np.delete(train_x, -1, axis=1)
    train_y = data[:, -1]
    theta = np.zeros(train_x.shape[1])
    for i in range(steps):
        gradient = np.zeros(train_x.shape[1])
        for x, y in zip(train_x, train_y):
            gradient += (y - sigmoid(theta, x)) * x
        theta += gradient * rate
    return theta


def main():
    data = input("1 for simple, 2 for netflix, 3 for heart, 4 for ancestry: ")
    rate = input("Enter learning rate: ")
    steps = input("Enter training steps: ")
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
    theta = train(train_data, float(rate), int(steps), dem)
    test(test_data, theta, dem)

    # train("data/ancestry-train.csv", 100, 12, False)


if __name__ == '__main__':
    main()
