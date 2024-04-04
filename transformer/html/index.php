<html>
<!DOCTYPE html>

<head>

    <?php
		include('configs.php');		
    ?>

    <title><?php echo $TITLE; ?></title>

    <style align="center" type="text/css">
        .container {
            text-align: center;		
	        width: 500;
	        clear: both;		
        }
        .container input {
	        text-align: left;		
	        width: 100%;
	        clear: both;
        }

        fieldset {
	        text-align: left;
	        display: inline-block;
	        vertical-align: middle;
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

<h2 align="center">Modified wave tables</h2>

<div class="content" align="center">
    
    <body>
        <form align="center" action='run_script.php' method = "POST">

            <fieldset align="center">	
	            <legend align= "center">Input</legend>
	            <table border=0>		
                    <tr>
                        <td>
                            Site:
                        </td>
                        <td>
                            <div id="sites" style: "display:inline-block;"></div>
                        </td>
                    </tr>    
                    <tr>
                        <td>
                            Table:
                        </td>
                        <td>
                            <div id="tables" style: "display:inline-block;">
                            </div>
                        </td>
                    </tr>    
                    <tr>
	                    <td><label for="theta1">Angle for western side: </label></td>
	                    <td><input type="number" id=theta1 name=theta1 size="5" min="0" max="360" value="180"></td>
                    </tr>		
                    <tr>
	                    <td><label for="theta2">Angle for eastern side: </label></td>
	                    <td><input type="number" id=theta2 name=theta2 size="5" min="0" max="360" value="180"></td>
                    </tr>		
                    <tr>
	                    <td><label for="multiplier">Multiplier: </label></td>
	                    <td><input type="number" id=multiplier name=multiplier step="0.05" min="0.20" max="2" value="1.0"></td>
                    </tr>		
                    <tr>
	                    <td><label for="attenuation">Period attenuation: </label></td>
	                    <td><input type="number" id=attenuation name=attenuation step="0.05" min="0.50" max="2" value="1.0"></td>
                    </tr>		
                    
                    <tr>
                        <td>
                            <label name="modelLabel">Model: </label>
                        </td>
                        <td>           
                            <select name="model">
                                <option value="long">Auswave long</option>		
                                <option value="short">Auswave short</option>		                            
                                <option value="ec">EC wave</option>		                            
                            </select>
                        </td>
                    </tr>
                    <tr>
	                    <td><label for="criteria_1">Threshold criteria (m) (colour highlights): </label></td>
	                    <td>
                            <input type="number" id=criteria_1 name=criteria_1 step="0.05" min="0.1" max="5" value="3" style="background-color: red">		                        
                            <input type="number" id=criteria_2 name=criteria_2 step="0.05" min="0.1" max="4" value="2.5" style="background-color: gold">		                        
                            <input type="number" id=criteria_3 name=criteria_3 step="0.05" min="0.1" max="3" value="2.0" style="background-color: lightgreen">		                        		                    
	                    </td>
                    </tr>		
                       
                </table>
               
                <table>
		            <tr>
			            <td><input type="submit"/> </td>
		            </tr>
	            </table>            
        
            </fieldset>

        </form>

    </body>
</div>

</html>
