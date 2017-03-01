function [ scene, mappings ] = MexximpRemodeller( scene, mappings, names, conditionValues, conditionNumber )

viewPoint = eval(rtbGetNamedValue(names,conditionValues,'viewPoint',[]));


% Point the camera towards the scene
% [scene, camera, cameraNode] = mexximpCentralizeCamera(scene,'viewAxis',[0 1 0],...
%                                                            'viewUp',[0 0 -1]);

% This adds a camera
scene = mexximpCentralizeCamera(scene,'viewAxis',viewPoint,...
                                      'viewUp',[0 1 0]);
                                                        

scene = mexximpAddLanterns(scene);







end

