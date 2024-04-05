var SITES;
var SITE_TABLES = {
    "Woodside - Mermaid Sound 7 days": {
        table: "Dampier_Nearshore",
        w_max: 330,
        e_max: 30,
        multi: 0.4,
        period: 1,
        crit_1: 0.3,
        crit_2: 0.2,
        crit_3: 0.15,
    },
    "Chevron - Wheatstone LNG Plant": {
        table: "Thevenard",
        w_max: 310,
        e_max: 30,
        multi: 0.4,
        period: 0.9,
        crit_1: 0.3,
        crit_2: 0.2,
        crit_3: 0.15,
    },
    "Chevron - Wheatstone LNG Plant AFS ext": {
        table: "Thevenard",
        w_max: 310,
        e_max: 30,
        multi: 0.4,
        period: 0.9,
        crit_1: 0.3,
        crit_2: 0.2,
        crit_3: 0.15,
    },
    "Dampier Salt - Cape Cuvier 7 days": {
        table: "Cape_Cuvier_Offshore",
        w_max: 262,
        e_max: 20,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Pilbara Ports Authority - Ashburton": {
        table: "Ashburton_Port",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 1.0,
        crit_2: 0.8,
        crit_3: 0.5,
    },
    "Pilbara Ports Authority - Dampier": {
        table: "Dampier_Port",
        w_max: 270,
        e_max: 40,
        multi: 1,
        period: 1,
        crit_1: 1.5,
        crit_2: 1.0,
        crit_3: 0.7,
    },
    "Pilbara Port Authority - Port Hedland": {
        table: "PH_Beacon16",
        w_max: 240,
        e_max: 50,
        multi: 0.9,
        period: 1,
        crit_1: 2,
        crit_2: 1.5,
        crit_3: 1.25,
    },
    "Abbot Point": {
        table: "Abbot_Point",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Woodside - Balnaves 7 days": {
        table: "Balnaves",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Santos - Barossa": {
        table: "Barossa",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Chevron Barrow Island AFS": {
        table: "Barrow_Island",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Chevron Barrow Island": {
        table: "Barrow_Island",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "UPS - Northern Endeavour": {
        table: "Bayu_Undan",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Santos ABUW - Bayu-Undan": {
        table: "Bayu_Undan",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Citic Pacific - Cape Preston Area": {
        table: "Cape_preston",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Indian Ocean Stevedores - Flying Fish Cove": {
        table: "ChrisIs_N",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "CITIC Pacific - Malus Island": {
        table: "Dampier_Nearshore",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Santos - Dorado - 7 days": {
        table: "Dorado",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Santos - Dorado - 4 days": {
        table: "Dorado",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Woodside - Enfield and Vincent 7 days": {
        table: "Enfield",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "BHP - Pyrenees": {
        table: "Enfield",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Santos - Van Gogh 4 days": {
        table: "Enfield",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    //{'table':'Esperance','w_max':180,'e_max':180,'multi':1,'period':1,'crit_1':3,'crit_2':2.5,'crit_3':2},
    //{'table':'Exmouth','w_max':180,'e_max':180,'multi':1,'period':1,'crit_1':3,'crit_2':2.5,'crit_3':2},
    //{'table':'Geraldton','w_max':180,'e_max':180,'multi':1,'period':1,'crit_1':3,'crit_2':2.5,'crit_3':2},
    "Chevron - Gorgon": {
        table: "Gorgon",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "INPEX - Ichthys 7 days": {
        table: "Ichthys",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    //{'table':'Inside_Barrow_Island','w_max':180,'e_max':180,'multi':1,'period':1,'crit_1':3,'crit_2':2.5,'crit_3':2},
    "Chevron - Jansz": {
        table: "Jansz_PTS",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Santos - John Brookes 4 days": {
        table: "John_Brookes",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    //{'table':'Jurien','w_max':180,'e_max':180,'multi':1,'period':1,'crit_1':3,'crit_2':2.5,'crit_3':2},
    "Oilsearch - Kumul Marine Terminal": {
        table: "Kumul_Platform",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Jadestone Energy - Montara": {
        table: "Montara",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    //{'table':'Noblige','w_max':180,'e_max':180,'multi':1,'period':1,'crit_1':3,'crit_2':2.5,'crit_3':2},
    //{'table':'NW_Exmouth','w_max':180,'e_max':180,'multi':1,'period':1,'crit_1':3,'crit_2':2.5,'crit_3':2},
    "Onslow Salt - Onslow Jetty": {
        table: "Onslow_Jetty",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Woodside - Pluto 7 days": {
        table: "PLA",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    //{'table':'Rottnest','w_max':180,'e_max':180,'multi':1,'period':1,'crit_1':3,'crit_2':2.5,'crit_3':2},
    "Woodside - North Rankin 7 days": {
        table: "Rankin",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Woodside - Scarborough 7 days": {
        table: "Scarborough_Infield",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Santos - Reindeer 4 days": {
        table: "Reindeer",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Santos - Reindeer 7 days": {
        table: "Reindeer",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "SupuraOMV - Eagle-1": {
        table: "Enfield",
        w_max: 330,
        e_max: 360,
        multi: 0.5,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Jadestone Energy - Stag": {
        table: "Stag",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "CITIC Pacific - Legendre Island": {
        table: "Stag",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Vermilion - Wandoo": {
        table: "Wando",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    //{'table':'Wheatstone','w_max':180,'e_max':180,'multi':1,'period':1,'crit_1':3,'crit_2':2.5,'crit_3':2},
    "Chevron - Wheatstone LNG Plant AFS": {
        table: "Wheatstone",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 0.9,
        crit_1: 0.3,
        crit_2: 0.2,
        crit_3: 0.15,
    },
    "Santos - Varanus 4 days": {
        table: "Varanus",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
    "Santos - MS1Standby 4 days": {
        table: "West_Darwin",
        w_max: 180,
        e_max: 180,
        multi: 1,
        period: 1,
        crit_1: 3,
        crit_2: 2.5,
        crit_3: 2,
    },
};

var TABLES = {
    Abbot_Point: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Ashburton_Port: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 1.0, crit_2: 0.8, crit_3: 0.5 },
    Balnaves: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Barossa: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Barrow_Island: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Bayu_Undan: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Cape_Cuvier_Offshore: { w_max: 262, e_max: 20, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Cape_preston: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    ChrisIs_N: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    ChrisIs_W: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Cuvier: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Dampier_Nearshore: { w_max: 330, e_max: 30, multi: 0.5, period: 1, crit_1: 0.3, crit_2: 0.2, crit_3: 0.15 },
    Dampier_Port: { w_max: 270, e_max: 40, multi: 1, period: 1, crit_1: 0.3, crit_2: 0.2, crit_3: 0.15 },
    Dorado: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Enfield: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Esperance: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Exmouth: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Geraldton: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Ichthys: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Inside_Barrow_Island: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Jansz_PTS: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    John_Brookes: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Jurien: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Kumul_Platform: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Montara: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Noblige: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    NW_Exmouth: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Onslow_Jetty: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    PH_Beacon16: { w_max: 240, e_max: 50, multi: 0.9, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Pt_Headland_Port: { w_max: 240, e_max: 50, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    PLA: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Pluto: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Rottnest: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Rankin: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Scarborough_Infield: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Wando: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Thevenard: { w_max: 310, e_max: 30, multi: 0.4, period: 0.9, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Reindeer: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Wando: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    Varanus: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 3, crit_2: 2.5, crit_3: 2 },
    West_Darwin: { w_max: 180, e_max: 180, multi: 1, period: 1, crit_1: 0.3, crit_2: 0.25, crit_3: 0.2 },
};

$(document).ready(function () {
    $("#site_select").selectmenu("destroy").selectmenu({ style: "dropdown" });
    load_tables();
    load_sites();
});

function load_tables(done) {
    var select = $("<select id='table_select' name='table_select'/>").change(function (e) {
        console.log("change site");
        var table_key = this.value;
        var table = TABLES[table_key];

        if (typeof table != "undefined") {
            console.log("table: " + table["table"]);
            $("#theta1").val(table["w_max"]);
            $("#theta2").val(table["e_max"]);
            $("#multiplier").val(table["multi"]);
            $("#attenuation").val(table["period"]);
            $("#criteria_1").val(table["crit_1"]);
            $("#criteria_2").val(table["crit_2"]);
            $("#criteria_3").val(table["crit_3"]);
        }
    });

    Object.entries(TABLES).forEach(([key, value]) => {
        $("<option />", { value: key, text: key }).appendTo(select);
    });

    select.appendTo("#tables");
}

function load_sites(done) {
    var select = $("#site_select");
    $.getJSON("../api.cgi", { get: "sites" }, function (d) {
        SITES = {};

        $.each(d, function (i, s) {
            SITES[s.name] = s;
        });

        // load tc swell id

        var select = $("<select id='site_select' name='site_select'/>").change(function (e) {
            console.log("change site");
            var table_key = this.value;
            var table = SITE_TABLES[table_key];

            if (typeof table != "undefined") {
                console.log("change table: " + table_key + "table: " + table["table"]);
                $("#table_select").val(table["table"]);
                $("#theta1").val(table["w_max"]);
                $("#theta2").val(table["e_max"]);
                $("#multiplier").val(table["multi"]);
                $("#attenuation").val(table["period"]);
                $("#criteria_1").val(table["crit_1"]);
                $("#criteria_2").val(table["crit_2"]);
                $("#criteria_3").val(table["crit_3"]);
            }
        });

        _.each(SITES, function (site, name) {
            $("<option />", { value: name, text: name }).appendTo(select);
        });

        select.appendTo("#sites");
    });
}