#pragma once
#include "worm/WormDebugState.h"
#include <string_view>
namespace ce { class BehaviorClassifier { public: static std::string_view classify(const WormDebugState&); }; }
