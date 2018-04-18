$(document).ready(function () {

    $('select').addClass('browser-default');
    pair_id = $('.pair_tr').data('pair-id');
    $('.pair_tr[data-pair-id=' + pair_id + ']').addClass('active_pair');
    var main_coin = $('.tabs a.active').text();
    var second_coin = $('.pair_tr[data-pair-id=' + pair_id + ']').children('td:eq(0)').text();
    document.title = $('.pair_tr[data-pair-id=' + pair_id + ']').children('td:eq(1)').text() + ' ' + main_coin + "/" + second_coin;
    $('#preview_coins h5 b').text(main_coin + '_' + second_coin);
    intervale = $('#buttons .candlestick').data('intervale');
    zoom = $('#buttons-zoom .zoom').data('zoom');
    draw_graph();

    $('.pair_tr').on('click', function () {
        var main_coin = $('.tabs a.active').text();
        var second_coin = $(this).children('td:eq(0)').text();
        $('#preview_coins h5 b').text(main_coin + '_' + second_coin);
        $('.pair_tr').removeClass('active_pair');
        $(this).addClass('active_pair');
        if ($(this).data('pair-id') != pair_id) {
            pair_id = $(this).data('pair-id');
            draw_graph();
        }
    });

    $('#buttons .candlestick').on('click', function () {
        $('#buttons div .candlestick').removeClass('green');
        $(this).addClass('green');
        intervale = $(this).data('intervale');
        draw_graph();
    });

    $('#buttons-zoom .zoom').on('click', function () {
        $('#buttons-zoom div .zoom').removeClass('green');
        $(this).addClass('green');
        zoom = $(this).data('zoom');
        draw_graph();
    });
    $('.tooltipped').tooltip({
        delay: 50,
        html: true
    });
    $('.add_coin').on('click', function (e) {
        $(this).parent('form').submit();
        return false;
    });
    $('.rank-up').on('click', function () {
        var user_pair_id = $(this).parent('td').parent('tr').data('pair-id');
        change_rank(user_pair_id, 'up');
    });
    $('.rank-down').on('click', function () {
        var user_pair_id = $(this).parent('td').parent('tr').data('pair-id');
        change_rank(user_pair_id, 'down');
    });

    function change_rank(pair_id, type) {
        $.ajax({
            url: '/trade/changerank/',
            dataType: 'html',
            type: 'post',
            cache: !1,
            data: {
                pair_id: pair_id,
                csrfmiddlewaretoken: getCookie('csrftoken'),
                type: type
            },
            success: function (data) {
                if ('false' === data) {
                    Materialize.toast('Error while changing rank', 1000)
                } else if ('ok' === data) {
                    location.reload();
                }
            }
        })
    }


    $('.pair-share').keypress(function (e) {
        if (e.which === 13) {
            var share = $(this).val();
            var user_exch = $('#exchange').val();
            if ('' !== share) {
                var user_pair_id = $(this).parent('td').parent('tr').data('pair-id');
                $.post('/trade/set_share/', {
                        pair_id: user_pair_id,
                        share: share,
                        user_exch: user_exch,
                        csrfmiddlewaretoken: getCookie('csrftoken')
                    },
                    function (data) {
                        'ok' === data ? location.reload() : Materialize.toast(data, 1000);
                    });
            }
        }
    }).on('focus', function () {
        $('.collapsible').collapsible('destroy');
    }).on('blur', function () {
        $('.collapsible').collapsible();
    });
    $('.delete-user-coin').on('click', function () {
        var user_pair_id = $(this).parent('td').parent('tr').data('pair-id');
        $.post('/trade/delete_user_pair/', {
            pair_id: user_pair_id,
            csrfmiddlewaretoken: getCookie('csrftoken')
        }, function (data) {
            'ok' === data ? location.reload() : Materialize.toast(data, 1000);
        })
    });
    $('#disable-script').on('change', function () {
        $.post('/trade/exchange_script_activity/', {
            user_exch: $('#exchange').val(),
            csrfmiddlewaretoken: getCookie('csrftoken')
        }, function (data) {
            if (data) {
                location.reload()
            } else Materialize.toast('Error while change script status', 1500)
        })
    });
    $('.change-primary-coin-status').on('change', function () {
        var pc = $(this).parent('.primary-coin').data('primary-coin');
        $.post('/trade/change_primary_coin/', {
            user_exch: $('#exchange').val(),
            csrfmiddlewaretoken: getCookie('csrftoken'),
            coin: pc
        }, function (data) {
            'ok' === data ? location.reload() : Materialize.toast('Error while changing status', 1000)
        })
    });

    $('.primary-rank').on('click', function () {
        change_primary_coin($(this).data('type'), $(this).parent('.primary-coin').data('primary-coin'));
    });

    function change_primary_coin(type, coin) {
        $.post('/trade/change_primary_coin_rank/', {
            user_exch: $('#exchange').val(),
            csrfmiddlewaretoken: getCookie('csrftoken'),
            coin: coin,
            type: type
        }, function (data) {
            'ok' === data ? location.reload() : Materialize.toast('Error while changing rank', 1000)
        })
    }

    function get_new_orders_to_trade() {
        $.ajax({
            url: '/trade/get_new_orders_to_trade/',
            type: 'post',
            dataType: 'html',
            data: {
                user_exch: $('#exchange').val(),
                csrfmiddlewaretoken: getCookie('csrftoken'),
                already: $('.orders_to_trade').length
            },
            success: function (data) {

                console.log(data)

            }
        })
    }

    // setInterval(get_new_orders_to_trade, 5000);

    $('#user_orders').DataTable();
    $('#calculated_to_trade').DataTable();
    $.extend($.fn.dataTable.defaults, {
        searching: false,
        ordering: false
    });


    function cl(value) {
        console.log(value)
    }

});

var ticker = {};

socket = new WebSocket("ws://" + window.location.host + "/trade/");
socket.onmessage = function (message) {
    var item = JSON.parse(message.data);
    if (item.pair_id in ticker) {
        if (item.last !== ticker[item.pair_id].last) {
            ticker[item.pair_id].last = item.last;
            ticker[item.pair_id].percent = item.percent;
        }
    } else {
        ticker[item.pair_id] = {'last': item.last, 'percent': item.percent}
    }
};

setInterval(function () {
    for (var item in ticker) {
        var prev_last = Number($('.pair_last#last_' + item).text());
        if (ticker[item].last > prev_last) {
            $('.pair_last#last_' + item).text(ticker[item].last).parent('tr').addClass('priceChangeUp');
            $('.pair_last#arrow_' + item).html('<i class="fa fa-arrow-up fa-1x green-text" aria-hidden="true"></i>');
        } else if (ticker[item].last < prev_last) {
            $('.pair_last#last_' + item).text(ticker[item].last).parent('tr').addClass('priceChangeDown');
            $('.pair_last#arrow_' + item).html('<i class="fa fa-arrow-down fa-1x red-text" aria-hidden="true"></i>');
        } else {
            $('.pair_last#arrow_' + item).html('');
        }
        if (ticker[item].percent > 0) {
            $('.pair_last#percent_' + item).text(Math.floor(ticker[item].percent * 100) / 100 + '%').removeClass('red-text').addClass('green-text');
        } else {
            $('.pair_last#percent_' + item).text(Math.floor(ticker[item].percent * 100) / 100 + '%').addClass('red-text').removeClass('green-text');
        }
        setTimeout(function () {
            $('.pair_last').parent('tr').removeClass('priceChangeDown priceChangeUp ');
        }, 600);
    }
}, 2000);

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function draw_graph() {
    var ohlcData = [];
    var extremums = [];
    $.post('/trade/get_ticker/', {
        pair_id: pair_id,
        csrfmiddlewaretoken: getCookie('csrftoken'),
        intervale: intervale,
        zoom: zoom
    }, function (data) {
        console.log(data)
        for (var i = 1; i < data['ticker'].length; i++) {
            ohlcData.push([new Date(Date.parse(data['ticker'][i].date)), round(data['ticker'][i].high), round(data['ticker'][i].low), round(data['ticker'][i].open), round(data['ticker'][i].close)]);
        }
        for (var j = 0; j < data['extremums'].length; j++) {
            extremums.push([
                new Date(Date.parse(data['extremums'][j][0])),
                round(data['extremums'][j][1]),
                data['extremums'][j][2]
            ]);
        }
        $('#jqChart').jqChart({
            legend: {visible: false},
            border: {lineWidth: 0, padding: 0},
            tooltips: {
                disabled: false,
                type: 'shared',
                borderColor: 'auto',
                snapArea: 100,
                highlighting: true,
                highlightingFillStyle: 'rgba(204, 204, 204, 0.5)',
                highlightingStrokeStyle: 'rgba(204, 204, 204, 0.5)'
            },
            crosshairs: {
                enabled: true,
                hLine: {strokeStyle: '#9c9b96'},
                vLine: {strokeStyle: '#9c9b96'},
                snapToDataPoints: false
            },
            toolbar: {
                visibility: 'visible', // auto, visible, hidden
                resetZoomTooltipText: 'Reset Zoom (100%)',
                zoomingTooltipText: 'Zoom in to selection area',
                panningTooltipText: 'Pan the chart'
            },
            mouseInteractionMode: 'zooming', // zooming, panning
            animation: {duration: 0.0001},
            axes: [
                {
                    type: 'dateTime',
                    location: 'bottom',
                    zoomEnabled: false
                },
                {
                    type: 'linear',
                    location: 'right',
                    zoomEnabled: false
                }
            ],
            // axes: [
            //     {
            //         type: 'linear',
            //         location: 'right',
            //         width: 80
            //     }
            // ],
            shadows: {
                enabled: true
            },

            series: [
                {
                    type: 'candlestick',
                    data: ohlcData,
                    priceUpFillStyle: '#4caf50',
                    priceDownFillStyle: '#f44336',
                    strokeStyle: 'black',
                    pointWidth: 0.8,
                    stringFormat: '%d'
                },
                {
                    type: 'scatter',
                    data: extremums,
                    title: 'Extremum',
                    markers: {
                        size: 10,
                        type: 'triangle',
                        strokeStyle: 'black',
                        lineWidth: 1,
                        fillStyle: 'black'
                    },
                    labels: {
                        fillStyle: 'black',
                        stringFormat: '%d'
                    }
                }

            ]
        });

    }, 'json');
    $('#jqChart').bind('dataPointLabelCreating', function (e, data) {
        console.log(data);
        var context = data.context;
        data.text = context.dataItem[2];
    });
}

function round(d) {
    return Math.round(100000000 * d) / 100000000
}
