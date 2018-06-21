# -*- coding: utf-8 -*-

from __future__ import print_function
from invoke import Collection, task
from util import join,joinline,joinlineif,clean,escape,escape_path,code2name
import csv
import codecs
import magic

import MARC21relaxed
import pyxb
import dublincore

import os
import fnmatch
from os.path import exists
from osgeo import gdal, osr
from pyproj import Proj, transform
import xml.sax.saxutils

import csw
import aseq
import sitemap
import geocoder
import regions

import xml.sax.saxutils

import time
from datetime import date
import requests

@task()
def rebuild_index(ctx):
    ctx.run('python /data/code/woldan/manage.py rebuild_index -v 3 --noinput')


@task()
def create_maps(ctx):
    cleanup_tmp(ctx)
    ctx.run('mkdir -p {path}'.format(path=ctx.gcp_dir))
    ctx.run('mkdir -p {path}'.format(path=ctx.vips_dir))
    #ctx.run('mkdir -p {path}'.format(path=ctx.warp_dir))
    ctx.run('mkdir -p {path}'.format(path=ctx.wld_dir))
    ctx.run('mkdir -p {path}'.format(path=ctx.output_dir))

    for root, dir, files in os.walk(ctx.input_dir):
        for tif in fnmatch.filter(files, "*.tif"):
            img = os.path.join(root,tif).replace(' ','\ ').replace('&','\&').replace("'","\'")
            filename, ext = os.path.splitext(tif)
            points_in = os.path.join(root,filename+'.tif.points')
            tiff_in = os.path.join(root,tif).replace("'","\\'")
            tiff_gcp = os.path.join(ctx.gcp_dir,clean(tif))
            tiff_warp = os.path.join(ctx.warp_dir,clean(tif).lower())
            tiff_vips = os.path.join(ctx.vips_dir,clean(tif).lower())
            tiff_wld = os.path.join(ctx.wld_dir,clean(tif))
            tiff_final = os.path.join(ctx.output_dir,clean(tif).lower())
            wld_gcp = os.path.join(ctx.gcp_dir,clean(filename)+'.wld')
            gtxt_out = os.path.join(ctx.output_dir,clean(filename).lower()+'.geo')

            #print ("Processing",img)

            if exists(tiff_final):
                print ("Skipping",img)
                continue

            if not exists(points_in):
                print("Missing",points_in," for",tiff_in)

            if not exists(tiff_gcp):
                ctx.run ('cp -v {tiff_in} {tiff_gcp}'.format(tiff_in=escape_path(tiff_in),tiff_gcp=escape_path(tiff_gcp)))

            if exists(tiff_gcp):
                if exists(wld_gcp):
                    ctx.run('rm -v {wld}'.format(wld=wld_gcp))

                if exists(points_in):
                    print ("Reading",points_in)
                    with open(points_in) as csvfile:
                        try:
                            reader = csv.DictReader(csvfile)
                            gcp=""
                            for row in reader:
                                gcp+="-gcp {pixelX} {pixelY} {mapX} {mapY} ".format(pixelX=row['pixelX'],pixelY=abs(float(row['pixelY'])),mapX=row['mapX'],mapY=row['mapY'])
                            ctx.run('gdal_edit.py -unsetgt -a_srs EPSG:3857 -mo NODATA_VALUES="255 255 255" {gcp} {tiff}'.format(gcp=gcp,tiff=tiff_gcp))
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

                else:
                    ctx.run('gdal_edit.py -a_srs EPSG:3857 -a_nodata 255  -mo NODATA_VALUES="255 255 255" -a_ullr 0 -20000000 20026376 -20026376.39 {tiff}'.format(tiff=tiff_gcp))

                ctx.run('gcps2wld.py {tiff} > {wld_out}'.format(tiff=tiff_gcp,wld_out=wld_gcp))
                ctx.run('gdal_translate -a_srs EPSG:3857 -mo NODATA_VALUES="255 255 255" {tiff_in} {tiff_out}'.format(tiff_in=tiff_gcp,tiff_out=tiff_wld))
                ctx.run("listgeo {tiff_in} > {gtxt_out}".format(tiff_in=escape_path(tiff_wld),gtxt_out=escape_path(gtxt_out)))

            if not exists(tiff_final):
                ctx.run("vips --vips-concurrency=16 im_vips2tiff {tiff_in} {tiff_out}:deflate,tile:256x256,pyramid".format(tiff_in=escape_path(tiff_gcp),tiff_out=escape_path(tiff_final)))
                ctx.run("applygeo {gtxt_in} {tiff_out}".format(gtxt_in=escape_path(gtxt_out),tiff_out=escape_path(tiff_final)))
                ctx.run('gdal_edit.py -mo NODATA_VALUES="255 255 255" {tiff_out}'.format(tiff_out=tiff_final))


    cleanup_tmp(ctx)


@task()
def create_sitemap(ctx):

    w3c_date=date.today().strftime("%Y-%m-%d")
    with open(ctx.geonode_dir+'/geonode/static/robots.txt', 'w')as robots_file:
            robots_file.write(sitemap.ROBOTS.format(url=ctx.url_site))

    with open(ctx.geonode_dir+'/geonode/static/sitemap.xml', 'w')as sitemap_file:
            sitemap_file.write(sitemap.HEADER.format(url_site=ctx.url_site,date=w3c_date))

            print ("Importing Metadata")
            records=aseq.load(ctx)

            for root, dir, files in os.walk(ctx.input_dir):
                for tif in fnmatch.filter(files, "*.tif"):
                    img = os.path.join(root,tif).replace(' ','\ ').replace('&','\&').replace("'","\'")
                    filename, ext = os.path.splitext(tif)
                    layer=clean(filename).lower()
                    title=filename.replace('_',' ').replace('[','').replace(']','')
                    title_short=' '.join(title.split(' ')[1:])

                    print ("Adding",layer)

                    fs=filename.split('_')
                    try:
                        ac,author,imgname,year = fs[0],fs[1],' '.join(fs[2:-1]).strip(),fs[-1]
                        name=' '.join(fs[1:])
                        ac = ac.strip()
                        #name = ' '.join([year,imgname,author]).strip()
                        name_url = clean(escape(name))
                    except IndexError:
                        print("Can't parse", filename)
                        continue

                    a331_a=aseq.get_key(records,ac,"331"," "," ","a")
                    a335_a=aseq.get_key(records,ac,"335"," "," ","a")
                    title=a331_a.replace('[','').replace(']','')
                    titleValue=join(a331_a,a335_a,' : ').replace('[','').replace(']','')
                    sitemap_file.write(sitemap.MAP.format(url_site=ctx.url_site,url_iiif=ctx.url_iiif,layer=layer,title=escape(title_short),caption=escape(titleValue),date=w3c_date,id=ac))
            sitemap_file.write(sitemap.FOOTER)
@task()
def update_cache(ctx):
    for root, dir, files in os.walk(ctx.input_dir):
        for tif in fnmatch.filter(files, "*.tif"):
            img = os.path.join(root,tif).replace(' ','\ ').replace('&','\&').replace("'","\'")
            filename, ext = os.path.splitext(tif)
            layer=clean(filename).lower()
            url_jpeg_standard = "{url_iiif}/?IIIF={layer}.tif/full/,1500/0/default.jpg".format(url_iiif=ctx.url_iiif,layer=layer)
            url_jpeg_large = "{url_iiif}/?IIIF={layer}.tif/full/,5000/0/default.jpg".format(url_iiif=ctx.url_iiif,layer=layer)
            url_geotiff_normal = "{url_iiif}/image/{layer}.tif".format(url_iiif=ctx.url_iiif,layer=layer)
            url_geotiff_transformed="{url_site}/geoserver/wcs?format=image%2Ftiff&request=GetCoverage&version=2.0.1&service=WCS&coverageid=geonode%3A{layer}".format(url_site=ctx.url_site,layer=layer)
            url_googleearth="{url_site}/geoserver/wms/kml?layers=geonode%3A{layer}".format(url_site=ctx.url_site,layer=layer)

            for url in (url_jpeg_standard,url_jpeg_large,url_geotiff_normal,url_geotiff_transformed,url_googleearth):
                r = requests.get(url)
                if r.status_code==200:
                    print ("SUCCESS",url)
                else:
                    print ("ERROR",url)

@task()
def create_metadata(ctx):

    print ("Importing Categories")
    category_dict={}
    with open(ctx.category, 'r')as category_file:
        category_csv = csv.DictReader(category_file,dialect='excel',delimiter=';')

        for row in category_csv:
            #print(row)
            category_dict[row['filename']]={
                'category1':row['category1'].decode('iso-8859-1').encode('utf8'),
                'category2':row['category2'].decode('iso-8859-1').encode('utf8'),
                'category3':row['category3'].decode('iso-8859-1').encode('utf8'),
                'category4':row['category4'].decode('iso-8859-1').encode('utf8'),
                'category5':row['category5'].decode('iso-8859-1').encode('utf8'),
                'blatt_titel':row['blatt_titel'].decode('iso-8859-1').encode('utf8'),
            }

            for i in range(1,250):
                try:
                    blatt=row['titel_blatt%02i'%i].decode('iso-8859-1').encode('utf8')
                    if blatt:
                        # print(row['\xef\xbb\xbffilename'],blatt)
                        category_dict[row['filename']].update({'titel_blatt%02i'%i:blatt})
                except KeyError:
                    pass

    print ("Importing Metadata")
    records=aseq.load(ctx)
    #print(records)
    #print (records['AC04408812']['677'])
    #csv_abstract=open("out/woldan_abstract.csv","w")
    #csv_abstract.write("title,abstract\n")
    ctx.run("mkdir -p %s"%ctx.log_dir)
    csv_import=open("%s/woldan_import.csv"%ctx.log_dir,"w")
    csv_import.write("filename,denominator,geo,abstract,biblio,category1,category2,category3,category4,category5\n")
    dc_import=open("%s/woldan_import_dc.xml"%ctx.log_dir,"w")
    dc_import.write(dublincore.HEADER)
    dc=""


    countries=regions.country2kontinent()

    for root, dir, files in os.walk(ctx.input_dir):
        for tif in fnmatch.filter(files, "*.tif"):
            img = os.path.join(root,tif).replace(' ','\ ').replace('&','\&').replace("'","\'")

            filename, ext = os.path.splitext(tif)

            tiff_in = os.path.join(root,tif)
            points_in = escape_path(os.path.join(root,filename+'.tif.points'))
            abstract_in= os.path.join(root,filename+'_Abstract.txt')
            biblio_in= os.path.join(root,filename+'_Biblio.txt')
            tiff_gcp = os.path.join(ctx.gcp_dir,clean(tif))
            tiff_warp = os.path.join(ctx.warp_dir,clean(tif).lower())
            tiff_vips = os.path.join(ctx.vips_dir,clean(tif).lower())
            tiff_wld = os.path.join(ctx.wld_dir,clean(tif))
            tiff_final = os.path.join(ctx.output_dir,clean(tif).lower())
            wld_gcp = os.path.join(ctx.gcp_dir,clean(filename)+'.wld')
            gtxt_out = os.path.join(ctx.output_dir,clean(filename).lower()+'.geo')
            xml_out = os.path.join(ctx.output_dir,clean(filename).lower()+'.xml')

            if exists(tiff_final):
                try:
                    dataset = gdal.Open(tiff_final)
                    cols = dataset.RasterXSize
                    rows = dataset.RasterYSize
                    bands = dataset.RasterCount
                except AttributeError:
                    continue

                ulx, xres, xskew, uly, yskew, yres  = dataset.GetGeoTransform()
                lrx = ulx + (dataset.RasterXSize * xres)
                lry = uly + (dataset.RasterYSize * yres)

                denominator=int(round(xres*dataset.RasterXSize))

                if denominator > 20000000:
                    denominator = 50000000

            else:
                ulx=0
                uly=0
                lry=0
                lrx=0

            inProj = Proj(init='epsg:3857')
            outProj = Proj(init='epsg:4326')
            west,north = transform(inProj,outProj,ulx,uly)
            east,south = transform(inProj,outProj,lrx,lry)
            fs=filename.split('_')
            try:
                ac,author,imgname,year = fs[0],fs[1],' '.join(fs[2:-1]).strip(),fs[-1]
                name=' '.join(fs[1:])
                ac = ac.strip()
                #name = ' '.join([year,imgname,author]).strip()
                name_url = clean(escape(name))
            except IndexError:
                print("Can't parse", filename)
                continue

            if exists(xml_out):
                print ("Passing",xml_out)
            else:
                print ("Writing",xml_out)
                abstract=""
                supplemental=""

                a010_a=aseq.get_key(records,ac,"010"," "," ","a")  # AC Nummer -> 331_a
                parent_a331_a=aseq.get_key(records,a010_a,"331"," "," ","a")
                a451_a=aseq.get_key(records,ac,"451"," "," ","a")
                a453ma=aseq.get_key(records,ac,"453","m"," ","a")
                a453ra=aseq.get_key(records,ac,"453","r"," ","a")
                parent_a453ma=aseq.get_key(records,a453ma,"331"," "," ","a")
                parent_a453ra=aseq.get_key(records,a453ra,"331"," "," ","a")
                a590_a=aseq.get_key(records,ac,"590"," "," ","a")
                a599_a=aseq.get_key(records,ac,"599"," "," ","a")
                parent_a599_a=aseq.get_key(records,a599_a,"331"," "," ","a")
                a034_b=aseq.get_key(records,ac,"034"," "," ","b")
                partOf=""
                if parent_a331_a:
                    partOf+=parent_a331_a +'\n'
                if parent_a453ma:
                    partOf+=parent_a453ma +'\n'
                if parent_a453ra:
                    partOf+=parent_a453ra +'\n'
                if parent_a599_a:
                    partOf+=parent_a599_a +'\n'

                try:
                    if (category_dict[filename]['blatt_titel']):
                        partOf=category_dict[filename]['blatt_titel']
                except KeyError:
                    pass
                    #print ("No partOf")

                supplemental+=joinlineif("**Gesamttitel:**  \n",partOf)
                a331_a=aseq.get_key(records,ac,"331"," "," ","a")
                a335_a=aseq.get_key(records,ac,"335"," "," ","a")
                title=a331_a.replace('[','').replace(']','')
                titleValue=join(a331_a,a335_a,' : ').replace('[','').replace(']','')
                supplemental+=joinlineif("**Titel:**  \n",titleValue)

                print("titleValue",titleValue)
                print("partOf",partOf)

                a089_p=aseq.get_key(records,ac,"089"," "," ","p")
                a089_n=aseq.get_key(records,ac,"089"," "," ","n")
                a455_a=aseq.get_key(records,ac,"455"," "," ","a")
                a596_a=aseq.get_key(records,ac,"596"," "," ","a")
                partNumber=joinline(a089_p,a089_n,' / ')
                partNumber=joinline(a455_a)
                partNumber=joinline(a596_a)
                supplemental+=joinlineif("**Zählung:**  \n",partNumber)

                a341_a=aseq.get_key(records,ac,"341"," "," ","a")
                a343_a=aseq.get_key(records,ac,"343"," "," ","a")
                a345_a=aseq.get_key(records,ac,"345"," "," ","a")
                a347_a=aseq.get_key(records,ac,"347"," "," ","a")
                a370aa=aseq.get_key(records,ac,"370","a"," ","a")
                titleVariant=joinline(a341_a,a343_a,j=' : ')
                titleVariant+=joinline(a345_a,a347_a,j=' : ')
                titleVariant+=joinline(a370aa)
                supplemental+=joinlineif("**Weitere Titel:**  \n",titleVariant)

                a100_p=aseq.get_key(records,ac,"100"," "," ","p")
                a100_d=aseq.get_key(records,ac,"100"," "," ","d")
                a100_4=code2name(aseq.get_key(records,ac,"100"," "," ","4"))
                a104ap=aseq.get_key(records,ac,"104","a"," ","p")
                a104ad=aseq.get_key(records,ac,"104","a"," ","d")
                a104a4=code2name(aseq.get_key(records,ac,"104","a"," ","4"))
                a108ap=aseq.get_key(records,ac,"108"," ","a","p")
                a108ad=aseq.get_key(records,ac,"108"," ","a","d")
                a108a4=code2name(aseq.get_key(records,ac,"108","a"," ","4"))
                a112ap=aseq.get_key(records,ac,"112","a"," ","p")
                a112a4=code2name(aseq.get_key(records,ac,"112","a"," ","4"))
                a100bp=aseq.get_key(records,ac,"100","b"," ","p")
                a100bd=aseq.get_key(records,ac,"100","b"," ","d")
                a100b4=code2name(aseq.get_key(records,ac,"100","b"," ","4"))
                a104bp=aseq.get_key(records,ac,"104","b"," ","p")
                a104bd=aseq.get_key(records,ac,"104","b"," ","d")
                a104b4=code2name(aseq.get_key(records,ac,"104","b"," ","4"))
                a108bp=aseq.get_key(records,ac,"108","b"," ","p")
                a108bd=aseq.get_key(records,ac,"108","b"," ","d")
                a108b4=code2name(aseq.get_key(records,ac,"108","b"," ","4"))
                a112ad=aseq.get_key(records,ac,"112","a"," ","d")
                a112bp=aseq.get_key(records,ac,"112","b"," ","p")
                a112bd=aseq.get_key(records,ac,"112","b"," ","d")
                a112b4=code2name(aseq.get_key(records,ac,"112","b"," ","4"))
                a200_k=aseq.get_key(records,ac,"200"," "," ","k")
                a200bh=aseq.get_key(records,ac,"200","b"," ","h")
                a200_h=aseq.get_key(records,ac,"200"," "," ","h")
                a200_4=code2name(aseq.get_key(records,ac,"200"," "," ","4"))
                a204ak=aseq.get_key(records,ac,"204","a"," ","k")
                a204ah=aseq.get_key(records,ac,"204","a"," ","h")
                a204a4=code2name(aseq.get_key(records,ac,"204","a"," ","4"))
                a208ak=aseq.get_key(records,ac,"208","a"," ","k")
                a208ah=aseq.get_key(records,ac,"208","a"," ","h")
                a208a4=code2name(aseq.get_key(records,ac,"208","a"," ","4"))
                a200bk=aseq.get_key(records,ac,"200","b"," ","k")
                a200b4=code2name(aseq.get_key(records,ac,"200","b"," ","4"))
                a204bk=aseq.get_key(records,ac,"204","b"," ","k")
                a204b4=code2name(aseq.get_key(records,ac,"204","b"," ","4"))
                a208bk=aseq.get_key(records,ac,"208","b"," ","k")
                a208bh=aseq.get_key(records,ac,"208","b"," ","h")
                a208b4=code2name(aseq.get_key(records,ac,"208","b"," ","4"))
                a677_p=aseq.get_key(records,ac,"677"," "," ","p")
                a677_d=aseq.get_key(records,ac,"677"," "," ","d")
                a677_4=code2name(aseq.get_key(records,ac,"677"," "," ","4"))


                a064aa=aseq.get_key(records,ac,"064","a"," ","a")
                a439_d=aseq.get_key(records,ac,"439"," "," ","d")
                a204bk=aseq.get_key(records,ac,"204","b"," ","k")
                a204bh=aseq.get_key(records,ac,"204","b"," ","h")
                a425a_=aseq.get_key(records,ac,"425","a"," ","")
                a001_a=aseq.get_key(records,ac,"001"," "," ","a")
                a034_d=aseq.get_key(records,ac,"034"," "," ","d")
                a034_g=aseq.get_key(records,ac,"034"," "," ","g")
                a034_e=aseq.get_key(records,ac,"034"," "," ","e")
                a034_f=aseq.get_key(records,ac,"034"," "," ","f")
                a037ba=aseq.get_key(records,ac,"037","b"," ","a")


                relator=joinline(a100_p,a100_d,a100_4,'; ')
                relator+=joinline(a104ap,a104ad,a104a4,'; ')
                relator+=joinline(a108ap,a108ad,a108a4,'; ')
                relator+=joinline(a112ap,a112ad,a112a4,'; ')
                relator+=joinline(a100bp,a100bd,a100b4,'; ')
                relator+=joinline(a104bp,a104bd,a104b4,'; ')
                relator+=joinline(a108bp,a108bd,a108b4,'; ')
                relator+=joinline(a112bp,a112bd,a112b4,'; ')
                relator+=joinline(a200_k,a200_h,a200_4,'; ')
                relator+=joinline(a204ak,a204ah,a204a4,'; ')
                relator+=joinline(a208ak,a208ah,a208b4,'; ')
                relator+=joinline(a200bk,a200bh,a200b4,'; ')
                relator+=joinline(a208bk,a208bh,a208b4,'; ')


                a677_ps=a677_p.split('\n\n')
                a677_ds=a677_d.split('\n\n')
                a677_4s=a677_4.split('\n\n')

                #print (a677_d)
                #print(len(a677_ps),a677_ps)
                #print(len(a677_ds),a677_ds)
                #print(len(a677_4s),a677_4s)

                for i in range(0,len(a677_ps)):
                    try:
                        ap= a677_ps[i]
                    except IndexError:
                        ap=''
                    try:
                        a4= a677_4s[i]
                    except IndexError:
                        a4=''
                    try:
                        ad= a677_ds[i].replace('""','')
                    except IndexError:
                        ad=''

                    if ap:
                        pers=ap+'; '+ad+' ['+a4+']\n\n'
                        relator+=pers.replace('  ',' ')


                #relator+=joinline(a677_p,a677_d,a677_4,'; ')

                person=joinline(a100_p,a100_d,a100_4,'; ')
                person+=joinline(a200_k,a200_h,a200_4,'; ')

                supplemental+=joinlineif("**Personen/Institution:**  \n",relator.replace('\n\n','  \n'))

                a359_a=aseq.get_key(records,ac,"359"," "," ","a")
                responsibilityStatement=joinline(a359_a)
                supplemental+=joinlineif("**Verantwortlichkeitsangabe:**  \n",responsibilityStatement)

                a403_a=aseq.get_key(records,ac,"403"," "," ","a")
                edition=joinline(a403_a).replace('_',' ').replace('[','').replace(']','')
                supplemental+=joinlineif("**Ausgabe:**  \n",edition)

                a419_a=aseq.get_key(records,ac,"419"," "," ","a")
                providerPlace=joinline(a419_a)
                supplemental+=joinlineif("**Ort:**  \n",providerPlace).replace('[','').replace(']','')

                a419_b=aseq.get_key(records,ac,"419"," "," ","b")
                providerName=joinline(a419_b).replace('_',' ').replace('[','').replace(']','')
                supplemental+=joinlineif("**Verlag/Druck:**  \n",providerName)

                a419_c=aseq.get_key(records,ac,"419"," "," ","c")
                providerDate=joinline(a419_c).replace('_',' ').replace('[','').replace(']','')
                supplemental+=joinlineif("**Datierung:**  \n",providerDate)

                a407_a=aseq.get_key(records,ac,"407"," "," ","a")
                cartographicScale=joinline(a407_a)
                supplemental+=joinlineif("**Maßstab:**  \n",cartographicScale)

                a433_a=aseq.get_key(records,ac,"433"," "," ","a")
                a437_a=aseq.get_key(records,ac,"437"," "," ","a")
                extend=join(a433_a,a437_a,' + ')
                supplemental+=joinlineif("**Umfang:**  \n",extend)

                a435_a=aseq.get_key(records,ac,"435"," "," ","a")
                dimension=join(a435_a)
                supplemental+=joinlineif("**Format:**  \n",dimension)

                a439_a=aseq.get_key(records,ac,"439"," "," ","d")
                baseMaterial=join(a439_a)
                supplemental+=joinlineif("**Reproduktionsverfahren:**  \n",baseMaterial)


                #
                # Bis Doppelpunkt fett und doppelter Zeilenumbruch
                #

                a501_a=aseq.get_key(records,ac,"501"," "," ","a")
                note=joinline(a501_a)
                note_mk=""
                for line in note.split('\n'):
                    ls= line.split(':')
                    if len(ls)==2:
                            note_mk+='\n**'+ls[0].strip()+':**  \n'+ls[1].strip()+'\n'
                #supplemental+=joinlineif("**Anmerkungen:**  \n",note_mk)
                supplemental+=joinlineif("",note_mk)

                blatt_exist=False

                # print (category_dict[filename])

                for i in range(1,250):
                    try:
                        blatt=(category_dict[filename]['titel_blatt%02i'%i])
                        if blatt:
                            blatt_exist=True
                    except KeyError:
                        pass

                if blatt_exist:
                    supplemental+="**Blätter**\n\n"

                    for i in range(1,250):
                        try:
                            blatt=(category_dict[filename]['titel_blatt%02i'%i])

                            if blatt:
                                # print (blatt)
                                supplemental+='  * '+blatt+'\n'
                        except KeyError:
                            pass

                if os.path.exists(abstract_in):
                    print ("Reading",abstract_in)

                    blob = open(abstract_in).read()
                    m = magic.Magic(mime_encoding=True)
                    encoding = m.from_buffer(blob)
                    print (abstract_in,'uses',encoding)

                    try:
                        abstract=escape(open(abstract_in).read().decode(encoding).encode('utf8')).replace('Abstract:','').replace('\n','\n\n')
                    except LookupError:
                        abstract=open(abstract_in).read().replace(chr(int('0x84',16)),'').replace(chr(int('0x93',16)),'').replace(chr(int('0x96',16)),'')
                        abstract=xml.sax.saxutils.escape(abstract.decode('iso-8859-1').encode('utf8')).replace('Abstract:','').replace('\n','\n\n')
                else:
                    print ('Abstract',abstract_in,'missing')


                if os.path.exists(biblio_in):

                    print ("Reading",biblio_in)

                    blob = open(biblio_in).read()
                    m = magic.Magic(mime_encoding=True)
                    try:
                        encoding = m.from_buffer(blob)
                        print (biblio_in,'uses',encoding)
                    except magic.MagicException:
                        encoding='iso-8859-1'
                        print (biblio_in,'setting encoding to',encoding)

                    try:
                        biblio=xml.sax.saxutils.escape(open(biblio_in).read().decode(encoding).encode('utf8'))
                    except LookupError:
                        biblio=open(biblio_in).read().replace(chr(int('0x84',16)),'').replace(chr(int('0x93',16)),'').replace(chr(int('0x96',16)),'')
                        biblio=xml.sax.saxutils.escape(biblio.decode('iso-8859-1').encode('utf8'))
                else:
                    print ('Biblio',biblio_in,'missing')
                    biblio=""

                biblio=biblio.replace('***','').replace('#','').replace('Quellen und weiterführende Literatur:','\n\n####Quellen und weiterführende Literatur:  \n')

                abstract+=biblio
                abstract=abstract.replace('\n','  \n')

                xml_file=codecs.open(xml_out, "w", "utf-8")
                xml_file=open(xml_out,'w')

                title=filename.replace('_',' ').replace('[','').replace(']','')
                title_short=' '.join(title.split(' ')[1:])

                keywords=''
                category=category1=category2=category3=category4=category5=''
                try:
                    if category_dict[filename]['category1']:
                        category1=category_dict[filename]['category1']
                        keywords+=csw.KEYWORD.format(keyword=category_dict[filename]['category1'])
                    if category_dict[filename]['category2']:
                        category2=category_dict[filename]['category2']
                        keywords+=csw.KEYWORD.format(keyword=category_dict[filename]['category2'])
                    if category_dict[filename]['category3']:
                        category3=category_dict[filename]['category3']
                        keywords+=csw.KEYWORD.format(keyword=category_dict[filename]['category3'])
                    if category_dict[filename]['category4']:
                        category4=category_dict[filename]['category4']
                        category=csw.CATEGORY.format(category=category_dict[filename]['category4'].lower())
                    if category_dict[filename]['category5']:
                        category5=category_dict[filename]['category5']
                        keywords+=csw.KEYWORD.format(keyword=category_dict[filename]['category5'])

                except KeyError:
                    pass
                # print(category)

                region=""

                if a034_b:
                    denominator = int(a034_b.strip().replace(' ',''))
                    # print ("Set denominator to",denominator)

                if denominator < 10000000:
                    region_list=regions.pos2region(countries,north,south,west,east)
                    for r in region_list:
                        if r:
                            #print (r)
                            region+=csw.REGION.format(region=r)
                try:
                    year=int(providerDate.replace('[','').replace(']','').replace('?',''))
                except:
                    year=0

                a425aa=aseq.get_key(records,ac,"425","a"," ","a")
                a425ab=aseq.get_key(records,ac,"425","a"," ","b")
                a425ac=aseq.get_key(records,ac,"425","a"," ","c")


                if a425aa:
                    year=a425aa
                if a425ab:
                    year=a425ab
                if a425ac:
                    date=a425ac

                print (denominator,title_short,partOf,titleValue)

                purpose=titleValue
                supplemental=supplemental.decode('utf-8','ignore').encode("utf-8").replace(chr(int('0x0b',16)),'')
                abstract=abstract.decode('utf-8','ignore').encode("utf-8").replace(chr(int('0x0b',16)),'')

                xml_file.write(csw.CSW.format(id=ac,name=escape(title_short),name_url=escape(name),geonode='http://localhost:8000',geoserver='http://localhost:8080/geoserver',west=west,east=east,north=north,south=south,z='{z}',x='{x}',y='{y}',supplemental=supplemental,abstract=abstract,purpose=purpose,keywords=keywords,category=category,region=region,year=year,denominator=abs(denominator)).replace('\n\n\n\n','\n\n'))
                xml_file.close()

                if abstract:
                    abst='yes'
                else:
                    abst='no'

                if biblio:
                    bib='yes'
                else:
                    bib='no'

                if west!=0.0 and north!=0.0 and east!=0.0 and south!=0.0:
                    geo='yes'
                else:
                    geo='no'

                #csv_abstract.write(filename+","+abst+"\n")
                csv_import.write(filename+','+str(denominator)+','+geo+','+abst+','+bib+','+category1+','+category2+','+category3+','+category4+','+category5+'\n')

                dc = dublincore.METADATA.format(a331_a=a331_a,a335_a=a335_a,a341_a=a341_a,a343_a=a343_a,
                                                           a345_a=a345_a,a347_a=a347_a,a370aa=a370aa,a359_a=a359_a,
                                                           a100_p=a100_p,a100_d=a100_d,a100_4=a100_4,
                                                           a104ap=a104ap,a104ad=a104ad,a104a4=a104a4,
                                                           a108ap=a108ap,a108ad=a108ad,a108a4=a108a4,
                                                           a112ap=a112ap,a112ad=a112ad,a112a4=a112a4,
                                                           a200_k=a200_k,a200_h=a200_h,a200_4=a200_4,
                                                           a204ak=a204ak,a204ah=a204ah,a204a4=a204a4,
                                                           a208ak=a208ak,a208ah=a208ah,a208a4=a208a4,
                                                           a064aa=a064aa,a407_a=a407_a,
                                                           a433_a=a433_a,a437_a=a437_a,a435_a=a435_a,
                                                           a439_d=a439_d,a501_a=a501_a,abstract=xml.sax.saxutils.escape(abstract),
                                                           filename=xml.sax.saxutils.escape(filename.lower()),
                                                           a419_b=a419_b,a419_a=a419_a,a419_c=a419_c,
                                                           a100bp=a100bp,a100bd=a100bd,a100b4=a100b4,
                                                           a104bp=a104bp,a104bd=a104bd,a104b4=a104b4,
                                                           a108bp=a108bp,a108bd=a108bd,a108b4=a108b4,
                                                           a112bp=a112bp,a112bd=a112bd,a112b4=a112b4,
                                                           a200bk=a200bk,a200bh=a200bh,a200b4=a200b4,
                                                           a204bk=a204bk,a204bh=a204bh,a204b4=a204b4,
                                                           a208bk=a208bk,a208bh=a208bh,a208b4=a208b4,
                                                           a677_p=a677_p,a677_d=a677_d,a677_4=a677_4,
                                                           a425a_=a425a_,a001_a=a001_a,a037ba=a037ba,
                                                           a010_a=a010_a,a453ma=a453ma,a453ra=a453ra,a599_a=a599_a,
                                                           a034_d=a034_d,a034_g=a034_g,a034_e=a034_e,a034_f=a034_f
                                                           )
                dc=dc.replace('<dcterms:alternative> :  </dcterms:alternative>\n','')
                dc=dc.replace('<dc:creator>;  </dc:creator>\n','')
                dc=dc.replace('<dc:contributor>;  </dc:contributor>\n','')
                dc=dc.replace('<dc:date></dc:date>\n','')
                dc=dc.replace('<dcterms:isPartOf></dcterms:isPartOf>\n','')
                dc_import.write(dc)


@task()
def update_layer(ctx,layer):

    if layer[-4:]==".tif":
        layer=layer[:-4]
    layer_tif=ctx.output_dir+layer+'.tif'
    layer_xml=ctx.output_dir+layer+'.xml'
    layer_geo=ctx.output_dir+layer+'.geo'
    if exists(layer_tif):
        for f in (layer_tif,layer_xml,layer_geo):
            ctx.run("rm -vf %s"%f)

        create_maps(ctx)
        create_metadata(ctx)
        importlayer='cd {geonode_dir};python ./manage.py importlayers -v3 -u {user} -o {tiff} '.format(geonode_dir=ctx.geonode_dir, user=ctx.user ,tiff=layer_tif)
        ctx.run(importlayer)
        cleanup_maps(ctx)
        rebuild_index(ctx)
    else:
        print ("Can't find tiff",layer_tif)


@task()
def import_maps(ctx):
    create_maps(ctx)
    create_metadata(ctx)
    importlayer='cd {geonode_dir};python ./manage.py importlayers -v3 -u {user} -o {tiff} '.format(geonode_dir=ctx.geonode_dir, user=ctx.user ,tiff=ctx.output_dir)
    ctx.run(importlayer)
    cleanup_maps(ctx)
    rebuild_index(ctx)



@task()
def update_maps(ctx):
    create_maps(ctx)
    create_metadata(ctx)
    importlayer='cd {geonode_dir};python ./manage.py importlayers -v3 -u {user} {tiff} '.format(geonode_dir=ctx.geonode_dir, user=ctx.user ,tiff=ctx.output_dir)
    ctx.run(importlayer)
    cleanup_maps(ctx)
    rebuild_index(ctx)


@task()
def cleanup_maps(ctx):
    cleanup_maps='rm -rf {geonode_dir}/geonode/uploaded/layers/*'.format(geonode_dir=ctx.geonode_dir)
    ctx.run(cleanup_maps)


@task()
def cleanup_tmp(ctx):
    ctx.run('rm -rf {dir}'.format(dir=ctx.gcp_dir))
    ctx.run('rm -rf {dir}'.format(dir=ctx.vips_dir))
    ctx.run('rm -rf {dir}'.format(dir=ctx.warp_dir))
    ctx.run('rm -rf {dir}'.format(dir=ctx.wld_dir))


@task()
def delete_maps(ctx):
    ctx.run('rm -rf {dir}/*'.format(dir=ctx.output_dir))

@task()
def delete_metadata(ctx):
    ctx.run('rm -rf {dir}/*.xml'.format(dir=ctx.output_dir))

@task()
def test_geocoder(ctx):

    countries=regions.country2kontinent()

    #regions.pos2region(countries,36.0654206327,2.27685164945,25.5277830434,71.2462763724)
    regions.pos2region(countries,47.1319451633,46.9127043394,12.8330743987,13.1941276942)
    #regions.pos2region(countries,5.56634191981,74.035496039,32.775356264,70.8293161903)
