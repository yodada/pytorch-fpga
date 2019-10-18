
set(USE_CUDA 0)
set(USE_OPENCL ON)
set(USE_FPGA ON)
find_package(SDAccel REQUIRED)
if (NOT SDACCEL_FOUND)
    MESSAGE(FATAL_ERROR
        "Could not find SDAccel installation")
endif()
set(CMAKE_C_COMPILER ${SDACCEL_XCPP})
set(CMAKE_CXX_COMPILER ${SDACCEL_XCPP})