//
//  main.cpp
//  ModelAnalyzer
//
//  Created by Henryk Blasinski on 1/13/17.
//  Copyright © 2017 Henryk Blasinski. All rights reserved.
//

#include <iostream>
#include <vector>
#include <set>
#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>
#include <assimp/Importer.hpp>      // C++ importer interface
#include <assimp/scene.h>           // Output data structure
#include <assimp/postprocess.h>     // Post processing flags
#include <assimp/Exporter.hpp>
#include "unzipper.h"

// Only the formats that are 'fully' suppored by ASSIMP
std::set<std::string> assimpInputFormats = {".fbx",".dae",".glb",".blend",".3ds",".ase",".obj",".ifc",".zgl",".xgl",\
                                            ".ply",".lwo",".lws",".lxo",".stl",".x","ac",".ms3d",".bvh",".xml",".irrmesh",\
                                            ".mdl",".md2",".md3",".pk3",".md5",".b3d",".q3d",".q3s",".nff",".off",".raw",".ter",".hmp", ".ndo"};

std::map<std::string,int> uniqueFormatCount;
std::map<std::string,int> globalFormatCount;
std::map<std::string,int> totalTexturesCount;
std::map<std::string,int> missingTexturesCount;
std::map<std::string,int> assimpImportErrors;

std::set<std::string> formatsToGenerate = {".obj",".fbx",".3ds",".dae",".stl"};


boost::filesystem::path findFile(const boost::filesystem::path& dir_path, const boost::filesystem::path& file_name) {
    const boost::filesystem::recursive_directory_iterator end;
    const auto it = std::find_if(boost::filesystem::recursive_directory_iterator(dir_path), end,
                            [&file_name](const boost::filesystem::directory_entry& e) {
                                return e.path().filename() == file_name;
                            });
    boost::filesystem::path result;
    if (it == end)
    {
        return result;
    } else
    {
        return it->path();
    }
}

std::set<std::string> checkModelTypes(boost::filesystem::path dirPath)
{
    //std::cout << "Model : " << dirPath << std::endl;
    
    std::set<std::string> modelFormats;
    
    std::vector<boost::filesystem::path> filePaths;
    copy(boost::filesystem::directory_iterator(dirPath),boost::filesystem::directory_iterator(),back_inserter(filePaths));
    for (std::vector<boost::filesystem::path>::const_iterator it = filePaths.begin(); it != filePaths.end(); ++it)
    {
        // if a file is in supported assimp formats, add it to model formats
        if (assimpInputFormats.find(boost::algorithm::to_lower_copy(it->extension().string())) != assimpInputFormats.end())
        {
            modelFormats.insert(boost::algorithm::to_lower_copy(it->extension().string()));
        }
    }
    
    std::cout << "    Number of formats: " << modelFormats.size() << std::endl;

    if (modelFormats.size() == 1)
    {
        uniqueFormatCount[*(modelFormats.begin())]++;
    }
    
    for (std::set<std::string>::iterator it = modelFormats.begin(); it != modelFormats.end(); ++it)
    {
        globalFormatCount[*it]++;
    }
    
    return modelFormats;
}


bool fixTextures(const aiScene* scene, boost::filesystem::path assetDirectory, boost::filesystem::path modelDirectory, std::string sourceFormat )
{
    // Now iterate over all texture images and copy those into the assetDirectory
    // Remember to change relative paths
    for (int i=0; i<scene->mNumMaterials; i++)
    {
        aiMaterial* mat = scene->mMaterials[i];
        
        
        
        // Check all possible texture types
        aiString s;
        if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_DIFFUSE(0),s)) {
            totalTexturesCount[sourceFormat]++;
            std::cout << "        map_Kd: " << s.data;
            boost::filesystem::path assetPath(s.data);
            boost::filesystem::path assetName = assetPath.filename();
            
            // Find file recursively
            boost::filesystem::path oldPath = findFile(assetDirectory,assetName);
            
            boost::filesystem::path newDirPath(modelDirectory/ "obj" / "images");
            boost::filesystem::path newPath(newDirPath / assetName);
            boost::filesystem::path newRelativePath("./images" /assetName);
            
            if (!boost::filesystem::exists(newPath) && boost::filesystem::exists(oldPath))
            {
                boost::filesystem::create_directories(newDirPath);
                boost::filesystem::copy_file(oldPath, newPath);
                
            } else
            {
                missingTexturesCount[sourceFormat]++;
                std::cout << " (MISSING)" << std::endl;
            }
            aiString str(newRelativePath.c_str());
            mat->AddProperty(&str,AI_MATKEY_TEXTURE_DIFFUSE(0));
            
        }
        if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_AMBIENT(0),s)) {
            totalTexturesCount[sourceFormat]++;
            std::cout << "        map_Ka: " << s.data;
            boost::filesystem::path assetPath(s.data);
            boost::filesystem::path assetName = assetPath.filename();
            
            // Find file recursively
            boost::filesystem::path oldPath = findFile(assetDirectory,assetName);
            
            boost::filesystem::path newDirPath(modelDirectory/ "obj" / "images");
            boost::filesystem::path newPath(newDirPath / assetName);
            boost::filesystem::path newRelativePath("./images" /assetName);
            
            if (!boost::filesystem::exists(newPath) && boost::filesystem::exists(oldPath))
            {
                boost::filesystem::create_directories(newDirPath);
                boost::filesystem::copy_file(oldPath, newPath);
            }  else
            {
                missingTexturesCount[sourceFormat]++;
                std::cout << " (MISSING)" << std::endl;
            }
            aiString str(newRelativePath.c_str());
            mat->AddProperty(&str,AI_MATKEY_TEXTURE_AMBIENT(0));
        }
        if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_SPECULAR(0),s)) {
            totalTexturesCount[sourceFormat]++;
            std::cout << "        map_Ks: " << s.data;
            boost::filesystem::path assetPath(s.data);
            boost::filesystem::path assetName = assetPath.filename();
            
            // Find file recursively
            boost::filesystem::path oldPath = findFile(assetDirectory,assetName);
            
            boost::filesystem::path newDirPath(modelDirectory/ "obj" / "images");
            boost::filesystem::path newPath(newDirPath / assetName);
            boost::filesystem::path newRelativePath("./images" /assetName);
            
            if (!boost::filesystem::exists(newPath) && boost::filesystem::exists(oldPath))
            {
                boost::filesystem::create_directories(newDirPath);
                boost::filesystem::copy_file(oldPath, newPath);
                std::cout << " (file found)" << std::endl;
            }  else
            {
                missingTexturesCount[sourceFormat]++;
                std::cout << " (MISSING)" << std::endl;
            }
            aiString str(newRelativePath.c_str());
            mat->AddProperty(&str,AI_MATKEY_TEXTURE_SPECULAR(0));
            
        }
        if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_SHININESS(0),s)) {
            totalTexturesCount[sourceFormat]++;
            std::cout << "        map_Ns: " << s.data;
            boost::filesystem::path assetPath(s.data);
            boost::filesystem::path assetName = assetPath.filename();
            
            // Find file recursively
            boost::filesystem::path oldPath = findFile(assetDirectory,assetName);
            
            boost::filesystem::path newDirPath(modelDirectory/ "obj" / "images");
            boost::filesystem::path newPath(newDirPath / assetName);
            boost::filesystem::path newRelativePath("./images" /assetName);
            
            if (!boost::filesystem::exists(newPath) && boost::filesystem::exists(oldPath))
            {
                boost::filesystem::create_directories(newDirPath);
                boost::filesystem::copy_file(oldPath, newPath);
            } else
            {
                missingTexturesCount[sourceFormat]++;
                std::cout << " (MISSING)" << std::endl;
            }
            aiString str(newRelativePath.c_str());
            mat->AddProperty(&str,AI_MATKEY_TEXTURE_SHININESS(0));
            
        }
        if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_OPACITY(0),s)) {
            totalTexturesCount[sourceFormat]++;
            std::cout << "        map_d: " << s.data;
            boost::filesystem::path assetPath(s.data);
            boost::filesystem::path assetName = assetPath.filename();
            
            // Find file recursively
            boost::filesystem::path oldPath = findFile(assetDirectory,assetName);
            
            boost::filesystem::path newDirPath(modelDirectory/ "obj" / "images");
            boost::filesystem::path newPath(newDirPath / assetName);
            boost::filesystem::path newRelativePath("./images" /assetName);
            
            if (!boost::filesystem::exists(newPath) && boost::filesystem::exists(oldPath))
            {
                boost::filesystem::create_directories(newDirPath);
                boost::filesystem::copy_file(oldPath, newPath);
            } else
            {
                missingTexturesCount[sourceFormat]++;
                std::cout << " (MISSING)" << std::endl;
            }
            aiString str(newRelativePath.c_str());
            mat->AddProperty(&str,AI_MATKEY_TEXTURE_OPACITY(0));
            
            
        }
        if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_HEIGHT(0),s)) {
            totalTexturesCount[sourceFormat]++;
            std::cout << "        Height map: " << s.data;
            boost::filesystem::path assetPath(s.data);
            boost::filesystem::path assetName = assetPath.filename();
            
            // Find file recursively
            boost::filesystem::path oldPath = findFile(assetDirectory,assetName);
            
            boost::filesystem::path newDirPath(modelDirectory/ "obj" / "images");
            boost::filesystem::path newPath(newDirPath / assetName);
            boost::filesystem::path newRelativePath("./images" /assetName);
            
            if (!boost::filesystem::exists(newPath) && boost::filesystem::exists(oldPath))
            {
                boost::filesystem::create_directories(newDirPath);
                boost::filesystem::copy_file(oldPath, newPath);
            } else
            {
                missingTexturesCount[sourceFormat]++;
                std::cout << " (MISSING)" << std::endl;
            }
            aiString str(newRelativePath.c_str());
            mat->AddProperty(&str,AI_MATKEY_TEXTURE_HEIGHT(0));
        }
        if(AI_SUCCESS == mat->Get(AI_MATKEY_TEXTURE_NORMALS(0),s)) {
            totalTexturesCount[sourceFormat]++;
            std::cout << "        Normals map: " << s.data;
            boost::filesystem::path assetPath(s.data);
            boost::filesystem::path assetName = assetPath.filename();
            
            // Find file recursively
            boost::filesystem::path oldPath = findFile(assetDirectory,assetName);
            
            boost::filesystem::path newDirPath(modelDirectory/ "obj" / "images");
            boost::filesystem::path newPath(newDirPath / assetName);
            boost::filesystem::path newRelativePath("./images" /assetName);
            
            if (!boost::filesystem::exists(newPath) && boost::filesystem::exists(oldPath))
            {
                boost::filesystem::create_directories(newDirPath);
                boost::filesystem::copy_file(oldPath, newPath);
            }  else
            {
                missingTexturesCount[sourceFormat]++;
                std::cout << " (MISSING)" << std::endl;
            }
            aiString str(newRelativePath.c_str());
            mat->AddProperty(&str,AI_MATKEY_TEXTURE_NORMALS(0));
        }
        
    }
    return true;
}





void writeModelToObj(boost::filesystem::path dirPath, boost::filesystem::path modelDirectory, std::string sourceFormat = ".obj")
{
    Assimp::Importer importer;
    Assimp::Exporter exporter;
    
     std::vector<boost::filesystem::path> filePaths;
     copy(boost::filesystem::directory_iterator(dirPath),boost::filesystem::directory_iterator(),back_inserter(filePaths));
    
     for (std::vector<boost::filesystem::path>::const_iterator it = filePaths.begin(); it != filePaths.end(); ++it)
     {
         // If unsupported file format, continue
         if (assimpInputFormats.find(boost::algorithm::to_lower_copy(it->extension().string())) == assimpInputFormats.end()) continue;
         
         // Not a file format we'd like to read from
         if (sourceFormat != it->extension().string()) continue;
     
         std::cout << "    Converting object file: " << it->c_str() <<std::endl;
     
     
         const aiScene* scene = importer.ReadFile(it->c_str(),
                                                  aiProcess_CalcTangentSpace       |
                                                  aiProcess_Triangulate            |
                                                  aiProcess_JoinIdenticalVertices  |
                                                  aiProcess_SortByPType);
     
     
         if (scene == NULL)
         {
             assimpImportErrors[sourceFormat]++;
             std::cout << "    ASSIMP import FAILURE (" << sourceFormat << ")" << std::endl;
             break;
         }
         
         if (fixTextures(scene,dirPath,modelDirectory,sourceFormat) == true)
         {
         
             boost::filesystem::path modelTargetPath( modelDirectory / "obj");
             boost::filesystem::create_directories(modelTargetPath);
     
             boost::filesystem::path modelTargetFileName(modelTargetPath / "model");
             aiReturn retVal = exporter.Export(scene, "obj", modelTargetFileName.c_str());
     
             // IF a conversion was a success rename files.
             if (retVal == AI_SUCCESS)
             {
                 boost::filesystem::path renamedModel(modelTargetFileName);
                 renamedModel += ".obj";
                 boost::filesystem::rename(modelTargetFileName, renamedModel);
             } else
             {
                 std::cout << "    ASSIMP model conversion FAILURE" << std::endl;
             }
         } else
         {
             std::cout << "Missing textures" <<std::endl;
         }
     
         break;
     
     }
}


int main(int argc, const char * argv[]) {
    // insert code here...
    
    boost::filesystem::path outputCollectionDirectory = "/Users/hblasinski/Desktop/SelectedCGTraderModels";
    boost::filesystem::path collectionDirectory(argv[1]);
    std::vector<boost::filesystem::path> modelPaths;
    copy(boost::filesystem::directory_iterator(collectionDirectory),boost::filesystem::directory_iterator(),back_inserter(modelPaths));
    
    int cntr = 1;
    unsigned long totalCount = modelPaths.size();
    
    for (std::vector<boost::filesystem::path>::const_iterator model = modelPaths.begin(); model != modelPaths.end(); ++model)
    {
        if (boost::filesystem::is_directory(*model) == false) continue;
        
        std::cout << "Processing model (" << cntr << "/" << totalCount << "): "  << model->c_str() << std::endl;
        
        std::string modelHash = model->filename().string();
        std::cout << "    Model hash: " << modelHash <<std::endl;
        
        boost::filesystem::path modelDirectory(model->c_str());
        boost::filesystem::path rawDataDirectory(modelDirectory / "raw");
        
        boost::filesystem::path tempDataDirectory(modelDirectory / "tmp");
        
        if (boost::filesystem::is_directory(tempDataDirectory))
        {
            // Remove the tmp folder if it exists
            boost::filesystem::remove_all(tempDataDirectory);
        }
        boost::filesystem::create_directory(tempDataDirectory);
        
        
        
        // List all the files in raw directory, and unzip every single one of them into
        // tmp folder. If a file is not an archive, simply copy it to the tmp folder.
        // This way moving forward we only are working from stuff inside the tmp folder.
        
        std::vector<boost::filesystem::path> filePaths;
        copy(boost::filesystem::directory_iterator(rawDataDirectory),boost::filesystem::directory_iterator(),back_inserter(filePaths));
        for (std::vector<boost::filesystem::path>::const_iterator it = filePaths.begin(); it != filePaths.end(); ++it)
        {
            if ((it->extension() == ".zip") || (it->extension() == ".ZIP"))
            {
                std::cout << "    Unzipping file: " << it->c_str() << std::endl;
                try {
                    ziputils::unzipper fileUnzipper;
                    fileUnzipper.open(it->c_str());
                    fileUnzipper.extractToDirectory(tempDataDirectory.c_str());
                    fileUnzipper.close();
                } catch (...)
                {
                    std::cout << "    Unzipping error:" << std::endl;
                }
            } else
            {
                boost::filesystem::path destinationFile(modelDirectory / "tmp" / it->filename());
                // We can't overwrite files.
                if (boost::filesystem::exists(destinationFile) == false)
                {
                    boost::filesystem::copy_file(*it,destinationFile);
                }
            }
        }
        
        
        // Now we can try to read in a model from the tmp folder
        // fix it and save it to a model subfolder
        std::set<std::string> modelTypes = checkModelTypes(tempDataDirectory);
        
        
        int minFormatCount = INT_MAX;
        for (std::set<std::string>::iterator it = formatsToGenerate.begin(); it != formatsToGenerate.end(); ++it)
        {
            minFormatCount = minFormatCount > globalFormatCount[*it] ? globalFormatCount[*it] : minFormatCount;
        }
        
        bool generateModel = (minFormatCount < 20);
        
        if (generateModel)
        {
            for (std::set<std::string>::iterator it = formatsToGenerate.begin(); it != formatsToGenerate.end(); ++it)
            {
            
                boost::filesystem::path outputPath(outputCollectionDirectory / it->substr(1) / modelHash);
                writeModelToObj(tempDataDirectory, outputPath, *it);
            }
        }
        
        /*
        if ((modelTypes.size() == 1) && (uniqueFormatCount[*modelTypes.begin()] <= 10) && (formatsToGenerate.find(*modelTypes.begin()) != formatsToGenerate.end()))
        {
            boost::filesystem::path extension(modelTypes.begin()->substr(1));
            boost::filesystem::path id(std::to_string(uniqueFormatCount[*modelTypes.begin()]));
            boost::filesystem::path outputPath(outputCollectionDirectory / extension / id);
            writeModelToObj(tempDataDirectory, outputPath);
        }*/
        
        
        
        // Remove temporary directory to save space
        // boost::filesystem::remove_all(tempDataDirectory);
        cntr++;
    }
    
    std::cout << "======= UNIQUE MODELS =======" << std::endl;
    for (std::map<std::string,int>::iterator it = uniqueFormatCount.begin(); it != uniqueFormatCount.end(); ++it)
    {
        std::cout << it->first << " : " << it->second << " models" << std::endl;
    }
    
    std::cout << "======= GLOBAL MODELS =======" << std::endl;
    for (std::map<std::string,int>::iterator it = globalFormatCount.begin(); it != globalFormatCount.end(); ++it)
    {
        std::cout << it->first << " : " << it->second << " models" << std::endl;
    }
    
    std::cout << "======= TOTAL TEXTURES =======" << std::endl;
    for (std::map<std::string,int>::iterator it = totalTexturesCount.begin(); it != totalTexturesCount.end(); ++it)
    {
        std::cout << it->first << " : " << it->second << " textures" << std::endl;
    }
    
    std::cout << "======= MISSING TEXTURES =======" << std::endl;
    for (std::map<std::string,int>::iterator it = missingTexturesCount.begin(); it != missingTexturesCount.end(); ++it)
    {
        std::cout << it->first << " : " << it->second << " textures" << std::endl;
    }
    
    std::cout << "======= IMPORT ERRORS =======" << std::endl;
    for (std::map<std::string,int>::iterator it = assimpImportErrors.begin(); it != assimpImportErrors.end(); ++it)
    {
        std::cout << it->first << " : " << it->second << " models" << std::endl;
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
                
     
                
                boost::filesystem::path modelPath( targetDirectory / "model");
                exporter.Export(scene, "obj", modelPath.c_str());
                
                
                
                

            }
        }
        
        
        
        
    }
    
    */
    
    return 0;
}
