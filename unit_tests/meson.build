gtest_dep = dependency('gtest',
                      main: true,
                      fallback: ['gtest', 'gtest_dep'],
                      required: true)
gmock_dep = dependency('gmock', 
                      fallback: ['gmock', 'gmock_dep'],
                      required: true)

test_exe = executable(
                'test_contextual_core_lib',
                'test_mylib.cpp',
                include_directories:include_directories('../src'),
                link_with: contextual_core_lib,
                dependencies: [gtest_dep, gmock_dep])

test('contextual core tests', test_exe)

