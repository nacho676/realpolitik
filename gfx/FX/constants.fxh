

Code
[[

// --------------------------------------------------------------
// A collection of constants that can be used to tweak the shaders
// To update: run "reloadfx all"
// --------------------------------------------------------------

// --------------------------------------------------------------
// ------------------    Light          -------------------------
// --------------------------------------------------------------
static const float NIGHT_AMBIENT_BOOST = 3.4f; // Realpolitik: was 3.0 (Cold War Iron Curtain look)


static const float3 DayAmbientMapPosX = float3(0.1, 0.1, 0.05);  // right
static const float3 DayAmbientMapNegX = float3(0.15, 0.15, 0.15);  // left
static const float3 DayAmbientMapPosY = float3(0.03, 0.03, 0.06);  // kills everything
static const float3 DayAmbientMapNegY = float3(0.0, 0.0, 0.0);  // from under
static const float3 DayAmbientMapPosZ = float3(0.0502, 0.05023, 0.1023);  // top
static const float3 DayAmbientMapNegZ = float3(0.03, 0.033, 0.033);  // bottom

static const float3 NightAmbientMapPosX = float3(0.2, 0.2, 0.2);  // right
static const float3 NightAmbientMapNegX = float3(0.0, 0.0, 0.0);  // left
static const float3 NightAmbientMapPosY = float3(0.01, 0.01, 0.01);  // kills everything
static const float3 NightAmbientMapNegY = float3(0.0, 0.0, 0.1);  // from under
static const float3 NightAmbientMapPosZ = float3(0.06, 0.1, 0.15);  // top
static const float3 NightAmbientMapNegZ = float3(0.14, 0.14, 0.2);  // bottom

// NOTE: regular unit ambient colors set from defines. this is night
static const float3 NightAmbientPosX = float3(2.0, 2.0, 2.0);  // right
static const float3 NightAmbientNegX = float3(0.2, 0.2, 0.2);  // left
static const float3 NightAmbientPosY = float3(0.1, 0.1, 0.1);  // kills everything
static const float3 NightAmbientNegY = float3(0.0, 0.0, 0.0);  // from under
static const float3 NightAmbientPosZ = float3(3.0, 3.0, 3.0);  // top
static const float3 NightAmbientNegZ = float3(0.8, 0.8, 0.8);  // bottom

// --------------------------------------------------------------
// ------------------    Specular       -------------------------
// --------------------------------------------------------------
static const float SPECULAR_WIDTH 				= 15.0;
static const float SPECULAR_MULTIPLIER			= 1.0;
static const float MAP_SPECULAR_WIDTH			= 15.0;

// --------------------------------------------------------------
// ------------------    TERRAIN        -------------------------
// --------------------------------------------------------------
static const float CITY_LIGHTS_TILING 			= 0.09103;
static const float CITY_LIGHTS_INTENSITY 		= 5.5;
static const float CITY_LIGHTS_BLOOM_FACTOR 	= 0.3;

static const float TERRAIN_TILE_FREQ 			= 128.0f;
static const float MAP_NUM_TILES 				= 4.0f;
static const float TEXELS_PER_TILE 				= 512.0f;
static const float ATLAS_TEXEL_POW2_EXPONENT	= 11.0f;
static const float TERRAIN_WATER_CLIP_HEIGHT    = 3.0f;
static const float TERRAIN_WATER_CLIP_CAM_HI	= 700.0f;
static const float TERRAIN_WATER_CLIP_CAM_LO	= 50.0f;

static const float MUD_TILING 					= 0.09;
static const float MUD_NORMAL_CUTOFF 			= 10.982;
static const float MUD_STRENGHTEN 				= 1.0;

static const float 	SNOW_OPACITY_MIN			= 0.95f;
static const float 	SNOW_OPACITY_MAX			= 0.2f;
static const float 	SNOW_CAM_MIN 				= 50.0f;
static const float 	SNOW_CAM_MAX 				= 300.0f;
static const float 	MUD_CAM_MIN 				= 50.0f;
static const float 	MUD_CAM_MAX 				= 300.0f;
static const float 	ICE_CAM_MIN 				= 100.0f;
static const float 	ICE_CAM_MAX 				= 350.0f;


static const float 	SNOW_START_HEIGHT 			= 3.0f;
static const float 	SNOW_RIDGE_START_HEIGHT 	= 11.0f;
static const float 	SNOW_NORMAL_START 			= 0.7f;
static const float3 SNOW_COLOR 					= float3( 0.46, 0.48, 0.69 );
static const float3 SNOW_WATER_COLOR 			= float3( 0.3, 0.6, 1.0 );
static const float 	SNOW_CLIFFS 				= 5.0f;
static const float 	SNOW_SPEC_GLOSS_MULT 		= 0.2f;
static const float 	SNOW_TILING  				= 0.05f;
static const float 	SNOW_NOISE_TILING  			= 0.06f;
static const float 	SNOW_ICE_NOISE_TILING  		= 0.0625f;
static const float 	SNOW_FROST_MIN_EFFECT  		= 0.4f;

static const float3 ICE_COLOR 					= float3( 0.5f, 0.6f, 0.9f );
static const float 	ICE_NOISE_TILING  			= 0.1f; //0.068f;

static const float WATER_COLOR_LIGHTNESS = 0.5;
static const float WATER_RIPPLE_EFFECT = 0.0025;

static const float COLORMAP_OVERLAY_STRENGTH 	= 0.75f;
static const float COLORMAP_MUD_OVERLAY_STRENGTH = 0.5f;

static const float3 FAKE_CUBEMAP_COLOR 			= float3(0.0f, 0.0f, 0.0f);

// MILD_WINTER_VALUE = ###,						defines.lua   (reload defines)
// NORMAL_WINTER_VALUE = ##,					defines.lua   (reload defines)
// SEVERE_WINTER_VALUE = ###,					defines.lua   (reload defines)


static const float 	BORDER_TILE					= 0.4f;
// BORDER_WIDTH		= ###						defines.lua   (reload defines)



// Snow color									standardfuncsgfx.fxh
// static const float3 SNOW_COLOR = float3( 0.8f, 0.8f, 0.8f );
// Snow fade									standardfuncsgfx.fxh
// 	float vSnow = saturate( saturate( vNoise - ( 1.0f - vIsSnow ) ) * 5.0f );

static const float 	TREE_SEASON_MIN 			= 0.5f;
static const float 	TREE_SEASON_FADE_TWEAK 		= 2.5f;

// --------------------------------------------------------------
// ------------------    HDR          	-------------------------
// --------------------------------------------------------------
static const float3 LUMINANCE_VECTOR  			= float3(0.2125f, 0.7154f, 0.0721f);

// --------------------------------------------------------------
// ------------------    TREES          -------------------------
// --------------------------------------------------------------
static const float 	TREE_SPECULAR = 0.1f;
static const float 	TREE_ROUGHNESS = 0.6f;

// --------------------------------------------------------------
// ------------------    WATER          -------------------------
// --------------------------------------------------------------

//static const float  WATER_TILE					= 4.0f;
static const float  WATER_TIME_SCALE			= 1.0f / 50.0f;
static const float  WATER_HEIGHT = 9.5f;
static const float  WATER_HEIGHT_RECP = 1.0f / WATER_HEIGHT;
static const float  WATER_HEIGHT_RECP_SQUARED = WATER_HEIGHT_RECP * WATER_HEIGHT_RECP;


// --------------------------------------------------------------
// ------------------    BUILDINGS      -------------------------
// --------------------------------------------------------------

//	PORT_SHIP_OFFSET = 2.0,					defines.lua   (reload defines)
//	SHIP_IN_PORT_SCALE = 0.25,
//  BUILDING SIZE?



// --------------------------------------------------------------
// ------------------    FOG            -------------------------
// --------------------------------------------------------------

static const float3 FOG_COLOR 					= float3( 0.32, 0.48, 0.65 ); // Realpolitik: was ( 0.12, 0.28, 0.6 ) (Cold War Iron Curtain look)
static const float 	FOG_BEGIN					= 1.0f;
static const float 	FOG_END 					= 150.0f;
static const float 	FOG_MAX 					= 0.35f;

//static const float 	FOG_MAX 					= 1000.7f;

// Fog of war
static const float 	FOW_MAX 					= 0.5f;
static const float  FOW_CAMERA_MIN				= 200;
static const float  FOW_CAMERA_MAX				= 500;


// --------------------------------------------------------------
// ------------------    BUILDINGS      -------------------------
// --------------------------------------------------------------


static const float  SHADOW_WEIGHT_TERRAIN    	= 0.7f;
static const float  SHADOW_WEIGHT_MAP    		= 0.7f;
static const float  SHADOW_WEIGHT_BORDER   		= 0.7f;
static const float  SHADOW_WEIGHT_WATER   		= 0.5f;
static const float  SHADOW_WEIGHT_RIVER   		= 0.2f; // Realpolitik: was 0.4 (Cold War Iron Curtain look)
static const float  SHADOW_WEIGHT_TREE   		= 0.7f;

// LIGHT_SHADOW_DIRECTION_X = -8.0				defines.lua   (reload defines)
// LIGHT_SHADOW_DIRECTION_Y = -8.0				defines.lua   (reload defines)
// LIGHT_SHADOW_DIRECTION_Z = 5.0				defines.lua   (reload defines)


// --------------------------------------------------------------
// ------------------    CAMERA         -------------------------
// --------------------------------------------------------------



// CAMERA_MIN_HEIGHT = 50.0,					defines.lua   (reload defines)
// CAMERA_MAX_HEIGHT = 3000.0,					defines.lua   (reload defines)

// --------------------------------------------------------------
// ------------------    GRADIENT BORDERS   ---------------------
// --------------------------------------------------------------

static const float GB_CAM_MIN = 100.0f;
static const float GB_CAM_MAX = 350.0f;
static const float GB_CAM_MAX_FILLING_CLAMP = 1.0f; // Realpolitik: was 0.8. Zoomed out, countries fill evenly instead of fading from the borders inward
static const float GB_THRESHOLD = 0.1f; // Realpolitik: was 0.05, a little more fill at mid zoom
static const float GB_THRESHOLD2 = 0.25f; // interpolation time
//static const float3 GB_OUTLINE_COLOR = float3( 0.0f, 0.0f, 0.0f );
static const float GB_OUTLINE_CUTOFF_SEA = 0.990f; // Magic number to balance cutoff on edges without neighbor (over Sea)
static const float GB_OPACITY_NEAR = 1.0f; // Transparency when camera is near
static const float GB_OPACITY_FAR = 0.95f; // Realpolitik: was 0.85 (Cold War Iron Curtain look)
static const float BORDER_NIGHT_DESATURATION_MAX = 0.4f; // Realpolitik: was 0.2 (Cold War Iron Curtain look)
static const float BORDER_FOW_REMOVAL_FACTOR = .845f; // Realpolitik: was .8 (Cold War Iron Curtain look)
static const float BORDER_LIGHT_REMOVAL_FACTOR = 0.2f; // Realpolitik: was 0.8. Country colors keep the terrain light and shade (Cold War Iron Curtain look)
static const float GB_STRENGTH_CH1 = 1.0; // Opacity of bottom layer
static const float GB_STRENGTH_CH2 = 0.8; // Realpolitik: was 1.0 (Cold War Iron Curtain look)
static const float GB_FIRST_LAYER_PRIORITY = 0.1; // Realpolitik: was 0.4 (Cold War Iron Curtain look)
static const float BORDER_MAP_TILE = 18000.0f;
// Realpolitik: width of the dark country outline, normal up close (the base game's 5.25) and thicker as the camera pulls back.
static const float GB_OUTLINE_WIDTH_NEAR = 5.25f / 255.0f;
static const float GB_OUTLINE_WIDTH_FAR = 8.5f / 255.0f; // was 18: thick dark bands stood out between countries
// Realpolitik: the country color keeps the terrain's light and shade instead of covering it, so relief shows through a solid color.
static const float GB_RELIEF = 0.23f; // 0 = flat color (base game), 1 = full terrain shading. Low: the lighting (BORDER_LIGHT_REMOVAL_FACTOR) already shades
static const float GB_RELIEF_MID = 0.37f; // terrain brightness that keeps the country color unchanged
static const float GB_OUTLINE_DARKEN = 0.71f; // base game 0.5: the line between countries, softer so it doesn't stand out
// Realpolitik: rivers stay blue over the country colors.
static const float3 RIVER_BLUE = float3( 0.08f, 0.3f, 0.72f );
static const float RIVER_BLUE_STRENGTH = 0.75f;
static const float RIVER_COUNTRY_TINT = 0.1f;
static const float RIVER_WIDEN_FAR = 1.6f; // extra half width from afar; if rivers get thinner when zooming out, make this negative
// Realpolitik: lakes without the country color (pdxmap.shader). Colormap water is (79, 102, 142): blue - red = 0.25.
static const float LAKE_BLUE_FROM = 0.13f;
static const float LAKE_KEEP_WATER = 0.93f; // share of the lake that shows water instead of the country color
static const float3 LAKE_COLOR = float3( 0.045f, 0.15f, 0.31f ); // a little lighter than the open sea (MDR_GLOBE_SEA_COLOR)
static const float LAKE_WATER_HEIGHT = 0.9248f; // pdxwater.shader: water height / water level. Sea 0.9195 (88), lakes from 0.930 (89)

// --------------------------------------------------------------
// ------------------    SECONDARY COLOR MAP   ------------------
// --------------------------------------------------------------

static const float SEC_MAP_TILE = 6000.0f;


// --------------------------------------------------------------
// ------------------    MAP ARROWS   ---------------------------
// --------------------------------------------------------------

static const float MAP_ARROW_SEL_BLINK_SPEED = 5.5f;
static const float MAP_ARROW_SEL_BLINK_RANGE = 0.7f;
static const float MAP_ARROW_NORMALS_STR_TERR = 0.0125f;
static const float MAP_ARROW_NORMALS_STR_WATER = 0.08f;

// --------------------------------------------------------------
// ------------------    PARTICLES   ----------------------------
// --------------------------------------------------------------
static const float PARTICLE_FADE_START_DISTANCE = 100;
static const float PARTICLE_FADE_STOP_DISTANCE = 350;

// --------------------------------------------------------------
// -------------    RIM LIGHT (PDXMESH)   -----------------------
// --------------------------------------------------------------
static const float 	RIM_START 		= 0.55f;
static const float 	RIM_END 		= 0.6f;
static const float4 RIM_COLOR 		= float4( 0.3f, 0.3f, 0.3f, 0.0f );


// --------------------------------------------------------------
// -------------    MAP BORDER (PDXMESH)   ----------------------
// --------------------------------------------------------------
static const float3 BORDER_SUN_INTENSITY = float3(1.0, 1.0, 1.1); // Realpolitik: was (1.5, 1.5, 1.6) (Cold War Iron Curtain look)
static const float3 BORDER_SUN_DIRECTION = float3(-0.2, 0.9, 0.1);
//static const float3 BORDER_SUN_DIRECTION = float3(-0.1, 0.5, 0.0);
//static const float3 BORDER_SUN_DIRECTION = float3(0.2, 0.5, 0.0);

// --------------------------------------------------------------
// ------------------    GLOBE (Realpolitik)  -------------------
// --------------------------------------------------------------
// MdrGlobePos in standardfuncsgfx.fxh. The camera goes up to CAMERA_MAX_HEIGHT (zz_mdr_defines.lua).
static const float MDR_GLOBE_ON = 1.0f; // 0 turns the globe off
static const float MDR_GLOBE_CAM_START = 1800.0f; // the map starts to roll, very slowly: at 2000 it is still almost flat
static const float MDR_GLOBE_SPREAD = 1.37f; // the game draws about +-2425 of the +-2816 around the camera at its top. Near a pole all of it shows, so the terrain's mesh spreads this much. More than needed costs nothing: what passes the back of the globe is clipped
static const float MDR_GLOBE_PAST_POLE = 0.00207f; // how much the globe keeps turning per row once the camera looks past the map's end (radians), as much as in the last rows: if it stopped at the pole, the camera would go on with nothing moving
static const float MDR_GLOBE_SOUTH_FROM = 252.0f; // from this row looked at, the globe turns evenly to the south pole
static const float MDR_GLOBE_SOUTH_POLE = -50.0f; // and this is where it gets there: a little past the map, in the margin
static const float MDR_GLOBE_SPREAD_ROWS = 1.73f; // and it draws from a third of the camera's height behind it: looking north, the rows further south go spread the same way
static const float MDR_GLOBE_CAM_TOP = 3000.0f; // it draws less the lower the camera, so the columns' spread grows from this height down
static const float MDR_GLOBE_SPREAD_LEVEL = 13.1f; // the mesh's heights stop matching once it spreads, so it goes flat: above WATER_HEIGHT + TERRAIN_WATER_CLIP_HEIGHT, so the underwater pass skips it
static const float MDR_GLOBE_SEA_BLUE = 0.1f; // the color map says what is sea: blue minus red. mark_sea_in_colormap in herramientas/construir_mapa.py leaves its sea at 0.25 (0.2 if the game reads it as sRGB) and its land under 0.05
static const float MDR_GLOBE_FRAME_HIDE = 1800.0f; // the map's frames and logo go above this camera height
static const float MDR_GLOBE_CAM_END = 3000.0f; // the map is a full sphere at the camera's top
static const float MDR_GLOBE_CLOSE = 1.2f; // near a pole and late in the roll the longitudes go around faster, so the sheet's open back is about 28 degrees at a bend of 0.8 and 5 at 0.9
static const float MDR_GLOBE_NAME_LAT_FROM = 1.17f; // the names fade between these latitudes (radians), about 67 and 70 degrees: above, their letters are a smear. Greenland's sits at 70 to 76
static const float MDR_GLOBE_NAME_LAT_TO = 1.22f;
static const float MDR_GLOBE_RELIEF = 1.0f; // height of the terrain on the sphere
static const float MDR_GLOBE_MIN_ROLL = 0.02f; // below this the map blends from flat
static const float MDR_GLOBE_WATER_FADE = 0.012f; // the real water fades up to this bend, about a height of 1930. The terrain finishes painting the sea at a quarter of it, so the sea floor does not show through
static const float3 MDR_GLOBE_SEA_COLOR = float3( 0.025f, 0.11f, 0.24f ); // the sea painted by the terrain
static const float3 MDR_GLOBE_SEA_BACK = float3( 0.001f, 0.006f, 0.026f ); // the same sea on the sphere behind the map: the sky shader's colors come out much brighter
static const float3 MDR_GLOBE_AIR_BACK = float3( 0.03f, 0.08f, 0.2f ); // and the atmosphere on it
static const float3 MDR_GLOBE_AIR_COLOR = float3( 0.2f, 0.42f, 0.85f ); // the atmosphere
static const float MDR_GLOBE_ATMOSPHERE = 0.45f; // how strong it is at the edge of the globe
static const float MDR_GLOBE_HALO_WIDTH = 0.06f; // the glow around the globe, in globe radii
static const float MDR_GLOBE_HALO_STRENGTH = 0.45f;
static const float MDR_GLOBE_SPACE_FROM = 1500.0f; // stars start to show at this camera height
static const float MDR_GLOBE_SPACE_FULL = 2400.0f;
static const float MDR_GLOBE_MOON_APART = 0.37f; // how far the moon is from the middle of the night (radians), so the globe does not hide it exactly when it hides the sun
static const float MDR_GLOBE_MOON_HEIGHT = 0.13f; // and above it
]]
