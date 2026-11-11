-- ============================================================================
-- Gauntlet Customizer Mod for Dauntless 1.14.7 (UE4SS v3.0.1)
-- Customizes Gauntlet Mode: 1-4 Behemoths, season switching, level & round configs.
-- Encounter definitions are injected natively via:
-- zzzzzzzzzzzzzzzz_GauntletThreeBehemoths_P.pak
-- ============================================================================

local function Valid(o)
    if not o then return false end
    local ok, v = pcall(function() return o:IsValid() end)
    return ok and v
end

local function NameOf(o)
    local ok, n = pcall(function() return o:GetFullName() end)
    return ok and n or nil
end

local function LogBehemoths()
    pcall(function()
        local allBehemoths = FindAllOf("ArchonBehemoth") or {}
        local count = 0
        print("[Gauntlet3] ==================== [ACTIVE BEHEMOTHS] ====================\n")
        for _, b in ipairs(allBehemoths) do
            if Valid(b) then
                local fn = NameOf(b) or ""
                if not fn:find("Default__", 1, true) then
                    count = count + 1
                    local loc = {X = 0, Y = 0, Z = 0}
                    pcall(function()
                        local v = b:K2_GetActorLocation()
                        if v then loc.X = math.floor(v.X); loc.Y = math.floor(v.Y); loc.Z = math.floor(v.Z) end
                    end)
                    print(string.format("[Gauntlet3]   [%d] %s at (%d, %d, %d)\n", count, fn, loc.X, loc.Y, loc.Z))
                end
            end
        end
        print(string.format("[Gauntlet3] Total active behemoths in arena: %d\n", count))
        print("[Gauntlet3] ============================================================\n")
    end)
end

-- Optional dev hotkey: F6 logs active arena behemoths into UE4SS.log
pcall(function()
    RegisterKeyBind(Key.F6, function()
        LogBehemoths()
    end)
end)

print("[Gauntlet3] Gauntlet Three Behemoths Mod active (native pak patch mounted).\n")
