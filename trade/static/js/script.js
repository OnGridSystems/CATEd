$(document).ready(function () {
    $('select').material_select();
    $('.modal').modal();

    $('.change_status').on('click', function () {
        var ue = $(this).parent('form').find('input[name="user-exchange"]').val();
        var csrf = $('input[name="csrfmiddlewaretoken"]').val();
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
                data === 'ok' ? location.reload() : Materialize.toast('Не удалось включить API');
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

});

