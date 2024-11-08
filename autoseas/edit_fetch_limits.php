<?php
	/*
		AutoSeas - Fetch Limits & Depths Management
	*/

	error_reporting(E_ALL);
	ini_set('display_errors', 1);

	date_default_timezone_set('Australia/Perth');
	define("TABLE_DIR", "fetchLimits/");

	$sites = getSiteNames(TABLE_DIR);

	define("WIND_DIRECTION_STEP", 10);
	define("MAX_WIND_DIRECTION", 350);
	$WIND_DIRS = range(0, MAX_WIND_DIRECTION, WIND_DIRECTION_STEP);
	$fields = array("windDir", "fetch", "depth");

	function siteToFileName($siteName) {
		return TABLE_DIR . str_replace(" ", "_", $siteName) . ".csv";
	}

	function fileToSiteName($fileName) {
		return str_replace("_", " ", substr($fileName, 0, -4));
	}

	function getSiteNames($directory) {
		$siteNames = array();
		if ($handle = opendir($directory)) {
			while (false !== ($entry = readdir($handle))) {
				if (strpos($entry, ".csv") !== false && strpos($entry, "___") === false) {
					$siteNames[] = fileToSiteName($entry);
				}
			}
			closedir($handle);
		}
		sort($siteNames);
		return $siteNames;
	}

	function loadTable($siteName) {
		$fileName = siteToFileName($siteName);
		if (!file_exists($fileName) || ($handle = fopen($fileName, "r")) === false) {
			return false;
		}

		$table = array();
		$fields = fgetcsv($handle);
		$windDirIndex = array_search("windDir", $fields);
		while (($row = fgetcsv($handle)) !== false) {
			foreach ($fields as $index => $field) {
				if ($field != 'windDir') {
					$table[$row[$windDirIndex]][$field] = $row[$index];
				}
			}
		}
		fclose($handle);
		return $table;
	}

	function saveTable($formData, $WIND_DIRS, $fields) {
		$siteName = isset($formData['site']) ? $formData['site'] : '';
		$fileName = siteToFileName($siteName);

		// Backup old file
		$backupFileName = siteToFileName($siteName . "___" . date("Ymd His"));
		if (file_exists($fileName) && !copy($fileName, $backupFileName)) {
			return "Failed to backup the old file.";
		}

		$data = array($fields);
		foreach ($WIND_DIRS as $windDir) {
			$row = array($windDir);
			foreach ($fields as $field) {
				if ($field != "windDir") {
					$row[] = isset($formData[$field . "_" . $windDir]) ? $formData[$field . "_" . $windDir] : '';
				}
			}
			$data[] = $row;
		}

		if (($handle = fopen($fileName, "w")) === false) {
			return "Failed to open file for writing.";
		}
		foreach ($data as $row) {
			fputcsv($handle, $row);
		}
		fclose($handle);
		return "Save successful.";
	}

	// Process form submission
    if (isset($_REQUEST['action']) && $_REQUEST['action'] == "save") {
        $saveMsg = saveTable($_REQUEST, $WIND_DIRS, $fields);

        // Redirect to refresh the page with the latest data
        $site = isset($_REQUEST['site']) ? $_REQUEST['site'] : '';
        header("Location: edit_fetch_limits.php?site=" . urlencode($site));
        exit;
    }

    // Load site data after the potential save operation
    $site = isset($_REQUEST['site']) ? $_REQUEST['site'] : '';
    $table = array();
    if ($site && $site != "new") {
        $loadedTable = loadTable($site);
        if ($loadedTable !== false) {
            $table = $loadedTable;
        } else {
            echo "<p>Error loading table for site: {$site}</p>";
        }
    }

	$saveMsg = '';
	if (isset($_REQUEST['action']) && $_REQUEST['action'] == "save") {
		$saveMsg = saveTable($_REQUEST, $WIND_DIRS, $fields);
	}

	$sites = getSiteNames(TABLE_DIR);
?>

<!DOCTYPE html>
<html>
<head>
    <title>Fetch Limits & Depths - AutoSeas</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
            color: #333;
            background-color: #f4f4f4;
            padding: 10px;
        }

        h3 {
            color: #0a0a0a;
        }

        .container {
            background-color: #fff;
            border: solid 1px #dddddd;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        table {
            width: 20%;
            border-collapse: collapse;
            border-collapse: collapse;
            margin-top: 20px;
        }

        table, th, td {
            text-align: "center";
            border: 1px solid #ddd;
            padding: 0px; /* Adjusted padding */
        }

        .msgBox {
            border: 1px solid #FF0000;
            background-color: #ffe5e5;
            padding: 10px;
            margin-bottom: 20px;
            color: #d8000c;
        }

        input[type="text"], select {
            padding: 0px;
            margin: 8px 0;
            border: 1px solid #ccc; /* Adjust padding */
            border-radius: 2px;
            box-sizing: border-box;
        }

        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #45a049;
        }

        a {
            color: #0077cc;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Autoseas - edit fetch limits and depth</h1>
        
        <i>
            <ul>
                <li>Site name: exactly like forecast name in Ofcast home page BUT with the shift brackets part removed and spaces replaced by underscores.</li>
                <li>Depth field needs to be either completely filled up or completely empty.</li>
                <li>If depth field used, shallow water equations used to limit fully developed height as well as fetch.</li>
                <li>Site can be 'copied' by choosing the copy site, changing the site name and hitting save.</li>
                <li>Depth: average representative depth.</li>
                <li>'U' is for unlimited fetch.</li>
            </ul>
        </i>
    </div>

    <?php
        if ($saveMsg) {
            echo "<div class='msgBox'>$saveMsg</div>";
        }
    ?>

    <div class="container">
        <b>Choose Site to edit</b>
        <form name="siteSelect" method="get" action="edit_fetch_limits.php">
            <select name="site" onchange="forms[0].submit()">
                <option></option>
                <?php
                    foreach($sites AS $siteName) {
                        $s = ($site == $siteName) ? "SELECTED" : "";
                        echo "<option value='$siteName' $s>$siteName</option>";
                    }
                ?>
            </select>
        </form>
        <p>OR</p>
        <p><a href="edit_fetch_limits.php?site=new">Create new site</a></p>
    </div>

    <div class="container">
        <form name="siteEdit" method="post" action="edit_fetch_limits.php">
            <input type="submit" value="Save">
            <input type="hidden" name="action" value="save">
            <p><b>Site Name: </b> <input type="text" name="site" value="<?php echo $site ?>" size="50"></p>

            <table>
                <tr>
                    <th>wind_dir (deg)</th>
                    <th>fetch (nm)</th>
                    <th>depth (m)</th>
                </tr>
                <?php
					foreach($WIND_DIRS as $dir) {
						$fetch = isset($table[$dir]['fetch']) ? $table[$dir]['fetch'] : '';
						$depth = isset($table[$dir]['depth']) ? $table[$dir]['depth'] : '';
						echo "<tr><td>$dir</td>";
						echo "<td><input type='text' size='4' name='fetch_$dir' value='$fetch'></td>";
						echo "<td><input type='text' size='4' name='depth_$dir' value='$depth'></td>";
						echo "</tr>\n";
					}
				?>
            </table>
        </form>
    </div>
</body>
</html>
