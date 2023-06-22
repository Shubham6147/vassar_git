<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" xmlns:sld="http://www.opengis.net/sld">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>2021_change_ktcc_landuse</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry quantity="1" label="Water" color="#419bdf"/>
              <sld:ColorMapEntry quantity="2" label="Tress" color="#397d49"/>
              <sld:ColorMapEntry quantity="3" label="Grass" color="#88b053"/>
              <sld:ColorMapEntry quantity="4" label="Flooded Vegitation" color="#7a87c6"/>
              <sld:ColorMapEntry quantity="5" label="Crop" color="#e49635"/>
              <sld:ColorMapEntry quantity="6" label="Shrub" color="#e49635"/>
              <sld:ColorMapEntry quantity="7" label="Urban" color="#c4281b"/>
              <sld:ColorMapEntry quantity="8" label="Bare" color="#a59b8f"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>
