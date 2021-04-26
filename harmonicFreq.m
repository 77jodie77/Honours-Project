function [peaks_x, peaks_y] = harmonicFreq(filename)

% Switch off warnings - these warnings show when a peak is not found in a
% sample which is supposed to happen if no music is played
warning('off','signal:findpeaks:largeMinPeakHeight')
warning('off','MATLAB:colon:nonIntegerIndex') 
wait = 0;
t=0;

progbar = waitbar(wait,'Please wait...', 'windowstyle', 'modal');

frames = java.awt.Frame.getFrames();
frames(end).setAlwaysOnTop(1); % Set the waitbar to always be on the top of the screen

peaks_y = zeros(1, 1000);
peaks_x = zeros(1, 1000);

[tunestereo,fs]=audioread(filename);
n = length(tunestereo);
for k = 1:fs/4:n
    t=t+1; %calculate the number of samples
end 
%https://uk.mathworks.com/matlabcentral/answers/455967-splitting-an-audio-file-into-1s-for-max-audio-files
for k = 1:fs/4:n
    wait=wait+(100/t); %increment the waitbar every sample
    waitbar(wait,progbar,'Loading your data')
    audioBlock = tunestereo(k:min(k + fs/4 - 1, n), :);
    



    tune_fft = fft(audioBlock);
    tune_fft = tune_fft(1:length(audioBlock)/2+1);
    %create freq vector
    freq = 0:fs/length(audioBlock):fs/2;
    
    [pks,locs] = findpeaks(20*log10(abs(tune_fft)), "MinPeakProminence", 25, 'MinPeakHeight',18, 'MinPeakDistance',18);
    
    %finds the peaks within the range of the fundamental frequency of the notes
    indesiredrange = locs > 50;

    %gets the subsets within range
    pks_subset = pks(indesiredrange);
    locs_subset = locs(indesiredrange);
    
    
    peaks_x = [peaks_x, freq(locs_subset)];
    
    peaks_x = [peaks_x, 999999];
end

peaks_y = [peaks_y, pks_subset];
close(progbar)


end

