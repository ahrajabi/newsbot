// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var URL = 'http://django.soor.ir/chrome_extension/news/1?format=json'
var username;
var password;
var all_data;


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
            if(all_data.length>0){
                var results = '<h3>اخبار هم اکنون</h3>';
                results+= "<div id='ajax-loader'><img src='ajax-loader.gif'/></div>"
                results += '<ul id="news-wrapper">'
                for(var i =0 ; i < all_data.length ; i++){
                    results += "<li class='results-item'>"+ all_data[i]['title'] + "</li>"
                }
                results += '</ul>'
                document.getElementById('results').innerHTML = results;
            }

        }
    });
}


function periodic_check_login(){
    check_login()
    self.setInterval(function() { check_login() }, 5000);
}

document.addEventListener('DOMContentLoaded', periodic_check_login);
