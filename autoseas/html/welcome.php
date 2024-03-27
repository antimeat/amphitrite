
<html>
    <?php include('configs.php');?>

	<head>
	    <title><?php echo $TITLE; ?></title>
	   
        <style>
            
            .indigenous {
                position: absolute;
                top: 150px;
                left: 0px;
                opacity: 0.6;
            }
            
            .mslp {
                position: relative;
                top: 50px;                
                opacity: 1;
            }
            
            .welcome {
                position: relative;
                top: 100px;                
                opacity: 1;
            }
            
            
        </style>

    </head>
    
    <body>
        
        <div class="container-fluid">
            <div style="position: relative; top: 100px">
                
                    <h1 style="text-align: left;"><i><p style="text-align: right;"></font></p>Welcome</i></h1>
                    <hr><br>
                        <img src=<?php echo($BASE_URL . "autoseas/html/img/ocean_robot.jpg");?> class="mslp" style="border-radius: 30px; display: block; margin-right: auto;  margin-right: auto;  width: 20%;"></img>
                        <!-- <img src="http://www.bom.gov.au/iwk/images/small-artwork.png" class="indigenous"  style="display: block; margin-right: auto;  margin-right: auto;  width: 55%;"/img> -->
                    <h2> 
                    <div class="welcome">
                            <h2><i> Autoseas: by default we use the Breugen Holthuijsen algorithm </i></h2>
                            <br>
                            <h5>
                                <ol>
                                    <li><h4>Site calculations</h4>
                                        <ul>
                                            <li><i>select an active ofcast site with sessionID</i></li>
                                        </ul>  
                                    </li>
                                    <br>                                        
                                    <li><h4>Edit fetch/depth</h4>
                                        <ul>
                                            <li><i>change the fetch and depth files for each site </i></li>
                                        </ul>  
                                    </li>
                                    <br>                                        
                                    <li><h4>Compare algorithms</h4>
                                        <ul>
                                            <li><i>run a comparision between defualt algorithm and the others using a default set of winds </i></li>
                                        </ul>
                                    </li>
                                    <br>
                                    <li><h4>API docs</h4>
                                        <ul>
                                            <li><i>README for API calls to return autoseas data </i> </li>
                                        </ul>  
                                    </li>
                                </ol>    
                            </h5>
                            <br>                            
                        </div>                        
                        
                    </h2>
                </div>         
            </div>
        </div>        
    </body>
</html>

        

