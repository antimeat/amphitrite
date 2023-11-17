<!doctype html>
<html lang="en">
	
	<?php include('configs.php');?>

	<head>
	    <title><?php echo $title; ?></title>
	
		<!-- Required meta tags -->
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=yes">

		<!-- Bootstrap CSS -->
		<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css">
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
		
		<!-- jQuery first, then Popper.js, then Bootstrap JS -->
		<script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
			
		<!-- Optional JavaScript below here -->
		<script>

			$(document).on('ready', function() {
                document.onkeypress = null
                changeLink('welcome');	
			});	
						
			function changeLink(input) {
				
				if (input == 'welcome') {
				    fileName = 'welcome.php';
					$("#imageContainer").load(fileName);
				}
				else if (input == 'config_check') {
				    fileName = 'config_check.php';
					$("#imageContainer").load(fileName);
				}
                else if (input == 'sites') {
				    fileName = 'sites.php';
					$("#imageContainer").load(fileName);
				}
				else if (input == 'database_check') {
				    fileName = 'database_check.php';
					$("#imageContainer").load(fileName);
				}
				else if (input == 'activate_run') {
				    fileName = 'activate_run.php';
					$("#imageContainer").load(fileName);
				}
				else if (input == 'edit-config') {
				    fileName = 'edit-config.php';
					$("#imageContainer").load(fileName);
				}				
				else if (input == 'edit-exclusion') {
				    fileName = 'edit-exclusion.php';
					$("#imageContainer").load(fileName);
				}
				
			}

		</script>

		
	</body>
</html>
