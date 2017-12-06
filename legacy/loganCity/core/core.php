<?php

ini_set("memory_limit", "-1");
set_time_limit(0);
error_reporting(0);
Define('LIB_PATH', './core/');

// load config file first
require_once(LIB_PATH.'config.php');
require_once(LIB_PATH.'connection.php');
// load basic functions next so that everything after can use them
require_once(LIB_PATH.'functions.php');

// load core objects
require_once(LIB_PATH.'dom.php');
require_once LIB_PATH.'spider.php';

//abstract class that contains the defualt header
require_once(LIB_PATH.'parser.php');

?>