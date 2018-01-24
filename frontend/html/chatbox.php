<?php
/**
 * @author kevin.r.jesse@gmail.com
 */

session_start();
#ini_set('display_errors', 1);
#ini_set('display_startup_errors', 1);
#error_reporting(E_ALL);
//if (!session_id()) {
//    session_id(uniqid());
//}

$UUID = uniqid();
?>

<html>
<head>
    <title>Chatbox</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="css/chat.css">
    <script src="css/jquery.js"></script>
</head>
<body>
<div class="chat">
    <div class="chat-title">
        <h1>Chatbot</h1>
        <h2>Interaction - Chatbox</h2>
        <figure class="avatar">
            <img src="lib/chatbox-small.png"/></figure>
    </div>
    <div id="messages" class="messages">
        <div id="messages-content" class="messages-content"></div>
    </div>
    <div class="message-box">
        <input name="chatInput" type='text' class="message-input" placeholder="Type message..."
               id="chatInput" onkeypress="enterPress(event)"/>
        <input type="button" class="message-submit" id="btnSend" value="Send"/>
    </div>
</div>
<div class="buttonCtrl" id="buttonCtrlForm">
    <form id="showSurveyForm" action="">
        <input type="button" class="next" id="btnShowSurvey" value="Next" />
    </form>
</div>
</body>
</html>

<script type="text/javascript">
    var d, m, s;
    var id = <?php echo json_encode($UUID);?>;
    var listen = false;
    $(window).onload = sendChatText("", false);
    //$(window).onunload = sendKill();
    $(document).ready(function () {
        $('#btnSend').click(function () {
            var chatInput = $('#chatInput').val();
            if (chatInput != "") {
                insertMessage(chatInput);
                sendChatText(chatInput, false);
                $('#chatInput').val(null);
            }
        });
        document.getElementById("btnShowSurvey").onclick = function () {
            /*request = $.ajax({
                type: "GET",
                url: "/submit.php?action=getJson&UUID="+ encodeURIComponent(id)
            });*/
            location.href = "survey.php?id="+ encodeURIComponent(id);
        };

        var position = $('.chat').offset();
        $('.buttonCtrl').offset({
            top: position.top + $('.chat').outerHeight(true),
            left: position.left
        })
    });

    function sendKill() {
        var request;
        request = $.ajax({
            type: "GET",
            url: "submit.php?action=kill&UUID="+ encodeURIComponent(id)
        });
        request.done(function (response) {
        });
    }

    function enterPress(e) {
        if (e.keyCode === 13) {
            e.preventDefault(); // Ensure it is only this code that rusn
            var chatInput = $('#chatInput').val();
            if (chatInput != "") {
                insertMessage(chatInput);
                sendChatText(chatInput, false);
                $('#chatInput').val(null);
            }
        }
    }

    function setDate() {
        d = new Date();
        if (m != d.getMinutes()) {
            m = d.getMinutes();
            $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
        }
    }

    function scrollDown(speed) {
        $("#messages").animate({scrollTop: $('#messages').prop("scrollHeight")}, speed);
    }

    function insertMessage(chatInput) {
        if (chatInput != "") {
            $('<div class="message message-personal" >' + chatInput + '</div>').appendTo($('.messages-content')).addClass('new');
            setDate();
            scrollDown(100)
        }
    }

    function insertAI(resp) {
        if (resp != "") {
            $('<div class="message loading new"><figure class="avatar"><img src="/lib/chatbox-small.png" ' +
                '/></figure><span></span></div>').appendTo($('.messages-content'));
            setTimeout(function () {
                $('.message.loading').remove();
                $('<div class="message new"><figure class="avatar"><img src="/lib/chatbox-small.png" /></figure>' +
                    resp + '</div>').appendTo($('.messages-content')).addClass('new');
                setDate();
                scrollDown(1000)
            }, 1000);
            $('#chatInput').val(null);
        }
    }

    function sendChatText(chatText, mode) {
        var request;
        var chatInput = chatText;
        request = $.ajax({
            type: "GET",
            url: "submit.php?action=submit&UUID="+ encodeURIComponent(id) +"&chattext=" + encodeURIComponent(chatInput) +"&mode="+mode
        });
        request.done(function (response) {
            respJSON = JSON.parse(response);

            console.log(response);


            insertAI(respJSON['response']);

            //if (listen === false) {
            ////////   listen = true;

            //sendChatText('', listen);

            //}
        });
        //listen = false;

    }

    function listener() {
        var request;
        if (listen === false) {
            listen = true;
            request = $.ajax({
                type: "GET",
                url: "submit.php?action=submit&UUID=" + encodeURIComponent(id) + "&chattext=" + encodeURIComponent('') + "&mode=" + true
            });
            request.done(function (response) {
                respJSON = JSON.parse(response);

                console.log(response);

                insertAI(respJSON['response']);
                //if (listen === false) {
                ////////   listen = true;

                //sendChatText('', listen);

                //}
                listen = false;
                if (respJSON['signal'] === "end") {
                    document.getElementById('buttonCtrlForm').style.display = "block"
                }
            });

        }
        //listen = false;

    }
    //
    setInterval(function() {listener();}, 2000);


</script>
