cmake_minimum_required(VERSION 4.0)
project(otbv)

add_subdirectory(otbv-cpp)
add_subdirectory(pybind11)

pybind11_add_module(${PROJECT_NAME} src/otbv.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE OTBV)