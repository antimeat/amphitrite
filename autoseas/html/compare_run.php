<html>

    <?php include('configs.php');?>

    <head>
        <title><?php echo $TITLE; ?></title>
        
        <style type="text/css">
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

         <!-- Replace the slim build with the full version of jQuery -->
        <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
        <!-- <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script> -->

        <!-- Bootstrap 4 CSS CDN -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">    

    </head>

    <body>
        <div class="container-fluid">
            <div style="position: relative; top: 100px;">
                <div style="width: 1200px; margin: 4px;">  
            
                    <h1 style="text-align: left;"><i>Compare algorithms for:</i></h1>
                    <hr>
                    <br>            
                    <form action='run_script.php' method="POST" onsubmit="showLoader()">
                        <div id = "loading" style = "display: none;">
                            <div>
                                <img src = <?php echo($BASE_URL . "autoseas/html/img/loading_icon.gif"); ?> width = 150 height = 100 />
                            </div>
                        </div>
                        <fieldset  class="fieldset" id="table" >    
                            <table>
                                <tr>
                                    <td><label for="sites"><b>Active sites:</b></label></td>
                                    <td style='padding-left:20px;padding-bottom:10px;'>
                                        <select id="sites" name="sites">
                                            <option value="all"></option>
                                        </select>
                                    </td>
                                </tr>
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
        <script>
            function showLoader() {
                document.getElementById("loading").style.display = "block";
                document.getElementById("table").style.display = "none";        
            }

            $(document).ready(function() {
                $.getJSON("<?php echo($BASE_URL . "sites_api.cgi?get=active_sites");?>", function(data) {
                    var sitesDropdown = $("#sites");
                    $.each(data, function(index, siteName) {
                        console.log(siteName);
                        sitesDropdown.append($('<option></option>').attr('value', siteName).text(siteName));
                    });
                });
            });
        </script>
    </body>
    

</html>


