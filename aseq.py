from __future__ import print_function
import MARC21relaxed
from util import clean,escape,escape_path

def get_key(records,df,tag,ind1,ind2,code):
    try:
        value = escape(records[df][tag][ind1][ind2][code]).encode('utf-8')
    except KeyError:
        value=""
    return value

def load(ctx):
    xmlIN = open(ctx.aseq_file).read()
    collection = MARC21relaxed.CreateFromDocument(xmlIN)

    records={}

    for record in collection.record:

        leader=""
        controlfields={}
        datafields={}

        for ld in record.leader:
            leader=ld.value()

        for cf in record.controlfield:
            #print(controlfield.tag,controlfield.value())
            controlfields[cf.tag]=cf.value()

        for df in record.datafield:

            if df.tag <> '677':
                for sf in df.subfield:
                    tag = df.tag
                    ind1 = df.ind1
                    ind2 = df.ind2
                    code = sf.code
                    value = sf.value()

                    if not tag in datafields:
                        datafields[tag]={}
                    if not ind1 in datafields[tag]:
                        datafields[tag][ind1]={}
                    if not ind2 in datafields[tag][ind1]:
                        datafields[tag][ind1][ind2]={}
                    try:
                        # print(tag, ind1, ind2, code,value)
                        value_orig=datafields[tag][ind1][ind2][code]
                        #datafields[tag][ind1][ind2][code]=value_orig.strip()+'\n\n'+value+'\n\n'
                        datafields[tag][ind1][ind2][code]=value_orig+'\n\n'+value
                        #print(tag,ind1,ind2,code,datafields[tag][ind1][ind2][code])
                    except KeyError:
                        datafields[tag][ind1][ind2][code]=value

            else:
                for sf in df.subfield:
                    tag = df.tag
                    ind1 = df.ind1
                    ind2 = df.ind2
                    code = sf.code
                    value = sf.value()

                    if not tag in datafields:
                        datafields[tag]={}
                    if not ind1 in datafields[tag]:
                        datafields[tag][ind1]={}
                    if not ind2 in datafields[tag][ind1]:
                        datafields[tag][ind1][ind2]={}
                    try:
                        value_orig=datafields[tag][ind1][ind2][code]
                        datafields[tag][ind1][ind2][code]=value_orig+'\n\n'+value

                        #datafields[tag][ind1][ind2][code]=value_orig.strip()+'\n\n'+value+'\n\n'
                        #print(tag,ind1,ind2,code,datafields[tag][ind1][ind2][code])
                    except KeyError:
                        datafields[tag][ind1][ind2][code]=value

                    #print(tag, ind1, ind2, code,len(datafields[tag][ind1][ind2][code].split('\n\n')))

                    try:
                        l677_p=len(datafields[tag][ind1][ind2]['p'].split('\n\n'))
                    except KeyError:
                        l677_p=0

                    try:
                        l677_4=len(datafields[tag][ind1][ind2]['4'].split('\n\n'))
                    except KeyError:
                        l677_4=0

                    try:
                        l677_d=len(datafields[tag][ind1][ind2]['d'].split('\n\n'))
                    except KeyError:
                        l677_d=0

                    if l677_p==2 and  l677_d==0:
                        datafields[tag][ind1][ind2]['d']='""\n\n'
                    if l677_p >  l677_d +1:
                        datafields[tag][ind1][ind2]['d']=datafields[tag][ind1][ind2]['d']+'""\n\n'





        ac = (datafields["001"][" "][" "]["a"])
        records[ac]=datafields

    return(records)
