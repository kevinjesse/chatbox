<?php
/**
 * @author kevin.r.jesse@gmail.com
 */
require_once("/home/ubuntu/chatbox/frontend/backend_connect.php");

if(function_exists($_GET['action'])) {
     echo $_GET['action']($s);
}
die();

function submit($s) {
    $chattext = strip_tags( $_GET['chattext'] );
    $UUID = strip_tags( $_GET['UUID'] );
    $json_array = array('id' => $UUID, 'text' => $chattext);
    $json = json_encode($json_array);
    socket_write($s, $json, strlen($json));
    $content = socket_read($s, 2048);
    socket_close($s);
    return $content;
}
?>