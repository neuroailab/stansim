import os
import sys
import glob
import shutil
import ctypes

import pyassimp
import pyassimp.postprocess



FORMAT_PREFERENCE = ['OBJ','3DS']

def get_model_path(sourcePath):

    for fmt in FORMAT_PREFERENCE:
        for case in ["lower","upper"]:
            if case=="lower":
                format = fmt.lower()
            else:
                format = fmt
    
            path = os.path.join(sourcePath,'*.%s' % format)
            files = glob.glob(path)
            if files:
                return files[0]





def correct_model(sourcePath, destPath):

    if not os.path.exists(destPath):
        os.makedirs(destPath)
    assetPath = os.path.join(destPath,'images')
    if not os.path.exists(assetPath):
        os.mkdir(assetPath)


    modelPath = get_model_path(sourcePath)

    model = pyassimp.load(modelPath)


    for index, material in enumerate(model.materials):
        
        print model.materials[index].properties
        
        for key,value in material.properties.iteritems():
            if key[0]=="diffuse":
                # fName = os.path.split(value)[1]
                # id = fName.rfind('\\')
                # originalFileName = fName[id+1:]
                
                # destFileName = originalFileName.replace(' ','_')
                # destFileName = destFileName.lower()
                
                # shutil.copyfile(os.path.join(sourcePath,originalFileName),os.path.join(assetPath,destFileName))
                
                # print originalFileName
                
                # newPath = u'./images/%s' % (destFileName)
                model.materials[index].properties[key] = [0.6,0.6,0.6]
        # for t in material.properties.keys():
# print t

    print

# print model.materials[index].properties
                    # for key in model.materials[index].properties:
# print key
# print tst
# model.materials[index].properties["file"] = value


    for index, material in enumerate(model.materials):
        for key,value in material.properties.iteritems():
            print '%s: %s' % (key,value)
    
    
    
    pyassimp.export(model,os.path.join(destPath,'model'),'obj')
    os.rename(os.path.join(destPath,'model'),os.path.join(destPath,'model.obj'))




if __name__ == '__main__':

    argv = sys.argv

    sourcePath = argv[1]
    destPath = argv[2]

    correct_model(sourcePath,destPath)
