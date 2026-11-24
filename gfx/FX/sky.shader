Includes = {
	"constants.fxh"
	"standardfuncsgfx.fxh"
}

PixelShader =
{
	Samplers =
	{
		ReflectionCubeMap =
		{
			Index = 0
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Clamp"
			AddressV = "Clamp"
			Type = "Cube"
		}
	}
}


VertexStruct VS_INPUT_SKY
{
    int2 position			: POSITION;
};

VertexStruct VS_OUTPUT_SKY
{
    float4 position	: PDX_POSITION;
	float3 pos		: TEXCOORD0;
};



VertexShader =
{
	MainCode VertexShader
	[[
		
		VS_OUTPUT_SKY main( const VS_INPUT_SKY VertexIn )
		{
			VS_OUTPUT_SKY VertexOut;
		
			VertexOut.position = float4( VertexIn.position, 1.0f, 1.0f );
			float4 position = mul( InvViewProjMatrix, VertexOut.position );
			position.xyz /= position.w;
			VertexOut.pos = position.xyz;
			return VertexOut;
		}
		
	]]
}

PixelShader =
{
	MainCode PixelShader
	[[
		// Realpolitik: globe. Space around it, all calculated: no new textures.
		float MdrHash( float3 v )
		{
			return frac( sin( dot( v, float3( 12.9898f, 78.233f, 37.719f ) ) ) * 43758.5453f );
		}

		float MdrNoise( float3 v )
		{
			float3 i = floor( v );
			float3 f = frac( v );
			f = f * f * ( 3.0f - 2.0f * f );
			return lerp(
				lerp( lerp( MdrHash( i ), MdrHash( i + float3( 1, 0, 0 ) ), f.x ), lerp( MdrHash( i + float3( 0, 1, 0 ) ), MdrHash( i + float3( 1, 1, 0 ) ), f.x ), f.y ),
				lerp( lerp( MdrHash( i + float3( 0, 0, 1 ) ), MdrHash( i + float3( 1, 0, 1 ) ), f.x ), lerp( MdrHash( i + float3( 0, 1, 1 ) ), MdrHash( i + float3( 1, 1, 1 ) ), f.x ), f.y ),
				f.z );
		}

		float MdrStars( float3 vDir, float vScale, float vRarity )
		{
			float3 vCell = floor( vDir * vScale );
			float vHash = MdrHash( vCell );
			float3 vStar = vCell + 0.25f + 0.5f * float3( MdrHash( vCell + 1.7f ), MdrHash( vCell + 3.1f ), MdrHash( vCell + 5.3f ) );
			float vDot = saturate( 1.0f - length( vDir * vScale - vStar ) * 5.0f );
			return vHash > vRarity ? vDot * vDot * ( vHash - vRarity ) / ( 1.0f - vRarity ) : 0.0f;
		}

		// The map's column over the middle of the night, as an angle around the sky: the sky turns with the map, so a column at
		// the angle a is the direction ( sin a, 0, cos a ). From what CalcGlobeNormal and DayNightFactor do. On the game's own
		// hour, the only clock here that stops when paused: vGlobalTime and FoWTime keep running. One turn per game day, and
		// sine and cosine join at midnight by themselves.
		float MdrNightAngle()
		{
			return atan2( DayNight_Hour_SunDir.y, DayNight_Hour_SunDir.w ) + 6.28318f * ( GMT_OFFSET / MAP_SIZE_X - DayNight_Hour_SunDir.x );
		}

		float3 MdrSkyDir( float vAngle, float vHeight )
		{
			float vFlat = sqrt( saturate( 1.0f - vHeight * vHeight ) );
			return float3( sin( vAngle ) * vFlat, vHeight, cos( vAngle ) * vFlat );
		}

		float3 MdrSpace( float3 vRay )
		{
			// The stars stay still around the Earth: turn the view with the globe, so moving the map moves them.
			float2 vLook = MdrGlobeLook();
			float vLat0 = MdrGlobeLat0( vLook ) * MdrGlobeBend();
			float vLon0 = vLook.x / MAP_SIZE_X * 6.28318f;
			float vPole = vRay.y * sin( vLat0 ) + vRay.z * cos( vLat0 );
			float vFront = vRay.y * cos( vLat0 ) - vRay.z * sin( vLat0 );
			float3 vSky = float3( vRay.x * cos( vLon0 ) + vFront * sin( vLon0 ), vPole, vFront * cos( vLon0 ) - vRay.x * sin( vLon0 ) );

			// Milky Way: a soft band across the sky.
			float vBand = dot( vSky, normalize( float3( 0.35f, 0.7f, 0.6f ) ) );
			vBand = exp( -vBand * vBand * 14.0f );
			float vCloud = MdrNoise( vSky * 5.0f ) * 0.6f + MdrNoise( vSky * 13.0f ) * 0.3f + MdrNoise( vSky * 31.0f ) * 0.1f;
			float3 vSpace = float3( 0.34f, 0.32f, 0.46f ) * vBand * vCloud * vCloud * 0.55f;

			float vStars = MdrStars( vSky, 95.0f, 0.86f ) + MdrStars( vSky, 210.0f, 0.9f ) * 0.7f;
			vStars += MdrStars( vSky, 340.0f, 0.86f ) * vBand * 0.8f;
			vSpace += float3( 0.95f, 0.97f, 1.0f ) * vStars;

			// The sun and the moon sit in the sky with the stars: moving the map moves them, and they pass behind the globe.
			float3 vSunDir = MdrSkyDir( MdrNightAngle() + 3.14159f, -DayNight_Hour_SunDir.z ); // over the middle of the day
			float vSunDot = saturate( dot( vSky, vSunDir ) );
			vSpace += float3( 1.0f, 0.95f, 0.85f ) * ( smoothstep( 0.99986f, 0.99993f, vSunDot ) * 3.0f + pow( vSunDot, 3400.0f ) * 0.6f + pow( vSunDot, 260.0f ) * 0.07f );

			float3 vMoonDir = MdrSkyDir( MdrNightAngle() + MDR_GLOBE_MOON_APART, DayNight_Hour_SunDir.z + MDR_GLOBE_MOON_HEIGHT ); // on the night side
			float vMoonDisc = smoothstep( 0.99995f, 0.99998f, saturate( dot( vSky, vMoonDir ) ) );
			float vMoonLit = 0.25f + 0.75f * saturate( dot( normalize( vSky - vMoonDir ), normalize( vSunDir - vMoonDir ) ) * 0.5f + 0.5f );
			vSpace = lerp( vSpace, float3( 0.3f, 0.3f, 0.29f ) * vMoonLit * ( 0.75f + 0.25f * MdrNoise( vSky * 500.0f ) ), vMoonDisc );

			// The atmosphere glows around the globe, only once it is one.
			float vRoll = saturate( ( MdrGlobeBend() - 0.75f ) / 0.25f );
			if( vRoll > 0.0f )
			{
				float3 vCenter = MdrGlobeCenter();
				float vRadius = WATER_HEIGHT - vCenter.y;
				float vAlong = dot( vCenter - vCamPos, vRay );
				float vMiss = length( vCamPos + vRay * vAlong - vCenter );
				float vHalo = saturate( 1.0f - ( vMiss - vRadius ) / ( vRadius * MDR_GLOBE_HALO_WIDTH ) );
				vSpace = lerp( vSpace, MDR_GLOBE_AIR_COLOR, vRoll * vHalo * vHalo * MDR_GLOBE_HALO_STRENGTH );
			}

			// An ocean sphere behind the map: it covers the last 5 degrees around the north pole, which the map does not
			// reach, and whatever the game does not draw.
			float vBack = saturate( ( MdrGlobeBend() - 0.3f ) / 0.3f );
			if( vBack > 0.0f )
			{
				float3 vCenter = MdrGlobeCenter();
				float vRadius = WATER_HEIGHT - vCenter.y;
				float vAlong = dot( vCenter - vCamPos, vRay );
				float vMiss = length( vCamPos + vRay * vAlong - vCenter );
				if( vMiss < vRadius && vAlong > 0.0f )
				{
					float vMissShare = vMiss / vRadius;
					float vEdge = 1.0f - sqrt( saturate( 1.0f - vMissShare * vMissShare ) );
					float3 vOcean = lerp( MDR_GLOBE_SEA_BACK, MDR_GLOBE_AIR_BACK, vEdge * vEdge * vEdge * MDR_GLOBE_ATMOSPHERE );
					vSpace = lerp( vSpace, vOcean, vBack * saturate( ( vRadius - vMiss ) / 3.0f ) );
				}
			}
			return vSpace;
		}

		float4 main( VS_OUTPUT_SKY Input ) : PDX_COLOR
		{
			float3 color = texCUBE( ReflectionCubeMap, normalize( Input.pos - vCamPos ) ).rgb;
			float3 fog = ApplyDistanceFog( color.rgb, Input.pos );
		
			color = lerp( fog, color, max( saturate( Input.pos.y / 300.0f ), NegFogMultiplier ) );
			float vSpaceFade = MDR_GLOBE_ON * smoothstep( MDR_GLOBE_SPACE_FROM, MDR_GLOBE_SPACE_FULL, vCamPos.y ); // Realpolitik: globe
			if( vSpaceFade > 0.0f )
				color = lerp( color, MdrSpace( normalize( Input.pos - vCamPos ) ), vSpaceFade );
			return float4( color, 1.0f );
		}
		
		
	]]
}


BlendState BlendState
{
	BlendEnable = no
	AlphaTest = no
}


Effect sky
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShader"
}

