<?php

/**
 * @author [Mubin]
 * @copyright 2013
 */

    //File will run automatically after half an hour and after that it will refresh all the IPs in list.txt and also in working.txt

    //include first the base class file(Library file).
    include_once ('proxy_lib/proxy_lib.php');
    $proxy = new proxy();
    $proxy->proxy_getter(); // call the function to import the proxy list
    //$proxy->proxy_verifier(); // call the fucntion to verify proxies
   // mail('mbnmughal30@gmail.com', 'Cron JOB', "Cron JOB for the proxy getting has been completed successfully");

?>