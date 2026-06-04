% Ground Test Plot Script
% This script reads the CSV log and plots RSSI, SNR, and latency by distance

clear;
clc;
close all;

% Read the CSV file
filename = 'ground_log_20260527_191406.csv';
T = readtable(filename);

% Keep only returned status packets
statusData = T(strcmp(T.event_type, 'STATUS_RECEIVED'), :);

% Remove startup packet and first extra test
statusData = statusData(statusData.command_id >= 2, :);

% Distances tested
distances = [20 40 60 80 100];

% There were 6 tests at each distance
testsPerDistance = 6;

% Assign distance to each row
distance_col = repelem(distances, testsPerDistance)';
statusData.Distance_ft = distance_col;

% Get average values by distance
avgRSSI = groupsummary(statusData, "Distance_ft", "mean", "rssi_dbm");
avgSNR = groupsummary(statusData, "Distance_ft", "mean", "snr_db");
avgLatency = groupsummary(statusData, "Distance_ft", "mean", "latency_sec");

% -----------------------------
% Plot 1: Average RSSI vs Distance
% -----------------------------
figure;
plot(avgRSSI.Distance_ft, avgRSSI.mean_rssi_dbm, '-o', 'LineWidth', 2, 'MarkerSize', 8);
grid on;
xlabel('Distance (ft)');
ylabel('Average RSSI (dBm)');
title('Average RSSI vs Distance');
set(gca, 'FontSize', 12);

% -----------------------------
% Plot 2: Average SNR vs Distance
% -----------------------------
figure;
plot(avgSNR.Distance_ft, avgSNR.mean_snr_db, '-o', 'LineWidth', 2, 'MarkerSize', 8);
grid on;
xlabel('Distance (ft)');
ylabel('Average SNR (dB)');
title('Average SNR vs Distance');
set(gca, 'FontSize', 12);

% -----------------------------
% Plot 3: Average Latency vs Distance
% -----------------------------
figure;
plot(avgLatency.Distance_ft, avgLatency.mean_latency_sec, '-o', 'LineWidth', 2, 'MarkerSize', 8);
grid on;
xlabel('Distance (ft)');
ylabel('Average Latency (sec)');
title('Average Latency vs Distance');
set(gca, 'FontSize', 12);

% -----------------------------
% Optional: Show summary in command window
% -----------------------------
disp('Average RSSI by Distance:');
disp(avgRSSI(:, {'Distance_ft', 'mean_rssi_dbm'}));

disp('Average SNR by Distance:');
disp(avgSNR(:, {'Distance_ft', 'mean_snr_db'}));

disp('Average Latency by Distance:');
disp(avgLatency(:, {'Distance_ft', 'mean_latency_sec'}));