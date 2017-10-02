<?php
/**
 * @author kevin.r.jesse@gmail.com
 */

#session_start();
#ini_set('display_errors', 1);
#ini_set('display_startup_errors', 1);
#error_reporting(E_ALL);
$UUID = uniqid();
?>

<html>
<head>
    <title>Chatbox</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/css/chat.css">
    <script src="/css/jquery.js"></script>
</head>
<body>
<div class="chat">
    <div class="chat-title">
        <h1>Cortana</h1>
        <h2>Chatbox</h2>
        <figure class="avatar">
            <img src="/lib/cortana.png"/></figure>
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
</body>
</html>

<script type="text/javascript">
    var d, m;

    $(window).onload = sendChatText("");

    $(document).ready(function () {
        $('#btnSend').click(function () {
            var chatInput = $('#chatInput').val();
            if (chatInput != "") {
                insertMessage(chatInput);
                sendChatText(chatInput);
            }
        });
    });

    function enterPress(e) {
        if (e.keyCode === 13) {
            e.preventDefault(); // Ensure it is only this code that rusn
            var chatInput = $('#chatInput').val();
            if (chatInput != "") {
                insertMessage(chatInput);
                sendChatText(chatInput);
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
            $('<div class="message loading new"><figure class="avatar"><img src="/lib/cortana.png" /></figure><span></span></div>').appendTo($('.messages-content'));
            setTimeout(function () {
                $('.message.loading').remove();
                $('<div class="message new"><figure class="avatar"><img src="/lib/cortana.png" /></figure>' + resp + '</div>').appendTo($('.messages-content')).addClass('new');
                setDate();
                scrollDown(1000)
            }, 1000);
        }
    }

    function sendChatText(chatText) {
        var request;
        var id = <?php echo json_encode($UUID);?>;
        var chatInput = chatText;
        request = $.ajax({
            type: "GET",
            url: "/submit.php?action=submit&UUID="+ encodeURIComponent(id) +"&chattext=" + encodeURIComponent(chatInput)
        });
        request.done(function (response) {
            insertAI(response)
        });
        $('#chatInput').val(null);
    }
</script>