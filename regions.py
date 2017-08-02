import csv
import geocoder

def country2kontinent():
    print ("Importing Kontinents")
    countries={}
    with open('country2kontinent.csv', 'r') as country_file:
        country_csv = csv.DictReader(country_file)
        for row in country_csv:
                countries[row['\xef\xbb\xbfcountry']]={'continent':row['continent']}
    return countries

def pos2region(countries,north,south,west,east):
    region=[]

    g_ul = geocoder.google([north,west], method='reverse',language='de')
    g_ur = geocoder.google([north,east], method='reverse',language='de')
    g_ll = geocoder.google([south,west], method='reverse',language='de')
    g_lr = geocoder.google([south,east], method='reverse',language='de')

    g_ul_continent=''
    g_ur_continent=''
    g_ll_continent=''
    g_lr_continent=''

    if g_ul.country:
        g_ul_continent=countries[g_ul.country]['continent']
    if g_ur.country:
            g_ur_continent=countries[g_ur.country]['continent']
    if g_ll.country:
            g_ll_continent=countries[g_ll.country]['continent']
    if g_lr.country:
            g_lr_continent=countries[g_lr.country]['continent']

    if g_ul.country_long == g_ur.country_long == g_ll.country_long ==  g_lr.country_long and g_ul_country != 'None':
        region.append(g_ul.country_long)

    if g_ul_continent == g_ur_continent == g_ll_continent == g_lr_continent and g_ul_continent != 'None':
        region.append(g_ul_continent)

    print(north,west,g_ul.country_long,g_ul_continent)
    print(north,east,g_ur.country_long,g_ur_continent)
    print(south,west,g_ll.country_long,g_ll_continent)
    print(south,east,g_lr.country_long,g_lr_continent)


    return region
