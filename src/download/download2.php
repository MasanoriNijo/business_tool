<?php
$filepath = './files/app-release_tb_stg_20250729000004.apk';  // ダウンロードさせたいファイルのパス
$filepath2 = './files/tb_stg_20240717000003.apk';  // ダウンロードさせたいファイルのパス

function downLoad($filepath){
    if (file_exists($filepath)) {
        // ファイルの種類（MIME）を指定
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($filepath) . '"');
        header('Content-Length: ' . filesize($filepath));
        readfile($filepath);  // ファイルの中身を出力
        exit;
    } else {
        echo "ファイルが見つかりません。";
    }
}

// downLoad($filepath);
downLoad($filepath2);
