add_executable(ce_psvaml_tests TestMain.cpp CoreTests.cpp)
target_link_libraries(ce_psvaml_tests PRIVATE ce_psvaml_core Catch2::Catch2WithMain)
include(Catch)
catch_discover_tests(ce_psvaml_tests)
