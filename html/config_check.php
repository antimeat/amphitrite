<html>
    <?php include('configs.php');?>

    <head>
	    <title><?php echo $TITLE; ?></title>
	</head>
	
    <body>
    
        <div class="container-fluid">
            <div style="position: relative; top: 100px">
                <div style="width: 1500px; margin: 4px">  
                    <h1 style="text-align: left;"><i>Configuration checker:</i></h1>
                    <hr>
                    
                    <div class="embed-responsive embed-responsive-1by1">
		                <iframe class="embed-responsive-item" src=<?php echo($BASE_URL . "sites_api.cgi?get=compare");?>></iframe>
                    </div>
                                                              
                    
                </div>
            </div>
        </div>
        
    </body>
</html>

