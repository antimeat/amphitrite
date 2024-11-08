<?php

include('configs.php');

// Enable error reporting for debugging
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Path to the configuration file
$configFile = $CONFIG_FILE_NAME;

if (!file_exists($configFile)) {
    header('Content-Type: application/json');
    echo json_encode(array('error' => 'Configuration file not found'));
    exit;
}

function parseConfig($configFile) {
    $config = array();
    $file = fopen($configFile, 'r');
    if (!$file) {
        header('Content-Type: application/json');
        echo json_encode(array('error' => 'Unable to open configuration file'));
        exit;
    }

    while (($line = fgets($file)) !== false) {
        // Skip comments and empty lines
        if (trim($line) == '' || strpos($line, '#') === 0) {
            continue;
        }

        // Parse the config line
        $parts = explode(',', $line);
        if (count($parts) >= 10) { // Ensure the line has enough parts
            $site = trim($parts[0]);
            $config[$site] = array(
                'theta_split' => (int) trim($parts[1]),
                'theta_1' => (int) trim($parts[2]),
                'theta_2' => (int) trim($parts[3]),
                'multi_short' => (float) trim($parts[4]),
                'multi_long' => (float) trim($parts[5]),
                'attenuation' => (float) trim($parts[6]),
                'crit_1' => (float) trim($parts[7]),
                'crit_2' => (float) trim($parts[8]),
                'crit_3' => (float) trim($parts[9])
            );
        } else {
            error_log("Line does not have enough parts: " . $line); // Log incomplete lines
        }
    }
    fclose($file);
    return $config;
}

header('Content-Type: application/json');
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
$configData = parseConfig($configFile);
echo json_encode($configData);
?>
