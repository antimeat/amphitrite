<html>

<?php include('configs.php');?>

<head>
    <title><?php echo $title; ?></title>
    
    <style type="text/css">
        .container-fluid {
            text-align: center;
        }

        .centered-content {
            margin: auto;
            margin-top: 50px;
            display: inline-block;
            text-align: left;
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
	        margin-top: 50px;
        }

    </style>
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>

    <script type="text/javascript">
        $(document).ready(function() {
            document.onkeypress = null
        });            
    </script>
        
</head>

<body>
    <div class="container-fluid">
        <div style="position: relative; top: 100px">
            <div style="width: 1500px; margin: 4px">  
        
                <h1 style="text-align: left;"><i>Activate a manual run:</i></h1>
                <hr>
                            
                <form action='run_script.php' method="POST" onsubmit="showLoader()">
                    <div id="loading" style="display: none">
                        <!-- Loading Image -->
                    </div>
            
                    <fieldset class="centered-content">    
                        <table>
                            <tr>
                                <td><label for="force"><b>Hit it!:</b></label></td>
                                <td style='padding-left:20px;padding-bottom:10px;'><input type="submit" id="force" name="force"/> </td>                   
                            </tr>
                        </table>            
                    </fieldset>
                </form>
            </div>
        </div>
    </div>
</body>
<script>
    function showLoader() {
        document.getElementById("loading").style.display = "block";
        document.getElementById("table").style.display = "none";        
    }
</script>

</html>


