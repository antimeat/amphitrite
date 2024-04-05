<html lang="en">
	<head>
		<?php header('Access-Control-Allow-Origin: *'); ?>

		<!-- Required meta tags -->
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

		<!-- Bootstrap CSS -->
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.1.3/dist/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
		
		<style>
            .container {
                text-align: center;		
	            width: 500;
	            clear: both;		
            }
            .container input {
	            text-align: left;		
	            width: 100%;
	            clear: both;
            }

            fieldset {
	            text-align: left;
	            display: inline-block;
	            vertical-align: middle;
            }
            input[type="radio"] {
	            vertical-align: left;
	            horizontal-align: left;
	            padding: 5px;
	            margin-left:10px;		
	            margin: 5px;	
	            margin-top: -5px;
            }

			.sidebar {
				position: fixed;
				top: 40px;
				bottom: 0;
				left: 0;
				z-index: 1000;
				display: block;
				padding: 20px;
				overflow-x: hidden;
				overflow-y: auto; /* Scrollable contents if viewport is shorter than content. */
				background-color: #f5f5f5;
				border-right: 1px solid #eee;
			}
			
			.alert {
                padding: 20px;
                background-color: #f44336;
                color: white;
                opacity: 1;
                transition: opacity 0.6s;
                margin-bottom: 15px;
            }

            .alert.success {background-color: #04AA6D;}
            .alert.info {background-color: #2196F3;}
            .alert.warning {background-color: #ff9800;}

            .closebtn {
                margin-left: 15px;
                color: white;
                font-weight: bold;
                float: right;
                font-size: 22px;
                line-height: 20px;
                cursor: pointer;
                transition: 0.3s;
            }

            .closebtn:hover {
                color: black;
            }
		</style>

	</head>

	<body>

	<div class="container-fluid">
		
		<?php
		    include('configs.php');
			$theta1 = $_REQUEST["theta1"];
			$theta2 = $_REQUEST["theta2"];
			$multiplier = $_REQUEST["multiplier"];
			$attenuation = $_REQUEST["attenuation"];
			$modelName = $_REQUEST["model"];
            $tableName = $_REQUEST["table_select"];
            $siteName = $_REQUEST["site_select"];
            $criteria_1 = $_REQUEST["criteria_1"];
		    $criteria_2 = $_REQUEST["criteria_2"];
		    $criteria_3 = $_REQUEST["criteria_3"];
			
			/*
			echo $theta;
			echo '<br>';
			echo $modelName;
			echo '<br>';
			*/
			
			#command to execute
			$cmd = 'cd ' . $BASE_DIR . ' && '. $BASE_DIR . 'waveTable.py';
			
			ob_start();

			//passthru("$cmd '$siteName' '$tableName' '$theta1' '$theta2' '$multiplier' '$attenuation' '$modelName' '$criteria_1' '$criteria_2' '$criteria_3'");
			passthru("$cmd "
                . "--siteName '$siteName' "
                . "--tableName '$tableName' "
                . "--theta_1 '$theta1' "
                . "--theta_2 '$theta2' "
                . "--multiplier '$multiplier' "
                . "--attenuation '$attenuation' "
                . "--model '$modelName' "
                . "--thresholds '$criteria_1,$criteria_2,$criteria_3'"
            );

			$buffer = ob_get_contents();
			ob_end_clean();
		?>
		
			<div class="alert success">
                <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span> 
                <?php echo('<b>Model:</b> ' . $modelName . ' <b>Table:</b> ' . $tableName . ' <b>Formula:</b> Hs = cos((&#960 &#8260 180)&#8901(dir - '. $theta1 . ' or ' . $theta2 . ' &#8901(hs)')?>
            </div>
	        
	        <div class="alert info">
                <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span> 
                <i>Load into vulture with </i> <b>data-source:</b> mod <b>site:</b> <?php echo($siteName);?>
            </div>
	        
	        <fieldset align="center">	
		        <?php print_r($buffer); ?>
			</fieldset>
		</div>

		<!-- Optional JavaScript -->
		<!-- jQuery first, then Popper.js, then Bootstrap JS -->
		<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.1.3/dist/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
	
	</body>
</html>
