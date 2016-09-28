// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var URL = 'http://django.soor.ir/chrome_extension/news/1?format=json'
var username;
var password;
var all_data;

$(document).ready(function () {
    $('body').on('click', 'a', function () {
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
                var results = '<h3>اخبار هم اکنون</h3>';
                results += "<div id='ajax-loader'><img src='ajax-loader.gif'/></div>"
                results += '<ul id="news-wrapper">'
                all_data.sort(
                    function (a, b) {
                        return new Date(b['published_date']).getTime() - new Date(a['published_date']).getTime()
                });
                for (var i = 0; i < all_data.length; i++) {
                    var date = new Date(all_data[i]['published_date']);
                    var today = new Date();
                    var diffMins = Math.round((today - date) / 60000); // minutes
                    results += "<li class='results-item'> <span>" + all_data[i]['agency'] +
                        "</span> - <a href=" + all_data[i]['link'] + ">" + all_data[i]['title'] + '</a>' + "</li>"
                    results += "<span>" + diffMins + "دقیقه‌ی گذشته" + "</span>"
                }
                results += '</ul>'
                results += '<button id="button-clear">پاکسازی</button>';
                document.getElementById('results').innerHTML = results;
            }

        }
    });
}

function periodic_check_login() {
    check_login()
    self.setInterval(function () {
        check_login()
    }, 1000);
}

document.addEventListener('DOMContentLoaded', periodic_check_login);


function clear() {
    $.get('http://django.soor.ir/chrome_extension/news/' + username + '?format=json', function (data, status) {
        chrome.storage.local.set({
            all_data: data,
        }, function () {
        });
    });
}

document.getElementById('button-clear').addEventListener('click',
    clear);

