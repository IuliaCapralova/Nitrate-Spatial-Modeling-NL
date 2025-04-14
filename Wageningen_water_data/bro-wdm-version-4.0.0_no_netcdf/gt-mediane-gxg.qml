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
<rasterrenderer classificationMin="1" alphaBand="-1" nodataColor="" classificationMax="19" band="1" type="singlebandpseudocolor" opacity="1">
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
<colorrampshader maximumValue="19" clip="0" minimumValue="1" labelPrecision="0" classificationMode="2" colorRampType="EXACT">
<item alpha="255" value="1" color="#440154" label="Ia (value=1)"/>
<item alpha="255" value="2" color="#481668" label="Ic (value=2)"/>
<item alpha="255" value="3" color="#482878" label="IIa (value=3)"/>
<item alpha="255" value="4" color="#443a83" label="IIb (value=4)"/>
<item alpha="255" value="5" color="#3e4a89" label="IIc (value=5)"/>
<item alpha="255" value="6" color="#37598c" label="IIIa (value=6)"/>
<item alpha="255" value="7" color="#31688e" label="IIIb (value=7)"/>
<item alpha="255" value="8" color="#2b758e" label="IVu (value=8)"/>
<item alpha="255" value="9" color="#26838e" label="IVc (value=9)"/>
<item alpha="255" value="10" color="#21908c" label="Vao (value=10)"/>
<item alpha="255" value="11" color="#1f9d89" label="Vad (value=11)"/>
<item alpha="255" value="12" color="#24ab82" label="Vbo (value=12)"/>
<item alpha="255" value="13" color="#35b779" label="Vbd (value=13)"/>
<item alpha="255" value="14" color="#4ec36b" label="VIo (value=14)"/>
<item alpha="255" value="15" color="#6cce59" label="VId (value=15)"/>
<item alpha="255" value="16" color="#8fd744" label="VIIo (value=16)"/>
<item alpha="255" value="17" color="#b4dd2c" label="VIId (value=17)"/>
<item alpha="255" value="18" color="#dae319" label="VIIIo (value=18)"/>
<item alpha="255" value="19" color="#fde725" label="VIIId (value=19)"/>
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
