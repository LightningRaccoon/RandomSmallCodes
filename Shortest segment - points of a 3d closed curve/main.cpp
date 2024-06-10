#include <iostream>
#include <cmath>

struct Point{
    double x;
    double y;
    double z;
};

bool test_1();
bool test_2();
bool test_3();
bool test_4();

double calculateDistance(Point a, Point b){
    return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2) + pow(a.z - b.z, 2));
}

double calculateShortestPath(Point* pointArray, int size){
    double shortestDistance = 0;
    for (int i = 0; i < size-1; ++i){
        double distance = calculateDistance(pointArray[i], pointArray[i+1]);
        if (shortestDistance > distance || shortestDistance == 0){
            shortestDistance = distance;
        }
    }
    return shortestDistance;
}

int main(){

    if (test_1()){
        std::cout << "Test 1 is OK" << std::endl;
    } else {
        std::cout << "Test 1 is NOT OK" << std::endl;
    }

    if (test_2()){
        std::cout << "Test 2 is OK" << std::endl;
    } else {
        std::cout << "Test 2 is NOT OK" << std::endl;
    }

    if (test_3()){
        std::cout << "Test 3 is OK" << std::endl;
    } else {
        std::cout << "Test 3 is NOT OK" << std::endl;
    }

    if (test_4()){
        std::cout << "Test 4 is OK" << std::endl;
    } else {
        std::cout << "Test 4 is NOT OK" << std::endl;
    }

    return 0;
}

bool test_1(){
    Point a = {0, 0, 0};
    Point b = {1, 1, 1};
    Point c = {2, 4, 2};
    Point d = {3, 9, 3};
    Point e = {4, 16, 4};


    Point pointArray[11] = {a, b, c, d, e};
    double result = calculateShortestPath(pointArray, 5);
    double expected = calculateDistance(a, b);
    std::cout << "Test_1 result: " << result << std::endl;

    return result == expected;
}

bool test_2(){
    Point a = {0, 1, 2};
    Point b = {1, 3, 5};
    Point c = {4, 5, 8};
    Point d = {9, 7, 12};
    Point e = {9, 8, 13};


    Point pointArray[5] = {a, b, c, d, e};
    double result = calculateShortestPath(pointArray, 5);
    double expected = calculateDistance(d, e);
    std::cout << "Test_2 result: " << result << std::endl;

    return result == expected;
}

bool test_3(){
    Point a = {0, 1, 0};
    Point b = {3, 4, -1};
    Point c = {6, 9, -2};
    Point d = {6, 10, -2.5};
    Point e = {12, 25, -4};



    Point pointArray[5] = {a, b, c, d, e};
    double result = calculateShortestPath(pointArray, 5);
    double expected = calculateDistance(c, d);
    std::cout << "Test_3 result: " << result << std::endl;

    return result == expected;
}

bool test_4(){
    Point a = {0, -1, 20};
    Point b = {1, -2, 10};
    Point c = {2, -4, 5};
    Point d = {3, -8, 2.5};
    Point e = {4, -16, 1.75};


    Point pointArray[5] = {a, b, c, d, e};
    double result = calculateShortestPath(pointArray, 5);
    double expected = calculateDistance(c, d);
    std::cout << "Test_4 result: " << result << std::endl;

    return result == expected;
}
