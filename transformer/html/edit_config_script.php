<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $title; ?></title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <!-- Bootstrap 4 CSS CDN -->
    <link rel="stylesheet" href="http://wa-vw-er/webapps/er_ml_projects/bootstrap/css/bootstrap.min.css">
    <style>
        #loading {
            display: none;
            position: fixed;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            z-index: 1000;
        }
        .table tbody tr td {
            padding: 4px;
            font-size: 14px;
        }
        .table thead tr th {
            padding: 4px;
            font-size: 14px;
            cursor: pointer; /* Add cursor to indicate sortable columns */
        }
        .form-group-padding {
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <?php 
        include('configs.php');
        
        // get the file and crack it open
        $csv_file = $CONFIG_FILE_NAME;
        $handle = fopen($csv_file, "r");
        $header_comments = array();
        if ($handle) {
            while (($line = fgets($handle)) !== false) {
                // Check if we have a header line "#"
                if (strpos(trim($line), "#") === 0 || strpos(trim($line), "") === 0) {
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

    <div class="container-fluid">
        <div style="position: relative; top: 100px">
        
            <form class="col-sm-12" action="run_edit_config_script.php" method="POST" onsubmit="return onSubmitForm();">
                <div id="loading" style="display: none;">
                    <div>
                        <img src="<?php echo($BASE_URL . "transformer/html/img/loading_icon.gif");?>" width="150" height="100" />
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

                            echo "<table class='table table-bordered table-hover caption-top' id='sitesTable'>\n";
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
                                    echo "<th onclick='sortTable(0)'>site_name</th>\n";
                                    echo "<th onclick='sortTable(1)'>theta_split</th>\n";
                                    echo "<th onclick='sortTable(2)'>theta_1</th>\n";
                                    echo "<th onclick='sortTable(3)'>theta_2</th>\n";
                                    echo "<th onclick='sortTable(4)'>multi_short</th>\n";
                                    echo "<th onclick='sortTable(5)'>multi_long</th>\n";
                                    echo "<th onclick='sortTable(6)'>attenuation</th>\n";
                                    echo "<th onclick='sortTable(7)'>criteria_1</th>\n";
                                    echo "<th onclick='sortTable(8)'>criteria_2</th>\n";
                                    echo "<th onclick='sortTable(9)'>criteria_3</th>\n";                                
                                    echo "</tr>\n";
                                    echo "</thead>\n<tbody>\n"; // Close the header and start the body
                                    echo "<tr>\n";
                                    foreach ($data as $cell) {
                                        echo "<td contentEditable='true'>" . htmlspecialchars($cell) . "</td>\n"; // Simplified class usage
                                    }
                                    echo "</tr>\n";
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
            $('#sitesTable').on('click', 'tbody tr', function() {
                selectedRow = $(this).index();
                console.log("Row selected: " + selectedRow); // Debugging output
            });

            // Ensure all cells are editable after page load
            $('#sitesTable tbody tr').each(function() {
                makeCellsEditable(this);
            });

            // Log the initial row count for debugging
            console.log("Initial row count (excluding header): " + $('#sitesTable tbody tr').length);
        });

        function tableToTextareas() {
            var sites = [];
            $('#sitesTable tbody tr').each(function() {
                var row = [];
                $(this).find('td').each(function() {
                    row.push($(this).text().trim());
                });
                sites.push(row.join(', '));
            });
            $('#data').val(sites.join('\n'));

            return true;
        }

        function makeCellsEditable(row) {
            $(row).find('td').attr('contentEditable', 'true');
        }

        function addEditableCells(row) {
            var cellCount = $('#sitesTable thead tr th').length; // Get the number of columns from the header row
            for (var i = 0; i < cellCount; i++) {
                var cell = row.insertCell(i);
                cell.contentEditable = 'true'; // Make cell editable
            }
        }

        function insertAbove() {
            if (selectedRow !== null) {
                var table = document.getElementById("sitesTable").getElementsByTagName('tbody')[0];
                var row = table.insertRow(selectedRow);
                addEditableCells(row);
            } else {
                alert("No row selected");
            }
        }

        function insertBelow() {
            if (selectedRow !== null) {
                var table = document.getElementById("sitesTable").getElementsByTagName('tbody')[0];
                var row = table.insertRow(selectedRow + 1);
                addEditableCells(row);
            } else {
                alert("No row selected");
            }
        }

        function deleteRow() {
            if (selectedRow !== null) {
                var table = document.getElementById("sitesTable").getElementsByTagName('tbody')[0];
                if (table.rows.length > 1) {  // Keep at least one row for data entry
                    table.deleteRow(selectedRow);
                }
                selectedRow = null;  // Reset selected row
            } else {
                alert("No row selected");
            }
        }

        function reverseTableRows() {
            var table = document.getElementById("sitesTable").getElementsByTagName('tbody')[0];

            // Get all the rows in the table
            var rows = Array.from(table.rows);

            // Reverse the array of rows
            rows.reverse();

            // Remove all rows from the table
            while (table.rows.length) {
                table.deleteRow(0);
            }

            // Append each row back to the table in reverse order and set contentEditable
            for (var i = 0; i < rows.length; i++) {
                var newRow = table.insertRow();
                for (var j = 0; j < rows[i].cells.length; j++) {
                    var newCell = newRow.insertCell(j);
                    newCell.innerHTML = rows[i].cells[j].innerHTML;
                    newCell.setAttribute('contentEditable', 'true');
                }
            }

            // Log the row count after reversing for debugging
            console.log("Row count after reversing (excluding header): " + $('#sitesTable tbody tr').length);
        }

        function showLoader() {
            document.getElementById("loading").style.display = "block";
            document.getElementById("sitesTable").style.display = "none";
        }

        function onSubmitForm() {
            tableToTextareas();
            showLoader();
            return true;
        }

        function sortTable(columnIndex) {
            var table = document.getElementById("sitesTable").getElementsByTagName('tbody')[0];
            var rows = Array.from(table.rows);
            var sortedRows = rows.sort((a, b) => {
                var aText = a.cells[columnIndex].innerText.trim().toLowerCase();
                var bText = b.cells[columnIndex].innerText.trim().toLowerCase();
                return aText.localeCompare(bText);
            });

            // Remove all rows from the table
            while (table.rows.length) {
                table.deleteRow(0);
            }

            // Append sorted rows back to the table and make cells editable
            sortedRows.forEach(row => {
                table.appendChild(row);
                makeCellsEditable(row);
            });
        }
    </script>

    <!-- jQuery, Popper.js, and Bootstrap JS via jsDelivr CDN -->
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js"></script>	

</body>
</html>
