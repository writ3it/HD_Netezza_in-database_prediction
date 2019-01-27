# -*- coding: utf-8 -*-
import csv
import random
import sys

if (len(sys.argv)<2):
    print("python generate.py <DATABASE_NAME> <optional:probe set size> <optional:train set size> <optional:test set size>");
    exit()
    
def get_default(i,dval):
    if (len(sys.argv)>=i+1):
        return int(sys.argv[i])
    else:
        return dval
    
databaseName = sys.argv[1]
probe_size = get_default(2,200)
train_size = get_default(3,2000)
test_size = get_default(4,1000)

print("DB=["+databaseName+"] probe_set_size="+str(probe_size)+" train_set_size="+str(train_size)+" test_set_size="+str(test_size))
    

def generate_data(datafile, count,tableName, useClass=True):
    for i in range(count):
        a = random.randint(0, 100)
        b = random.randint(0, 100)

        if (a >= 50):
            c = "a"
        else:
            c = "b"

        if (b >= 50):
            c = c + "a"
        else:
            c = c + "b"
        if useClass:
            datafile.write("INSERT INTO "+tableName+" (attrib_a, attrib_b, class) VALUES (" + str(a) + ", " + str(b) + ", '" + c + "');\n");
        else:
            datafile.write("INSERT INTO "+tableName+" (attrib_a, attrib_b) VALUES (" + str(a) + ", " + str(b) + ");\n");

with open('data.sql', 'wb') as datafile:
    #próbka
    datafile.write("SET CATALOG "+databaseName+";\n");
    if(probe_size>0):
        datafile.write("\n"+
                       "CREATE TABlE example_probe ( \n" +
                       "attrib_a float, \n" +
                       "attrib_b float, \n" +
                       "class CHAR(2) \n" +
                       ") DISTRIBUTE ON RANDOM; \n\n");

        generate_data(datafile, probe_size, "example_probe")
    if(train_size>0):
        datafile.write("\n\n" +
                       "CREATE TABlE example_train ( \n" +
                       "attrib_a float, \n" +
                       "attrib_b float, \n" +
                       "class CHAR(2) \n" +
                       ") DISTRIBUTE ON RANDOM; \n\n");
        generate_data(datafile, train_size, "example_train")

    if (test_size>0):
        datafile.write("\n\n" +
                       "CREATE TABlE example_test ( \n" +
                       "attrib_a float, \n" +
                       "attrib_b float \n" +
                       ") DISTRIBUTE ON RANDOM; \n\n");
        generate_data(datafile, test_size, "example_test",useClass=False)
                   

    
   
        
