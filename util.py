# -*- coding: utf-8 -*-

from __future__ import print_function
import xml.sax.saxutils

def join(s1,s2='',j=''):
    if s1 and s2:
        return j.join((s1,s2))
    else:
        if s1:
            return s1
        if s2:
            return s2
        return ""

def joinline(s1,s2='',s3='',j=''):
    line=join(s1,s2,j)
    if s3:
        line+=' ['+s3+']'
    if line:
        return (line.strip()+'\n\n')
    else:
        return ''

def joinlineif(s1,s2='',s3='',j=''):
    if s2:
        return  joinline(s1,s2,s3,j)+'\n\n'
    else:
        return ''

def clean(txt):
    txt=txt.replace(' ','_')
    txt=txt.replace('Ä','Ae')
    txt=txt.replace('Ö','Oe')
    txt=txt.replace('Ü','Ue')
    txt=txt.replace('ä','ae')
    txt=txt.replace('ö','oe')
    txt=txt.replace('ü','ue')
    txt=txt.replace('&','_und_')
    txt=txt.replace("'","_")
    txt=txt.replace("__","_")
    txt=txt.replace("<","")
    txt=txt.replace(">","")
    txt=txt.replace("-","_")
    txt=txt.replace("__","_")
    return txt

def escape(s):
    return xml.sax.saxutils.escape(s).strip().replace("<","").replace("&lt;","").replace("&gt;","")

def escape_path(p):
    return p.replace(' ','\ ').replace('&','\&').replace("'","\'")

def list2options(tag,list):
    #print ("DEBUG list2options",tag,list)
    option=''
    for element in list:
        option+=tag+' '
        option+=element+' '
    return option
def ctx2options(ctx,image):
    #print ("DEBUG ctx2options",ctx.images[image])
    options=''
    ctx_image=ctx.images[image]

    if ctx_image:
        if 'links' in ctx_image:
            options+=list2options('--link',ctx_image.links)
        if 'ports' in ctx_image:
            options+=list2options('-p',ctx_image.ports)
        if 'env' in ctx_image:
            options+=list2options('-e',ctx_image.env)
        if 'volumes' in ctx_image:
            for volume in ctx_image.volumes:
                #print ('DEBUG volume',ctx_image.volumes[volume])
                options+=' -v '+ctx.data_dir+'/'+ctx.network+'/'+image+'/'+volume+':'+ctx_image.volumes[volume]
        if 'hostname' in ctx_image:
            hostname=ctx_image.hostname
        else:
            hostname=image
        options+=" --network={network} --hostname {hostname} --network-alias={hostname}".format(network=ctx.network,hostname=hostname)
    return options

def code2name(code):
    code=code.replace('edt','HerausgeberIn')
    code=code.replace('aut','VerfasserIn')
    code=code.replace('ctg','KartografIn')
    code=code.replace('pbl','VerlegerIn')
    code=code.replace('prt','DruckerIn')
    code=code.replace('dst','Vertrieb')
    code=code.replace('mfr','HerstellerIn')
    code=code.replace('ltg','LithographIn')
    code=code.replace('etr','RadiererIn')
    code=code.replace('egr','StecherIn')
    code=code.replace('isb','herausgebendes Organ')
    code=code.replace('oth','Sonstige')
    code=code.replace('dte','WidmugsempfängerIn')
    return code

#def name2options(ctx,image):
#    network = ctx.network
#    #print ("DEBUG name2options",ctx.images[image])
#    try:
#        version = ctx.images[image].version
#    except AttributeError:
#        version = ctx.version
    #try:
#    options = ctx2options(ctx,image)
    #except AttributeError:
    #    options=''
#    return (network,version,options)

def ctx2version(ctx,image):

    if ctx.images[image] and ('version' in ctx.images[image]):
        version = ctx.images[image].version
    else:
        version = ctx.version

    return version
