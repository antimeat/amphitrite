<?php
    $PYTHON_PATH = "/cws/anaconda/envs/mlenv/bin/python";
    $BASE_DIR = dirname(dirname(__FILE__)) . "/";
    $BASE_URL = str_replace("/cws/op","http://wa-vw-er", $BASE_DIR); 
    $HTML_DIR = "html/";
    $CONFIG_FILE_NAME = $BASE_DIR . "site_config.txt";
    $EXCLUSION_FILE_NAME = $BASE_DIR . "exclusion_list.txt";
    $TITLE = "Amphitrite (dev)";
?>