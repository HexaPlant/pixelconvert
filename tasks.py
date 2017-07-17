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
                    except:
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
                    except:
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

@task()
def createxml(ctx):

    print ("Importing Metadata")
    records=aseq.load(ctx)

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
            xml_out = os.path.join(ctx.output_dir,clean(filename).lower()+'.xml')
            abstract_in= escape_path(os.path.join(root,filename+'_Abstract.txt'))

            if exists(tiff_final):
                dataset = gdal.Open(tiff_final)
                cols = dataset.RasterXSize
                rows = dataset.RasterYSize
                bands = dataset.RasterCount

                ulx, xres, xskew, uly, yskew, yres  = dataset.GetGeoTransform()
                lrx = ulx + (dataset.RasterXSize * xres)
                lry = uly + (dataset.RasterYSize * yres)

            else:
                dataset = gdal.Open(tiff_in)
                ulx=dataset.RasterXSize
                uly=dataset.RasterYSize
                lry=0
                lrx=0


            inProj = Proj(init='epsg:3857')
            outProj = Proj(init='epsg:4326')
            west,north = transform(inProj,outProj,ulx,uly)
            east,south = transform(inProj,outProj,lrx,lry)
            fs=filename.split('_')
            ac,author,imgname,year = fs[0],fs[1],' '.join(fs[2:-1]).strip(),fs[-1]
            name=' '.join(fs[1:])
            ac = ac.strip()
            #name = ' '.join([year,imgname,author]).strip()
            name_url = clean(escape(name))

            print ("Writing",xml_out)
            supplemental=""

            a010_a=aseq.get_key(records,ac,"010"," "," ","a")
            a451_a=aseq.get_key(records,ac,"451"," "," ","a")
            a590_a=aseq.get_key(records,ac,"590"," "," ","a")
            partOf=joinline(a010_a)
            partOf+=joinline(a451_a)
            partOf+=joinline(a590_a)
            supplemental+=joinlineif("\nGesamttitel: ",partOf)

            a331_a=aseq.get_key(records,ac,"331"," "," ","a")
            a335_a=aseq.get_key(records,ac,"335"," "," ","a")
            titleValue=join(a331_a,a335_a,' : ')
            supplemental+=joinlineif("\nTitel: ",titleValue)

            a089_p=aseq.get_key(records,ac,"089"," "," ","p")
            a089_n=aseq.get_key(records,ac,"089"," "," ","n")
            a455_a=aseq.get_key(records,ac,"455"," "," ","a")
            a596_a=aseq.get_key(records,ac,"596"," "," ","a")
            partNumber=joinline(a089_p,a089_n,' / ')
            partNumber=joinline(a455_a)
            partNumber=joinline(a596_a)
            supplemental+=joinlineif("\nZählung: ",partNumber)

            a341_a=aseq.get_key(records,ac,"341"," "," ","a")
            a343_a=aseq.get_key(records,ac,"343"," "," ","a")
            a345_a=aseq.get_key(records,ac,"345"," "," ","a")
            a347_a=aseq.get_key(records,ac,"347"," "," ","a")
            a370aa=aseq.get_key(records,ac,"370","a"," ","a")
            titleVariant=joinline(a341_a,a343_a,' : ')
            titleVariant+=joinline(a345_a,a347_a,' : ')
            titleVariant+=joinline(a370aa)
            supplemental+=joinlineif("\nWeitere Titel: ",titleVariant)

            a100_p=aseq.get_key(records,ac,"100"," "," ","p")
            a100_d=aseq.get_key(records,ac,"100"," "," ","d")
            a100_4=aseq.get_key(records,ac,"100"," "," ","4*")
            a104ap=aseq.get_key(records,ac,"104","a"," ","p")
            a104ad=aseq.get_key(records,ac,"104","a"," ","d")
            a104a4=aseq.get_key(records,ac,"104","a"," ","4*")
            a108ap=aseq.get_key(records,ac,"108"," ","a","p")
            a108ad=aseq.get_key(records,ac,"108"," ","a","d")
            a108a4=aseq.get_key(records,ac,"108","a"," ","4*")
            a112ap=aseq.get_key(records,ac,"112","a"," ","p")
            a112a4=aseq.get_key(records,ac,"112","a"," ","4")
            a100bp=aseq.get_key(records,ac,"100","b"," ","p")
            a100bd=aseq.get_key(records,ac,"100","b"," ","d")
            a100b4=aseq.get_key(records,ac,"100","b"," ","4*")
            a104bp=aseq.get_key(records,ac,"104","b"," ","p")
            a104bd=aseq.get_key(records,ac,"104","b"," ","d")
            a104b4=aseq.get_key(records,ac,"104","b"," ","4*")
            a108bp=aseq.get_key(records,ac,"108","b"," ","p")
            a108bd=aseq.get_key(records,ac,"108","b"," ","d")
            a108b4=aseq.get_key(records,ac,"108","b"," ","4*")
            a112bp=aseq.get_key(records,ac,"112","b"," ","p")
            a112bd=aseq.get_key(records,ac,"112","b"," ","d")
            a112b4=aseq.get_key(records,ac,"112","b"," ","4*")
            a200_k=aseq.get_key(records,ac,"200"," "," ","k")
            a200_h=aseq.get_key(records,ac,"200"," "," ","h")
            a200_4=aseq.get_key(records,ac,"200"," "," ","4*")
            a204ak=aseq.get_key(records,ac,"204","a"," ","k")
            a204ah=aseq.get_key(records,ac,"204","a"," ","h")
            a204a4=aseq.get_key(records,ac,"204","a"," ","4*")
            a208ak=aseq.get_key(records,ac,"208","a"," ","k")
            a208ah=aseq.get_key(records,ac,"208","a"," ","h")
            a208a4=aseq.get_key(records,ac,"208","a"," ","4*")
            a200bk=aseq.get_key(records,ac,"200","b"," ","k")
            a200b4=aseq.get_key(records,ac,"200","b"," ","4*")
            a204bk=aseq.get_key(records,ac,"204","b"," ","k")
            a204b4=aseq.get_key(records,ac,"204","b"," ","4*")
            a208bk=aseq.get_key(records,ac,"208","b"," ","k")
            a208bh=aseq.get_key(records,ac,"208","b"," ","h")
            a208b4=aseq.get_key(records,ac,"208","b"," ","4*")
            a677_p=aseq.get_key(records,ac,"677"," "," ","p")
            a677_d=aseq.get_key(records,ac,"677"," "," ","d")
            a677_4=aseq.get_key(records,ac,"677"," "," ","4*")

            relator=joinline(a100_p,a100_d,'; ')
            relator+=joinline(a104ap,a104ad,'; ')
            relator+=joinline(a108ap,a108ad,'; ')
            relator+=joinline(a100bp,a100bd,'; ')
            relator+=joinline(a104bp,a104bd,'; ')
            relator+=joinline(a108bp,a108bd,'; ')
            relator+=joinline(a112bp,a112bd,'; ')
            relator+=joinline(a204ak,a204ah,'; ')
            relator+=joinline(a208ak,a208ah,'; ')
            relator+=joinline(a208bk,a208bh,'; ')
            relator+=joinline(a677_p,a677_d,'; ')

            relatorRole=joinline(a100_4)
            relatorRole+=joinline(a104a4)
            relatorRole+=joinline(a108a4)
            relatorRole+=joinline(a112a4)
            relatorRole+=joinline(a100b4)
            relatorRole+=joinline(a104b4)
            relatorRole+=joinline(a108b4)
            relatorRole+=joinline(a112b4)
            relatorRole+=joinline(a200_4)
            relatorRole+=joinline(a204a4)
            relatorRole+=joinline(a208a4)
            relatorRole+=joinline(a204b4)
            relatorRole+=joinline(a208b4)
            relatorRole+=joinline(a677_4)

            supplemental+=joinlineif("\nPersonen/Institution: ",relator)
            supplemental+=joinlineif("\nPersonen/Institution: ",relatorRole)

            a359_a=aseq.get_key(records,ac,"359"," "," ","a")
            responsibilityStatement=joinline(a359_a)
            supplemental+=joinlineif("\nVerantwortlichkeitsangabe: ",responsibilityStatement)

            a403_a=aseq.get_key(records,ac,"403"," "," ","a")
            edition=joinline(a403_a)
            supplemental+=joinlineif("\nAusgabe: ",edition)

            a419_a=aseq.get_key(records,ac,"419"," "," ","a")
            providerPlace=joinline(a419_a)
            supplemental+=joinlineif("\nOrt: ",providerPlace)

            a419_b=aseq.get_key(records,ac,"419"," "," ","b")
            providerName=joinline(a419_b)
            supplemental+=joinlineif("\nVerlag/Druck: ",providerName)

            a419_c=aseq.get_key(records,ac,"419"," "," ","c")
            providerDate=joinline(a419_c)
            supplemental+=joinlineif("\nDatierung ",providerDate)

            a407_a=aseq.get_key(records,ac,"407"," "," ","a")
            cartographicScale=joinline(a407_a)
            supplemental+=joinlineif("\nMaßstab: ",cartographicScale)

            a433_a=aseq.get_key(records,ac,"433"," "," ","a")
            a437_a=aseq.get_key(records,ac,"437"," "," ","a")
            extend=join(a433_a,a437_a,' + ')
            supplemental+=joinlineif("\nUmfang:\n",extend)

            a435_a=aseq.get_key(records,ac,"435"," "," ","a")
            dimension=join(a435_a)
            supplemental+=joinlineif("\nFormat: ",dimension)

            a439_a=aseq.get_key(records,ac,"439"," "," ","d")
            baseMaterial=join(a439_a)
            supplemental+=joinlineif("\nReproduktionsverfahren: ",baseMaterial)

            a501_a=aseq.get_key(records,ac,"501"," "," ","a")
            note=join(a501_a)
            supplemental+=joinlineif("\nAnmerkungen: ",note)

            if os.path.exists(abstract_in):
                abstract=open(abstract_in).read()

            else:
                abstract=""

            #try:
            #    abstract = escape(records[ac]["331"][" "][" "]["a"]).encode('utf-8')
            #    supplemental = escape(records[ac]["359"][" "][" "]["a"]).encode('utf-8')

            #except KeyError:
            #    if 'AC' in ac:
            #        abstract = "No metadata found for %s"%ac
            #    else:
            #        abstract = "%s is not an AC number"%ac
            #        supplemental = abstract

            # print (ac,'-',titleValue,'-',abstract,'-',supplemental)

            xml_file=codecs.open(xml_out, "w", "utf-8")
            xml_file=open(xml_out,'w')

            title=filename.replace('_',' ').replace('[','').replace(']','')
            supplemental=supplemental.replace('_',' ').replace('[','').replace(']','')
            print (ac,title,abstract,supplemental)
            xml_file.write(csw.TEMPLATE.format(id=ac,name=escape(title),name_url=escape(name),geonode='http://localhost:8000',geoserver='http://localhost:8080/geoserver',west=west,east=east,north=north,south=south,z='{z}',x='{x}',y='{y}',abstract=abstract,supplemental=supplemental))
            xml_file.close()
