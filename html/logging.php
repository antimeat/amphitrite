<html>
    <?php include('configs.php');?>

    <head>
        <title><?php echo $TITLE; ?></title>
    </head>

    <body>

        <div class="container-fluid" style="position: relative; top: 100px">
            <div style="width: 1500px; margin: 4px;">  
                <h1 style="text-align: left;"><i>Partition log:</i></h1>
                <hr>
                
                <textarea style="width: 80%; height: 800px; resize: none;" readonly><?php
                    $logFilePath = $BASE_DIR . "logfile.log"; 
                    if (file_exists($logFilePath)) {
                        $logFile = file($logFilePath);
                        $logFile = array_reverse($logFile);
                        foreach ($logFile as $line) {
                            echo htmlspecialchars(trim($line)) . "\n";
                        }
                    } else {
                        echo "Log file not found or cannot be read.";
                    }
                ?></textarea>
                
            </div>
        </div>

    </body>
</html>