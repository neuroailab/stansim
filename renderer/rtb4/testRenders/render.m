%%% RenderToolbox3 Copyright (c) 2012-2013 The RenderToolbox3 Team.
%%% About Us://github.com/DavidBrainard/RenderToolbox3/wiki/About-Us
%%% RenderToolbox3 is released under the MIT License.  See LICENSE.txt.

% This script uses RTB4 and PBRT to render all the obj files from a
% particular directory with a particular directory structure. Each model is
% rendered from 5 different viewpoints approximately equispaced on a
% sphere.
%

%% Scene description

% Henryk Blasinski
close all;
clear all;
clc;

ieInit;

modelDirectory = fullfile('/','home','hblasins','testOutputFolder');
destDirectory = fullfile('/','home','hblasins','testOutputRenderings');
if exist(destDirectory,'dir') == 0,
    mkdir(destDirectory);
end


%% Simulation parameters

cameraMode = {'pinhole'}; % {'lightfield'}; %{'pinhole','lightfield','50mm','depth'}; %{'lightfield','50mm','100mm','pinhole','depth'};
mode = {'radiance'};

% Positive z is up.
% Scene is about 200x200m, units are mm.
% However we should specify meters, as they are automatically converted to
% mm in remodellers.

pixelSamples = 128;

filmDist = 37.5;
filmDiag = 35;
microlensDim = [0, 0];

viewPoints = 1.2*sampleSphere(5);

%% Choose renderer options.
hints.imageWidth = 640;
hints.imageHeight = 480;
hints.recipeName = 'StansimModels'; % Name of the render
hints.renderer = 'PBRT'; % We're only using PBRT right now
hints.copyResources = 1;
hints.batchRenderStrategy = RtbAssimpStrategy(hints);

% Change the docker container
hints.batchRenderStrategy.renderer.pbrt.dockerImage = 'vistalab/pbrt-v2-spectral';
hints.batchRenderStrategy.remodelPerConditionAfterFunction = @MexximpRemodeller;
hints.batchRenderStrategy.converter.remodelAfterMappingsFunction = @PBRTRemodeller;
hints.batchRenderStrategy.converter.rewriteMeshData = false;

resourceFolder = rtbWorkingFolder('folderName','resources',...
                                  'rendererSpecific',false,...
                                  'hints',hints);


modelFormats = dir(modelDirectory);

for f=1:length(modelFormats)
    if modelFormats(f).name(1) == '.', continue; end
    
    models = dir(fullfile(modelDirectory,modelFormats(f).name));
    
    for m=1:length(models)
        if models(m).name(1) == '.', continue; end
        

        conditionsFile = fullfile(resourceFolder,sprintf('%s_to_%s_%s_Conditions.txt',modelFormats(f).name,'obj',models(m).name));


        %% Choose files to render
        parentSceneFile = fullfile(modelDirectory,modelFormats(f).name,models(m).name,'obj','model.obj');


        [scene, elements] = mexximpCleanImport(parentSceneFile,...
            'ignoreRootTransform',true,...
            'flipUVs',true,...
            'imagemagicImage','hblasins/imagemagic-docker',...
            'toReplace',{'jpg','png'},...
            'targetFormat','exr',...
            'makeLeftHanded',true,...
            'flipWindingOrder',true,...
            'workingFolder',resourceFolder);


        % Create a list of render conditions
        nConditions = length(cameraMode);
        names = {'imageName','cameraMode','mode','pixelSamples','filmDist','filmDiag','microlensDim','viewPoint'};

        values = cell(nConditions,numel(names));
        cntr = 1;
        for mo=1:length(mode)
            for mc=1:length(cameraMode)
                for vp=1:size(viewPoints,1);
                    
                    
                    fName = sprintf('%s_to_%s_%s_vp_%i_%s',modelFormats(f).name,'obj',models(m).name,vp,cameraMode{mc});
                    
                    switch mode{mo}
                        case {'depth','material','mesh'}
                            fName = sprintf('%s_%s',fName,mode{mo});
                    end
                    
                    values(cntr,1) = {fName};
                    values(cntr,2) = cameraMode(mc);
                    values(cntr,3) = mode(mo);
                    values(cntr,4) = num2cell(pixelSamples,1);
                    values(cntr,5) = num2cell(filmDist,1);
                    values(cntr,6) = num2cell(filmDiag,1);
                    values(cntr,7) = {mat2str(microlensDim)};
                    values(cntr,8) = {mat2str(viewPoints(vp,:))};
                    
                    
                    cntr = cntr+1;
                end
            end
        end


        rtbWriteConditionsFile(conditionsFile,names,values);

        % Generate files and render

        nativeSceneFiles = rtbMakeSceneFiles(scene, 'hints', hints,...
            'conditionsFile',conditionsFile);


        radianceDataFiles = rtbBatchRender(nativeSceneFiles, 'hints', hints);

        for i=1:length(radianceDataFiles)
            radianceData = load(radianceDataFiles{i});
            
            
            %% Create an oi
            oiParams.lensType = 'pinhole';
            oiParams.filmDistance = 10;
            oiParams.filmDiag = 20;
            
            label = sprintf('%s_to_%s_%s_vp_%i',modelFormats(f).name,'obj',models(m).name,i);
            
            oi = BuildOI(radianceData.multispectralImage, [], oiParams);
            oi = oiSet(oi,'name',label);
            
            
            ieAddObject(oi);
            oiWindow;
            
            img = oiGet(oi,'rgb image');
            % figure; imshow(img);
            imwrite(img,fullfile(destDirectory,sprintf('%s_to_%s_%s_vp_%i.png',modelFormats(f).name,'obj',models(m).name,i)));
        end

    end
end