/**
 * Created by amirhosssein on 9/25/16.
 */

var URL = 'http://django.soor.ir/chrome_extension/news/1?format=json'


var username;
var password;
var all_data = [];

function connect() {
    var ss;
    $.get(URL, function (data, status) {
        var i,j;
        var text = ''
        var tekrar;
        for (i = 0; i < data.length; i++) {
            tekrar = 0
            for(j = 0 ; j<all_data.length; j++){
                if (data[i]['id']==all_data[j]['id']){
                    tekrar = 1;
                }
            }
            if(tekrar == 0){
                all_data.push(data[i]);
            }

        }
        all_data = data
        chrome.extension.getBackgroundPage().console.log(all_data)
        chrome.storage.local.set({
            all_data: all_data,
        }, function () {
        });
    });
}


chrome.storage.local.get({
    username: '',
    password: '',
    all_data: []
}, function (items) {
    username = items.username;
    password = items.password;
    if (username.length > 0) {
        connect()
        var intervalID = self.setInterval(function() { connect() }, 5000);

    }
});