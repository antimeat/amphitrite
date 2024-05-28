$(document).ready(function () {
    $("#site_select").selectmenu("destroy").selectmenu({ style: "dropdown" });
    load_sites();
});

function load_sites() {
    var select = $("#site_select");
    // Fetch site names from api.cgi
    $.getJSON("../api.cgi", { get: "sites_from_config" }, function (siteData) {
        SITES = {};

        $.each(siteData, function (i, s) {
            SITES[s.name] = s;
        });

        // Fetch the SITE_TABLES from the PHP script
        $.getJSON("../html/get_transformer_configs.php", function (tableData) {
            SITE_TABLES = tableData;
            console.log("SITE_TABLES: ", SITE_TABLES);

            var select = $("<select id='site_select' name='site_select'/>").change(function (e) {
                console.log("change site");
                var table_key = this.value;
                var table = SITE_TABLES[table_key];

                // Default values if table is undefined
                if (typeof table === "undefined") {
                    table = {
                        theta_1: 0,
                        theta_2: 0,
                        theta_split: 180,
                        multi_short: 1,
                        multi_long: 1,
                        attenuation: 1,
                        crit_1: 3,
                        crit_2: 2.5,
                        crit_3: 2.0,
                    };
                }

                console.log("change table: " + table_key + " table: " + JSON.stringify(table));
                $("#theta_1").val(table["theta_1"]);
                $("#theta_2").val(table["theta_2"]);
                $("#theta_split").val(table["theta_split"]);
                $("#multi_short").val(table["multi_short"]);
                $("#multi_long").val(table["multi_long"]);
                $("#attenuation").val(table["attenuation"]);
                $("#criteria_1").val(table["crit_1"]);
                $("#criteria_2").val(table["crit_2"]);
                $("#criteria_3").val(table["crit_3"]);
            });

            $.each(SITES, function (name, site) {
                $("<option />", { value: name, text: name }).appendTo(select);
            });

            select.appendTo("#sites");

            // Manually trigger change event for the first site in the list
            $("#site_select").val($("#site_select option:first").val()).change();
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.error("Failed to fetch site tables: ", textStatus, errorThrown);
        });
    }).fail(function (jqXHR, textStatus, errorThrown) {
        console.error("Failed to fetch site names: ", textStatus, errorThrown);
    });
}
