import os
import subprocess
import hashlib
import shutil
import json



PATH = '/Volumes/MyPassport/CGTrader'

# There is a separate function to consolidate each database,
# beacuse each one is different ...


def read_metadata(path):

    models = os.listdir(path)

    jsonEntries = [];

    for model in models:
        
        if os.path.isdir(os.path.join(PATH,model)):
        
            jsonFile = os.path.join(PATH,model,'%s.json' % model)
        
            print jsonFile
        
            with open(jsonFile) as data_file:
                data = json.load(data_file)
                jsonEntries.append(data)
        

    with open('CGTrader_subset.json', 'w') as outfile:
        json.dump(jsonEntries, outfile)



    with open('CGTrader_subset.json','r') as outfile:
        data = json.load(outfile)
        print data[2]


if __name__ == '__main__':
    read_metadata(PATH)
