<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld">
<UserLayer>
<sld:LayerFeatureConstraints>
<sld:FeatureTypeConstraint/>
</sld:LayerFeatureConstraints>
<sld:UserStyle>
<sld:Name>./data/derived/tif/references</sld:Name>
<sld:FeatureTypeStyle>
<sld:Rule>
<sld:RasterSymbolizer>
<sld:ChannelSelection>
<sld:GrayChannel>
<sld:SourceChannelName>1</sld:SourceChannelName>
</sld:GrayChannel>
</sld:ChannelSelection>
<sld:ColorMap type="values">
<sld:ColorMapEntry color="#440154" label="de Gruijter et al., 2004" quantity="1"/>
<sld:ColorMapEntry color="#3b528b" label="Hoogland et al., 2014" quantity="2"/>
<sld:ColorMapEntry color="#21908c" label="Gerritsen et al., 2021" quantity="3"/>
<sld:ColorMapEntry color="#5dc963" label="Walvoort et al., 2023" quantity="4"/>
<sld:ColorMapEntry color="#fde725" label="Teuling et al., 2024" quantity="5"/>
</sld:ColorMap>
</sld:RasterSymbolizer>
</sld:Rule>
</sld:FeatureTypeStyle>
</sld:UserStyle>
</UserLayer>
</StyledLayerDescriptor>
