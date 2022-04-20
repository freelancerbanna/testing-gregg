/*
The MIT License (MIT)

Copyright (c) 2014 Matthew A Sewell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

/*
 * If using csrf tokens, we need a list of methods that don't require them
 */
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/*
 * Main function that handles a ReST transaction through AJAX. Returns false if
 * no callback is specified or the return value of the callback if it was 
 * specified. Takes the following arguments:
 *      *   endpoint - Full URL of the API endpoint including 'http(s)'
 *      *   action - One of the standard actions used by Django's 
 *          ReST Framework ( list, create, retrieve, update, partial_update,
 *          destroy )
 *      *   data - JSON representation of the data to be sent to with the
 *          action / request
 *      *   success - function to be performed upon successful completeion of
 *          the transaction.
 *      *   failure - function to be performed if the transaction fails.
 *           
 */
jdRest = function( endpoint, action, csrf_token, data, success, failure ){
    var method, request_type;
    var headers = {};
    switch(action){
        case "list":
        case "retrieve":
            method = "GET";
            break;
        case "create":
            method = "POST";
            break;
        case "update":
            method = "POST";
            headers =  {'X-HTTP-Method-Override': 'PUT'};
            break;
        case "partial_update":
            method = "POST";
            headers =  {'X-HTTP-Method-Override': 'PATCH'};
            break;
        case "destroy":
            method = "POST";
            headers =  {'X-HTTP-Method-Override': 'DELETE'};
            break;
    }
    
    if( csrf_token ){
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                }
            }
        });
    }
    
    var request = $.ajax({
                        url: endpoint,
                        type: method,
                        headers: headers,
                        data: data
                        });
 
    request.done(function( msg ) {
        if( success ){ //If the success callback was specified...
            return success(msg);
        }
        return false;
    });
 
    request.fail(function( jqXHR, textStatus ) {
        if( failure ){ //If the failure callback was specified
            return failure( jqXHR, textStatus );
        }
        return false;
    }); 
}



