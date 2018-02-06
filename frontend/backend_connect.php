<?php
$s = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if ($s === false)
    echo "socket_create() fail\n";
else {
    $result = socket_connect($s, "localhost", 13137);
    if ($result === false)
        echo "socket_connect() failed.\nReason: ($result) " . socket_strerror(socket_last_error($s)) . "\n";
}
?>
