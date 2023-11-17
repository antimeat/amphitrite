
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
                top: 800px;                
                opacity: 1;
            }
            
            
        </style>

    </head>
    
    <?php
        $fp = fopen($fileName, "r");
        $content = fread($fp, filesize($fileName));
        $lines = explode("::", $content);
        $date = $lines[0];
        fclose($fp);        
    ?>
    
    <body>
        
        <div class="container-fluid">
            <div style="position: relative; top: 100px">
                
                    <h1 style="text-align: left;"><i><p style="text-align: right;"> <font color="lightgrey" size="4"><?php echo('Sites list last updated: ' . $date) ?></font></p>Welcome</i></h1>
                    <hr><br><br>
                        <img src="http://www.bom.gov.au/difacs/IDX0894.gif" class="mslp" style="display: block; margin-right: auto;  margin-right: auto;  width: 55%;"></img>
                        <!-- <img src="http://www.bom.gov.au/iwk/images/small-artwork.png" class="indigenous"  style="display: block; margin-right: auto;  margin-right: auto;  width: 55%;"/img> -->
                    <h2> 
                        <div class="welcome">
                            <H2> Acknowledgment of Country </H2>
                            <h5><i>The Bureau of Meteorology acknowledges the Traditional Owners and Custodians of Country throughout Australia and acknowledges their continuing connection to land, sea and community. We recognise the continuation of cultural and weather knowledge practices of Aboriginal and Torres Strait Islander peoples. We pay our respects to the people and their Elders past and present.</i></h5>
                            <br>
                            <!--
                            <?php 
                                foreach($welcome as $note) {
                                    if (ctype_space($note) == false) {
                                        echo($note."<br>");
                                    }
                                }
                            ?>
                            -->
                        </div>
                        
                    </h2>
                </div>         
            </div>
        </div>        
    </body>
</html>

        

