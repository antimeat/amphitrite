<?php

	// extract a list of site names from the fetchLimits directory
	require_once "lib.php";
	$sites = getSiteNames("fetchLimits");
	foreach($sites AS $s) echo "$s\n";

?>