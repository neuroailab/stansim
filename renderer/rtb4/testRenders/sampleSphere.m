function [ points ] = sampleSphere( nSamples )

rnd = 1;

points = zeros(nSamples,3);
offset = 2/nSamples;
increment = pi*(3 - sqrt(5));

for i=1:nSamples
    y = ((i-1)*offset - 1) + offset/2;
    r = sqrt(1 - y.^2);
    phi = rem(i-1+rnd,nSamples) * increment;
    
    x = cos(phi)*r;
    z = sin(phi)*r;

    points(i,:) = [x, y, z];

end

