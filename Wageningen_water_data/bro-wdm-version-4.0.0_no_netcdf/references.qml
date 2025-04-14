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
<rasterrenderer classificationMin="1" alphaBand="-1" nodataColor="" classificationMax="5" band="1" type="singlebandpseudocolor" opacity="1">
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
<colorrampshader maximumValue="5" clip="0" minimumValue="1" labelPrecision="0" classificationMode="2" colorRampType="EXACT">
<item alpha="255" value="1" color="#440154" label="de Gruijter et al., 2004 (value=1)"/>
<item alpha="255" value="2" color="#3b528b" label="Hoogland et al., 2014 (value=2)"/>
<item alpha="255" value="3" color="#21908c" label="Gerritsen et al., 2021 (value=3)"/>
<item alpha="255" value="4" color="#5dc963" label="Walvoort et al., 2023 (value=4)"/>
<item alpha="255" value="5" color="#fde725" label="Teuling et al., 2024 (value=5)"/>
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
