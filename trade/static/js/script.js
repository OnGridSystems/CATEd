$(document).ready(function () {
    $('select').material_select();
    $('.modal').modal();
    $('#yandex-wallet-add').hide();

    $('.input-field select').addClass('material');

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
});

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

var grid = document.getElementById('grid');

grid.onclick = function (e) {
    if (e.target.tagName != 'TH') return;
    sortGrid(e.target.cellIndex, e.target.getAttribute('data-type'));
};

function sortGrid(colNum, type) {
    var tbody = grid.getElementsByTagName('tbody')[0];
    var rowsArray = [].slice.call(tbody.rows);
    var compare;
    switch (type) {
        case 'number':
            compare = function (rowA, rowB) {
                return rowA.cells[colNum].innerHTML - rowB.cells[colNum].innerHTML;
            };
            break;
        case 'string':
            compare = function (rowA, rowB) {
                return rowA.cells[colNum].innerHTML > rowB.cells[colNum].innerHTML ? 1 : -1;
            };
            break;
    }
    rowsArray.sort(compare);
    grid.removeChild(tbody);
    for (var i = 0; i < rowsArray.length; i++) {
        tbody.appendChild(rowsArray[i]);
    }
    grid.appendChild(tbody);
}

Storage.prototype.setObject = function (key, value) {
    this.setItem(key, JSON.stringify(value));
};

Storage.prototype.getObject = function (key) {
    var value = this.getItem(key);
    try {
        return JSON.parse(value);
    }
    catch(err) {
        console.log("JSON parse failed for lookup of ", key, "\n error was: ", err);
        return null;
    }
};


// function initHashChanges() {
// 	var h = window.location.hash;
// 	var pair = h.toUpperCase();
// 	pair = pair.substr(1, pair.length); // trim #
//
// 	// trace('on load hash is [' + h + ']');
// 	// set this so we know not to override it with localStorage or default currencyPair
// 	if (currencyPairArray.indexOf(pair) != -1) {
// 		hasHashCurrencyPair = true;
// 	}
//
// 	evaluateHash(h);
//
// 	window.onhashchange = function() {
// 		// trace("hash changed: " + window.location.hash);
// 		clearTimeout(hashTimer);
// 		evaluateHash(window.location.hash);
// 	};
// }