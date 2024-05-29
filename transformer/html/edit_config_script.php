<html>
    <?php 
        include('configs.php');
        
        // get the file and crack it open
        $csv_file = $CONFIG_FILE_NAME;
        $handle = fopen($csv_file, "r");
        $header_comments = array();
        if ($handle) {
            while (($line = fgets($handle)) !== false) {
                // Check if we have a header line "#"
                if (strpos(trim($line), "#") === 0 || strpos(trim($line), "##################################################################################################################################") === 0) {
                    $header_comments[] = trim($line);
                }
            }
            fclose($handle);
        } else {
            // Error opening the file
            echo "Error opening the file.";
        }

        $header_comments = implode("\n", $header_comments); // Convert the array to a single string
    ?>

    <head>
        <title><?php echo $title; ?></title>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>

        <!-- Bootstrap 4 CSS CDN -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    </head>

    <body>
        <div class="container-fluid">
        <div style="position: relative; top: 100px">
            <form class="col-sm-12" action="run_edit_config_script.php" method="POST" onsubmit="return tableToCSV();">
                <div id = "loading" style = "display: none;">
                    <div>
                        <img src = <?php echo($BASE_URL . "html/img/loading_icon.gif");?> width = 150 height = 100 />
                    </div>
                </div>
                        
                <div class="row form-group col-sm-10">
                    <div class="col-sm-12">
                        <textarea class="form-control" rows="10" readonly><?php echo htmlspecialchars($header_comments); ?></textarea>
                    </div>
                </div>

                <div class="row form-group col-sm-10">
                    <div class="table-responsive w-100">
                        <?php
                            // Check if the file exists and is readable to prevent errors
                            if (!file_exists($csv_file) || !is_readable($csv_file)) {
                                echo "<p>File not found or not readable</p>";
                                return; // Exit the function if the file can't be opened
                            }

                            // Attempt to open the CSV file
                            $handle = fopen($csv_file, "r");
                            if (!$handle) {
                                echo "<p>Error opening the file.</p>";
                                return; // Exit the function if the file handle isn't obtained
                            }

                            echo "<table class='table table-bordered table-hover caption-top' id='editableTable'>\n";
                            echo "<thead>\n";
                            $counter = 0; // Define a counter to identify the header row

                            // Loop through the CSV rows
                            while (($data = fgetcsv($handle)) !== FALSE) {
                                // Skip lines starting with '#' (commented out lines in the CSV)
                                if (strpos($data[0], "#") === 0) {
                                    continue;
                                }

                                // Distinguish between header and data rows
                                if ($counter == 0) {
                                    echo "<tr class='table-header'>\n"; // Use class for styling if needed
                                    echo "<th>site_name</th>\n";
                                    echo "<th>theta_split</th>\n";
                                    echo "<th>theta_1</th>\n";
                                    echo "<th>theta_2</th>\n";
                                    echo "<th>multi_short</th>\n";
                                    echo "<th>multi_long</th>\n";
                                    echo "<th>attenuation</th>\n";
                                    echo "<th>criteria_1</th>\n";
                                    echo "<th>criteria_2</th>\n";
                                    echo "<th>criteria_3</th>\n";                                
                                    echo "</tr>\n";
                                    echo "</thead>\n<tbody>\n"; // Close the header and start the body
                                } else {
                                    echo "<tr>\n";
                                    foreach ($data as $cell) {
                                        echo "<td contentEditable='true'>" . htmlspecialchars($cell) . "</td>\n"; // Simplified class usage
                                    }
                                    echo "</tr>\n";
                                }
                                $counter++; // Increment counter after processing each row
                            }
                            echo "</tbody>\n</table>\n"; // Close the table body and the table

                            fclose($handle); // Close the CSV file handle
                        ?>
                    </div>    
                </div>
                <input type="hidden" id="data" name="data">
                <input type="hidden" id="header_comments" name="header_comments" value="<?php echo htmlspecialchars($header_comments); ?>">
                
                <div class="row flex justify-content-left">
                    <div class="col-sm-2">
                        <button type="button" onclick="insertAbove()" class="btn btn-primary btn-save btn-block" style="margin-top: 20px;">Insert above</button>
                    </div>
                    <div class="col-sm-2">
                        <button type="button" onclick="insertBelow()" class="btn btn-primary btn-save btn-block" style="margin-top: 20px;">Insert below</button>
                    </div>
                    <div class="col-sm-2">
                        <button type="button" onclick="deleteRow()" class="btn btn-primary btn-save btn-block" style="margin-top: 20px;">Delete row</button>
                    </div>
                    <div class="col-sm-2">
                        <button type="button" onclick="reverseTableRows()" class="btn btn-primary btn-save btn-block" style="margin-top: 20px;">Reverse Rows</button>
                    </div>
                </div>
                <br>
                <br>
                <div class="row flex justify-content-left">        
                    <div class="col-sm-1">
                        <button type="submit" class="btn btn-success btn-save btn-block" style="margin-top: 20px;">Save</button>
                    </div>
                    <div class="col-sm-11 input-group mt-3">
                        <div class="input-group-prepend">
                            <span class="input-group-text" id="basic-addon5">filename</span>
                            <input type="text" id="filename" name="filename" value="<?php echo basename($csv_file); ?>" disabled>                    
                        </div>                        
                    </div>
                    
                </div>
            </form>         
        </div>
        </div>

        <script type="text/javascript">
            var selectedRow = null;

            $(document).ready(function() {
                // Initialize row selection handling
                $('#editableTable').on('click', 'tr', function() {
                    selectedRow = $(this).index() + 1;
                    console.log("Row selected: " + selectedRow); // Debugging output
                });

                $('#editableTable').on('blur', 'td', function() {
                    var content = $(this).text();
                    if (content.includes('.')) {
                        $(this).text(parseFloat(content).toFixed(3));
                    }                    
                });
            });

            function showLoader() {
                document.getElementById("loading").style.display = "block";
                // document.getElementById("table").style.display = "none";        
            }

            function tableToCSV() {
                var csv_data = [];
                var cell_str = "";
                var rows = document.getElementById('editableTable').getElementsByTagName('tr');
                console.log(rows.length);
                for (var i = 0; i < rows.length; i++) {
                    // Change this line to include 'th' elements as well
                    var cols = rows[i].querySelectorAll('th, td');

                    var csvrow = [];
                    for (var j = 0; j < cols.length; j++) {
                        cell_str = cols[j].innerHTML;
                        cell_str = cell_str.replace(/\r/g, ''); // remove any carriage returns
                        csvrow.push(cell_str);
                    }
                    csv_data.push(csvrow.join(","));
                }

                csv_data = csv_data.join("\n");

                // Put the CSV data into the hidden form field
                document.getElementById('data').value = csv_data;

                showLoader();
                
                // Allow the form to submit
                return true;
            }

            function addEditableCells(row) {
                var cellCount = $('#editableTable tr').eq(0).find('th').length; // Get the number of columns from the header row
                for (var i = 0; i < cellCount; i++) {
                    var cell = row.insertCell(i);
                    cell.contentEditable = 'true'; // Make cell editable
                }
            }

            function insertAbove() {
                if (selectedRow !== null) {
                    var table = document.getElementById("editableTable");
                    var row = table.insertRow(selectedRow);
                    addEditableCells(row);
                } else {
                    alert("No row selected");
                }
            }

            function insertBelow() {
                if (selectedRow !== null) {
                    var table = document.getElementById("editableTable");
                    var row = table.insertRow(selectedRow + 1);
                    addEditableCells(row);
                } else {
                    alert("No row selected");
                }
            }

            function deleteRow() {
                if (selectedRow !== null) {
                    var table = document.getElementById("editableTable");
                    if (table.rows.length > 1) {  // Keep at least one row for data entry
                        table.deleteRow(selectedRow);
                    }
                    selectedRow = null;  // Reset selected row
                } else {
                    alert("No row selected");
                }
            }

            function reverseTableRows() {
                var table = document.getElementById("editableTable");

                // Get all the rows in the table, except the header row
                var rows = Array.from(table.rows).slice(1);

                // Reverse the array of rows
                rows = rows.reverse();

                // Remove all rows, except the header row, from the table
                while(table.rows.length > 1) {
                    table.deleteRow(1);
                }

                // Append each row back to the table in reverse order
                for (var i = 0; i < rows.length; i++) {
                    table.appendChild(rows[i]);
                }
            }

        </script>

        <!-- Bootstrap 4 JS CDN -->
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>

    </body>
</html>
