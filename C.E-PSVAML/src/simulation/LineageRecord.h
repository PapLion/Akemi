#pragma once
#include "core/Types.h"
#include <optional>
#include <vector>
namespace ce {
struct LineageRecord {
    EntityId id=0,parentId=0;
    std::uint32_t generation=0;
    std::uint64_t birthTick=0;
    std::optional<std::uint64_t> deathTick;
    DeathCause deathCause=DeathCause::None;
    std::vector<EntityId> childIds;
};
}
