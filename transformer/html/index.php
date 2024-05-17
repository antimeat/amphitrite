<html>
<!DOCTYPE html>

<head>

    <?php
		include('configs.php');		
    ?>

    <title><?php echo $TITLE; ?></title>

    <style align="center" type="text/css">
        fieldset {
	        text-align: left;
	        display: inline-block;
	        vertical-align: middle;
            width: 30%;
        }
        input[type="radio"] {
	        vertical-align: left;
	        horizontal-align: left;
	        padding: 5px;
	        margin-left:10px;		
	        margin: 5px;	
	        margin-top: -5px;
        }

    </style>

	<script type="text/javascript" src="../js/jquery-3.6.0.js"></script>
    <script type="text/javascript" src="../js/jquery-ui/jquery-ui.js"></script>
    <script type="text/javascript" src="../js/moment.min.js"></script>
    <script type="text/javascript" src="../js/underscore-min.js"></script>
    <script type="text/javascript" src="../js/sites.js"></script>

    <link rel="stylesheet" media="all" type="text/css" href="../js/jquery-ui/jquery-ui.css" />
    <link rel="stylesheet" media="all" type="text/css" href="../js/jquery-ui-timepicker-addon.css" />
</head>

<h2 align="center">Transform site</h2>
<h3 align="center">(partition table is the site table defined in Amphitrite)</h3>

<div class="content" align="center">
    
    <body>
        <form align="center" action='run_script.php' method = "POST">

            <fieldset align="center">	
	            <legend align= "center">Input</legend>
	            <table border=0>		
                    <tr><td><hr></td><td><hr></td></tr>
        
                    <tr>
                        <td>
                            Site:
                        </td>
                        <td>
                            <div id="sites" style: "display:inline-block;"></div>
                        </td>
                    </tr> 
                    <tr><td><hr></td><td><hr></td></tr>
   
                    <tr>
	                    <td><label for="theta1">Angle for &#952;<sub>1</sub>: </label></td>
	                    <td><input type="number" id=theta1 name=theta1 size="5" min="0" max="360" value="0"></td>
                    </tr>		
                    <tr>
	                    <td><label for="theta2">Angle for &#952;<sub>2</sub> </label></td>
	                    <td><input type="number" id=theta2 name=theta2 size="5" min="0" max="360" value="0"></td>
                    </tr>		
                    <tr>
	                    <td><label for="theta_split">Angle for &#952;<sub>split</sub> </label></td>
	                    <td><input type="number" id=theta_split name=theta_split size="5" min="0" max="360" value="90"></td>
                    </tr>		
                    <tr>
	                    <td><label for="multi_short">Multiplier (short): </label></td>
	                    <td><input type="number" id=multi_short name=multi_short step="0.01" min="0.20" max="2" value="1.0"></td>
                    </tr>		
                    <tr>
	                    <td><label for="multi_long">Multiplier (long): </label></td>
	                    <td><input type="number" id=multi_long name=multi_long step="0.01" min="0.20" max="2" value="1.0"></td>
                    </tr>		
                    <tr>
	                    <td><label for="attenuation">Period attenuation: </label></td>
	                    <td><input type="number" id=attenuation name=attenuation step="0.05" min="0.50" max="2" value="1.0"></td>
                    </tr>		
                    
                    <tr>
	                    <td><label for="criteria_1">Threshold criteria (m): </label></td>
	                    <td>
                            <input type="number" id=criteria_1 name=criteria_1 step="0.05" min="0.1" max="5" value="3" style="background-color: red">		                        
                            <input type="number" id=criteria_2 name=criteria_2 step="0.05" min="0.1" max="4" value="2.5" style="background-color: gold">		                        
                            <input type="number" id=criteria_3 name=criteria_3 step="0.05" min="0.1" max="3" value="2.0" style="background-color: lightgreen">		                        		                    
	                    </td>
                    </tr>		
                    <tr>
                    <tr><td><hr></td><td><hr></td></tr>
                    <td><label for="save_output">Save output:</label></td>
                        <td><input type="checkbox" id="save_output" name="save_output"></td>
                    </tr>
                    <tr><td><hr></td><td><hr></td></tr>
                            
                </table>
               
                <table>
		            <tr>
			            <td><input type="submit"/> </td>
		            </tr>
	            </table>            
        
            </fieldset>
            <br>
            <br>
            <div align="center">
                <img src=<?php echo($BASE_URL . "/docs/transformer_reference_scenario_legend.png");?> alt="Algorithm" width="50%"/>
            </div>


        </form>

    </body>
</div>

</html>
