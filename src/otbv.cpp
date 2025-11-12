#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "otbv.h"

PYBIND11_MODULE(otbv, handle) {
    handle.doc() = "something";
    handle.def("load", &otbv::load);
    handle.def("save", pybind11::overload_cast<const std::string&, const std::vector<bool>&, const std::tuple<size_t, size_t, size_t>&>(&otbv::save));
    handle.def("save", pybind11::overload_cast<const std::string&, const std::vector<std::vector<std::vector<bool>>>&>(&otbv::save));
}