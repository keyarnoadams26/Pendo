cmake_minimum_required(VERSION 3.16)
project(pendo_core LANGUAGES CXX)
add_library(pendo_core SHARED pendo_core.cpp)
set_target_properties(pendo_core PROPERTIES CXX_STANDARD 17)
