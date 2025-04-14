<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.22.3" minScale="0" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" maxScale="0">
<flags>
<Identifiable>1</Identifiable>
<Removable>1</Removable>
<Searchable>1</Searchable>
<Private>0</Private>
</flags>
<temporal fetchMode="0" enabled="0" mode="0">
<fixedRange>
<start></start>
<end></end>
</fixedRange>
</temporal>
<customproperties>
<Option type="Map">
<Option name="WMSBackgroundLayer" value="false" type="bool"/>
<Option name="WMSPublishDataSourceUrl" value="false" type="bool"/>
<Option name="embeddedWidgets/count" value="0" type="int"/>
<Option name="identify/format" value="Value" type="QString"/>
</Option>
</customproperties>
<pipe-data-defined-properties>
<Option type="Map">
<Option name="name" value="" type="QString"/>
<Option name="properties"/>
<Option name="type" value="collection" type="QString"/>
</Option>
</pipe-data-defined-properties>
<pipe>
<provider>
<resampling maxOversampling="2" enabled="false" zoomedOutResamplingMethod="nearestNeighbour" zoomedInResamplingMethod="nearestNeighbour"/>
</provider>
<rasterrenderer classificationMin="10" alphaBand="-1" nodataColor="" classificationMax="254" band="1" type="singlebandpseudocolor" opacity="1">
<rasterTransparency/>
<minMaxOrigin>
<limits>None</limits>
<extent>WholeRaster</extent>
<statAccuracy>Estimated</statAccuracy>
<cumulativeCutLower>0.02</cumulativeCutLower>
<cumulativeCutUpper>0.98</cumulativeCutUpper>
<stdDevFactor>2</stdDevFactor>
</minMaxOrigin>
<rastershader>
<colorrampshader maximumValue="254" clip="0" minimumValue="10" labelPrecision="0" classificationMode="2" colorRampType="DISCRETE">
<item alpha="255" value="10" color="#46085c" label="0 - 10"/>
<item alpha="255" value="20" color="#481769" label="10 - 20"/>
<item alpha="255" value="30" color="#482475" label="20 - 30"/>
<item alpha="255" value="40" color="#46307e" label="30 - 40"/>
<item alpha="255" value="50" color="#433d84" label="40 - 50"/>
<item alpha="255" value="60" color="#3f4889" label="50 - 60"/>
<item alpha="255" value="70" color="#3a538b" label="60 - 70"/>
<item alpha="255" value="80" color="#355e8d" label="70 - 80"/>
<item alpha="255" value="90" color="#31688e" label="80 - 90"/>
<item alpha="255" value="100" color="#2c718e" label="90 - 100"/>
<item alpha="255" value="110" color="#297b8e" label="100 - 110"/>
<item alpha="255" value="120" color="#25848e" label="110 - 120"/>
<item alpha="255" value="130" color="#218e8d" label="120 - 130"/>
<item alpha="255" value="140" color="#1f978b" label="130 - 140"/>
<item alpha="255" value="150" color="#1fa188" label="140 - 150"/>
<item alpha="255" value="160" color="#24aa83" label="150 - 160"/>
<item alpha="255" value="170" color="#2eb37c" label="160 - 170"/>
<item alpha="255" value="180" color="#3dbc74" label="170 - 180"/>
<item alpha="255" value="190" color="#50c46a" label="180 - 190"/>
<item alpha="255" value="200" color="#65cb5e" label="190 - 200"/>
<item alpha="255" value="210" color="#7cd250" label="200 - 210"/>
<item alpha="255" value="220" color="#95d840" label="210 - 220"/>
<item alpha="255" value="230" color="#b0dd2f" label="220 - 230"/>
<item alpha="255" value="240" color="#cae11f" label="230 - 240"/>
<item alpha="255" value="250" color="#e5e419" label="240 - 250"/>
<item alpha="255" value="254" color="#fde725" label=">250"/>
<rampLegendSettings prefix="" maximumLabel="" minimumLabel="" orientation="2" direction="0" useContinuousLegend="1" suffix="">
<numericFormat id="basic">
<Option type="Map">
<Option name="decimal_separator" value="" type="QChar"/>
<Option name="decimals" value="6" type="int"/>
<Option name="rounding_type" value="0" type="int"/>
<Option name="show_plus" value="false" type="bool"/>
<Option name="show_thousand_separator" value="true" type="bool"/>
<Option name="show_trailing_zeros" value="false" type="bool"/>
<Option name="thousand_separator" value="" type="QChar"/>
</Option>
</numericFormat>
</rampLegendSettings>
</colorrampshader>
</rastershader>
</rasterrenderer>
<brightnesscontrast gamma="1" brightness="0" contrast="0"/>
<huesaturation colorizeBlue="128" grayscaleMode="0" colorizeRed="255" colorizeGreen="128" saturation="0" invertColors="0" colorizeStrength="100" colorizeOn="0"/>
<rasterresampler maxOversampling="2"/>
<resamplingStage>resamplingFilter</resamplingStage>
</pipe>
<blendMode>0</blendMode>
</qgis>
