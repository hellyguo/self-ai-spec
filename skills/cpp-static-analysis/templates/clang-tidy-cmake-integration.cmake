set(CMAKE_CXX_CLANG_TIDY
    clang-tidy
    --checks='bugprone-*,performance-*,modernize-*'
    --warnings-as-errors='*'
)

add_custom_target(tidy
    COMMAND run-clang-tidy -p ${CMAKE_BINARY_DIR} -j 4
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Running clang-tidy..."
)
