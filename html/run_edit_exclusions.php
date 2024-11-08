<?php
    include('configs.php');
    $dir = $BASE_DIR;
    
    $sites = $_REQUEST["sites"];            
    // $sites = str_replace("'", "&apos;",$sites);
    $comments = $_REQUEST["comments"];            
    $comments = str_replace("'", "&apos;",$comments);
    
    ob_start();
    passthru("cd $dir && $dir" . "save_exclusions.py '$sites' '$comments' $EXCLUSION_FILE_NAME");
    $buffer = ob_get_contents();
    ob_end_clean();
    header("Location: dashboard.php");
?>


