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
        /* The Modal (background) */
        .modal {
            display: none; /* Hidden by default */
            position: fixed; /* Stay in place */
            z-index: 1; /* Sit on top */
            left: 0;
            top: 0;
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            overflow: auto; /* Enable scroll if needed */
            background-color: rgb(0,0,0); /* Fallback color */
            background-color: rgba(0,0,0,0.4); /* Black w/ opacity */
        }

        /* Modal Content */
        .modal-content {
            background-color: #fefefe;
            text-align: "center";
            margin: 15% auto; /* 15% from the top and centered */
            padding: 20px;
            border: 1px solid #888;
            width: 30%; /* Could be more or less, depending on screen size */
            border-radius: 30px; /* Rounded edges */
        }

        /* The Close Button */
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
        }

        .close:hover,
        .close:focus {
            color: black;
            text-decoration: none;
            cursor: pointer;
        }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            color: #333;
            background-color: #f4f4f4;
            padding: 20px;
            margin: 0;
        }

        /* Style for the outer flex container */
        .outer-container {
            display: flex;
            flex-direction: row; /* Align children side by side */
            justify-content: flex-start; /* Adjust spacing as needed */
            align-items: flex-start; 
            flex-wrap: wrap;
            padding: 20px;

        }

        /* Style for the outer flex container */
        .inner-container {
            display: flex;
            min-width: 20%;
            height: 20%;
            padding: 20px;
            flex-direction: column;
            justify-content: flex-start; /* Adjust spacing as needed */
            align-items: flex-start; 
            flex-wrap: wrap;
        }

        .flex-container {
            min-height: 100px;
            display: flex; /* Enables flexbox layout */
            align-items: center; /* Aligns items vertically in the center */
            flex-wrap: wrap;
        }

        .flex-container > div {
            margin-right: 10px; /* Adds some space between the div elements */
            min-height: 60px;
        }

        /* Adjust this as necessary for your layout */
        #fetchTable, .container {
            /* Ensures that the fetchTable has a similar style and width as other containers */
            min-width: 300px; /* Adjust this value as needed */
            width: 100%;
            height: 100%;
            margin-top: 20px;
            padding: 20px;
            border: 1px solid #ddd;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-radius: 8px;
            justify-content: flex-start; /* Spaces the child elements evenly */
            align-items: flex-start; /* Aligns items at the start of the container */
            flex-wrap: wrap;
        }

        .tables-container {
            width: 50%;
            display: flex;
            justify-content: flex-start; /* Spaces the child elements evenly */
            align-items: flex-start; /* Aligns items at the start of the container */
            flex-wrap: wrap;
        }
        
        .container, .site, .settings, #fetchTable, .seasCopyContainer, .editLinkContainer, .algorithmInfo {
            background-color: #fff;
            border: solid 1px #ddd;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 60px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-radius: 8px;
            margin-top: 20px;
            min-width: 300px;     
            justify-content: flex-start; /* Spaces the child elements evenly */
            align-items: flex-start; /* Aligns items at the start of the container */
            flex-wrap: wrap;       
        }

        a {
            color: #007bff;
            text-decoration: none;
            background-color: #f8f9fa;
            padding: 8px 12px;
            border-radius: 5px;
            border: 1px solid #ddd;
            margin-right: 5px;
            transition: background-color 0.2s, color 0.2s;
        }

        a:hover {
            background-color: #e2e6ea;
            color: #0056b3;
        }

        /* New button style */
        .btn {
            display: inline-block;
            background-color: #007bff;
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            border: none; /* No border for button */
            cursor: pointer; /* Change cursor to pointer on hover */
            transition: background-color 0.3s ease;
        }

        .btn:hover {
            background-color: #0056b3;
        }

        /* Adjust input[type="text"] width if necessary */
        input[type="text"] {
            height: 30px;
            width: auto; /* Adjust based on your layout needs */
            padding: 4px 12px;
            margin-right: 10px; /* Ensures some space between the input and the button */
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }

        textarea {
            width: 100%;
            min-width: 300px;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
            justify-content: flex-end; /* Spaces the child elements evenly */
            align-items: flex-end; /* Aligns items at the start of the container */
            flex-wrap: nowrap;
        }

        select {
            width: 70%;
            height: 40px;
            min-width: 200px;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
            justify-content: flex-end; /* Spaces the child elements evenly */
            align-items: flex-end; /* Aligns items at the start of the container */
            flex-wrap: nowrap;
        }

        .flex-container {
            display: flex;
            align-items: flex-start;
            flex-wrap: nowrap; /* Prevents wrapping, ensuring elements stay in a single line */
        }

        .actions a, .editLinkContainer a {
            display: inline-block;
            background-color: #007bff;
            color: white;
            transition: background-color 0.3s ease;
        }

        .actions a:hover, .editLinkContainer a:hover {
            background-color: #0056b3;
        }

        table {
            min-width: 300px; /* Adjust this value as needed */
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        table, th, td {
            border: 1px solid #ddd;
            padding: 0px;
            text-align: left;
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        .table-container {
            overflow-x: auto;
        }

        .settings {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            padding: 20px;

        }

        .settings > div, .settings > form {
            width: 50%;
            margin-top: 10px;
            padding: 20px;

        }

        .algorithmInfo ul {
            padding-left: 20px;
            list-style-type: disc;
        }

        @media (max-width: 768px) {
            .settings, .editLinkContainer, .seasCopyContainer {
                width: 50%;
            }
        }
    
    </style>
</head>
<body>  

    <div class = "outer-container">    
        <div class="settings">
            <h1>Autoseas: calculate seas </h1><br>
            <div class="algorithmInfo">
                <h2>Algorithm Information & Changes</h2>
                
                <section>
                    <h3>Changes 2023</h3>
                    <ul>
                        <li>implement and use the Breugem-Holthuijsen algorithm as the default <a href="https://repository.oceanbestpractices.org/bitstream/handle/11329/121/702_en_for_approval.pdf?sequence=4&isAllowed=y" target="_blank">article</a>.</li>                    
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

        <div class = "inner-container">
            <div class="container">
                Site: <select id="siteSelect"></select>
            </div>
            <div id="session_box" class="container">
                Session: <input type="text" size="10" id="session">
                <button type="button" onclick="storeValues()" id="button" name="button" class="btn">Set Cookie</button>
            </div>
            <div class="container actions">
                <a href="javascript:loadWinds()">Load Winds</a>
                <a href="javascript:refreshSeas()">Calc Seas</a>
            </div>
            <div class="container actions">
                <a href="edit_fetch_limits.php">Edit Fetch Limits</a>
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
