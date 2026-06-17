py_dep = py.dependency()
numpy_dep = dependency('numpy')

x2py_runtime_incdir = include_directories('.')

x2py_runtime_dep = declare_dependency(sources: 'python_runtime.c',
                                      include_directories : x2py_runtime_incdir,
                                      dependencies: [py_dep, numpy_dep])
