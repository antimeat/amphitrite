<?php

    /*
		Add / edit fetch limit tables for auto seas.
    */
	
	require_once "../lib.php";
	
	// CSV fields (order is important)
	$FIELDS = array("windDir", "fetch", "depth");
	
	for ($i=0; $i<=35; $i++) $WIND_DIRS[] = 10 * $i;
	

	function loadTable($siteName) {
		// load the fetch and depth table for this site
		$h = fopen(siteToFileName($siteName), "r");
		
		if ($h === FALSE) return FALSE;
		
		$fields = fgetcsv($h);
		
		$windDirIndex = array_search("windDir", $fields);

		while(($t = fgetcsv($h)) !== FALSE) {
			foreach($fields AS $f => $field) {
				if ($field != 'windDir') {
					$table[$t[$windDirIndex]][$field] = $t[$f];
				}
			}
		}
		
		fclose($h);
		
		return $table;
	}

	function saveTable($formData) {
		// save the data in the submitted form

		global $WIND_DIRS, $FIELDS;
		
		$siteName = $formData[site];
		$fileName = siteToFileName($siteName);

		// preserve the old version
		$copyDest = siteToFileName($siteName ."___". date("Ymd His"));
		copy($fileName, $copyDest);
		
		$data[] = $FIELDS;
		
		foreach($WIND_DIRS AS $windDir) {
			$fetch = $formData["fetch_". $windDir];
			$depth = $formData["depth_". $windDir];
			
			$data[] = array($windDir, $fetch, $depth);
		}
		
		$h = fopen($fileName, "w+");

		if ($h === FALSE) return "Failed to open file. There may be permissions problems.";
		
		//print_r($data);
		//echo "handle ". $h;

		foreach($data AS $d) {
			fputcsv($h, $d);
		}
		
		fclose($h);

		return "Save successful";
	}
	
	$site = "";
	if ($_REQUEST[site]) $site = $_REQUEST[site];

	// Save first if requested
	$saveMsg = FALSE;
	if ($_REQUEST[action] == "save") {
		$saveMsg = saveTable($_REQUEST);
	}

	$sites = getSiteNames(".");
	
	// show the user the saved version always
	if ($site != "" AND $site != "new") $table = loadTable($site);
	
?>
<html>
<head>
<title>Fetch Limits & Depths - AutoSeas</title>
</head>

<style>
body,td,p,a { font-family:arial,sans-serif; font-size: 12px }
h1, h2, h3, h4 { }

th { background-color: black; color: white}

.msgBox { border: 1px solid #FF0000; margin: 4px; padding: 4px; clear: both }

</style>

<body>

<div style="border: solid 1px #AAAAAA; margin: 4px; padding: 4px">

<h3>AutoSeas - Edit Fetch Limits and Depth</h3>

Help

<ul>
<li>Site name: exactly like forecast name in Ofcast home page BUT with the shift brackets part removed and spaces replaced by underscores.
<li>Depth field needs to be either completely filled up or completely empty.
<li>If depth field used, shallow water equations used to limit fully developed height as well as fetch.
<li>Site can be 'copied' by choosing the copy site, changing the site name and hitting save.
<li>Depth: average representative depth.
<li>'U' is for unlimited fetch
</ul>

</div>

<?php
	if ($saveMsg) {
		echo "<div class=msgBox>$saveMsg</div>";
	}
?>

<div style="border: 1px solid #AAAAAA; margin: 4px; padding: 4px">
<b>Choose Site to edit</b>

<form name=siteSelect method=get action=edit.php>
<select name=site onchange="forms[0].submit()">
<option></option>
<?php
	foreach($sites AS $siteName) {
		$s = ($site == $siteName) ? "SELECTED" : "";
		echo "<option value='$siteName' $s>$siteName</option>";
	}
?>
</select>
</form>

OR 
<p>
<a href=edit.php?site=new>Create new site</a>

</div>

<div style="border: 1px solid #666666; margin: 4px; clear: both">

<form name=siteEdit method=post action=edit.php>

<input type=submit value=Save><br>

<input type=hidden name=action value=save>

Site Name: <input type=text name=site value="<?php echo $site ?>" size=50> (see help)

<table border=0>
<tr>
<td>windDir</td><td>fetch (nm)</td><td>depth (m)</td>
</tr>

<?php

	foreach($WIND_DIRS AS $dir) {
		$fetch = $table[$dir][fetch];
		$depth = $table[$dir][depth];
		echo "<tr><td>$dir</td>";
		echo "<td><input type=text size=4 name=fetch_$dir value='$fetch'></td>";
		echo "<td><input type=text size=4 name=depth_$dir value='$depth'></td>";
		echo "</tr>\n";
	}

?>
</table>
</form>
</body>
</html>