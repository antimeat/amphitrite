
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
                position: absolute;
                top: 150px;                
                opacity: 1;
            }
            
            .welcome {
                position: absolute;
                top: 650px;                
                opacity: 1;
            }
            
            
        </style>

    </head>
    
    <body>
        
        <div class="container-fluid">
            <div style="position: relative; top: 100px">
                
                    <h1 style="text-align: left;"><i><p style="text-align: right;"></font></p>Welcome</i></h1>
                    <hr><br>
                        <img src="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/html/img/neptune_amphitrite.jpg" class="mslp" style="display: block; margin-right: auto;  margin-right: auto;  width: 30%;"></img>
                        <!-- <img src="http://www.bom.gov.au/iwk/images/small-artwork.png" class="indigenous"  style="display: block; margin-right: auto;  margin-right: auto;  width: 55%;"/img> -->
                    <h2> 
                    <div class="welcome">
                            <h2><i> Amphitrite was Queen of Atlantis, wife to Nepture, and the patron of wave partitions! </i></h2>
                            <br>
                            <h5>
                                <ol>
                                    <li>Config check
                                    <ul>
                                        <li>check our configuration file is in line with Active sites in Ofcast</li>
                                    </ul>  
                                    </li>
                                    <li>Sites list
                                    <ul>
                                        <li>the current list of database site partitions using the latest available time for that site </li>
                                    </ul>  
                                    <li>Database check
                                    <ul>
                                        <li>Print out the state of the database with saved sites and the available run_times </li>
                                    </ul>
                                    </li>
                                    <li>Activate run
                                    <ul>
                                        <li>manually generate the wave partions based on Active Ofcast sites that are in the configuration file </li>
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

        

