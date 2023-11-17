
<html>
    <?php include('configs.php');?>

	<head>
	    <title><?php echo $title; ?></title>
	</head>
	
    <?php
        $fp = fopen($fileName, "r");
        $content = fread($fp, filesize($fileName));
        $lines = explode("::", $content);
        $date = $lines[0];
        $name = explode("\n",$lines[1]);
        $name = array_filter($name, function($hash) {return strcmp(trim($hash)[0],'#') !== 0;}); 
        $welcome = explode("\n",$lines[2]);
        $welcome = array_filter($welcome, function($hash) {return strcmp(trim($hash)[0],'#') !== 0;}); 
        $notes = explode("\n",$lines[3]);
        $notes = array_filter($notes, function($hash) {return strcmp(trim($hash)[0],'#') !== 0;}); 
        $summary = explode("\n",$lines[4]);
        $summary = array_filter($nsummary, function($hash) {return strcmp(trim($hash)[0],'#') !== 0;}); 
        fclose($fp);        
    ?>
    
    <body>
        <div class="container-fluid">
            <div style="position: relative; top: 100px">
                <div style="width: 1200px; margin: 4px">  
                    <h1 style="text-align: left;"><i><p style="text-align: right;"> <font color="lightgrey" size="4"><?php foreach($name as $n) {if (ctype_space($n) == false) {echo($n);}}echo(', ' . $date) ?></font></p>Welcome</i></h1>
                    <hr><br><br>
                    <h2> 
                        <?php 
                            foreach($welcome as $note) {
                                if (ctype_space($note) == false) {
                                    echo($note."<br>");
                                }
                            }
                        ?>
                        
                    </h2>
                </div>         
            </div>
        </div>        
    </body>
</html>

        

