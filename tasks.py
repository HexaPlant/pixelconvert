# -*- coding: utf-8 -*-

from __future__ import print_function
from invoke import Collection, task
from util import join,joinline,joinlineif,clean,escape,escape_path
import csv
import codecs

import MARC21relaxed
import pyxb

import os
import fnmatch
from os.path import exists
from osgeo import gdal, osr
from pyproj import Proj, transform
import xml.sax.saxutils

import csw
import aseq

@task()
def convert(ctx):

    #print ("Importing Metadata")
    #records=aseq.load(ctx)


    ctx.run('mkdir -p {path}'.format(path=ctx.gcp_dir))
    ctx.run('mkdir -p {path}'.format(path=ctx.vips_dir))
    ctx.run('mkdir -p {path}'.format(path=ctx.warp_dir))
    ctx.run('mkdir -p {path}'.format(path=ctx.wld_dir))
    ctx.run('mkdir -p {path}'.format(path=ctx.output_dir))

    for root, dir, files in os.walk(ctx.input_dir):
        for tif in fnmatch.filter(files, "*.tif"):
            img = os.path.join(root,tif).replace(' ','\ ').replace('&','\&').replace("'","\'")

            filename, ext = os.path.splitext(tif)
            points_in = escape_path(os.path.join(root,filename+'.tif.points'))
            tiff_in = os.path.join(root,tif)
            tiff_gcp = os.path.join(ctx.gcp_dir,clean(tif))
            tiff_warp = os.path.join(ctx.warp_dir,clean(tif).lower())
            tiff_vips = os.path.join(ctx.vips_dir,clean(tif).lower())
            tiff_wld = os.path.join(ctx.wld_dir,clean(tif))
            tiff_final = os.path.join(ctx.output_dir,clean(tif).lower())
            wld_gcp = os.path.join(ctx.gcp_dir,filename+'.wld')
            gtxt_out = os.path.join(ctx.output_dir,clean(filename).lower()+'.geo')


            print ("Processing",img)

            if exists(tiff_final):
                print ("Skipping",img)
                continue

            if not exists(tiff_gcp) and exists(points_in):
                ctx.run ('cp -v {tiff_in} {tiff_gcp}'.format(tiff_in=escape_path(tiff_in),tiff_gcp=escape_path(tiff_gcp)))

            if exists(tiff_gcp):
                if exists(wld_gcp):
                    ctx.run('rm -v {wld}'.format(wld=wld_gcp))
                print ("Reading",points_in)
                with open(points_in) as csvfile:
                    try:
                        reader = csv.DictReader(csvfile)
                        gcp=""
                        for row in reader:
                            gcp+="-gcp {pixelX} {pixelY} {mapX} {mapY} ".format(pixelX=row['pixelX'],pixelY=abs(float(row['pixelY'])),mapX=row['mapX'],mapY=row['mapY'])
                        ctx.run('gdal_edit.py -unsetgt -a_srs EPSG:3857 -a_nodata 255  -mo NODATA_VALUES="255 255 255" {gcp} {tiff}'.format(gcp=gcp,tiff=tiff_gcp))
                    #ctx.run('gdal_edit.py -unsetgt -unsetmd -a_srs EPSG:3857 -a_nodata 255  -mo NODATA_VALUES="255 255 255" {gcp} {tiff}'.format(gcp=gcp,tiff=tiff_gcp))
                    #ctx.run('gdal_edit.py -unsetgt -unsetmd -a_srs EPSG:3857 -mo NODATA_VALUES="255 255 255" {gcp} {tiff}'.format(gcp=gcp,tiff=tiff_gcp))
                    except _csv.Error:_csv.Error:
                        print("Failed to read point file")
                        continue

                    try:
                        dataset = gdal.Open(tiff_gcp)
                        gcps = dataset.GetGCPs()
                        geotransform = gdal.GCPsToGeoTransform(gcps)

                        ulx, xres, xskew, uly, yskew, yres  = gdal.GCPsToGeoTransform( gcps)
                        lrx = ulx + (dataset.RasterXSize * xres)
                        lry = uly + (dataset.RasterYSize * yres)

                        proj3857 = Proj(init='epsg:3857')
                        proj4326 = Proj(init='epsg:4326')
                        west,north = transform(proj3857,proj4326,ulx,uly)
                        east,south = transform(proj3857,proj4326,lrx,lry)
                    except AttributeError:
                        print("Failed to read gcp points")
                        continue

                    ctx.run('gcps2wld.py {tiff} > {wld_out}'.format(tiff=tiff_gcp,wld_out=wld_gcp))
                    ctx.run('gdal_translate -a_srs EPSG:3857 -mo NODATA_VALUES="255 255 255" {tiff_in} {tiff_out}'.format(tiff_in=tiff_gcp,tiff_out=tiff_wld))
                    ctx.run("listgeo {tiff_in} > {gtxt_out}".format(tiff_in=escape_path(tiff_wld),gtxt_out=escape_path(gtxt_out)))

                if not exists(tiff_final):
                     ctx.run("vips --vips-progress  --vips-concurrency=16 im_vips2tiff {tiff_in} {tiff_out}:deflate,tile:256x256,pyramid".format(tiff_in=escape_path(tiff_gcp),tiff_out=escape_path(tiff_final)))
                     ctx.run("applygeo {gtxt_in} {tiff_out}".format(gtxt_in=escape_path(gtxt_out),tiff_out=escape_path(tiff_final)))
                     ctx.run('gdal_edit.py -a_nodata 255 -mo NODATA_VALUES="255 255 255" {tiff_out}'.format(tiff_out=tiff_final))

                     #ctx.run('gdal_edit.py -unsetgt -unsetmd -a_srs EPSG:3857 -a_nodata 255  -mo NODATA_VALUES="255 255 255" {gcp} {tiff}'.format(gcp=gcp,tiff=tiff_vips))
                     #ctx.run('gdal_edit.py -unsetgt -a_srs EPSG:3857 -a_nodata 255  -mo NODATA_VALUES="255 255 255" {gcp} {tiff}'.format(gcp=gcp,tiff=tiff_vips))


                #if not exists(tiff_warp):
                #    ctx.run('gdalwarp  -dstalpha  -co "COMPRESS=DEFLATE" -co BIGTIFF=YES -co TILED=YES -r lanczos  -s_srs EPSG:3857 -t_srs EPSG:3857  -multi -wo NUM_THREADS=ALL_CPU {tiff_gcp} {tiff_warp}'.format(tiff_gcp=tiff_gcp,tiff_warp=tiff_warp))
                    #ctx.run('gdalwarp  -dstalpha  -co "COMPRESS=DEFLATE"  -tps -refine_gcps 10 30 -s_srs EPSG:3857 -t_srs EPSG:3857  -multi -wo NUM_THREADS=ALL_CPU {tiff_gcp} {tiff_warp}'.format(tiff_gcp=tiff_gcp,tiff_warp=tiff_warp))
                    #ctx.run('gdaladdo  --config COMPRESS_OVERVIEW DEFLATE -r lanczos {tiff_warp} 2 4 8 16 32'.format(tiff_warp=tiff_warp))

            #if exists(tiff_gcp) and exists(tiff_warp) and exists(tiff_vips):
            #d    ctx.run('rm -v {tiff}'.format(tiff=tiff_gcp))
