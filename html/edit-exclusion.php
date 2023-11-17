<html>
    <?php include('configs.php');?>

    <head>
        <title><?php echo $title; ?></title>
    </head>
    
    <script type="text/javascript">
        $(document).ready(function() {
            document.onkeypress = null;
        });            
    </script>
    
    <?php
        function loadConfigFile($configFile) {
            $siteTables = array();
            $comments = array();

            // Open the file
            $file = fopen($configFile, 'r');
            if (!$file) {
                return array("sites" => $siteTables, "comments" => $comments); // Return empty arrays if file can't be opened
            }

            while (($line = fgets($file)) !== false) {
                // Capture comment lines
                if (strpos($line, '#') === 0) {
                    $comments[] = trim($line);
                    continue;
                }
        
                $site = trim($line);
                $siteTables[$site] = $site;                
            }
        
            fclose($file);
            return array("sites" => $siteTables, "comments" => $comments);
        }
        
        // Use the new function to load the site configurations
        $configData = loadConfigFile($exclusion_file_name);
        $siteTables = $configData["sites"];
        $comments = $configData["comments"];
        
        // Prepare sites data for display in the textarea
        $sitesDisplay = '';
        foreach ($siteTables as $site => $info) {
            $sitesDisplay .= $site;
            $sitesDisplay .= "\n";
        }

        // Prepare comments for display
        $commentsDisplay = implode("\n", $comments);
    ?>
    
    <body>
        <div class="container-fluid">
            <form class="col-lg-10" style="top:200px" action="run_edit_exclusions.php" method="POST">
                <div class="form-group row">
                    <label for="sites" class="col-sm-1 col-form-label">Exclusion sites</label>
                    <div class="col-sm-11">
                        <textarea class="form-control" name="sites" id="sites" cols="10" rows="30"><?php echo htmlspecialchars($sitesDisplay); ?></textarea>
                    </div>
                    <!-- Hidden div for comments -->
                    <textarea style="display: none;" name="comments" id="comments"><?php echo htmlspecialchars($commentsDisplay); ?></textarea>
                </div>
                
                <div class="form-group row">
                    <button type="submit" class="btn btn-save col-sm-1">save</button>
                </div>
            </form>         
        </div>
    </body>
</html>
