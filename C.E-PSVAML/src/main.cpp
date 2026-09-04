#include <iostream>
#include "core/Version.h"
int main() {
    std::cout << "C.E-PSVAML " << ce::version() << '\n';
    return 0;
}
