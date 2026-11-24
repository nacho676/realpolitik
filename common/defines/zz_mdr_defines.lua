-- Loads after Millennium Dawn's MD_defines.lua (alphabetical order), so these values win.
NDefines.NBuildings.MAX_SHARED_SLOTS = 104 -- Millennium Dawn: 80. 104 fills 8 rows of 13 in the state view.
NDefines.NProduction.MAX_EQUIPMENT_RESOURCES_NEED = 5 -- Millennium Dawn: 4. Rare earths are one more material on modern designs.

-- Command and production limits. Defines are global: they apply to every country, AI included.
NDefines.NMilitary.CORPS_COMMANDER_DIVISIONS_CAP = 76 -- Millennium Dawn: 24
NDefines.NMilitary.FIELD_MARSHAL_DIVISIONS_CAP = 76 -- Millennium Dawn: 20
NDefines.NMilitary.FIELD_MARSHAL_ARMIES_CAP = 10 -- Millennium Dawn: 4
NDefines.NProduction.MAX_CIV_FACTORIES_PER_LINE = 25 -- vanilla 15. Fixed: the engine has no per-country or in-game control.
NDefines.NProduction.CONVOY_MAX_NAV_FACTORIES_PER_LINE = 50 -- Millennium Dawn: 15
NDefines.NProduction.DEFAULT_MAX_NAV_FACTORIES_PER_LINE = 30 -- Millennium Dawn: 5
NDefines.NProduction.CAPITAL_SHIP_MAX_NAV_FACTORIES_PER_LINE = 25 -- Millennium Dawn: 5
NDefines.NProduction.FLOATING_HARBOR_MAX_NAV_FACTORIES_PER_LINE = 30 -- vanilla 5 (Modular Causeway System and other floating harbors)
NDefines.NProduction.RAILWAY_GUN_MAX_MIL_FACTORIES_PER_LINE = 30 -- vanilla 5

-- Country colors and borders like Cold War Iron Curtain: a little more saturated, firmer borders, thinner center gradient.
NDefines.NGraphics.COUNTRY_COLOR_SATURATION_MODIFIER = 0.7 -- vanilla 0.6
NDefines.NGraphics.COUNTRY_COLOR_BRIGHTNESS_MODIFIER = 0.8 -- vanilla 0.8
NDefines.NGraphics.BORDER_WIDTH = 1.75 -- Millennium Dawn: 1.0
NDefines.NGraphics.GRADIENT_BORDERS_COUNTRY_CENTER_THICKNESS = 1.0 -- Millennium Dawn: 0

-- Map readability. City names and small victory points stay visible further out (Millennium Dawn: {180, 420, 1000}).
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF = {260, 560, 1150}
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF_MAX = 1150.0 -- vanilla 800
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_DOT_CUTOFF_MAX = 1300.0 -- vanilla 1000
NDefines.NGraphics.AIRBASE_ICON_DISTANCE_CUTOFF = 1200 -- vanilla 900
NDefines.NGraphics.NAVALBASE_ICON_DISTANCE_CUTOFF = 1200 -- Millennium Dawn 900
-- Stronger counter colors in the allegiance color mode.
NDefines.NGraphics.COUNTER_MODE_ALLEGIANCE_OURS = { 0.24, 0.84, 0.34, 1.0 }
NDefines.NGraphics.COUNTER_MODE_ALLEGIANCE_ALLIED = { 0.22, 0.6, 1.0, 1.0 }
NDefines.NGraphics.COUNTER_MODE_ALLEGIANCE_ENEMY = { 1.0, 0.22, 0.22, 1.0 }

-- Globe: the game stops the camera where its view reaches the map's edge plus this margin (Millennium Dawn: 100). At full zoom-out
-- the view goes from height / 3 behind the camera to height * 0.4913 ahead. This is big enough for the camera to look at both ends
-- of the map from its top, so zooming out leaves it over the same place, and each pole is just past the last row (see MdrGlobeLat0).
-- With zoom close the margin shows past the map: seven frames each way in map/ambient_object.txt cover it.
NDefines.NGraphics.CAMERA_OUTSIDE_MAP_DISTANCE_TOP = 1300.0
NDefines.NGraphics.CAMERA_OUTSIDE_MAP_DISTANCE_BOTTOM = 1280.0

-- AI (MEJORAR IA.md, stage 1): fewer reckless attacks, fewer encirclements, motorize supply earlier.
-- ATTACK_HEAVILY_DEFENDED_LIMIT (MD 1.2, vanilla 0.5) is already cautious and is left alone.
NDefines.NAI.PLAN_ATTACK_DEPTH_FACTOR = 0.83 -- Millennium Dawn: 1.2, vanilla 0.5. Shorter thrusts that can't be cut off.
NDefines.NAI.GARRISON_FRACTION = 0.11 -- vanilla 0.0. Part of each front keeps holding the line while the rest attacks.
NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_MED = 0.77 -- vanilla 0.7. Attack only with rested units.
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_MED = 0.57 -- vanilla 0.5
NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_HIGH = 0.53 -- vanilla 0.45
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_HIGH = 0.37 -- vanilla 0.3
NDefines.NAI.DIVISION_SUPPLY_RATIO_TO_MOTORIZE = 0.93 -- vanilla 0.8. Trucks before units starve, not after.
NDefines.NAI.MAIN_ENEMY_FRONT_IMPORTANCE = 3.3 -- Millennium Dawn: 2.5, vanilla 4. The main front gets more units.
