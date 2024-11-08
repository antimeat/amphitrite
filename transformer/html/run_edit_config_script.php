<?php
    include('configs.php');

    $dir = $BASE_DIR . "transformer/";
    $file_name = $CONFIG_FILE_NAME;
    $csv_data = $_POST['data'];
    $header_comments = $_POST['header_comments']; 

    // Escape the command arguments to handle special characters correctly
    $escaped_csv_data = escapeshellarg($csv_data);
    $escaped_header_comments = escapeshellarg($header_comments);
    $escaped_file_name = escapeshellarg($file_name);

    $command = "cd $dir && $dir" . "save_transformer_config.py --csv_data $escaped_csv_data --header_comments $escaped_header_comments --file_name $escaped_file_name";
    
    ob_start();
    passthru($command);
    $buffer = ob_get_contents();
    $htmlBuffer = str_replace("\n", "<br>", $buffer);
    passthru("cd $BASE_DIR && $BASE_DIR" . "run_transform.py --all");
    ob_end_clean();

    // header("Location: edit_config_script.php");
?>

<!DOCTYPE html>
<html>
    <head>
        <title>Results</title>
        <!-- Include Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css">
    </head>
    <body>                    
        <!-- Bootstrap Modal -->
        <div class="modal fade" id="resultModal" tabindex="-1" role="dialog" aria-labelledby="resultModalLabel" aria-hidden="true" data-backdrop="false">
            <div class="modal-dialog modal-lg" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="resultModalLabel">Results from config update</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <?php echo($htmlBuffer); ?>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
        <!-- Include jQuery and Bootstrap JavaScript -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>

        <script>
        $(document).ready(function() {
            $('#resultModal').modal('show');
            $('#resultModal').on('hidden.bs.modal', function () {
                window.location.href = 'index.php'; // Redirect URL
            });
        });
        </script>

    </body>
</html>
