$(document).ready(function () {
    pair_id = $('.pair_tr').data('pair-id');
    $('.pair_tr[data-pair-id=' + pair_id + ']').addClass('yellow lighten-3');
    intervale = $('#buttons .candlestick').data('intervale');
    zoom = $('#buttons .zoom').data('zoom');
    draw_graph();

    $('.pair_tr').on('click', function () {
        $('.pair_tr').removeClass('yellow lighten-3');
        $(this).addClass('yellow lighten-3');
        if ($(this).data('pair-id') != pair_id) {
            pair_id = $(this).data('pair-id');
            draw_graph();
        }
    });

    $('#buttons .candlestick').on('click', function () {
        $('#buttons .candlestick').removeClass('green');
        $(this).addClass('green');
        intervale = $(this).data('intervale');
        draw_graph();
    });
    $('#buttons .zoom').on('click', function () {
        $('#buttons .zoom').removeClass('green');
        $(this).addClass('green');
        zoom = $(this).data('zoom');
        draw_graph();
    });

    $('select').material_select();
    $('.modal').modal();
    $('#yandex-wallet-add').hide();

    $('.change_status').on('click', function () {
        var ue = $(this).parent('form').find('input[name="user-exchange"]').val();
        var csrf = getCookie('csrftoken');
        $.ajax({
            url: '/change_status/',
            type: 'post',
            cache: !1,
            dataType: 'html',
            data: {
                ue: ue,
                csrfmiddlewaretoken: csrf
            },
            success: function (data) {
                data === 'ok' ? location.reload() : data === '{"location": "/change_status/"}' ? Materialize.toast('У Вас недостаточно прав', 2000) : Materialize.toast('Не удалось изменить статус', 2000);
            }
        });
        return false;
    });
    $('.api-incorrect').on('click', function () {
        Materialize.toast('Api Key/Secret is incorrect', 2000);
        return false;
    });
    $('#hidenull').on('click', function () {
        var hide = $(this).prop('checked');
        hide0balances(hide);
    });
    function hide0balances(hide) {
        if (hide) {
            for (var i = 0; i < $('.balance').length; i++) {
                var balance = $('.balance:eq(' + i + ')');
                if (parseFloat(balance.text().replace(",", ".")) == 0) {
                    balance.parent('tr').hide();
                }
            }
        } else {
            $('.balances').show();
        }
    }

    $('#wallet').find('select').on('change', function () {
        var wallet = $("#wallet").find("select option:selected").text();
        if (wallet === 'Yandex Money') {
            $('#wallet').find('input#id_address').attr('disabled', true);
            $('#yandex-wallet-add').show();
            $('#add-wallet-but').text('Продолжить')
        } else {
            $('#yandex-wallet-add').hide();
            $('#wallet').find('input#id_address').attr('disabled', false);
            $('#add-wallet-but').text('Отправить')
        }
    });

    $('.fa-commenting').on('click', function () {
        $('#user_comment_modal').modal('open');
        $('input[name="tr_id"]').val($(this).attr('data-id'));
    });
    $('#comment-form').on('submit', function () {
        var f = $(this).serializeArray();
        $('i#trans' + f[1].value).parent('td').html(f[2].value);
        $.ajax({
            url: '/transaction/new_comment/',
            type: 'post',
            dataType: 'html',
            data: f,
            success: function (q) {
                if ('ok' === q) {
                    $('#user_comment_modal').modal('close');
                    $('#comment-form')[0].reset();
                    $('i#trans' + f[1].value).parent('td').html(f[2].value);
                } else if ('none' === q) {
                    Materialize.toast('Error while saving comment')
                }
            }
        });
        return false;
    });
    $('a.scrollto').on('click', function () {
        var name = $(this).attr('href').slice(1);
        $('.collapsible').collapsible('open', $('a[name="' + name + '"]').parent('li').index() - 3);
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
        var user_coin_id = $(this).parent('td').parent('tr').attr('data-coin-id');
        change_rank(user_coin_id, 'up');
    });
    $('.rank-down').on('click', function () {
        var user_coin_id = $(this).parent('td').parent('tr').attr('data-coin-id');
        change_rank(user_coin_id, 'down');
    });

    function change_rank(coin_id, type) {
        $.ajax({
            url: '/trade/changerank/',
            dataType: 'html',
            type: 'post',
            data: {
                coin_id: coin_id,
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

    $('.pair').on('click', function () {
        var pair_id = $(this).attr('data-pair-id');

        if (!$(this).hasClass('unactive')) {
            if (confirm('Are you really want to deactivate pair ' + $(this).text())) {
                toggle_pair(pair_id)
            }
        } else {
            toggle_pair(pair_id)
        }
    });

    function toggle_pair(pair_id) {
        var user_exch = $('#exchange').val();
        $.post('/trade/toggle_pair/', {
            pair_id: pair_id,
            user_exch: user_exch,
            csrfmiddlewaretoken: getCookie('csrftoken')
        }, function (data) {
            'ok' === data ? location.reload() : Materialize.toast(data, 1500)
        });
    }

    $('.pair-share').keypress(function (e) {
        if (e.which === 13) {
            var share = $(this).val();
            var user_exch = $('#exchange').val();
            if ('' !== share) {
                var user_coin_id = $(this).parent('td').parent('tr').attr('data-coin-id');
                $.post('/trade/set_share/', {
                        coin_id: user_coin_id,
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
        var user_coin_id = $(this).parent('td').parent('tr').attr('data-coin-id');
        $.post('/trade/delete_user_coin/', {
            coin_id: user_coin_id,
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
});

socket = new WebSocket("ws://" + window.location.host + "/trade/");
socket.onmessage = function (message) {
    var data = JSON.parse(message.data);
    data.map(function (item) {
        $('.pair_last#last_' + item.pair_id).text(item.last);
        $('.pair_last#percent_' + item.pair_id).text(item.percent + '%');
        if (item.percent > 0) {
            $('.pair_last#percent_' + item.pair_id).removeClass('red-text').addClass('green-text');
            $('.pair_last#last_' + item.pair_id).parent('tr').addClass('priceChangeUp');
            $('.pair_last#arrow_' + item.pair_id).html('<i class="fa fa-arrow-up fa-1x green-text" aria-hidden="true"></i>');
        } else if (item.percent < 0) {
            $('.pair_last#percent_' + item.pair_id).removeClass('green-text').addClass('red-text');
            $('.pair_last#last_' + item.pair_id).parent('tr').addClass('priceChangeDown');
            $('.pair_last#arrow_' + item.pair_id).html('<i class="fa fa-arrow-down fa-1x red-text" aria-hidden="true"></i>');
        } else {
            $('.pair_last#percent_' + item.pair_id).removeClass('green-text red-text');
            $('.pair_last#arrow_' + item.pair_id).html('');
        }
    });
    setTimeout(function () {
        $('.pair_last').parent('tr').removeClass('priceChangeDown priceChangeUp');
    }, 600);
    draw_graph();
};

function draw_graph() {
    var ohlcData = [];
    var volumeData = [];
    $.post('/trade/get_ticker/', {
        pair_id: pair_id,
        csrfmiddlewaretoken: getCookie('csrftoken'),
        intervale: intervale,
        zoom: zoom
    }, function (ticker) {
        for (var i = 1; i < ticker.length; i++) {
            console.log(ticker[i].date);
            console.log('Это ' + new Date(ticker[i].date*1000));
            ohlcData.push([new Date(ticker[i].date * 1000), round(ticker[i].high), round(ticker[i].low), round(ticker[i].open), round(ticker[i].close)]);
            var volume = 100 + 15 * Math.random();
            volumeData.push([new Date(ticker[i].date * 1000), round(volume)]);
        }
        $('#jqChart').jqChart({
            legend: {visible: false},
            border: {lineWidth: 1, padding: 0},
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
            animation: {duration: 0.0001},
            axes: [
                {
                    type: 'linear',
                    location: 'right',
                    width: 80
                }
            ],
            series: [
                {
                    type: 'candlestick',
                    data: ohlcData,
                    priceUpFillStyle: '#4caf50',
                    priceDownFillStyle: '#f44336',
                    strokeStyle: 'black',
                    pointWidth: 0.6
                }
            ]
        });
        $('#jqChartVolume').jqChart({
            legend: {visible: false},
            border: {lineWidth: 1, padding: 0},
            tooltips: {
                disabled: false,
                type: 'shared',
                borderColor: 'black',
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
            animation: {duration: 0.0001},
            axes: [
                {
                    type: 'dateTime',
                    location: 'bottom'
                },
                {
                    type: 'linear',
                    location: 'right',
                    width: 80
                }
            ],
            series: [
                {
                    type: 'column',
                    data: volumeData,
                    fillStyle: 'lightgrey'
                }
            ]
        });
        var isHighlighting = false;

        $('#jqChart').bind('dataHighlighting', function (event, data) {

            if (!data) {
                $('#jqChartVolume').jqChart('highlightData', null);
                return;
            }

            $('#open').html(data.open);
            $('#high').html(data.high);
            $('#low').html(data.low);
            $('#close').html(data.close);

            var date = data.chart.stringFormat(data.x, "dd.mm.yyyy HH:MM");

            $('#date').html(date);

            if (!isHighlighting) {

                isHighlighting = true;

                var index = $.inArray(data.dataItem, ohlcData);
                $('#jqChartVolume').jqChart('highlightData', [volumeData[index]]);
            }

            isHighlighting = false;
        });

        $('#jqChartVolume').bind('dataHighlighting', function (event, data) {

            if (!data) {
                $('#jqChart').jqChart('highlightData', null);
                return;
            }

            $('#volume').html(data.y);

            if (!isHighlighting) {

                isHighlighting = true;

                var index = $.inArray(data.dataItem, volumeData);
                $('#jqChart').jqChart('highlightData', [ohlcData[index]]);
            }

            isHighlighting = false;
        });

        $('#jqChart').jqChart('highlightData', [ohlcData[0]]);
        $('#jqChartVolume').jqChart('highlightData', [volumeData[0]]);
    }, 'json');
}

function round(d) {
    return Math.round(100000000 * d) / 100000000
}

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