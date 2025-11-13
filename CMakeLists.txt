cmake_minimum_required(VERSION 4.0)
project(pyotbv)

add_subdirectory(libotbv)
add_subdirectory(pybind11)

pybind11_add_module(${PROJECT_NAME} src/otbv.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE otbv)
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME "otbv")