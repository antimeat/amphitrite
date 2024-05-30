<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $TITLE; ?></title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <!-- Bootstrap 4 CSS CDN -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
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

<?php
include('configs.php');
function loadConfigFile($configFile) {
    $siteTables = array();
    $comments = array();

    // Open the file
    $file = fopen($configFile, 'r');
    if (!$file) {
        return array("sites" => $siteTables, "comments" => $comments); // Return empty arrays if file can't be opened
    }

    while (($line = fgets($file)) !== false) {
        $trimmedLine = trim($line);

        // Capture comment lines or empty lines
        if ($trimmedLine === '' || strpos($trimmedLine, '#') === 0) {
            if ($trimmedLine !== '') {
                $comments[] = $trimmedLine; // Only add non-empty comment lines
            }
            continue;
        }

        $parts = explode(', ', $trimmedLine);
        if (count($parts) < 3) {
            continue; // Skip malformed lines
        }

        $site = $parts[0];
        $table = $parts[1];

        // Parse all split ranges
        $splitRanges = array();
        for ($i = 2; $i < count($parts); $i++) {
            list($start, $end) = explode('-', $parts[$i]);
            $splitRanges[] = $start . '-' . $end;
        }

        $siteTables[$site] = array("table" => $table, "parts" => implode(', ', $splitRanges));
    }

    fclose($file);
    return array("sites" => $siteTables, "comments" => $comments);
}

// Use the new function to load the site configurations and comments
$configData = loadConfigFile($CONFIG_FILE_NAME);
$siteTables = $configData["sites"];
$comments = $configData["comments"];

// Prepare sites data for display in the table
$siteRows = '';
foreach ($siteTables as $site => $info) {
    $siteRows .= "<tr>";
    $siteRows .= "<td contentEditable='true'>" . htmlspecialchars($site) . "</td>";
    $siteRows .= "<td contentEditable='true'>" . htmlspecialchars($info['table']) . "</td>";
    $siteRows .= "<td contentEditable='true'>" . htmlspecialchars($info['parts']) . "</td>";
    $siteRows .= "</tr>";
}

// Prepare comments for display in the textarea
$commentsDisplay = implode("\n", $comments);
?>

<body>
    <div class="container-fluid">
        <form class="col-lg-10" style="top:0px" action="run_edit_config_script.php" method="POST" onsubmit="return onSubmitForm();">
            <div id="loading">
                <div>
                    <img src="<?php echo($BASE_URL . "html/img/loading_icon.gif");?>" width="150" height="100" />
                </div>
            </div>

            <div class="form-group row">
                <div class="col-sm-11">
                    <textarea class="form-control" name="comments" id="comments" cols="10" rows="8" disabled><?php echo htmlspecialchars($commentsDisplay); ?></textarea>
                </div>
            </div>

            <div class="form-group row">
                <div class="col-sm-11">
                    <div class="table-responsive">
                        <table class="table table-bordered table-hover" id="sitesTable">
                            <thead>
                                <tr>
                                    <th onclick="sortTable(0)">Site</th>
                                    <th onclick="sortTable(1)">Table</th>
                                    <th onclick="sortTable(2)">Partitions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php echo $siteRows; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

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
            <div class="row flex justify-content-left form-group-padding">
                <div class="col-sm-1">
                    <button type="submit" class="btn btn-success btn-save btn-block" style="margin-top: 20px;">Save</button>
                </div>
                <div class="col-sm-11 input-group mt-3">
                    <div class="input-group-prepend">
                        <span class="input-group-text">filename</span>
                        <input type="text" id="filename" name="filename" value="<?php echo basename($CONFIG_FILE_NAME); ?>" disabled>
                    </div>
                </div>
            </div>
            <input type="hidden" id="commentsHidden" name="commentsHidden">
            <input type="hidden" id="sitesHidden" name="sitesHidden">
        </form>
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

            // Trim the comments field initially to remove any extra spaces or newlines
            $('#comments').val($('#comments').val().trim());

            // Log the initial row count for debugging
            console.log("Initial row count (excluding header): " + $('#sitesTable tbody tr').length);
        });

        function tableToTextareas() {
            var comments = $('#comments').val().trim();
            $('#commentsHidden').val(comments);

            var sites = [];
            $('#sitesTable tbody tr').each(function() {
                var row = [];
                $(this).find('td').each(function() {
                    row.push($(this).text().trim());
                });
                sites.push(row.join(', '));
            });
            $('#sitesHidden').val(sites.join('\n'));

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
            $('#loading').show();
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

    <!-- Include jQuery and Bootstrap JavaScript -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js"></script>
</body>
</html>
