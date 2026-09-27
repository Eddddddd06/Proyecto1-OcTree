cmake_minimum_required(VERSION 3.14)
project(OctreeProject)

set(CMAKE_CXX_STANDARD 17)

include_directories(include)

add_executable(main_test src/main_test.cpp src/Octree.cpp)

# raylib solo para la parte grafica , la logica sigue siendo la de Octree.cpp
find_package(raylib 4.0 QUIET)
if(NOT raylib_FOUND)
    include(FetchContent)
    set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    set(CMAKE_POLICY_VERSION_MINIMUM 3.10 CACHE STRING "" FORCE)
    FetchContent_Declare(
        raylib
        GIT_REPOSITORY https://github.com/raysan5/raylib.git
        GIT_TAG 5.5
        GIT_SHALLOW TRUE
    )
    FetchContent_MakeAvailable(raylib)
endif()

# la mini app vive en la carpeta del motor grafico , pero usa el mismo Octree.cpp
set(MOTOR_GRAFICO ${CMAKE_CURRENT_SOURCE_DIR}/../animacion/motor_grafico)

add_executable(octree_visual ${MOTOR_GRAFICO}/octree_visual.cpp src/Octree.cpp)
target_link_libraries(octree_visual raylib)
