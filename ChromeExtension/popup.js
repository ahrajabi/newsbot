// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var URL = 'http://django.soor.ir/chrome_extension/news/1'

function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

function connect() {
  var results = document.getElementById('results')
  results.innerHTML = httpGet(URL)
}

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('submit').addEventListener(
      'click', connect);
});
