add_library(x2py_runtime OBJECT python_runtime.c)

target_include_directories(x2py_runtime
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(x2py_runtime
    PUBLIC
    Python::NumPy
)
