ROBOTS="""
User-agent: *
Disallow: /catalogue/
Disallow: /search/
Disallow: /geoserver/
Disallow: /uploaded/
Allow: /
Sitemap: {url}/sitemap.xml
"""

HEADER="""<?xml version="1.0" encoding="UTF-8"?>
<urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
<url>
    <loc>{url_site}</loc>
    <lastmod>{date}</lastmod>
    <priority>1.0</priority>
    <changefreq>always</changefreq>
</url>
"""


MAP="""<url>
    <loc>{url_site}/layers/geonode:{layer}</loc>
    <lastmod>{date}</lastmod>
    <changefreq>always</changefreq>
    <priority>0.8</priority>
    <PageMap xmlns="http://www.google.com/schemas/sitemap-pagemap/1.0">
         <DataObject type="document" id="{id}">
           <Attribute name="title">{title}</Attribute>
           <Attribute name="description">{caption}</Attribute>
         </DataObject>
    </PageMap>
    <image:image>
        <image:loc>{url_iiif}/?IIIF={layer}.tif/full/,1500/0/default.jpg'</image:loc>
        <image:title>{title}</image:title>
        <image:caption>{caption}</image:caption>
        <image:license>https://creativecommons.org/licenses/by/4.0/</image:license>
    </image:image>
</url>
<url>
    <loc>{url_site}/layers/geonode:{layer}/metadata_detail</loc>
    <lastmod>{date}</lastmod>
    <changefreq>always</changefreq>
<priority>0.2</priority>
</url>
"""

FOOTER="""
</urlset>
"""
