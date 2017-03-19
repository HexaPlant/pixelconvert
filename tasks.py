# -*- coding: utf-8 -*-

from __future__ import print_function
from invoke import Collection, task
import os
import fnmatch

#INPUT=AC00677476_MAYR_Salzburg_1880.tif
#GEOREF=AC00677476_MAYR_Salzburg_1880_E3857.tif
#RESULT=MAYR_Salzburg_1880.tif

#gdal_translate -a_srs EPSG:3857  -co TILED=YES -co COMPRESS=DEFLATE $INPUT $GEOREF
#listgeo $GEOREF > $INPUT\.txt
#vips --vips-progress  --vips-concurrency=4 im_vips2tiff $GEOREF $RESULT:deflate,tile:256x256,pyramid
#applygeo $INPUT\.txt $RESULT
#gdalinfo $RESULT

def clean(txt):
    txt=txt.replace(' ','_')
    txt=txt.replace('Ä','Ae')
    txt=txt.replace('Ö','Oe')
    txt=txt.replace('Ü','Ue')
    txt=txt.replace('ä','ae')
    txt=txt.replace('ö','oe')
    txt=txt.replace('ü','ue')
    return txt


@task(help={'image': "Image name to run."})
def convert(ctx):
    # print(ctx.input_dir,ctx.tmp_dir,ctx.output_dir)

    ctx.run( "mkdir -p %s"%ctx.tmp_dir)
    ctx.run( "mkdir -p %s"%ctx.output_dir)
    for root, dir, files in os.walk(ctx.input_dir):
        for tif in fnmatch.filter(files, "*.tif"):
            tif =tif.replace(' ','\\ ')
            root=root.replace(' ','\\ ')
            img = os.path.join(root,tif)
            name, ext = os.path.splitext(tif)
            points_in = os.path.join(root,name+'.tif.points')
            points_out = os.path.join(ctx.output_dir,name+'.gcp')
            wld = os.path.join(root,name+'.wld')
            georef = os.path.join(ctx.tmp_dir,clean(tif))
            gtiff = os.path.join(ctx.output_dir,clean(tif))
            gtxt = os.path.join(ctx.output_dir,clean(name)+'.geo')

            if os.path.exists(wld) and not os.path.exists(georef) and not os.path.exists(gtiff):
                ctx.run ("gdal_translate -a_srs EPSG:3857  -co TILED=YES -co COMPRESS=DEFLATE {img} {georef}".format(img=img,georef=georef))

            if os.path.exists(georef) and not os.path.exists(gtiff):
                ctx.run ("cp {points_in} {points_out}".format(points_in=points_in,points_out=points_out))
                ctx.run ("listgeo {georef} > {gtxt}".format(georef=georef,gtxt=gtxt))
                ctx.run ("vips --vips-progress  --vips-concurrency=8 im_vips2tiff {georef} {gtiff}:deflate,tile:256x256,pyramid".format(georef=georef,gtiff=gtiff))
                ctx.run ("applygeo {gtxt} {gtiff}".format(gtxt=gtxt,gtiff=gtiff))
                # ctx.run ("gdalinfo {gtiff}".format(gtiff=gtiff))
