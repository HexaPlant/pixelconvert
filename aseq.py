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
            #print(datafield.tag,datafield.ind1,datafield.ind2)

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
                    datafields[tag][ind1][ind2][code]=value_orig.strip()+'\n'+value+'\n\n'
                    #print(tag,ind1,ind2,code,datafields[tag][ind1][ind2][code])

                except KeyError:
                    datafields[tag][ind1][ind2][code]=value




        ac = (datafields["001"][" "][" "]["a"])
        records[ac]=datafields

    return(records)
