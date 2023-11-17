<?php
    include 'configs.php';
    $dir = $baseDir;
    
    $sites = $_REQUEST["sites"];            
    $sites = str_replace("'", "&apos;",$sites);
    $comments = $_REQUEST["comments"];            
    $comments = str_replace("'", "&apos;",$comments);
        
    ob_start();
    passthru("cd $dir &&  $dir" . "save_config.py '$sites' '$comments' $config_file_name");
    $buffer = ob_get_contents();
    ob_end_clean();
    header("Location: dashboard.php");
?>


