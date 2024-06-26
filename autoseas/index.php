<?php

    define("WIND_DIRECTION_STEP", 10);
    define("MAX_WIND_DIRECTION", 350);
    $WIND_DIRS = range(0, MAX_WIND_DIRECTION, WIND_DIRECTION_STEP);
    $fields = array("windDir", "fetch", "depth");

	function siteToFileName($str) {
		return str_replace(" ", "_", $str) .".csv";
	}
	
	function fileToSiteName($str) {
		return str_replace("_", " ", substr($str, 0, -4));
	}
	
	function getSiteNames($dir) {
		// read the list of csv files in this dir, these are the site names
		$h = opendir($dir);
		while(false !== ($entry = readdir($h))) {
			// only list csv files and non backup ones
			if ((strpos($entry, ".csv") > 0) AND (strpos($entry, "___") === FALSE)) {
				$files[] = fileToSiteName($entry);
			}
		}
		sort($files);
		return $files;
	}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Auto Seas</title>

    <!-- Updated jQuery from CDN -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
    <script type="text/javascript" src="js/index.js?<?php echo time(); ?>"></script>
    <script type="text/javascript" src="js/cookie_stuff.js"></script>
    <?php
        // Include your configuration settings
        include('html/configs.php');
    ?>

    <script>
        // Declare JavaScript variables and assign PHP values to them
        var BASE_DIR = "<?php echo $BASE_DIR; ?>";
        var BASE_URL = "<?php echo $BASE_URL; ?>";
        var BASE_HTML = "<?php echo $HTML_DIR; ?>";
        var TITLE = "<?php echo $TITLE; ?>";

        // Now you can use these variables in your JavaScript code
        console.log(BASE_DIR, BASE_URL, BASE_HTML, TITLE);
    </script>
    
    <script>

        function setCookie(name, value)
        {
            var today = new Date();
            var expiry = new Date(today.getTime() + 1 * 12 * 3600 * 1000); // plus 12 hours

            document.cookie=name + "=" + escape(value) + "; path=/; expires=" + expiry.toGMTString();
        }

        function getCookie(name)
        {
            var re = new RegExp(name + "=([^;]+)");
            var value = re.exec(document.cookie);
            return (value != null) ? unescape(value[1]) : null;
        }


        function storeValues()  
        {
            setCookie("sessionID", document.getElementById("session").value);
            return true;
        }
    </script>

    <!-- Modernized CSS -->
	<style>
    /* Simplified and Streamlined CSS */
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: #333;
    background-color: #f4f4f4;
    padding: 20px;
    margin: 0;
}

.modal {
    display: none;
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0,0,0,0.4);
}

.modal-content, .container {
    background-color: #fefefe;
    margin: 15% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 80%;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
}

.close:hover, .close:focus {
    color: black;
    text-decoration: none;
    cursor: pointer;
}

.outer-container, .flex-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
}

.inner-container, .settings, .editLinkContainer, .actions {
    padding: 20px;
    margin: 10px 0;
    border: 1px solid #ddd;
    border-radius: 8px;
}

select, input[type="text"], textarea {
    width: 100%;
    padding: 0px;
    margin: 10px 0;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
}

.btn, a {
    display: inline-block;
    /* background-color: #007bff; */
    background-color: #4CAF50; /* Changed to green */
    color: white;
    padding: 8px 12px;
    margin-right: 10px;
    border-radius: 4px;
    text-decoration: none;
    transition: background-color 0.3s;
}

.btn:hover, a:hover {
    /* background-color: #0056b3; */
    background-color: #367c39;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

table, th, td {
    text-align: "center";
    border: 1px solid #ddd;
    padding: 0px; /* Adjusted padding */
}

th {
    background-color: #4CAF50;
    color: white;
}

.flex-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between; /* Adjusts spacing between child elements */
    margin-top: 20px; /* Space above the container */
}

.container, .settings {
    flex: 1; /* Allows each container to grow equally */
    padding: 20px;
    margin: 10px; /* Space between containers */
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    min-width: 300px; /* Minimum width to prevent containers from becoming too narrow */
    background-color: rgba(255,255,255);

}
@media (max-width: 768px) {
    .inner-container, .settings, .editLinkContainer, .actions {
        width: 100%;
    }
    .flex-container {
        flex-direction: column; /* Stack the containers on smaller screens */
    }
    .container {
        width: 100%; /* Full width containers on smaller screens */
        margin-bottom: 20px; /* Space between stacked containers */
    }
}

    </style>
</head>
<body>  

    <div class = "outer-container">    
        <div class = "algorithmInfo">
            <div class="container actions">
                <div id="session_box" class="container">
                    Session: <input type="text" size="10" id="session" style="width: 50%">
                    <button type="button" onclick="storeValues()" id="button" name="button" class="btn">Set Cookie</button>
                </div>
                <div class="container actions flex" style="display: flex; align-items: right; width: 80%;">
                    <!-- Radio buttons for Server choice -->
                    <span>Ofcast server:<br> </span>
                    <form id="serverChoice" style="display: flex; align-items: right; width: 100%;">
                        <label><input type="radio" name="serverSelect" value="op"> <b>operations</b></label>
                        <label><input type="radio" name="serverSelect" value="dev" checked> <b>develpoment</b></label>
                    </form>
                </div>
            </div>
            <div class="container actions">
                <div class="container actions flex" sytle="flex; align-items: right; width: 80%;">
                    Site: <select id="siteSelect" style="width: 80%"></select>
                </div>
            
                <div class="container actions flex" style="width: 80%;">
                    <!-- Radio buttons for algorithm choice -->
                    <h3>Algorithm</h3>
                    <form id="algorithmChoice">
                        <label><input type="radio" name="algorithm" value="holthuijsen" checked> Breugem Holthuijsen</label>
                        <label><input type="radio" name="algorithm" value="bretschneider"> Bretschneider</label>
                        <label><input type="radio" name="algorithm" value="shallow"> Shallow</label>
                    </form>
                </div>
                <div class="container actions flex" style="width: 80%;">
                    <a href="javascript:loadWinds()">Load Winds</a>
                    <a href="javascript:refreshSeas()">Calc Seas</a>                
                </div>                
            </div>
            
            <!-- <div class="container actions">
                <a href="edit_fetch_limits.php">Edit Fetch Limits</a>
            </div> -->
        </div>
        <div class="settings">
            <h1>Autoseas: calculate seas </h1><br>
            <div class="algorithmInfo">
                <h2>Algorithm Information & Changes</h2>
                
                <section>
                    <h3>Changes 2023</h3>
                    <ul>
                        <li>implement and use the Breugem-Holthuijsen algorithm as the default.</li>                    
                    </ul>
                </section>

                <section>
                    <h3>Changes 2017</h3>
                    <ul>
                        <li>Enable paste of ht, period, and direction.</li>
                    </ul>
                </section>

                <section>
                    <h3>Changes August 2015</h3>
                    <ul>
                        <li>Wind weights: 75% of previous if speeds decreasing, 75% of new if speeds increasing.</li>
                        <li>When 'use varying decay factor' ticked: decay over time dependent on fetch. 0.7 at 25 nm to 0.9 at 100nm.</li>
                        <li>Wind is applied to bins out to 80 degrees from wind direction but decreased with a factor of cos(angle diff) ** 2.</li>
                    </ul>
                </section>
            </div>
        </div>

    </div>    

    <div class="flex-container">
        <div id="fetchTable" class="container">
            <h3>Fetch Limits</h3>
        </div>
        <div id="windsTableContainer" class="container">
            <h3>Winds</h3> <!-- Title for the winds Table -->
        </div>
        <div class="container">
            <div>
                Seas:<br>
                <textarea id="seasCopy" rows="4"></textarea></br>
            </div>                
            <div>
                Seas, period, and direction:<br>
                <textarea id="seasAndDirCopy" rows="4"></textarea></br>
            </div>
            <div>
                Seas and no range period:<br>
                <textarea id="seasAndPeriodCopy" rows="4"></textarea></br>
            </div>
        </div>        
    </div>      
    
    <!-- The Modal -->
    <div id="errorModal" class="modal" style="display:none;">
        <!-- Modal content -->
        <div class="modal-content">
            <span class="close">&times;</span>
            <p id="errorMessage">An error occurred.</p>
        </div>
    </div>

</body>
</html>
