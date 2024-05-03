<html>
    <?php include('configs.php');?>

    <head>
        <title><?php echo $TITLE; ?></title>
    </head>
    
    <script type="text/javascript">
        $(document).ready(function() {
            document.onkeypress = null;
        });            
    </script>
    
    <?php
        function loadConfigFile($configFile) {
            $siteData = array();
            $comments = array();

            // Open the file
            $file = fopen($configFile, 'r');
            if (!$file) {
                return array("sites" => $siteData, "comments" => $comments); // Return empty arrays if file can't be opened
            }

            while (($line = fgets($file)) !== false) {
                // Capture comment lines
                if (strpos($line, '#') === 0) {
                    $comments[] = trim($line);
                    continue;
                }

                $parts = explode(', ', trim($line));
                if (count($parts) < 3) {
                    continue; // Skip malformed lines
                }

                $site = $parts[0];
                $theta_split = $parts[1];
                $theta_1 = $parts[2];
                $theta_2 = $parts[3];
                $multi_upper = $parts[4];
                $multi_lower = $parts[5];
                $attenuation = $parts[6];
                $high = $parts[7];
                $mid = $parts[8];
                $low = $parts[9];
                
                $siteData[$site] = array("theta_split" => $theta_split, "theta_1" => $theta_1, "theta_2" => $theta_2, "multi_upper" => $multi_upper, "multi_lower" => $multi_lower, "attenuation" => $attenuation, "high" => $high, "mid" => $mid, "low" => $low);
            }

            fclose($file);
            return array("sites" => $siteData, "comments" => $comments);
        }
        
        // Use the new function to load the site configurations and comments
        $configData = loadConfigFile($CONFIG_FILE_NAME);
        $siteData = $configData["sites"];
        $comments = $configData["comments"];

        // Prepare sites data for display in the textarea
        $sitesDisplay = '';
        foreach ($siteData as $site => $info) {
            $sitesDisplay .= $site .  ', ' . $info['theta_split'] . ', ' . $info['theta_1'] . ', ' . $info['theta_2'] . ', ' . $info['multi_upper'] . ', ' . $info['multi_lower'] . ', ' . $info['attenuation'] . ', ' . $info['high'] . ', ' . $info['mid'] . ', ' . $info['low'];
            $sitesDisplay .= "\n";
        }

        // Prepare comments for display
        $commentsDisplay = implode("\n", $comments);
    ?>
    
    <body>
        <div class="container-fluid">
            <form class="col-lg-10" style="top:200px" action="run_edit_config_script.php" method="POST">
                <div class="form-group row">
                    <label for="comments" class="col-sm-1 col-form-label">Notes</label>
                    <div class="col-sm-11">
                        <!-- text area should be readonly -->
                        <textarea class="form-control" readonly name="comments" id="comments" cols="10" rows="7"><?php echo htmlspecialchars($commentsDisplay); ?></textarea>
                    </div>
                    
                    <label for="sites" class="col-sm-1 col-form-label">Sites</label>
                    <div class="col-sm-11">
                        <textarea class="form-control" name="sites" id="sites" cols="10" rows="10"><?php echo htmlspecialchars($sitesDisplay); ?></textarea>
                    </div>
                    <!-- Hidden div for comments -->
                    
                </div>
                
                <div class="form-group row">
                    <button type="submit" class="btn btn-save col-sm-1">save</button>
                </div>
            </form>         
        </div>
    </body>
</html>
