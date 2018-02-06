<?php
/**
 * @author kevin.r.jesse@gmail.com
 */
require("/home/ubuntu/chatbox/frontend/backend_connect.php");

if(function_exists($_GET['action'])) {
    echo $_GET['action']($s);
}
die();

function submit($s) {
    $chattext = strip_tags( $_GET['chattext'] );
    $UUID = strip_tags( $_GET['UUID'] );
    $mode = strip_tags( $_GET['mode'] );
    $json_array = array('id' => $UUID, 'text' => $chattext, 'mode' => $mode);
    $json = json_encode($json_array);
    socket_write($s, $json, strlen($json));
    $content = socket_read($s, 2048);
    #socket_close($s);
    return $content;
}

function getJson($s) {
    $json = json_encode(array('getJson' => true));
}

function kill($s) {
    socket_write($s, "log", strlen("log"));
    $content = socket_read($s, 2048);
}
?>