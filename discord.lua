local json = require "json"
local GLOBAL = _G

-- Danh sách boss cần theo dõi
local death_list = {
    alterguardian_phase1=1, alterguardian_phase2=1, alterguardian_phase3=1,
    antlion=1, bearger=1, beequeen=1, claywarg=1, crabking=1, deerclops=1, dragonfly=1,
    gingerbreadwarg=1, eyeofterror=1, klaus=1, koalefant_summer=1, koalefant_winter=1,
    leif=1, lordfruitfly=1, malbatross=1, minotaur=1, moose=1,
    shadow_knight=1, shadow_bishop=1, shadow_rook=1, spat=1, spiderqueen=1,
    stalker_atrium=1, stalker_forest=1, stalker=1, toadstool_dark=1, toadstool=1,
    twinofterror1=1, twinofterror2=1, walrus=1, warg=1,
    mutatedbearger=1, mutateddeerclops=1, mutatedwarg=1, daywalker=1, daywalker2=1
}

local function IsMasterShard()
    local shard = GLOBAL.TheShard
    return shard and shard:GetShardId() == "1"
end

local function WriteOnlinePlayers()
    local players = {}
    for _, player in ipairs(GLOBAL.AllPlayers) do
        local days = 0
        if player.components and player.components.age then
            days = math.floor(player.components.age:GetAgeInDays() or 0)
        end

        table.insert(players, {
            name = player.name,
            userid = player.userid,
            prefab = player.prefab,
            days_survived = days
        })
    end

    local json_data = json.encode({ players = players })
    GLOBAL.TheSim:SetPersistentString("online_players.json", json_data, false)
end

local function WriteWorldStatus()
    if not IsMasterShard() then return end

    local state = GLOBAL.TheWorld and GLOBAL.TheWorld.state
    if not state then return end

    local season = state.season or "unknown"
    local day = (state.cycles or 0) + 1
    local days_remaining = state.remainingdaysinseason or 0

    local data = {
        season = season,
        current_day = day,
        days_remaining = days_remaining
    }

    local json_data = json.encode(data)
    GLOBAL.TheSim:SetPersistentString("world_status.json", json_data, false)
end

-- Tên hiển thị boss
local name_map = {
    alterguardian_phase1 = "Celestial Champion (P1)",
    alterguardian_phase2 = "Celestial Champion (P2)",
    alterguardian_phase3 = "Celestial Champion (P3)",
    antlion = "Antlion",
    bearger = "Bearger",
    beequeen = "Bee Queen",
    claywarg = "Clay Warg",
    crabking = "Crab King",
    deerclops = "Deerclops",
    dragonfly = "Dragonfly",
    gingerbreadwarg = "Gingerbread Warg",
    eyeofterror = "Eye of Terror",
    klaus = "Klaus",
    koalefant_summer = "Summer Koalefant",
    koalefant_winter = "Winter Koalefant",
    leif = "Treeguard",
    lordfruitfly = "Lord of the Fruit Flies",
    malbatross = "Malbatross",
    minotaur = "Ancient Guardian",
    moose = "Moose/Goose",
    shadow_knight = "Shadow Knight",
    shadow_bishop = "Shadow Bishop",
    shadow_rook = "Shadow Rook",
    spat = "Ewecus",
    spiderqueen = "Spider Queen",
    stalker_atrium = "Fuelweaver",
    stalker_forest = "Forest Stalker",
    stalker = "Stalker",
    toadstool_dark = "Misery Toadstool",
    toadstool = "Toadstool",
    twinofterror1 = "Retinazor",
    twinofterror2 = "Spazmatism",
    walrus = "MacTusk",
    warg = "Warg",
    mutatedbearger = "Armored Bearger",
    mutateddeerclops = "Crystal Deerclops",
    mutatedwarg = "Possessed Varg",
    daywalker = "Nightmare Werepig",
    daywalker2 = "Scrappy Werepig"
}

-- Tên world theo shard ID
local world_names = {
    ["1"] = "World 1",
    ["2"] = "World 2",
    ["3"] = "World 3",
    ["4"] = "World 4"
}

-- Lấy tên hiển thị
local function lang(prefab)
    return name_map[prefab] or prefab or "Unknown"
end

-- Lấy tên world
local function get_world()
    local shard_id = tostring(GLOBAL.TheShard and GLOBAL.TheShard:GetShardId() or "?")
    return world_names[shard_id] or ("World " .. shard_id)
end

-- 🔔 Boss chết
local function onEntityDeath(inst, data)
    local aff = data and data.afflicter
    if aff and aff:IsValid() then
        local who = aff:HasTag("player") and (aff.name or "Người chơi") or lang(aff.prefab)
        local target = lang(inst.prefab)

        local world = get_world()
        local msg = string.format("[THÔNG BÁO] %s đã tiêu diệt %s ở %s!", who, target, world)

        print("[BossKill] " .. msg)
        GLOBAL.TheNet:Announce(msg)
    end
end

local function TrackBossSpawners()
    local world = get_world()
    for _, ent in pairs(Ents) do
        if ent.prefab == "beequeenhive" and not ent._hooked_bq then
            ent._hooked_bq = true
            ent:ListenForEvent("timerdone", function()
                local msg = string.format("[THÔNG BÁO] Bee Queen đã xuất hiện ở %s!", world)
                if ent:GetDisplayName() == "Honey Patch" then
                    TheNet:Announce(msg)
                end
            end)

        elseif ent.prefab == "dragonfly_spawner" and not ent._hooked_df then
            ent._hooked_df = true
            ent:ListenForEvent("timerdone", function()
                local msg = string.format("[THÔNG BÁO] Dragonfly đã xuất hiện ở %s!", world)
                TheNet:Announce(msg)
            end)

        elseif ent.prefab == "toadstool_cap" and not ent._hooked_toad then
            ent._hooked_toad = true
            ent:ListenForEvent("ms_spawntoadstool", function()
                local msg = string.format("[THÔNG BÁO] %s đã xuất hiện ở %s!", ent:GetDisplayName(), world)
                TheNet:Announce(msg)
            end)

        elseif ent.prefab == "atrium_gate" and not ent._hooked_atrium then
            ent._hooked_atrium = true
            ent:ListenForEvent("timerdone", function()
                if ent.components.trader and ent.components.trader.enabled then
                    local msg = string.format("[THÔNG BÁO] %s is Available Now in %s!", ent:GetDisplayName(), world)
                    TheNet:Announce(msg)
                end
            end)

        elseif ent.prefab == "klaus_sack" and not ent._hooked_klaus then
            ent._hooked_klaus = true
            ent:DoTaskInTime(1, function()
                local msg = string.format("[THÔNG BÁO] %s đã xuất hiện ở %s!", ent:GetDisplayName(), world)
                TheNet:Announce(msg)
            end)

        elseif ent.prefab == "crabking" and not ent._hooked_crab then
            ent._hooked_crab = true
            ent:DoTaskInTime(1, function()
                local msg = string.format("[THÔNG BÁO] %s đã xuất hiện ở %s!", ent:GetDisplayName(), world)
                TheNet:Announce(msg)
            end)
        
        elseif ent.prefab == "minotaur" and not ent._hooked_crab then
            ent._hooked_crab = true
            ent:DoTaskInTime(1, function()
                local msg = string.format("[THÔNG BÁO] %s đã xuất hiện ở %s!", ent:GetDisplayName(), world)
                TheNet:Announce(msg)
            end)
        
        elseif ent.prefab == "daywalker" and not ent._hooked_crab then
            ent._hooked_crab = true
            ent:DoTaskInTime(1, function()
                local msg = string.format("[THÔNG BÁO] %s đã xuất hiện ở %s!", ent:GetDisplayName(), world)
                TheNet:Announce(msg)
            end)
        
        elseif ent.prefab == "daywalker2" and not ent._hooked_crab then
            ent._hooked_crab = true
            ent:DoTaskInTime(1, function()
                local msg = string.format("[THÔNG BÁO] %s đã xuất hiện ở %s!", ent:GetDisplayName(), world)
                TheNet:Announce(msg)
            end)
        end
    end
end

-- Gắn sự kiện theo dõi
local function AttachDeathListeners()
    for _, ent in pairs(GLOBAL.Ents) do
        if ent.prefab and not ent._death_hooked and death_list[ent.prefab] then
            ent:ListenForEvent("death", onEntityDeath)
            ent._death_hooked = true
        end
    end
end

-- 📥 Nhận lệnh từ Discord
local function CheckCommand()
    GLOBAL.TheSim:GetPersistentString("cmd_queue.json", function(success, data)
        if success and data then
            local ok, parsed = pcall(json.decode, data)
            if ok and parsed and parsed.command and parsed.command ~= "" then
                print("⏩ Thực thi từ Discord: " .. parsed.command)
                local ok2, err = pcall(loadstring(parsed.command))
                if not ok2 then
                    print("⚠️ Lỗi thực thi: " .. tostring(err))
                    GLOBAL.TheNet:Announce("[LỖI] Không thể thực thi lệnh từ Discord.")
                end
                GLOBAL.TheSim:SetPersistentString("cmd_queue.json", json.encode({command="", discord_msg=nil}), false)
            end
        end
    end)
end

-- 📨 Chat từ Discord
local function CheckQueue()
    GLOBAL.TheSim:GetPersistentString("chat_queue.json", function(success, data)
        if success and data then
            if data:find("KLEI") then data = data:sub(11) end
            local ok, decoded = pcall(json.decode, data)
            if ok and type(decoded) == "table" and #decoded > 0 then
                local next = table.remove(decoded, 1)
                if next and next.from and next.text then
                    local msg = string.format("[DISCORD] %s: %s", next.from, next.text)
                    GLOBAL.TheNet:Announce(msg)
                    local new = json.encode(decoded)
                    GLOBAL.TheSim:SetPersistentString("chat_queue.json", new, false)
                end
            end
        end
    end)
end

-- 🚀 Chờ TheWorld khởi tạo
local function WaitForTheWorld()
    while GLOBAL.TheWorld == nil do coroutine.yield(1) end
    print("[DiscordScript] ✅ Bắt đầu khi TheWorld sẵn sàng")
    GLOBAL.TheWorld:DoPeriodicTask(5, AttachDeathListeners)
    GLOBAL.TheWorld:DoPeriodicTask(5, TrackBossSpawners)
    GLOBAL.TheWorld:DoPeriodicTask(1, CheckCommand)
    GLOBAL.TheWorld:DoPeriodicTask(1, CheckQueue)
    GLOBAL.TheWorld:DoPeriodicTask(60, WriteOnlinePlayers)
    GLOBAL.TheWorld:DoPeriodicTask(60, WriteWorldStatus)
end

-- Gọi coroutine
local co = coroutine.create(WaitForTheWorld)
local function StepCoroutine()
    local success, delay = coroutine.resume(co)
    if coroutine.status(co) ~= "dead" then
        GLOBAL.scheduler:ExecuteInTime(delay or 1, StepCoroutine)
    end
end

StepCoroutine()
