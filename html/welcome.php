
<html>
    <?php include('configs.php');?>

	<head>
	    <title><?php echo $title; ?></title>
	   
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
                        <img src="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite_dev/amphitrite/html/img/neptune_amphitrite.jpg" class="mslp" style="display: block; margin-right: auto;  margin-right: auto;  width: 20%;"></img>
                        <!-- <img src="http://www.bom.gov.au/iwk/images/small-artwork.png" class="indigenous"  style="display: block; margin-right: auto;  margin-right: auto;  width: 55%;"/img> -->
                    <h2> 
                    <div class="welcome">
                            <h2><i> Amphitrite: Queen of Atlantis, patron of wave partitions and wife to Poseidon </i></h2>
                            <br>
                            <h5>
                                <ol>
                                    <li><h4>Config check</h4>
                                        <ul>
                                            <li><i>check our configuration file is in line with Active sites in Ofcast</i></li>
                                        </ul>  
                                    </li>
                                    <br>                                        
                                    <li><h4>Sites partition tables</h4>
                                        <ul>
                                            <li><i>drill down to each site to see the current data/run-time available </i></li>
                                        </ul>  
                                    </li>
                                    <br>                                        
                                    <li><h4>Database check</h4>
                                        <ul>
                                            <li><i>state of the database with site info and available run_times </i></li>
                                        </ul>
                                    </li>
                                    <br>
                                    <li><h4>Activate run</h4>
                                        <ul>
                                            <li><i>manually generate new partitions based on latest available data (if automation fails) </i> </li>
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

        

