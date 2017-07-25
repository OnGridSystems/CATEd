$(document).ready(function () {
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
