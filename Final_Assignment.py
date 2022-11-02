#Data Analysis and Programming for Operations Management 2021-2022
#Individual Assignment

#autor : Mattia Bonotto
#date: 29/10/2021
%reset -f

from elasticsearch import Elasticsearch
from datetime import datetime
from gurobipy import Model, GRB, quicksum
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import json
import smopy
import random
import holidays
import randomcolor


#################################
# STEP 1: locations and districts
#################################

#1.1 - Query the location and delivery data from the database postcodes.
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

search_body_postcodes = {
'size': 10000,
'query': {
    'match_all': {}
}
}
result = es.search(index='postcodes', body=search_body_postcodes, ignore=400)
df_postcodes = pd.DataFrame(result['hits']['hits'])
df_postcodes = df_postcodes['_source'].apply(pd.Series)

#1.2 - Plot all locations and visualize them geographically with smopy.
df_postcodes['Longitude'] = df_postcodes['Longitude'].astype(float)
df_postcodes['Latitude'] = df_postcodes['Latitude'].astype(float)

#create a map of the city
map = smopy.Map(min(df_postcodes['Latitude']), min(df_postcodes['Longitude']),
                max(df_postcodes['Latitude']), max(df_postcodes['Longitude']), z = 12)
ax = map.show_mpl(figsize=(15,10))

#create a list of districts
districts = []
for i in range(len(df_postcodes)):
    onlynum = ((df_postcodes['Postcode'][i][:-2]))
    if onlynum not in districts:
        districts.append(onlynum)

#create a list with random colors
rand_color = randomcolor.RandomColor()
color = (rand_color.generate(count=len(districts)))

for p in range(len(df_postcodes)):
    x, y  = map.to_pixels(df_postcodes['Latitude'][p], df_postcodes['Longitude'][p])
    onlynum = (df_postcodes['Postcode'][p][:-2])
    for c in range(len(districts)):
        if onlynum in districts[c]:
            ax.plot(x, y, 'or', color=color[c], ms=5, mew=5)


#1.3 - Compute the daily average deliveries for each location and district
#create a list of the holidays in the Netherlands then implement it in a for loop
#in order to query from the deliveries database only the working days in the year.
#After aggregate them from postcode in order to have the deliveries per locations in 2020
#and put the data into a DataFrame
holidays_list = []
for date, name in sorted(holidays.Netherlands(years=2020).items()):
    holidays_list.append(date.strftime('%Y-%m-%d'))

holidays_to_remove = []
for d in holidays_list:
    holidays_to_remove.append(
    {
        'range': {
            'deliveries_datetime': {
                'gte': d,
                'lte': d,
                'format': 'yyyy-MM-dd'
            }
        }
    }
    )

search_body_deliveries_1 = {
'size': 0,
'query': {
    'bool': {
        'must_not': holidays_to_remove
    }
},
'size': 0,
'aggs': {
    'locations': {
        'terms': {
            'field': 'postcodes_column',
            'size': 10000
        }
    }
}
}
result = es.search(index='deliveries', body=search_body_deliveries_1, ignore=400)
df_locations = pd.DataFrame(result['aggregations']['locations'])
df_locations = df_locations['buckets'].apply(pd.Series)

#computate the daily average deliveries for each location
avg_location_deliveries = []
for i in range(len(df_locations)):
    a = df_locations['doc_count'][i]/(366-len(holidays_list))
    avg_location_deliveries.append(a)

df_locations.loc[:,'average_deliveries_per_day'] = avg_location_deliveries

#Now aggregate from district in order to have the deliveries per district in 2020
#and put the data in a DataFrame
search_body_deliveries_2 = {
'size': 0,
'query': {
    'bool': {
        'must_not': holidays_to_remove
    }
},
'aggs': {
    'disticts': {
        'terms': {
            'size': 100,
            'script': {
                'source': "return doc['postcodes_column'].value.substring(0,4)",
                'lang': 'painless'
            }
        }
    }
}
}
result = es.search(index='deliveries', body=search_body_deliveries_2, ignore=400)
df_districts = pd.DataFrame(result['aggregations']['disticts'])
df_districts = df_districts['buckets'].apply(pd.Series)

#computate the daily average deliveries per district
avg_districts_deliveries = []
for i in range(len(df_districts)):
    a = df_districts['doc_count'][i]/(366-len(holidays_list))
    avg_districts_deliveries.append(a)

df_districts.loc[:,'average_deliveries_per_day'] = avg_districts_deliveries


#1.4 - Plot total average deliveries for each district on a bar chart
df_districts.set_axis(['districts', 'total_deliveries', 'average_deliveries_per_day'],
                        axis='columns', inplace=True)
barchart = df_districts.plot.barh(x='districts', y='average_deliveries_per_day', figsize=(13,8))


####################
#STEP 2:Optimization
####################

#2.1 - Query the info for all possible (customer) location and (pickup) location
# pairs in a single district from the database distances.
locations = df_locations['key']
districts.sort()
n_of_pickup = []

#Main loop
for d in range(len(districts)):
    print('###############', districts[d], '###############')
    locs_in_dist = [i for i in locations if i[:4] == districts[d]]
    locs_in_dist.sort()
    seconds = []

    #create two lists for the indices
    n = [i for i in range(len(locs_in_dist))]
    N = [(i,j) for i in n for j in n]

    #loop for evry location in a district
    for p in range(len(locs_in_dist)):
        search_body_distances = {
            'size': 10000,
            'query': {
                'bool': {
                    'must': [
                        {'term': {'src': locs_in_dist[p]}},
                        {'wildcard': {'dest': str(districts[d] + '*')}}
                    ]
                }
            },
            'sort': [
                {'dest': {'order': 'asc'}}
            ]
        }
        result = es.search(index='distances', body=search_body_distances)
        values = result['hits']['hits']

        #Add the seconds for all possible (customer) location and (pickup) location
        #in a district with a list. Then manually add the 0s in a determinate
        #position when (customer) location and (pickup) location are the same.
        for k in range(len(values)):
            seconds.append(float(values[k]['_source']['seconds'])/60)
        seconds.insert(p+(len(values)+1)*p,0)

    #compute the percentage of parcels that will be delivered via self-pickups
    #in a particular district.
    percentages = []
    for i in seconds:
        a = 0.4-(0.1*i)
        if a < 0:
            percentages.append(0)
        else:
            percentages.append(a)

    #The percentage of parcels that will be delivered via self-pickups
    W = dict(zip(N, percentages))
    #The max capacity of each pickup in a year
    C = 50*(366-len(holidays_list))
    #The percentage of self-pickups should be at least 30% of the total number of deliveries.
    P = 0.3
    #The number of deliveries in a particular location
    D = []
    for i in locs_in_dist:
        a = int(df_locations[df_locations['key'] == i].index.values)
        D.append(df_locations.iloc[a][1])
    DE = sum(D)


    # 2.3 - NETWORK MODEL and optimization
    m = Model("Network_Model")

    #VARIABLES: x,y
    x = m.addVars(N, vtype=GRB.BINARY, name='x')
    y = m.addVars(n, vtype=GRB.BINARY, name='y')

    #OBJECTIVE: minimize the number of pickup points
    m.setObjective(quicksum(y[j] for j in n), GRB.MINIMIZE)

    #COSTRAINS
    #Each location should be allocated to at most one pickup point
    m.addConstrs(quicksum(x[i,j] for j in n) <= 1 for i in n)
    #The number of self-pickups from each pickup point should be below the capacity
    m.addConstrs(quicksum(D[i]*x[i,j]*W[(i,j)] for i in n) <= C*y[j] for j in n)
    #The total number of self pickups should be at least P percent of the total number of deliveries.
    m.addConstr(quicksum(D[i]*x[i,j]*W[(i,j)] for i in n for j in n) >= P*DE)
    #The ith location can be assigned to the pickup point at the jth location only if a pickup point is
    #opened at the jth location
    m.addConstrs((x[i,j]) <= y[j] for i in n for j in n)
    #The ith location should not be assigned to the pickup point at the jth location if the associated
    #percentage of self-pickups is zero
    m.addConstrs((x[i,j]) == 0 for i in n for j in n if W[(i,j)] == 0)

    m.optimize()

    #SOLUTIONS: Then from the guroby solution reconize the right locations and
    #put them in a list
    solutions = [[v.varName, v.x] for v in m.getVars()]
    pic_loc = []
    for i in range(len(solutions)):
        if solutions[i][0][0] == 'y' and solutions[i][1] == 1:
            a = int(len(solutions[i][0])-1)
            index = int(solutions[i][0][2:a])
            pic_loc.append(locs_in_dist[index])

    n_of_pickup.append(len(pic_loc))


    #2.4 - Plot the locations of all pickup points with smopy, along with all locations
    Postcode = []
    Latitude = []
    Longitude = []
    for i in range(len(df_postcodes)):
        if districts[d] == df_postcodes['Postcode'][i][:-2]:
            Postcode.append(df_postcodes['Postcode'][i])
            Latitude.append(float(df_postcodes['Latitude'][i]))
            Longitude.append(float(df_postcodes['Longitude'][i]))

    map = smopy.Map(min(Latitude), min(Longitude),
                    max(Latitude), max(Longitude), z = 16)
    ax = map.show_mpl(figsize=(15,10))

    for i in range(len(Postcode)):
        x, y  = map.to_pixels(Latitude[i], Longitude[i])
        if Postcode[i] not in pic_loc:
            ax.plot(x, y, 'or', color='yellow', ms=5, mew=5)
        else:
            ax.plot(x, y, 'or', color='red', ms=8, mew=8)


#2.5 - Plot the number of pickup points in each district on a bar chart
#use a list n_of_pickup created before
plt.figure(figsize=(12,8))
plt.title('Number of pickup points in each district')
plt.ylabel('Districts')
plt.xlabel('Number of pickup points ')
plt.barh(districts, n_of_pickup)


###################
#STEP 3:Sensitivity
###################

#3.1 - Randomly pick one of the districts
random_district = random.choice(districts)

#Extract the needed data for the optimization model
locs_in_dist = [i for i in locations if i[:4] == random_district]
locs_in_dist.sort()
seconds = []
n_of_pickup_random = []
print('############## Random district is:', random_district, '##############')

n = [i for i in range(len(locs_in_dist))]
N = [(i,j) for i in n for j in n]


for p in range(len(locs_in_dist)):
    search_body_distances_random = {
        'size': 10000,
        'query': {
            'bool': {
                'must': [
                    {'term': {'src': locs_in_dist[p]}},
                    {'wildcard': {'dest': str(random_district + '*')}}
                ]
            }
        },
        'sort': [
            {'dest': {'order': 'asc'}}
        ]
    }

    result = es.search(index='distances', body=search_body_distances_random)
    #print(json.dumps(result, indent=4))
    data = result['hits']['hits']
    for k in range(len(data)):
        seconds.append(float(data[k]['_source']['seconds'])/60)
    seconds.insert(p+(len(data)+1)*p,0)


percent = []
for i in seconds:
    a = 0.4-(0.1*i)
    if a < 0:
        percent.append(0)
    else:
        percent.append(a)


W = dict(zip(N, percent))

C = 50*355

D = []
for i in locs_in_dist:
    a = int(df_locations[df_locations['key'] == i].index.values)
    D.append(df_locations.iloc[a][1])

DE = sum(D)

#3.2 - Conduct a sensitivity analysis and iteratively solve the network
# design problem considering differents % of deliveries to be self-pickups
P = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]

for r in range(len(P)):
    m = Model("Network_Model_Random")

    y = m.addVars(n, vtype=GRB.BINARY, name='y')
    x = m.addVars(N, vtype=GRB.BINARY, name='x')

    m.setObjective(quicksum(y[j] for j in n), GRB.MINIMIZE)

    #COSTRAINS
    m.addConstrs(quicksum(x[i,j] for j in n) <= 1 for i in n)
    m.addConstrs(quicksum(D[i]*x[i,j]*W[(i,j)] for i in n) <= C*y[j] for j in n)
    m.addConstr(quicksum(D[i]*x[i,j]*W[(i,j)] for i in n for j in n) >= P[r]*DE)
    m.addConstrs((x[i,j]) <= y[j] for i in n for j in n)
    m.addConstrs((x[i,j]) == 0 for i in n for j in n if W[(i,j)] == 0)

    m.optimize()

    solutions = [[v.varName, v.x] for v in m.getVars()]
    pic_loc_random = []
    for i in range(len(solutions)):
        if solutions[i][0][0] == 'y' and solutions[i][1] == 1:
            a = int(len(solutions[i][0])-1)
            index = int(solutions[i][0][2:a])
            pic_loc_random.append(locs_in_dist[index])

    n_of_pickup_random.append(len(pic_loc_random))

P = ['10%','15%','20%','25%','30%','35%','40%']

#3.4 - Plot the optimal number of pickup points for different self-pickup percentages on a bar chart
plt.figure(figsize=(12,8))
plt.title('Number of pickup points in a random district for different self-pickup percentages.')
plt.xlabel('Percentages')
plt.ylabel('Number of pickup points ')
plt.bar(P, n_of_pickup_random)

#endcode
