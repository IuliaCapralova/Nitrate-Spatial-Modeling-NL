<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld">
<UserLayer>
<sld:LayerFeatureConstraints>
<sld:FeatureTypeConstraint/>
</sld:LayerFeatureConstraints>
<sld:UserStyle>
<sld:Name>./data/derived/tif/ghg-mediaan</sld:Name>
<sld:FeatureTypeStyle>
<sld:Rule>
<sld:RasterSymbolizer>
<sld:ChannelSelection>
<sld:GrayChannel>
<sld:SourceChannelName>1</sld:SourceChannelName>
</sld:GrayChannel>
</sld:ChannelSelection>
<sld:ColorMap type="intervals">
<sld:ColorMapEntry color="#46085c" label="0 - 10" quantity="10"/>
<sld:ColorMapEntry color="#481769" label="10 - 20" quantity="20"/>
<sld:ColorMapEntry color="#482475" label="20 - 30" quantity="30"/>
<sld:ColorMapEntry color="#46307e" label="30 - 40" quantity="40"/>
<sld:ColorMapEntry color="#433d84" label="40 - 50" quantity="50"/>
<sld:ColorMapEntry color="#3f4889" label="50 - 60" quantity="60"/>
<sld:ColorMapEntry color="#3a538b" label="60 - 70" quantity="70"/>
<sld:ColorMapEntry color="#355e8d" label="70 - 80" quantity="80"/>
<sld:ColorMapEntry color="#31688e" label="80 - 90" quantity="90"/>
<sld:ColorMapEntry color="#2c718e" label="90 - 100" quantity="100"/>
<sld:ColorMapEntry color="#297b8e" label="100 - 110" quantity="110"/>
<sld:ColorMapEntry color="#25848e" label="110 - 120" quantity="120"/>
<sld:ColorMapEntry color="#218e8d" label="120 - 130" quantity="130"/>
<sld:ColorMapEntry color="#1f978b" label="130 - 140" quantity="140"/>
<sld:ColorMapEntry color="#1fa188" label="140 - 150" quantity="150"/>
<sld:ColorMapEntry color="#24aa83" label="150 - 160" quantity="160"/>
<sld:ColorMapEntry color="#2eb37c" label="160 - 170" quantity="170"/>
<sld:ColorMapEntry color="#3dbc74" label="170 - 180" quantity="180"/>
<sld:ColorMapEntry color="#50c46a" label="180 - 190" quantity="190"/>
<sld:ColorMapEntry color="#65cb5e" label="190 - 200" quantity="200"/>
<sld:ColorMapEntry color="#7cd250" label="200 - 210" quantity="210"/>
<sld:ColorMapEntry color="#95d840" label="210 - 220" quantity="220"/>
<sld:ColorMapEntry color="#b0dd2f" label="220 - 230" quantity="230"/>
<sld:ColorMapEntry color="#cae11f" label="230 - 240" quantity="240"/>
<sld:ColorMapEntry color="#e5e419" label="240 - 250" quantity="250"/>
<sld:ColorMapEntry color="#fde725" label=">250" quantity="254"/>
</sld:ColorMap>
</sld:RasterSymbolizer>
</sld:Rule>
</sld:FeatureTypeStyle>
</sld:UserStyle>
</UserLayer>
</StyledLayerDescriptor>
