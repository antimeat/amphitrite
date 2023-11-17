<html>
    <?php include('configs.php');?>

    <head>
	    <title><?php echo $title; ?></title>
	</head>
	
    <body>
    
        <div class="container-fluid">
            <div style="position: relative; top: 100px">
                <div style="width: 1200px; margin: 4px">  
                    <h1 style="text-align: left;"><i>Site summary:</i></h1>
                    <hr><br><br>
                    <div class="embed-responsive embed-responsive-1by1">
                        <iframe class="embed-responsive-item" src="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=list_html"></iframe>
                    </div>
                </div>
            </div>
        </div>
        
    </body>
</html>

