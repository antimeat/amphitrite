<html>
    <?php include('configs.php');?>

    <head>
	    <title><?php echo $TITLE; ?></title>
	</head>

    <script>
        function syncBackgroundColor() {
            var iframe = document.getElementById('iframeID');
            var iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
            var bgColor = iframeDocument.body.style.backgroundColor;

            // If the background color is not set directly via the style attribute,
            // you may need to compute it instead
            if (!bgColor) {
                bgColor = window.getComputedStyle(iframeDocument.body, null).getPropertyValue('background-color');
            }

            document.getElementById('index').style.backgroundColor = bgColor;
        }
    </script>

    <body>
    
        <div class="container-fluid" id="index">
            <div style="position: relative; top: 100px; height:2500px">
                <div class="embed-responsive embed-responsive-1by1">
                    <!-- <iframe class="embed-responsive-item" src="http://wa-aifs-local.bom.gov.au/vulture/dev/index.php"></iframe> -->
                    <iframe class="embed-responsive-item" src="index.php"></iframe>
                </div>                   
            </div>
        </div>                    
        
    </body>

</html>

