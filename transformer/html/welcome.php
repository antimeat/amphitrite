
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
                        <img src=<?php echo($BASE_URL . "transformer/html/img/transformers.jpg");?> class="mslp" style="border-radius: 30px; display: block; margin-right: auto;  margin-right: auto;  width: 30%;"></img>
                        <!-- <img src="http://www.bom.gov.au/iwk/images/small-artwork.png" class="indigenous"  style="display: block; margin-right: auto;  margin-right: auto;  width: 55%;"/img> -->
                    <h2> 
                    <div class="welcome">
                            <h5>
                                <ol>
                                    <li><h4>Edit config</h4>
                                        <ul>
                                            <li><i>edit the config file to change transformer defaults for each site</i></li>
                                        </ul>  
                                    </li>    
                                    <br>
                                    <li><h4>Transformer interface</h4>
                                        <ul>
                                            <li><i>select an active ofcast site to view the transform</i></li>
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

        

