<?php

    /**
     * @author [Mubin]
     * @copyright 2013
     */
    include_once ('proxy_lib/proxy_lib.php');
    $verify_proxy = new proxy(); // create new object to verify proxy list
    $verfied_proxies = $verify_proxy->proxy_verifier(); // call the fucntion to verify proxies
    mail('mbnmughal30@gmail.com', 'Cron JOB(Proxy Verification)', "Cron JOB for the proxy verification has been completed successfully");

?>