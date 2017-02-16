//
//  main.cpp
//  ModelAnalyzer
//
//  Created by Henryk Blasinski on 1/13/17.
//  Copyright © 2017 Henryk Blasinski. All rights reserved.
//

#include <iostream>
#include <vector>
#include <boost/filesystem.hpp>
#include <assimp/Importer.hpp>      // C++ importer interface
#include <assimp/scene.h>           // Output data structure
#include <assimp/postprocess.h>     // Post processing flags
#include <assimp/Exporter.hpp>
#include "unzipper.h"

int main(int argc, const char * argv[]) {
    // insert code here...
    
    boost::filesystem::path collectionDirectory(argv[1]);
    std::vector<boost::filesystem::path> modelPaths;
    copy(boost::filesystem::directory_iterator(collectionDirectory),boost::filesystem::directory_iterator(),back_inserter(modelPaths));
    
    for (std::vector<boost::filesystem::path>::const_iterator model = modelPaths.begin(); model != modelPaths.end(); ++model)
    {
        if (boost::filesystem::is_directory(*model) == false) continue;
        
        std::cout << "Processing model: " << model->c_str() << std::endl;
        
        boost::filesystem::path modelDirectory(model->c_str());
        boost::filesystem::path rawDataDirectory(modelDirectory / "raw");
        
        boost::filesystem::path tempDataDirectory(modelDirectory / "tmp");
        boost::filesystem::create_directory(tempDataDirectory);
        
        
        // List all the files in raw directory, and unzip every single one of them into
        // tmp
        
        std::vector<boost::filesystem::path> filePaths;
        copy(boost::filesystem::directory_iterator(rawDataDirectory),boost::filesystem::directory_iterator(),back_inserter(filePaths));
        for (std::vector<boost::filesystem::path>::const_iterator it = filePaths.begin(); it != filePaths.end(); ++it)
        {
            if ((it->extension() == ".zip") || (it->extension() == ".ZIP"))
            {
                std::cout << "Unzipping file: " << it->c_str() << std::endl;
                ziputils::unzipper fileUnzipper;
                fileUnzipper.open(it->c_str());
                fileUnzipper.extractToDirectory(tempDataDirectory.c_str());
                fileUnzipper.close();
            }
        }
        
    }
    
    
    
    
    
    
    /*
    boost::filesystem::path modelDirectory(argv[1]);
    
    boost::filesystem::path targetDirectory(argv[2]);
    boost::filesystem::create_directory(targetDirectory);
    
    boost::filesystem::path assetDirectory(targetDirectory / "images");
    boost::filesystem::create_directory(assetDirectory);
    
    
    Assimp::Importer importer;
    Assimp::Exporter exporter;
    
    
    if (boost::filesystem::is_directory(modelDirectory))
    {
        std::vector<boost::filesystem::path> filePaths;
        copy(boost::filesystem::directory_iterator(modelDirectory),boost::filesystem::directory_iterator(),back_inserter(filePaths));
        
        for (std::vector<boost::filesystem::path>::const_iterator it = filePaths.begin(); it != filePaths.end(); ++it)
        {
            
            if ((it->extension() == ".3DS") || (it->extension() == ".3ds"))
            {
                std::cout << *it << " " << it->extension() << '\n';
                
                const aiScene* scene = importer.ReadFile(it->c_str(),
                                                         aiProcess_CalcTangentSpace       |
                                                         aiProcess_Triangulate            |
                                                         aiProcess_JoinIdenticalVertices  |
                                                         aiProcess_SortByPType);
                
                // Now iterate over all texture images and copy those into the assetDirectory
                // Remember to change relative paths
                for (int i=0; i<scene->mNumMaterials; i++)
                {
                    aiMaterial* mat = scene->mMaterials[i];
                    
                    
                    
                    // Check all possible texture types
                    aiString s;
                    if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_DIFFUSE(0),s)) {
                        std::cout << "map_Kd " << s.data << std::endl;
                        boost::filesystem::path assetName(s.data);
                        boost::filesystem::path newPath(assetDirectory / assetName);
                        boost::filesystem::path newRelativePath("./images" /assetName);

                        if (!boost::filesystem::exists(newPath))
                        {
                            boost::filesystem::copy_file(boost::filesystem::path(modelDirectory /assetName), newPath);
                        }
                        aiString str(newRelativePath.c_str());
                        mat->AddProperty(&str,AI_MATKEY_TEXTURE_DIFFUSE(0));

                    }
                    if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_AMBIENT(0),s)) {
                        std::cout << "map_Ka " << s.data << std::endl;
                        boost::filesystem::path assetName(s.data);
                        boost::filesystem::path newPath(assetDirectory / assetName);
                        boost::filesystem::path newRelativePath("./images" /assetName);
                        
                        if (!boost::filesystem::exists(newPath))
                        {
                            boost::filesystem::copy_file(boost::filesystem::path(modelDirectory /assetName), newPath);
                        }
                        aiString str(newRelativePath.c_str());
                        mat->AddProperty(&str,AI_MATKEY_TEXTURE_AMBIENT(0));
                    }
                    if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_SPECULAR(0),s)) {
                        std::cout << "map_Ks " << s.data << std::endl;
                        boost::filesystem::path assetName(s.data);
                        boost::filesystem::path newPath(assetDirectory / assetName);
                        boost::filesystem::path newRelativePath("./images" /assetName);

                        if (!boost::filesystem::exists(newPath))
                        {
                            boost::filesystem::copy_file(boost::filesystem::path(modelDirectory /assetName), newPath);
                        }
                        aiString str(newRelativePath.c_str());
                        mat->AddProperty(&str,AI_MATKEY_TEXTURE_SPECULAR(0));
                    
                    }
                    if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_SHININESS(0),s)) {
                        std::cout << "map_Ns " << s.data << std::endl;
                        boost::filesystem::path assetName(s.data);
                        boost::filesystem::path newPath(assetDirectory / assetName);
                        boost::filesystem::path newRelativePath("./images" /assetName);

                        if (!boost::filesystem::exists(newPath))
                        {
                            boost::filesystem::copy_file(boost::filesystem::path(modelDirectory /assetName), newPath);
                        }
                        aiString str(newRelativePath.c_str());
                        mat->AddProperty(&str,AI_MATKEY_TEXTURE_SHININESS(0));
                    
                    }
                    if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_OPACITY(0),s)) {
                        std::cout << "map_d " << s.data << std::endl;
                        boost::filesystem::path assetName(s.data);
                        boost::filesystem::path newPath(assetDirectory / assetName);
                        boost::filesystem::path newRelativePath("./images" /assetName);

                        if (!boost::filesystem::exists(newPath))
                        {
                            boost::filesystem::copy_file(boost::filesystem::path(modelDirectory /assetName), newPath);
                        }
                        aiString str(newRelativePath.c_str());
                        mat->AddProperty(&str,AI_MATKEY_TEXTURE_OPACITY(0));
                    
                    
                    }
                    if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_HEIGHT(0),s)) {
                        std::cout << s.data << std::endl;
                        boost::filesystem::path assetName(s.data);
                        boost::filesystem::path newPath(assetDirectory / assetName);
                        boost::filesystem::path newRelativePath("./images" /assetName);

                        if (!boost::filesystem::exists(newPath))
                        {
                            boost::filesystem::copy_file(boost::filesystem::path(modelDirectory /assetName), newPath);
                        }
                        aiString str(newRelativePath.c_str());
                        mat->AddProperty(&str,AI_MATKEY_TEXTURE_HEIGHT(0));
                    }
                    if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_NORMALS(0),s)) {
                        std::cout << s.data << std::endl;
                        boost::filesystem::path assetName(s.data);
                        boost::filesystem::path newPath(assetDirectory / assetName);
                        boost::filesystem::path newRelativePath("./images" /assetName);

                        if (!boost::filesystem::exists(newPath))
                        {
                            boost::filesystem::copy_file(boost::filesystem::path(modelDirectory /assetName), newPath);
                        }
                        aiString str(newRelativePath.c_str());
                        mat->AddProperty(&str,AI_MATKEY_TEXTURE_NORMALS(0));
                    }

                    
                    
                    
                }
                
                
                boost::filesystem::path modelPath( targetDirectory / "model");
                exporter.Export(scene, "obj", modelPath.c_str());
                
                
                
                

            }
        }
        
        
        
        
    }
    
    */
    
    return 0;
}
