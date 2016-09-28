/**
 * Created by amirhosssein on 9/26/16.
 */

var all_data = [];

function notification(noti, link) {
    var n = noty({
        text: noti,
        layout: 'topCenter',
        type: 'error',
        buttons: [
            {
                addClass: 'btn btn-primary', text: 'برو به خبر', onClick: function ($noty) {

                // this = button element
                // $noty = $noty element
                var win = window.open(link, '_blank');
                win.focus();
                $noty.close();
            }
            },
            {
                addClass: 'btn btn-danger', text: 'باشه', onClick: function ($noty) {
                $noty.close();
            }
            }
        ]
    });
}


function alerting() {
    chrome.storage.local.get({
        all_data: '',
        notif_mark: []
    }, function (items) {
        var marks = items.notif_mark
        all_data = items.all_data;
        for (var i = 0; i < all_data.length; i++) {
            if ($.inArray(all_data[i]['id'], marks) == -1) {
                notification(all_data[i]['title'], all_data[i]['link'])
                marks.push(all_data[i]['id'])
            }
        }
        chrome.storage.local.set({
            notif_mark: marks,
        }, function () {
        });

    });
}

function periodic_alert() {
    alerting()
    self.setInterval(function () {
        alerting()
    }, 5000);
}

periodic_alert()