<?php
    class connection{
        public function __construct(){
            
        }
        
        public static function open_connection(){
            $connection = mysqli_connect(DB_SERVER, DB_USER, DB_PASS, DB_NAME) or die(print(mysqli_error($connection)));
            mysqli_set_charset($connection, "utf8");
            return $connection;
        }
        
        public static function close_connection($connection){
            mysqli_close($connection);
        }

    }


