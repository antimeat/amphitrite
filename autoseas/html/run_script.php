<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
</head>
<body>

<?php
	include('configs.php');
	ini_set('display_errors', 1);
	error_reporting(E_ALL);

	if(isset($_REQUEST["sites"])) {
	 	$site = $_REQUEST["sites"];
		$encodedSite = urlencode($site);
	 	$url = $BASE_URL . "autoseas/comparison_api.cgi?site=" . $encodedSite;

	 	// Use file_get_contents to make the GET request
	 	$options = array(
	 		"http" => array(
	 			"method" => "GET",
	 			"header" => "Accept: text/html\r\n"							
			)
		);
		$context = stream_context_create($options);
		$response = file_get_contents($url, false, $context);

		if($response === FALSE) {
			$response = "Error fetching data.";
		}
	} else {
		$response = "Site parameter is missing.";
	}
	
?>

<div class="container-fluid">
    <div style="position: relative; top: 100px">
        <div style="width: 1500px; margin: 4px">  
            <h1 style="text-align: left;"><i>Compare algorithms:</i></h1>
            <hr>
            
            <!-- Display the response -->
            <?php echo $response; ?>
            
        </div>
    </div>
</div>

<!-- Optional JavaScript; choose one of the two! -->

<!-- Option 1: jQuery and Bootstrap Bundle (includes Popper) -->
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.bundle.min.js" integrity="sha384-p34f1UUtsS3wqzfto2FbZR9HXQc23+MzZPjtbY3F3C/3jCEQjlr4K7SlNT/aClAf" crossorigin="anonymous"></script>

</body>
</html>
