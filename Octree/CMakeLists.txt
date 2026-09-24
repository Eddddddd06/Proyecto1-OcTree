cmake_minimum_required(VERSION 3.10)
project(OctreeProject)

set(CMAKE_CXX_STANDARD 17)

include_directories(include)

add_executable(main_test src/main_test.cpp src/Octree.cpp)
