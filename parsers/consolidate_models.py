import os
import subprocess
import hashlib
import shutil
import json

# Local computer
# CGTRADER_PATH = '/Volumes/Stansim/stansim_models/raw_models/download_cgtrader'
# DIGIMATION_PATH = '/Volumes/Stansim/stansim_models/raw_models/digimation'
# ARCHIBASE_PATH = '/Volumes/Stansim/stansim_models/raw_models/download_archibase'
# OPEN3DMODEL_PATH = '/Volumes/Stansim/stansim_models/raw_models/download_open3dmodel'

# DESTINATION_PATH = '/Volumes/Stansim/stansim_models/consolidated_models'


# Kanefsky
CGTRADER_PATH = '/mnt/falas_stansim/stansim_models/raw_models/download_cgtrader'
DIGIMATION_PATH = '/mnt/falas_stansim/stansim_models/raw_models/digimation'
ARCHIBASE_PATH = '/mnt/falas_stansim/stansim_models/raw_models/download_archibase'
OPEN3DMODEL_PATH = '/mnt/falas_stansim/stansim_models/raw_models/download_open3dmodel'

DESTINATION_PATH = '/mnt/falas_stansim/stansim_models/consolidated_models'

# There is a separate function to consolidate each database,
# beacuse each one is different ...


def read_model_json(file):
    data = None
    with open(file) as data_file:
        data = json.load(data_file)
    return data

def write_model_json(file,data):
    with open(file,'w') as data_file:
        json.dump(data,data_file)

def consolidate_open3dmodel():

    formats = os.listdir(OPEN3DMODEL_PATH)

    for format in formats:
        formatDir = os.path.join(OPEN3DMODEL_PATH,format)
        files = os.listdir(formatDir)

        for file in files:

            filePath = os.path.join(OPEN3DMODEL_PATH,format,file)
            hash = get_hash(filePath)

            print "%s : %s" % (file,hash)

            destPath = os.path.join(DESTINATION_PATH,hash,'raw')
            if not os.path.exists(destPath):
                print destPath
                os.makedirs(destPath,0777)

            shutil.copy(filePath,os.path.join(destPath,file))

            json = dict()
            json["source_website"] = "open3dmodel"

            jsonFile = os.path.join(DESTINATION_PATH,hash,"%s.json" % hash)
            write_model_json(jsonFile,json)




def consolidate_cgtrader():
    models = os.listdir(CGTRADER_PATH)
    
    for model in models:
        fullPath = os.path.join(CGTRADER_PATH,model)
        if os.path.isfile(fullPath):
            continue

        hash = get_hash(fullPath)
        print "%s : %s" % (model,hash)
        
        destPath = os.path.join(DESTINATION_PATH,hash,'raw')
        
        
        if not os.path.exists(destPath):
            os.makedirs(destPath)
        else:
            shutil.rmtree(destPath)
            
            # print("Hasing function produced a hash that exists in the output directory, exiting")
            # exit()
    
        json = None
        files = os.listdir(fullPath)
        
        if len(files) <= 1:
            # Only a single file in the directory, presumably the .json
            # Ignore this model.
            continue
                
        os.makedirs(destPath)
        
        for file in files:
            if file.endswith('.json'):
                jsonFile = os.path.join(CGTRADER_PATH,model,file)
                json = read_model_json(jsonFile)
            else:
                sourceFile = os.path.join(CGTRADER_PATH,model,file)
                destFile = os.path.join(DESTINATION_PATH,hash,'raw',file)
                shutil.copy(sourceFile,destFile)
            
        if json == None:
            json = dict()

        json["source_website"] = "cgtrader"
        jsonFile = os.path.join(DESTINATION_PATH,hash,"%s.json" % hash)
        write_model_json(jsonFile,json)






def consolidate_archibase():
    
    sessions = os.listdir(ARCHIBASE_PATH)
    
    for session in sessions:
    
        print "Processing session %s " % session
        models = os.listdir(os.path.join(ARCHIBASE_PATH,session))
    
        for model in models:
            
            # Model files are always zipped
            if model.endswith(".zip"):
                
                sourceFile = os.path.join(ARCHIBASE_PATH,session,model)
                hash = get_hash(sourceFile)
                print "%s : %s" % (model,hash)


                fullPathElements = sourceFile.split('.')

                jsonFile = fullPathElements[0] + '.json'
                htmlFile = fullPathElements[0] + '_data.html'
                
                json = read_model_json(jsonFile)
                with open(htmlFile) as file:
                    htmlData = file.read()
                
                json["source_website_html"] = htmlData
                json["source_website"] = "archibase"
                
                destPath = os.path.join(DESTINATION_PATH,hash,'raw')
                destFile = os.path.join(destPath,model)
                destJson = os.path.join(DESTINATION_PATH,hash,'%s.json' % hash)
                
                # print sourceFile
                # print jsonFile
                # print htmlFile
                
                if not os.path.exists(destPath):
                    os.makedirs(destPath)
                    shutil.copy(sourceFile,destFile)
                    write_model_json(destJson,json)
                
                else:
                    print("Hasing function produced a hash that exists in the output directory, exiting")
                    exit()


def consolidate_digimation():

    models = os.listdir(DIGIMATION_PATH)

    for model in models:
        fullPath = os.path.join(DIGIMATION_PATH,model)
        if os.path.isfile(fullPath):
            continue

        hash = get_hash(fullPath)
        print "%s : %s" % (model,hash)

        destPath = os.path.join(DESTINATION_PATH,hash,'raw')
        if not os.path.exists(destPath):
            os.makedirs(destPath)
        else:
            print('Found a directory with a given has, skipping')
            continue
            # print("Hasing function produced a hash that exists in the output directory, exiting")
            # exit()

        json = None
        files = os.listdir(fullPath)
        for file in files:
            if file.endswith('.json'):
                jsonFile = os.path.join(DIGIMATION_PATH,model,file)
                json = read_model_json(jsonFile)
            else:
                sourceFile = os.path.join(DIGIMATION_PATH,model,file)
                destFile = os.path.join(DESTINATION_PATH,hash,'raw',file)
                shutil.copy(sourceFile,destFile)

        if json == None:
            json = dict()
        
        json["source_website"] = "digimation"
        jsonFile = os.path.join(DESTINATION_PATH,hash,"%s.json" % hash)
        write_model_json(jsonFile,json)





## Dan's hashing function
def get_hash(dirn):
    command = "find '%s' -type f -print0 | sort -z | xargs -0 sha1sum" % dirn
    proc = subprocess.Popen(command,stdout=subprocess.PIPE,shell=True)
    (out, err) = proc.communicate()
    if err is not None:
        print("Error getting hash for %s" % dirn)
    else:
        r = out.strip().split('\n')
        strs = []
        for _r in r:
            sha1 = _r.split(' ')[0]
            fn = os.path.relpath(' '.join(_r.split(' ')[1:]).strip(), start=dirn)
            strs.append(sha1 + '  ' + fn)
    strv = ''.join(strs)
    return hashlib.sha1(strv).hexdigest()




if __name__ == '__main__':
    # consolidate_open3dmodel()
    # consolidate_digimation()
    # consolidate_archibase()
    consolidate_cgtrader()
