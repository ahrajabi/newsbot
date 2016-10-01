// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var URL = 'http://django.soor.ir/chrome_extension/news/1?format=json'
var username;
var password;
var all_data;

$(document).ready(function () {
    $('body').on('click', 'li a', function () {
        chrome.tabs.create({url: $(this).attr('href')});
        return false;
    });
});


function check_login() {
    chrome.storage.local.get({
        username: '',
        password: '',
        all_data: []
    }, function (items) {
        username = items.username;
        password = items.password;
        all_data = items.all_data;
        if (username.length > 0) {
            document.getElementById('check-login').style.display = 'none';
            document.getElementById('change-user').innerHTML = 'کاربر ' + username + ' وارد شده است.';
            if (all_data.length > 0) {
                var results = '<div id="news-wrapper" class="ui styled accordion">'
                all_data.sort(
                    function (a, b) {
                        return new Date(b['published_date']).getTime() - new Date(a['published_date']).getTime()
                    });
                for (var i = 0; i < all_data.length; i++) {
                    var date = new Date(all_data[i]['published_date']);
                    var today = new Date();
                    var diffMins = Math.round((today - date) / 60000); // minutes

                    results += '<div class="title"><i class="triangle left red rss icon"></i>'

                    results += all_data[i]['title']

                    results += '<div>'
                    results += diffMins + "دقیقه‌ی پیش توسط " + all_data[i]['agency']
                    results += '</div>'

                    results += '</div>'


                    results += '<div class="content">'

                    results += '<p class="transition hidden">'
                    results += all_data[i]['summary']
                    results += '</p></div>'

                }
                results += '</div>'

                document.getElementById('results').innerHTML = results;
                $('.ui.accordion').accordion();
            }

        }
    });
}

function periodic_check_login() {
    check_login()
    self.setInterval(function () {
        check_login()
    }, 5000);
}

document.addEventListener('DOMContentLoaded', periodic_check_login);


function clear() {
    chrome.storage.local.set({
        all_data: [],
    }, function () {
    });
    doument.getElementById('results').innerHTML = ' ';
}


$(document).ready(function () {
    $('.ui.accordion').accordion();
});