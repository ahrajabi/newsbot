/**
 * Created by amirhosssein on 9/25/16.
 */

var username;
var password;
var all_data = [];

function connect() {
    chrome.storage.local.get({
        username: '',
        password: '',
        all_data: []
    }, function (items) {
        username = items.username;
        password = items.password;


    });

    var ss;
    $.get('http://django.soor.ir/chrome_extension/news/' + username + '?format=json', function (data, status) {
        if (data == 0) {
            chrome.storage.local.set({
                all_data: [],
            }, function () {
                doument.getElementById('results').innerHTML = ' ';
            });
            return 0;
        }

        var i, j;
        var text = ''
        var tekrar;

        for (i = 0; i < data.length; i++) {
            tekrar = 0
            for (j = 0; j < all_data.length; j++) {
                if (data[i]['id'] == all_data[j]['id']) {
                    tekrar = 1;
                }
            }
            if (tekrar == 0) {
                all_data.push(data[i]);
            }

        }
        chrome.storage.local.set({
            all_data: all_data,
        }, function () {
        });
    });
}


connect()
var intervalID = self.setInterval(function () {
    connect()
}, 5000);
