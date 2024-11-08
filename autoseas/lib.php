<?php

	// common php functions

	function siteToFileName($str) {
		return str_replace(" ", "_", $str) .".csv";
	}
	
	function fileToSiteName($str) {
		return str_replace("_", " ", substr($str, 0, -4));
	}
	
	function getSiteNames($dir) {
		// read the list of csv files in this dir, these are the site names
		$h = opendir($dir);
		while(false !== ($entry = readdir($h))) {
			// only list csv files and non backup ones
			if ((strpos($entry, ".csv") > 0) AND (strpos($entry, "___") === FALSE)) {
				$files[] = fileToSiteName($entry);
			}
		}
		sort($files);
		return $files;
	}

?>