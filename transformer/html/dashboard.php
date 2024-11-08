<!doctype html>
<html lang="en">
	
	<?php include('configs.php');?>

	<head>
	    <title><?php echo $TITLE; ?></title>
	
		<!-- Required meta tags -->
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=yes">

		<!-- Bootstrap CSS -->
		<link rel="stylesheet" href="http://wa-vw-er/webapps/er_ml_projects/bootstrap/css/bootstrap.min.css">
		<style>     
		    .bomImage { width: position: absolute; left: 1000px; top: 950px  }
		</style>			
	</head>
    
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    
    <body>
	
		<!-- Load the top navbar from navBar.html	-->			
		<?php include("navBar.html");?>
	
		<div class="container-fluid">
			
			<div class="row">
				
				<div class="col-3">		
					<!-- Load the side bar from nav.html -->				
					<?php include("nav.html");?>
				</div>
				
				<div class="container col-9" id="imageContainer">
				    <?php include("welcome.php");?>				    
				</div>					
      		    
      		</div>
      	</div>		
		
		<!-- jQuery, Popper.js, and Bootstrap JS via jsDelivr CDN -->
		<script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
		<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js"></script>	
				
		<!-- Optional JavaScript below here -->
		<script>

			$(document).on('ready', function() {
            	changeLink('welcome');	
			});	
						
			function changeLink(input) {
				
				if (input == 'welcome') {
				    fileName = 'welcome.php';
					$("#imageContainer").load(fileName);
				}
				else if (input == 'transformer') {
				    fileName = 'index_wrapper.php';
					$("#imageContainer").load(fileName);
				}
				else if (input == 'readme_algorithm') {
				    fileName = 'readme_algorithm.php';
					$("#imageContainer").load(fileName);
				}
				else if (input == 'readme') {
				    fileName = 'readme.php';
					$("#imageContainer").load(fileName);
				}
				else if (input == 'edit-config') {
				    //fileName = 'edit-config.php';
					fileName = 'edit_config_wrapper.php';
					$("#imageContainer").load(fileName);
				}
			}

		</script>
		
	</body>
</html>
