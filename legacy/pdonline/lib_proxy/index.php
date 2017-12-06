<?php 
session_start();
// time calculation script
$time = microtime();
$time = explode(" ", $time);
$time = $time[1] + $time[0];
$start = $time;
//time calculation script




/// proxy code starts


require_once('./proxy_lib/proxy_lib.php');
 $proxy_list = new proxy(); // create new object to call the class proxy
 $proxy_list->proxy_getter(); // call the function to import the proxy list

 $verify_proxy = new proxy(); // create new object to verify proxy list
 $verfied_proxies = $verify_proxy->proxy_verifier(); // call the fucntion to verify proxies
 echo "Total verified Proxies: ".$verfied_proxies."</br>";
// include_once('proxy_lib/proxy_lib.php'); // lnclude the proxy lib
 $get_proxy = new proxy(); // create new object to verify proxy list
 $random_proxy = $get_proxy->get_proxy();// call the fucntion to verify proxies
 echo "Random Proxy from verified List: ".$random_proxy."</br>";


/// proxy code ends



//time calculation script
$time = microtime();
$time = explode(" ", $time);
$time = $time[1] + $time[0];
$finish = $time;
$totaltime = ($finish - $start);
printf ("<br>This page took %f seconds to load.", $totaltime);
//time calculation script



?>