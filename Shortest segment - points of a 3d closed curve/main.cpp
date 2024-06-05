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

double calculateDistance(Point a, Point b){
    return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2) + pow(a.z - b.z, 2));
}

double calculateShortestPath(Point* pointArray, int size){
    double shortestDistance = 0;
    for (int i = 0; i < size-1; ++i){
        double distance = calculateDistance(pointArray[i], pointArray[i+1]);
        std::cout << distance << std::endl;
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
    std::cout << result << std::endl;
    return result == 1.732051;
}

bool test_2(){
    Point a = {0, 1, 2};
    Point b = {1, 3, 5};
    Point c = {4, 5, 8};
    Point d = {9, 7, 12};
    Point e = {16, 9, 15};


    Point pointArray[5] = {a, b, c, d, e};
    double result = calculateShortestPath(pointArray, 5);
    std::cout << result << std::endl;
    return result == sqrt(3);
}

bool test_3(){
    Point a = {0, 1, 0};
    Point b = {3, 4, -1};
    Point c = {6, 9, -2};
    Point d = {9, 16, -3};
    Point e = {12, 25, -4};



    Point pointArray[5] = {a, b, c, d, e};
    double result = calculateShortestPath(pointArray, 5);
    std::cout << result << std::endl;
    return result == sqrt(3);
}

bool test_4(){
    Point a = {0, 0, 0};
    Point b = {0.1, 1.5, -1.67};
    Point c = {0.01, 3, -3.34};
    Point d = {0.0001, 4.5, -5.01};
    Point e = {0.00000001, 6, -6.68};

    Point pointArray[5] = {a, b, c, d, e};
    double result = calculateShortestPath(pointArray, 5);
    std::cout << result << std::endl;
    return result == sqrt(3);
}
