//
//  main.cpp
//  ObjectExtractor
//
//  Created by Henryk Blasinski on 2/15/17.
//  Copyright © 2017 Henryk Blasinski. All rights reserved.
//

#include <iostream>
#include <fstream>
#include <zlib.h>
#include "unzipper.h"


int main(int argc, const char * argv[])
{

    ziputils::unzipper zipFile;
    zipFile.open("/Users/hblasinski/Desktop/testFolder/raw/Archive.zip");
    auto filenames = zipFile.getFilenames();
    
    int fileID = 0;
    for ( auto it = filenames.begin(); it != filenames.end(); it++ )
    {
        std::cout << "Processing file: " << (*it).c_str() << " " << fileID << std::endl;
        zipFile.openEntry( (*it).c_str() );
        
        std::ofstream myFile;
        myFile.open("/Users/hblasinski/Desktop/testFolder/result.txt");
        
        zipFile >> myFile;
        fileID++;
    }
    
    // insert code here...
    std::cout << "Hello, World!\n";
    return 0;
}
