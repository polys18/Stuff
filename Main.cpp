// This program uses the minimax algorithm to create a tic-tac-toe game (human vs the algorithm).
#include <iostream>
#include "console.h"
#include "vector.h"
using namespace std;

// This function sets up the initial state of the game and prints out the starting empty game board.
Vector<Vector<string>> setup() {
    Vector<Vector<string>> initialState = {
        {"*", "*", "*"},
        {"*", "*", "*"},
        {"*", "*", "*"}
    };
    for (Vector<string> line: initialState) {
        cout << line << endl;
    }
    return initialState;
}

// This function retursns the player (either x or o) that has the turn to play.
string player(Vector<Vector<string>> state) {
    int x = 0;
    int o = 0;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (state[i][j] == "x") {
                x++;
            } else if (state[i][j] == "o") {
                o++;
            }
        }
    }
    if (x > o) {
        return "o";
    } else {
        return "x";
    }
}

// This function returns true if the state is a terminal state, i.e. the game is over.
bool terminal(Vector<Vector<string>> state) {
    if ((state[0][0] == "x" && state[0][1] == "x" && state[0][2] == "x") || (state[0][0] == "o" && state[0][1] == "o" && state[0][2] == "o")) {
        return true;
    } else if ((state[1][0] == "x" && state[1][1] == "x" && state[1][2] == "x") || (state[1][0] == "o" && state[1][1] == "o" && state[1][2] == "o")) {
        return true;
    } else if ((state[2][0] == "x" && state[2][1] == "x" && state[2][2] == "x") || (state[2][0] == "o" && state[2][1] == "o" && state[2][2] == "o")) {
        return true;
    } else if ((state[0][0] == "x" && state[1][0] == "x" && state[2][0] == "x") || (state[0][0] == "o" && state[1][0] == "o" && state[2][0] == "o")) {
        return true;
    } else if ((state[0][1] == "x" && state[1][1] == "x" && state[2][1] == "x") || (state[0][1] == "o" && state[1][1] == "o" && state[2][1] == "o")) {
        return true;
    } else if ((state[0][2] == "x" && state[1][2] == "x" && state[2][2] == "x") || (state[0][2] == "o" && state[1][2] == "o" && state[2][2] == "o")) {
        return true;
    } else if ((state[0][0] == "x" && state[1][1] == "x" && state[2][2] == "x") || (state[0][0] == "o" && state[1][1] == "o" && state[2][2] == "o")) {
        return true;
    } else if ((state[0][2] == "x" && state[1][1] == "x" && state[2][0] == "x") || (state[0][2] == "o" && state[1][1] == "o" && state[2][0] == "o")) {
        return true;
    }
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (state[i][j] == "*") {
                return false;
            }
        }
    }

    return true;
}

//Utility is the score of the teaminal states. 1 means x wins and -1 means that o wins.
int utility(Vector<Vector<string>> state) {
    if (!terminal(state)) {
        error("utility cannot be used wnen the state is not terminal.");
    } else {
        if (state[0][0] == "x" && state[0][1] == "x" && state[0][2] == "x") {
            return 1;
        } else if (state[1][0] == "x" && state[1][1] == "x" && state[1][2] == "x") {
            return 1;
        } else if (state[2][0] == "x" && state[2][1] == "x" && state[2][2] == "x") {
            return 1;
        } else if (state[0][0] == "x" && state[1][0] == "x" && state[2][0] == "x") {
            return 1;
        } else if (state[0][1] == "x" && state[1][1] == "x" && state[2][1] == "x") {
            return 1;
        } else if (state[0][2] == "x" && state[1][2] == "x" && state[2][2] == "x") {
            return 1;
        } else if (state[0][0] == "x" && state[1][1] == "x" && state[2][2] == "x") {
            return 1;
        } else if (state[0][2] == "x" && state[1][1] == "x" && state[2][0] == "x") {
            return 1;
        } else if (state[0][0] == "o" && state[0][1] == "o" && state[0][2] == "o") {
            return -1;
        } else if (state[1][0] == "o" && state[1][1] == "o" && state[1][2] == "o") {
            return -1;
        } else if (state[2][0] == "o" && state[2][1] == "o" && state[2][2] == "o") {
            return -1;
        } else if (state[0][0] == "o" && state[1][0] == "o" && state[2][0] == "o") {
            return -1;
        } else if (state[0][1] == "o" && state[1][1] == "o" && state[2][1] == "o") {
            return -1;
        } else if (state[0][2] == "o" && state[1][2] == "o" && state[2][2] == "o") {
            return -1;
        } else if (state[0][0] == "o" && state[1][1] == "o" && state[2][2] == "o") {
            return -1;
        } else if (state[0][2] == "o" && state[1][1] == "o" && state[2][0] == "o") {
            return -1;
        } else {
            return 0;
        }
    }
}

Vector<Vector<string>> result(Vector<Vector<string>> state, Vector<int> action) {
    string ply = player(state);
    state[action[0]][action[1]] = ply;
    return state;
}

Vector<Vector<int>> actions(Vector<Vector<string>> state) {
    Vector<Vector<int>> result;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (state[i][j] == "*") {
                result.add({i, j});
            }
        }
    }
    return result;
}

// The minplay and maxplay are the actual recursive algorithm that drive this program.
int minPlay(Vector<Vector<string>> state, Vector<int>& actn);

int maxPlay(Vector<Vector<string>> state, Vector<int>& actn) {
    if (terminal(state)) {
        return utility(state);
    } else {
        int v = -2;
        for (Vector<int> action: actions(state)) {
            v = max(v, minPlay(result(state, action), actn));
        }
        return v;
    }
}

int minPlay(Vector<Vector<string>> state, Vector<int>& actn) {
    if (terminal(state)) {
        return utility(state);
    } else {
        int v = 2;
        for (Vector<int> action: actions(state)) {
            int tempv = v;
            v = min(v, maxPlay(result(state, action), actn));
            if (v < tempv) {
                actn = action;
            }
        }
        return v;
    }
}

void player2(Vector<Vector<string>>& state) {
    int y;
    int x;
    cout << "type y coordinates: ";
    cin >> y;
    cout << "type x coordinates: ";
    cin >> x;
    state = result(state, {y, x});
    for( Vector<string> line: state) {
        cout << line << endl;
    }
}

int main() {
    Vector<Vector<string>> state = setup();
    while (!terminal(state)) {
        player2(state);
        cout << " " << endl;
        Vector<int> action = {0, 0};
        int v = minPlay(state, action);
        state = result(state, action);
        for ( Vector<string> line: state) {
            cout << line << endl;
        }
        cout << v << endl;
    }
    return 0;
}
