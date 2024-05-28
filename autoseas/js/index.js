var sites;
var siteTypes = {};
var sitesWithSeaTables = []; // "Chevron - Thevenard Island", "Chevron - Barrow Island"

// Global flag to track fetch table loading
var isFetchTableLoaded = false;

$(document).ready(function () {
    // $(".windInput").each(function (i, wind) {
    //     $(wind).change(function (e) {
    //         refreshSeas();
    //     });
    // });

    if (!isFetchTableLoaded) {
        $.get("siteNames.php", function (data) {
            sites = data.split("\n");

            $.each(sites, function (s, site) {
                $("#siteSelect").append(new Option(site, site));
            });
        });
    }

    // ofcast server selector
    $("#siteSelect").change(function (e) {
        isFetchTableLoaded = false; // Reset flag when site changes
        loadFetchTable();
        isFetchTableLoaded = true; // Set flag to true
    });

    // When the user clicks on <span> (x), close the modal
    $(".close").click(function () {
        $("#errorModal").css("display", "none");
    });

    // Also close the modal if the user clicks anywhere outside of the modal
    $(window).click(function (event) {
        if ($(event.target).is("#errorModal")) {
            $("#errorModal").css("display", "none");
        }
    });
});

function createWindsTable(winds) {
    var numDays = winds.length / 8;
    var day = 0;
    var t = 0;
    var d = 0;
    var dayLabel = "";

    var html = "<h3 style='margin-bottom:40px;'>Winds</h3>";
    html += "<table><tr><th>Day</th><th>Hours</th><th>Wind Dir</th><th>Spd (kts)</th><th>Seas (m)</th></tr>";

    winds.forEach(function (wind, i) {
        t = i * 3;
        d = t / 24.0;
        dayLabel = "";
        if (d === Math.floor(d)) {
            day = d;
            dayLabel = day.toString();
        }
        var h = t - day * 24;

        html += `<tr>
                    <td>${dayLabel}</td>
                    <td>${wind["hour"]}</td>
                    <td><input type='text' id='dirn_${i}' name='dirn_${i}' class='windInput' value='${wind["dir"]}' size='4'></td>
                    <td><input type='text' id='spd_${i}' name='spd_${i}' class='windInput' value='${wind["spd"]}' size='3'></td>
                    <td><div id='seas_${i}' name='seas_${i}' class='seas'></div></td>
                </tr>`;
    });

    html += "</table>";
    return html;
}

function loadWinds() {
    var site_name = $("#siteSelect").val();
    var session_id = $("#session").val();
    var server_select = $("#serverSelect").val();

    if (session_id !== "") {
        var opts = {
            fName: site_name,
            sessionID: session_id,
            get: "ofcast_archived",
            archive: 0,
            data_type: "forecast",
            server: server_select,
        };

        $.getJSON("get_winds.cgi", opts)
            .done(function (data) {
                // Transform data into a structured format for the winds table
                var windsData = data.map(function (item, index) {
                    // Assuming each item is an array [direction, speed, hourSinceLast]
                    // and 'hour' needs to be calculated cumulatively
                    if (item[0] == 0) {
                        item[0] = 360;
                    }
                    var hour =
                        index > 0
                            ? data.slice(0, index + 1).reduce(function (acc, curr) {
                                  return acc + curr[2]; // Accumulate hours
                              }, 0)
                            : 0;
                    return {
                        hour: hour,
                        dir: item[0],
                        spd: item[1],
                    };
                });

                // Create winds table HTML and update the webpage
                var windsTableHtml = createWindsTable(windsData);
                $("#windsTableContainer").html(windsTableHtml); // Make sure you have a div with id="windsTableContainer"
            })
            .fail(function () {
                // Handle error
                $("#errorMessage").html("<h3><i>Winds not available for: </i>" + site_name + "</h3>");
                $("#errorModal").show();
            });
    }
}

function siteToFileName(site) {
    // convert site to a fileName
    var fileName = site.split(" ").join("_") + ".csv";
    console.log(fileName);
    return fileName;
}

function transformSiteName(site) {
    var siteName = str.replace(/_/g, " ").trim();
    console.log(siteName);
    return siteName;
}

function loadFetchTable() {
    var site = $("#siteSelect").val();

    if (site == null || isFetchTableLoaded) return; // Skip if already loaded

    if ($.inArray(site, sitesWithSeaTables) >= 0) {
        siteTypes[site] = "mixed";
        $("#fetchTable").html("Uses fully developed seas table.");
    } else {
        var file_name = siteToFileName(site);
        var base_url = BASE_URL + "autoseas/fetchLimits/" + file_name;
        console.log(base_url);
        Papa.parse(base_url, {
            download: true,
            header: true,
            complete: function (results) {
                var tbl = results.data;

                // Remaining processing logic...
                var noDepth = tbl.every((t) => t.depth === "");
                var note = "";
                tbl = tbl.filter((t) => {
                    if (t.windDir === "note") {
                        note = t.fetch;
                        return false;
                    }
                    return true;
                });

                siteTypes[site] = noDepth ? "deep" : "shallow";

                if (note !== "") {
                    $("#fetchTable").html("Note: " + note);
                } else {
                    $("#fetchTable").html("<h3 style='margin-bottom:40px;'>Fetch-limits</h3>");
                }

                $("#fetchTable").append(htmlTable(tbl, ["windDir", "fetch", "depth"]));
            },
        });
    }
}

function htmlTable(data, fields) {
    var html = "<table>";
    // Generate the header row
    html += '<tr valign="bottom">';
    fields.forEach(function (field) {
        html += "<th>" + capitalizeFirstLetter(field) + "</th>"; // Capitalize headers for consistency
    });
    html += "</tr>";

    // Generate the body rows
    data.forEach(function (row) {
        html += "<tr>";
        fields.forEach(function (field) {
            // Check if field is 'windDir', 'fetch', or 'depth' to insert input or div accordingly
            if (field == "windDir" || field == "fetch") {
                html += '<td><input class="windInput" value="' + (row[field] || "") + '" readonly></td>';
            } else if (field == "depth") {
                html +=
                    '<td><div class="seas" value="' +
                    (row[field] || "") +
                    '" readonly</div>' +
                    (row[field] || "") +
                    "</td>";
            } else {
                html += "<td>" + (row[field] || "") + "</td>";
            }
        });
        html += "</tr>";
    });

    html += "</table>";
    return html;
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function getDateString() {
    //format a date string from midnight of the current day using format 'YYYYMMDDHH'
    var date = new Date();
    date.setHours(0, 0, 0, 0);

    // Helper function to pad numbers to two digits
    const padToTwoDigits = (num) => num.toString().padStart(2, "0");

    // Extracting year, month, day, and hour from the date
    const year = date.getFullYear();
    const month = padToTwoDigits(date.getMonth() + 1); // getMonth() returns month from 0-11
    const day = padToTwoDigits(date.getDate());
    const hour = padToTwoDigits(date.getHours());

    // Constructing the formatted string
    return `${year}${month}${day}${hour}`;
}

function refreshSeas() {
    midnight = getDateString();

    // get the site and seas algo
    var site = $("#siteSelect").val();
    var algo_form = document.getElementById("algorithmChoice");
    var form_data = new FormData(algo_form);
    var algo = form_data.get("algorithm");
    console.log(site);
    console.log(algo);

    // collect all the values
    var winds = {};

    seasData = {};

    $(".windInput").each(function (i, input) {
        var name = input.name;
        var n = name.split("_");
        var field = n[0];
        var hour = n[1];
        var val = input.value;

        if (val != "") {
            if (winds[hour] == undefined) {
                //console.log('adding', hour)
                winds[hour] = [];
            }
            winds[hour][field] = val;
        }

        //console.log(name, field, hour, val);

        return true;
    });

    console.log(winds);

    var windStr = [];

    var hoursInUse = [];

    //console.log(winds)

    var prevHour = 0;
    $.each(winds, function (i, w) {
        hoursInUse.push(i);
        var step = i - prevHour;
        prevHour = i;
        if (w["dirn"] != undefined && w.spd != undefined) {
            windStr.push([w.dirn, w.spd, step].join("/"));
        }
    });

    windStr = windStr.join(",");

    console.log(windStr);

    //, 'uSeas'
    $.each(["seas"], function (i, name) {
        var opts = {
            winds: windStr,
            site: site,
            returnPdDir: 1,
            type: "new",
            src: "autoseas",
            first_time_step: midnight,
        };

        // algorithm
        var algo = $("#algorithm").val();
        if (algo) {
            opts.type = algo;
        }

        console.log(opts);

        $.getJSON(BASE_URL + "autoseas.cgi", opts, function (data) {
            //console.log(data);
            data = data["seas"];
            seasData[name] = data;

            var hts = [];
            var htPdAndDirs = [];
            var htAndPds = [];

            $.each(data, function (i, s) {
                // hour comes from the hoursInUse list
                var h = hoursInUse[i];
                //console.log(i, s, h);
                var id = "#" + name + "_" + h;
                $(id).html(s[0].toFixed(1) + " / " + s[1]);

                hts.push(s[0]);

                // push hts and dirs consecutively
                htPdAndDirs.push(s[0]);
                htPdAndDirs.push(s[1]);
                htPdAndDirs.push(s[2]);

                htAndPds.push(s[0]);
                htAndPds.push(s[1]);
            });

            $("#seasCopy").val(hts.join(", "));
            $("#seasAndDirCopy").val(htPdAndDirs.join(", "));
            $("#seasAndPeriodCopy").val(htAndPds.join(", "));
        });
    });
}

function calcAutoSeas(site, winds, opts, callback) {
    // make wind string
    var windStr = [];
    $.each(winds, function (i, w) {
        if (w.dt == undefined) w.dt = 3.0;
        windStr.push([w.dir, w.spd, w.dt].join("/"));
    });
    windStr = windStr.join(",");

    if (windStr != "") {
        var thisOpts = {
            winds: windStr,
            site: site,
            src: "autoseas",
            first_time_step: midnight,
            returnDir: 1,
        };

        if (opts != undefined) $.extend(thisOpts, opts);

        $.getJSON(BASE_URL + "autoseas.cgi", thisOpts, function (data) {
            callback(data["seas"]);
        });
    }
}

function fileToSiteName(str) {
    return str.replace(/_/g, " ").trim();
}
