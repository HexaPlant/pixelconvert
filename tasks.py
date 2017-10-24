# -*- coding: utf-8 -*-

from __future__ import print_function
from invoke import Collection, task
from util import join,joinline,joinlineif,clean,escape,escape_path,code2name
import csv
import codecs
import magic

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
import geocoder
import regions

@task()
def convert(ctx):
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

            if not exists(tiff_gcp) and exists(points_in):
                ctx.run ('cp -v {tiff_in} {tiff_gcp}'.format(tiff_in=escape_path(tiff_in),tiff_gcp=escape_path(tiff_gcp)))
            else:
                print("Missing",points_in," for",tiff_in)

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
                if not exists(tiff_final):
                    ctx.run('gcps2wld.py {tiff} > {wld_out}'.format(tiff=tiff_gcp,wld_out=wld_gcp))
                    ctx.run('gdal_translate -a_srs EPSG:3857 -mo NODATA_VALUES="255 255 255" {tiff_in} {tiff_out}'.format(tiff_in=tiff_gcp,tiff_out=tiff_wld))
                    ctx.run("listgeo {tiff_in} > {gtxt_out}".format(tiff_in=escape_path(tiff_wld),gtxt_out=escape_path(gtxt_out)))


                    ctx.run("vips --vips-progress  --vips-concurrency=16 im_vips2tiff {tiff_in} {tiff_out}:deflate,tile:256x256,pyramid".format(tiff_in=escape_path(tiff_gcp),tiff_out=escape_path(tiff_final)))
                    ctx.run("applygeo {gtxt_in} {tiff_out}".format(gtxt_in=escape_path(gtxt_out),tiff_out=escape_path(tiff_final)))
                    ctx.run('gdal_edit.py -a_nodata 255 -mo NODATA_VALUES="255 255 255" {tiff_out}'.format(tiff_out=tiff_final))

                    #if exists(tiff_final):
                    #    ctx.run('rm -v {tiff}'.format(tiff=tiff_gcp))
                    #    ctx.run('rm -v {tiff}'.format(tiff=tiff_wld))
                    #    ctx.run('rm -v {wld}'.format(wld=wld_gcp))

                     #ctx.run('gdal_edit.py -unsetgt -unsetmd -a_srs EPSG:3857 -a_nodata 255  -mo NODATA_VALUES="255 255 255" {gcp} {tiff}'.format(gcp=gcp,tiff=tiff_vips))
                     #ctx.run('gdal_edit.py -unsetgt -a_srs EPSG:3857 -a_nodata 255  -mo NODATA_VALUES="255 255 255" {gcp} {tiff}'.format(gcp=gcp,tiff=tiff_vips))


                #if not exists(tiff_warp):
                #    ctx.run('gdalwarp  -dstalpha -tps -co "COMPRESS=DEFLATE" -co BIGTIFF=YES -co TILED=YES -r lanczos  -s_srs EPSG:3857 -t_srs EPSG:3857  -multi -wo NUM_THREADS=ALL_CPU {tiff_gcp} {tiff_warp}'.format(tiff_gcp=tiff_gcp,tiff_warp=tiff_warp))
                    #ctx.run('gdalwarp  -dstalpha  -co "COMPRESS=DEFLATE"  -tps -refine_gcps 10 30 -s_srs EPSG:3857 -t_srs EPSG:3857  -multi -wo NUM_THREADS=ALL_CPU {tiff_gcp} {tiff_warp}'.format(tiff_gcp=tiff_gcp,tiff_warp=tiff_warp))
                    #ctx.run('gdaladdo  --config COMPRESS_OVERVIEW DEFLATE -r lanczos {tiff_warp} 2 4 8 16 32'.format(tiff_warp=tiff_warp))



@task()
def createxml(ctx):

    print ("Importing Categories")
    category_dict={}
    with open(ctx.category, 'r') as category_file:
        category_csv = csv.DictReader(category_file)
        for row in category_csv:
            #print (row)
            category_dict[row['filename']]={
                'category1':row['category1'],
                'category2':row['category2'],
                'category3':row['category3'],
                'category4':row['category4'],
                'category5':row['category5'],
            }

    print ("Importing Metadata")
    records=aseq.load(ctx)
    #csv_abstract=open("out/woldan_abstract.csv","w")
    #csv_abstract.write("title,abstract\n")
    csv_import=open("out/woldan_import.csv","w")
    csv_import.write("filename,geo,abstract,biblio,category1,category2,category3,category4,category5\n")

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
                dataset = gdal.Open(tiff_final)
                cols = dataset.RasterXSize
                rows = dataset.RasterYSize
                bands = dataset.RasterCount

                ulx, xres, xskew, uly, yskew, yres  = dataset.GetGeoTransform()
                lrx = ulx + (dataset.RasterXSize * xres)
                lry = uly + (dataset.RasterYSize * yres)

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
                partOf=joinline(parent_a331_a)
                partOf=joinline(parent_a453ma)
                partOf=joinline(parent_a453ra)
                partOf=joinline(parent_a599_a)
                abstract+=joinlineif("**Gesamttitel:** ",partOf)

                a331_a=aseq.get_key(records,ac,"331"," "," ","a")
                a335_a=aseq.get_key(records,ac,"335"," "," ","a")
                titleValue=join(a331_a,a335_a,' : ').replace('[','').replace(']','')
                abstract+=joinlineif("**Titel:** ",titleValue)

                a089_p=aseq.get_key(records,ac,"089"," "," ","p")
                a089_n=aseq.get_key(records,ac,"089"," "," ","n")
                a455_a=aseq.get_key(records,ac,"455"," "," ","a")
                a596_a=aseq.get_key(records,ac,"596"," "," ","a")
                partNumber=joinline(a089_p,a089_n,' / ')
                partNumber=joinline(a455_a)
                partNumber=joinline(a596_a)
                abstract+=joinlineif("**Zählung:** ",partNumber)

                a341_a=aseq.get_key(records,ac,"341"," "," ","a")
                a343_a=aseq.get_key(records,ac,"343"," "," ","a")
                a345_a=aseq.get_key(records,ac,"345"," "," ","a")
                a347_a=aseq.get_key(records,ac,"347"," "," ","a")
                a370aa=aseq.get_key(records,ac,"370","a"," ","a")
                titleVariant=joinline(a341_a,a343_a,j=' : ')
                titleVariant+=joinline(a345_a,a347_a,j=' : ')
                titleVariant+=joinline(a370aa)
                abstract+=joinlineif("**Weitere Titel:** ",titleVariant)

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
                relator+=joinline(a677_p,a677_d,a677_4,'; ')

                abstract+=joinlineif("**Personen/Institution:** ",relator)

                a359_a=aseq.get_key(records,ac,"359"," "," ","a")
                responsibilityStatement=joinline(a359_a)
                abstract+=joinlineif("**Verantwortlichkeitsangabe:** ",responsibilityStatement)

                a403_a=aseq.get_key(records,ac,"403"," "," ","a")
                edition=joinline(a403_a).replace('_',' ').replace('[','').replace(']','')
                abstract+=joinlineif("**Ausgabe:** ",edition)

                a419_a=aseq.get_key(records,ac,"419"," "," ","a")
                providerPlace=joinline(a419_a)
                abstract+=joinlineif("**Ort:** ",providerPlace).replace('[','').replace(']','')

                a419_b=aseq.get_key(records,ac,"419"," "," ","b")
                providerName=joinline(a419_b).replace('_',' ').replace('[','').replace(']','')
                abstract+=joinlineif("**Verlag/Druck:** ",providerName)

                a419_c=aseq.get_key(records,ac,"419"," "," ","c")
                providerDate=joinline(a419_c).replace('_',' ').replace('[','').replace(']','')
                abstract+=joinlineif("**Datierung:** ",providerDate)

                a407_a=aseq.get_key(records,ac,"407"," "," ","a")
                cartographicScale=joinline(a407_a)
                abstract+=joinlineif("**Maßstab:** ",cartographicScale)

                a433_a=aseq.get_key(records,ac,"433"," "," ","a")
                a437_a=aseq.get_key(records,ac,"437"," "," ","a")
                extend=join(a433_a,a437_a,' + ')
                abstract+=joinlineif("**Umfang:** ",extend)

                a435_a=aseq.get_key(records,ac,"435"," "," ","a")
                dimension=join(a435_a)
                abstract+=joinlineif("**Format:** ",dimension)

                a439_a=aseq.get_key(records,ac,"439"," "," ","d")
                baseMaterial=join(a439_a)
                abstract+=joinlineif("**Reproduktionsverfahren:** ",baseMaterial)

                a501_a=aseq.get_key(records,ac,"501"," "," ","a")
                note=join(a501_a)
                abstract+=joinlineif("**Anmerkungen:** ",note)

                if os.path.exists(biblio_in):

                    blob = open(biblio_in).read()
                    m = magic.Magic(mime_encoding=True)
                    try:
                        encoding = m.from_buffer(blob)
                        print (biblio_in,'uses',encoding)
                    except magic.MagicException:
                        encoding='iso-8859-1'

                    if encoding=='unknown-8bit' or encoding=='binary':
                        encoding='iso-8859-1'

                    biblio=escape(open(biblio_in).read().decode(encoding).encode('utf8')).replace('Quellen und weiterführende Literatur:','**Quellen und weiterführende Literatur:**')
                    abstract+=biblio

                else:
                    print ('Biblio',biblio_in,'missing')
                    biblio=""

                if os.path.exists(abstract_in):

                    blob = open(abstract_in).read()
                    m = magic.Magic(mime_encoding=True)
                    encoding = m.from_buffer(blob)
                    print (abstract_in,'uses',encoding)

                    try:
                        supplemental=escape(open(abstract_in).read().decode(encoding).encode('utf8')).replace('Abstract:','')
                    except LookupError:
                        supplemental=open(abstract_in).read().replace(chr(int('0x84',16)),'').replace(chr(int('0x93',16)),'')
                        supplemental=escape(supplemental.decode('iso-8859-1').encode('utf8')).replace('Abstract:','')

                else:
                    print ('Abstract',abstract_in,'missing')

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
                region_list=regions.pos2region(countries,north,south,west,east)
                for r in region_list:
                    if r:
                        region+=csw.REGION.format(region=r.encode('utf8'))
                        print ("Region",r)


                try:
                    year=int(providerDate.replace('[','').replace(']','').replace('?',''))
                except:
                    year=0

                print (title_short,partOf,titleValue)

                xml_file.write(csw.CSW.format(id=ac,name=escape(title_short),name_url=escape(name),geonode='http://localhost:8000',geoserver='http://localhost:8080/geoserver',west=west,east=east,north=north,south=south,z='{z}',x='{x}',y='{y}',supplemental=supplemental,abstract=abstract,purpose=titleValue,keywords=keywords,category=category,region=region,year=year))
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
                csv_import.write(filename+','+geo+','+abst+','+bib+','+category1+','+category2+','+category3+','+category4+','+category5+'\n')

@task()
def importlayers(ctx):
    importlayer='cd {geonode_dir};./manage.py importlayers -v3 -o {tiff} '.format(geonode_dir=ctx.geonode_dir, tiff=ctx.output_dir)
    rebuild_index='cd {geonode_dir};./manage.py rebuild_index --noinput'.format(geonode_dir=ctx.geonode_dir)
    ctx.run(importlayer)
    ctx.run(rebuild_index)

@task()
def test_geocoder(ctx):

    countries=regions.country2kontinent()

    #regions.pos2region(countries,36.0654206327,2.27685164945,25.5277830434,71.2462763724)
    regions.pos2region(countries,47.1319451633,46.9127043394,12.8330743987,13.1941276942)
    #regions.pos2region(countries,5.56634191981,74.035496039,32.775356264,70.8293161903)
