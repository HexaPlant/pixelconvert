# -*- coding: utf-8 -*-

KEYWORD="""<gmd:MD_Keywords>
    <gmd:keyword>
        <gco:CharacterString>{keyword}</gco:CharacterString>
        </gmd:keyword>
        <gmd:type>
        <gmd:MD_KeywordTypeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_KeywordTypeCode" codeListValue="temporal">temporal</gmd:MD_KeywordTypeCode>
        </gmd:type>
</gmd:MD_Keywords>"""

CATEGORY="""
       <gmd:topicCategory>
                   <gmd:MD_TopicCategoryCode>{category}</gmd:MD_TopicCategoryCode>
      </gmd:topicCategory>"""

REGION="""<gmd:keyword>
    <gco:CharacterString>{region}</gco:CharacterString>
    </gmd:keyword>
    <gmd:type>
    <gmd:MD_KeywordTypeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_KeywordTypeCode" codeListValue="place">place</gmd:MD_KeywordTypeCode>
    </gmd:type>
"""

CSW="""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<csw:GetRecordByIdResponse xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dct="http://purl.org/dc/terms/" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gml="http://www.opengis.net/gml" xmlns:ows="http://www.opengis.net/ows" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd"><gmd:MD_Metadata xsi:schemaLocation="http://www.isotc211.org/2005/gmd http://www.isotc211.org/2005/gmd/gmd.xsd">
   <gmd:fileIdentifier>
     <gco:CharacterString>{id}</gco:CharacterString>
   </gmd:fileIdentifier>
   <gmd:language>
     <gco:CharacterString>eng</gco:CharacterString>
   </gmd:language>
   <gmd:characterSet>
     <gmd:MD_CharacterSetCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CharacterSetCode" codeListValue="utf8">utf8</gmd:MD_CharacterSetCode>
   </gmd:characterSet>
   <gmd:hierarchyLevel>
    <gmd:MD_ScopeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>
   </gmd:hierarchyLevel>
   <gmd:contact>
     <gmd:CI_ResponsibleParty>
       <gmd:individualName gco:nilReason="BAS:IS">

       </gmd:individualName>
       <gmd:organisationName gco:nilReason="missing">

       </gmd:organisationName>
       <gmd:positionName gco:nilReason="Akademie der Wissenschaften">

       </gmd:positionName>
       <gmd:contactInfo>
         <gmd:CI_Contact>
           <gmd:phone>
             <gmd:CI_Telephone>
               <gmd:voice gco:nilReason="missing">

               </gmd:voice>
               <gmd:facsimile gco:nilReason="missing">

               </gmd:facsimile>
             </gmd:CI_Telephone>
           </gmd:phone>
           <gmd:address>
             <gmd:CI_Address>
               <gmd:deliveryPoint gco:nilReason="missing">

               </gmd:deliveryPoint>
               <gmd:city gco:nilReason="Dr. Ignaz Seipel-Platz 2,1010 Wien,Austria">

               </gmd:city>
               <gmd:administrativeArea gco:nilReason="Vienna">

               </gmd:administrativeArea>
               <gmd:postalCode gco:nilReason="1010">

               </gmd:postalCode>
               <gmd:country gco:nilReason="Austria">

               </gmd:country>
               <gmd:electronicMailAddress>
                 <gco:CharacterString>webmaster@oeaw.ac.at</gco:CharacterString>
               </gmd:electronicMailAddress>
             </gmd:CI_Address>
           </gmd:address>

         </gmd:CI_Contact>
       </gmd:contactInfo>
       <gmd:role>
         <gmd:CI_RoleCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="pointOfContact">pointOfContact</gmd:CI_RoleCode>
       </gmd:role>
     </gmd:CI_ResponsibleParty>
   </gmd:contact>
   <gmd:dateStamp>
     <gco:DateTime>{year}-01-91T12:00:00Z</gco:DateTime>
   </gmd:dateStamp>
   <gmd:metadataStandardName>
     <gco:CharacterString>ISO 19115:2003 - Geographic information - Metadata</gco:CharacterString>
   </gmd:metadataStandardName>
   <gmd:metadataStandardVersion>
     <gco:CharacterString>ISO 19115:2003</gco:CharacterString>
   </gmd:metadataStandardVersion>
   <gmd:spatialRepresentationInfo/>
   <gmd:referenceSystemInfo>
     <gmd:MD_ReferenceSystem>
       <gmd:referenceSystemIdentifier>
         <gmd:RS_Identifier>
           <gmd:code>
             <gco:CharacterString>4326</gco:CharacterString>
           </gmd:code>
           <gmd:codeSpace>
             <gco:CharacterString>EPSG</gco:CharacterString>
           </gmd:codeSpace>
           <gmd:version>
             <gco:CharacterString>6.11</gco:CharacterString>
           </gmd:version>
         </gmd:RS_Identifier>
       </gmd:referenceSystemIdentifier>
     </gmd:MD_ReferenceSystem>
   </gmd:referenceSystemInfo>
   <gmd:identificationInfo>
     <gmd:MD_DataIdentification>
       <gmd:citation>
         <gmd:CI_Citation>
           <gmd:title>
             <gco:CharacterString>{name}</gco:CharacterString>
           </gmd:title>
           <gmd:CI_Date>
                <gmd:date>
                    <gco:DateTime>{year}-01-01T12:00:00Z</gco:DateTime>
                </gmd:date>
                <gmd:dateType>
                    <gmd:CI_DateTypeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_DateTypeCode" codeListValue="publication">publication</gmd:CI_DateTypeCode>
                </gmd:dateType>
            </gmd:CI_Date>

           <gmd:edition gco:nilReason="missing">

           </gmd:edition>
           <gmd:presentationForm>
             <gmd:CI_PresentationFormCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_PresentationFormCode" codeListValue="mapDigital">mapDigital</gmd:CI_PresentationFormCode>
           </gmd:presentationForm>
         </gmd:CI_Citation>
       </gmd:citation>
       <gmd:abstract>
         <gco:CharacterString>{abstract}</gco:CharacterString>
       </gmd:abstract>
       <gmd:purpose gco:nilReason="missing">

       </gmd:purpose>
       <gmd:status>
         <gmd:MD_ProgressCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ProgressCode" codeListValue="completed">completed</gmd:MD_ProgressCode>
       </gmd:status>

       <gmd:graphicOverview>
         <gmd:MD_BrowseGraphic>
           <gmd:fileName>
             <gco:CharacterString>{geonode}/uploaded/thumbs/layer-{id}-thumb.png</gco:CharacterString>
           </gmd:fileName>
           <gmd:fileDescription>
             <gco:CharacterString>Thumbnail for '{name}'</gco:CharacterString>
           </gmd:fileDescription>
           <gmd:fileType>
             <gco:CharacterString>image/png</gco:CharacterString>
           </gmd:fileType>
         </gmd:MD_BrowseGraphic>
       </gmd:graphicOverview>
       <gmd:resourceFormat>
         <gmd:MD_Format>
           <gmd:name>

             <gco:CharacterString>ESRI Shapefile</gco:CharacterString>

           </gmd:name>
           <gmd:version>
             <gco:CharacterString>1.0</gco:CharacterString>
           </gmd:version>
         </gmd:MD_Format>
       </gmd:resourceFormat>
        <gmd:descriptiveKeywords>
            <gmd:MD_Keywords>
                {region}
            </gmd:MD_Keywords>
            {keywords}
        </gmd:descriptiveKeywords>
       <gmd:resourceConstraints>
         <gmd:MD_LegalConstraints>
           <gmd:useConstraints>
              <gmd:MD_RestrictionCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue=""/>
           </gmd:useConstraints>
           <gmd:otherConstraints>
             <gco:CharacterString>None</gco:CharacterString>
           </gmd:otherConstraints>
         </gmd:MD_LegalConstraints>
       </gmd:resourceConstraints>
       <gmd:spatialRepresentationType>
         <gmd:MD_SpatialRepresentationTypeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_SpatialRepresentationTypeCode" codeListValue=""/>
       </gmd:spatialRepresentationType>
       <gmd:language>
         <gco:CharacterString>eng</gco:CharacterString>
       </gmd:language>
       <gmd:characterSet>
         <gmd:MD_CharacterSetCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CharacterSetCode" codeListValue="utf8">utf8</gmd:MD_CharacterSetCode>
       </gmd:characterSet>
       {category}
       <gmd:extent>
         <gmd:EX_Extent>
           <gmd:geographicElement>
             <gmd:EX_GeographicBoundingBox>
               <gmd:westBoundLongitude>
                 <gco:Decimal>{west}</gco:Decimal>
               </gmd:westBoundLongitude>
               <gmd:eastBoundLongitude>
                 <gco:Decimal>{east}</gco:Decimal>
               </gmd:eastBoundLongitude>
               <gmd:southBoundLatitude>
                 <gco:Decimal>{south}</gco:Decimal>
               </gmd:southBoundLatitude>
               <gmd:northBoundLatitude>
                 <gco:Decimal>{north}</gco:Decimal>
               </gmd:northBoundLatitude>
             </gmd:EX_GeographicBoundingBox>
           </gmd:geographicElement>
         </gmd:EX_Extent>
       </gmd:extent>

       <gmd:supplementalInformation>
         <gco:CharacterString>{supplemental}</gco:CharacterString>
       </gmd:supplementalInformation>
     </gmd:MD_DataIdentification>
   </gmd:identificationInfo>
   <gmd:contentInfo>

     <gmd:MD_CoverageDescription>
       <gmd:attributeDescription gco:nilReason="inapplicable"/>
       <gmd:contentType>
         <gmd:MD_CoverageContentTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml" codeListValue="image">image</gmd:MD_CoverageContentTypeCode>
       </gmd:contentType>
     </gmd:MD_CoverageDescription>

   </gmd:contentInfo>
   <gmd:distributionInfo>
     <gmd:MD_Distribution>
       <gmd:transferOptions>
         <gmd:MD_DigitalTransferOptions>

           <gmd:onLine>
             <gmd:CI_OnlineResource>
               <gmd:linkage>
                 <gmd:URL>{geoserver}/wcs?format=image%2Ftiff&amp;request=GetCoverage&amp;version=2.0.1&amp;service=WCS&amp;coverageid=geonode%3A{name_url}</gmd:URL>
               </gmd:linkage>
               <gmd:protocol>
                 <gco:CharacterString>WWW:DOWNLOAD-1.0-http--download</gco:CharacterString>
               </gmd:protocol>
               <gmd:name>
                 <gco:CharacterString>{name_url}.geotiff</gco:CharacterString>
               </gmd:name>
               <gmd:description>
                 <gco:CharacterString>{name} (GeoTIFF Format)</gco:CharacterString>
               </gmd:description>
             </gmd:CI_OnlineResource>
           </gmd:onLine>

           <gmd:onLine>
             <gmd:CI_OnlineResource>
               <gmd:linkage>
                 <gmd:URL>{geoserver}/wms/kml?layers=geonode%3A{name_url}&amp;mode=refresh</gmd:URL>
               </gmd:linkage>
               <gmd:protocol>
                 <gco:CharacterString>WWW:DOWNLOAD-1.0-http--download</gco:CharacterString>
               </gmd:protocol>
               <gmd:name>
                 <gco:CharacterString>{name_url}.kml</gco:CharacterString>
               </gmd:name>
               <gmd:description>
                 <gco:CharacterString>{name} (View in Google Earth Format)</gco:CharacterString>
               </gmd:description>
             </gmd:CI_OnlineResource>
           </gmd:onLine>

         </gmd:MD_DigitalTransferOptions>
       </gmd:transferOptions>
     </gmd:MD_Distribution>
   </gmd:distributionInfo>
   <gmd:dataQualityInfo>
     <gmd:DQ_DataQuality>
       <gmd:scope>
         <gmd:DQ_Scope>
           <gmd:level>
             <gmd:MD_ScopeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>
           </gmd:level>
         </gmd:DQ_Scope>
       </gmd:scope>
       <gmd:lineage>
         <gmd:LI_Lineage>
           <gmd:statement gco:nilReason="missing"/>
         </gmd:LI_Lineage>
       </gmd:lineage>
     </gmd:DQ_DataQuality>
   </gmd:dataQualityInfo>
 </gmd:MD_Metadata></csw:GetRecordByIdResponse>
 """
