function [ nativeScene ] = PBRTRemodeller( parentScene, nativeScene, mappings, names, conditionValues, conditionNumbers )

cameraMode = rtbGetNamedValue(names,conditionValues,'cameraMode',[]);
mode = rtbGetNamedValue(names,conditionValues,'mode',[]);
pixelSamples = rtbGetNamedNumericValue(names,conditionValues,'pixelSamples',[]);
filmDist = rtbGetNamedNumericValue(names,conditionValues,'filmDist',[]);
filmDiag = rtbGetNamedNumericValue(names,conditionValues,'filmDiag',[]);
microlensDim = eval(rtbGetNamedValue(names,conditionValues,'microlensDim',[]));



switch cameraMode
    
    case 'perspective'
        camera = nativeScene.overall.find('Camera');
        camera.setParameter('fov','float',35);
        
    case 'pinhole'
        camera = nativeScene.overall.find('Camera');
        camera.parameters = [];
        camera.type = 'pinhole';
        
    case '50mm'
        camera = nativeScene.overall.find('Camera');
        camera.type = 'realisticDiffraction';
        camera.setParameter('aperture_diameter','float',10);
        camera.setParameter('filmdiag','float',filmDiag);
        camera.setParameter('filmdistance','float',filmDist);
        camera.setParameter('num_pinholes_h','float',0);
        camera.setParameter('num_pinholes_w','float',0);
        camera.setParameter('microlens_enabled','float',0);
        camera.setParameter('specfile','string','resources/dgauss.50mm.dat');
        
    case '100mm'
        camera = nativeScene.overall.find('Camera');
        camera.type = 'realisticDiffraction';
        camera.setParameter('aperture_diameter','float',5);
        camera.setParameter('filmdiag','float',filmDiag);
        camera.setParameter('filmdistance','float',filmDist);
        camera.setParameter('num_pinholes_h','float',0);
        camera.setParameter('num_pinholes_w','float',0);
        camera.setParameter('microlens_enabled','float',0);
        camera.setParameter('specfile','string','resources/dgauss.100mm.dat');
    
    case 'lightfield'
        % Remove the default camera
        camera = nativeScene.overall.find('Camera');
        camera.type = 'realisticDiffraction';
        camera.setParameter('aperture_diameter','float',20);
        camera.setParameter('filmdiag','float',filmDiag);
        camera.setParameter('filmdistance','float',filmDist);
        camera.setParameter('num_pinholes_h','float',microlensDim(1));
        camera.setParameter('num_pinholes_w','float',microlensDim(2));
        camera.setParameter('microlens_enabled','float',1);
        camera.setParameter('specfile','string','resources/dgauss.50mm.dat');

end

integrator = nativeScene.overall.find('SurfaceIntegrator');
sampler = nativeScene.overall.find('Sampler');


switch mode
    case {'depth'}
        integrator.type = 'metadata';
        integrator.parameters = [];
        integrator.setParameter('strategy','string','depth');
        
        sampler.type = 'stratified';
        sampler.parameters = [];
        sampler.setParameter('jitter','bool','false');
        sampler.setParameter('xsamples','integer',1);
        sampler.setParameter('ysamples','integer',1);
        sampler.setParameter('pixelsamples','integer',1);
        
    case {'material'}
        integrator.type = 'metadata';
        integrator.parameters = [];
        integrator.setParameter('strategy','string','material');
        
        sampler.type = 'stratified';
        sampler.parameters = [];
        sampler.setParameter('jitter','bool','false');
        sampler.setParameter('xsamples','integer',1);
        sampler.setParameter('ysamples','integer',1);
        sampler.setParameter('pixelsamples','integer',1);
        
    case {'mesh'}
        integrator.type = 'metadata';
        integrator.parameters = [];
        integrator.setParameter('strategy','string','mesh');
        
        sampler.type = 'stratified';
        sampler.parameters = [];
        sampler.setParameter('jitter','bool','false');
        sampler.setParameter('xsamples','integer',1);
        sampler.setParameter('ysamples','integer',1);
        sampler.setParameter('pixelsamples','integer',1);
        
    otherwise % Generate radiance data
        
        integrator.type = 'path';
        
        sampler.setParameter('pixelsamples','integer',pixelSamples);
end







end


