<html lang="en">
	<head>
		<!-- Required meta tags -->
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

		<!-- Bootstrap CSS -->
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
		
		<!-- <style>
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
	    </style> -->

	</head>

	<body>

	    <?php
	        ob_start();
		    passthru("cd /cws/op/webapps/er_ml_projects/davink/amphitrite/ && /cws/op/webapps/er_ml_projects/davink/amphitrite/partitionSplitter.py --site all");
            $buffer = ob_get_contents();
		    ob_end_clean();
	    ?>
	
	    <div class="container-fluid" align="left">
    	    <hr>
            <br>
            <div class="embed-responsive embed-responsive-1by1">
                <iframe class="embed-responsive-item" src="<?php echo($buffer); ?>" align="center" width="1200" height="1200"></iframe>
            </div>
		</div>

		<!-- Optional JavaScript -->
		<!-- jQuery first, then Popper.js, then Bootstrap JS -->
		<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
		<script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
	
	</body>
</html>

