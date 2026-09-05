cmake_minimum_required(VERSION 3.20)
project(ce_psvaml LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(FetchContent)
FetchContent_Declare(raylib GIT_REPOSITORY https://github.com/raysan5/raylib.git GIT_TAG 5.5)
FetchContent_Declare(Catch2 GIT_REPOSITORY https://github.com/catchorg/Catch2.git GIT_TAG v3.8.1)
FetchContent_MakeAvailable(raylib Catch2)
list(APPEND CMAKE_MODULE_PATH ${catch2_SOURCE_DIR}/extras)

enable_testing()
add_library(ce_psvaml_core STATIC src/core/Version.cpp src/core/Random.cpp
    src/world/ScalarField.cpp src/world/FoodField.cpp
    src/world/MechanicalEnvironment.cpp src/world/World.cpp src/worm/Body.cpp src/worm/Physiology.cpp)
target_include_directories(ce_psvaml_core PUBLIC src ${raylib_SOURCE_DIR}/src)
add_executable(ce_psvaml src/main.cpp)
target_link_libraries(ce_psvaml PRIVATE ce_psvaml_core raylib)
add_subdirectory(src/tests)
