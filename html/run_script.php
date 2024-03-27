<html lang="en">
	<head>
		<?php include('configs.php');?>

		<!-- Required meta tags -->
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

		<!-- Bootstrap CSS -->
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
	</head>

	<body>

		<?php
			$dir = $BASE_DIR;
			$outputFile = $dir . "test_output.txt";  // Concatenating the directory with the filename
			putenv("NUMBA_CACHE_DIR=/tmp/numba_cache");
			
			$site = $_REQUEST["sites"];
			
			chdir($dir);

			$pythonPath = $PYTHON_PATH;
			$scriptPath = $dir . "partitionSplitter.py";
			// $escapedSite = escapeshellarg("");

			$command = "$pythonPath $scriptPath --site '$site' > $outputFile 2>&1";
			passthru($command);


			// Read the output file and convert for html
			$output = file_get_contents($outputFile);			
		?>

		<!-- <div class="container-fluid">
			<hr>
			<br>
			<div class="embed-responsive embed-responsive-1by1">
				<iframe srcdoc="<?php echo htmlspecialchars($output); ?>" width="80%" height="500px"></iframe>
			</div>
		</div> -->

		<div class="container-fluid">
            <div style="position: relative; top: 100px">
                <div class="row min-vh-100">
                    <div class="col-lg-10 h-100">
                        <textarea class="w-100" style="min-height: 900px; min-width: 1400px" spellcheck="false" disabled readonly><?php echo htmlspecialchars($output); ?></textarea>
                    </div>                
                </div>                
            </div>
        </div>


		<!-- Optional JavaScript -->
		<!-- jQuery first, then Popper.js, then Bootstrap JS  -->
		<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
		<script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
	
	</body>
</html>

