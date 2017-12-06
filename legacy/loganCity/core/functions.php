<?php
    //require_once("core.php");
     /**
     * Description of class
     *                      includes all the common features that will be used for scrapping the data, cleaning the data and other
     * @author Mubin Khalid
     */
     $functions = new functions();
    class functions{
        public $line;
        public function __construct() {

            $this->line = "___________________________________________________________________________________";
        }
	public function getHiddenFields($html){
            $fields = array();
            foreach ($html->find('input[type=hidden]') as $input)  {    
                $fields[$input->name] = html_entity_decode($input->value, ENT_QUOTES, 'UTF-8');
            }
            return $fields;
        }
      
        public function normalize($string){
                return strtolower($string);
        }
        public function GetHTMLFromDom($domNodeList){ 
            $domDocument = new DOMDocument(); 
            foreach ($domNodeList as $node) {

                $domDocument->appendChild($domDocument->importNode($node, true)); 
                $domDocument->appendChild($domDocument->createTextNode(" ")); 
            }
            return $domDocument->saveHTML(); 
        }
        public function clean_text($string){
            $string = strip_tags($string);
            $string = str_replace("â€", "-", $string);

            $string = str_replace("&nbsp;"," ",$string);
            $string = str_replace("  "," ",$string);
            $string = str_replace("&quot;","",$string);
            $string = str_replace("\n","",$string);
            $string = str_replace("\r","",$string);
            $string = str_replace("\t","",$string);
            $string = str_replace(chr(194),"",$string);
            $string = str_replace("â‚¬", "€", $string);
            $string = trim($string);
            return $string;
        }
        public function clean_number($string){
            $string = str_replace("$","",$string);
            $string = str_replace("£","",$string);
            $string = str_replace("€","",$string);
            $string = str_replace(",","",$string);
            $string = trim($string);
            $string = strip_tags($string);
            return $string;
        }
        public function beHuman(){
            sleep(rand(3, 7));
        }
        public function populateDB($data, $table = 'job_requests', $useQuery = false)
        {
            //open connection from the connection file
            //it'll reccieve table as a String and data in the form of array(key value pair) and adjust those key values to a query
            // $where is an array that will take array as first one and impose that as an 'WHERE' clause and will set its values.
            if(!$useQuery)$data['required_credentials'] = implode(', ', $data['required_credentials']);
            $connection = connection::open_connection();
            $fields = array();
            $values = array();
            $val = '';
            foreach ($data as $key => $value) {
                $fields[] = "`$key`";
                $values[] = "'" . mysqli_real_escape_string($connection, $value) . "'";
            }
            if (count($fields) == count($values)) {
                $insert = implode(", ", $fields);
                $val = implode(", ", $values);
            }
            $val  = utf8_encode($val);
            //mysql_set_charset('utf8');
            mysqli_query($connection, "SET NAMES 'utf8'");
            $sql = "INSERT INTO $table($insert) VALUES($val) ";
            if($useQuery){
                unset($useQuery['url']);
                $sql .= $this->createUpdate($connection, $useQuery);
            }else{
                $sql .= " ON DUPLICATE KEY UPDATE `start_date` = '".($data['start_date'])."', `end_date` = '".($data['end_date'])."', `rate` = '".($data['rate'])."';";
            }
            //print($sql);
            mysqli_query($connection, $sql)or die(print(mysqli_error($connection))."<br />".print($sql));
            connection::close_connection($connection);

        }
        private function createUpdate($connection, $data = array()){
            if(count($data) > 0){
                $sql = " ON DUPLICATE KEY UPDATE ";
                $keys = array();
                foreach($data as $key => $value){
                    $value = mysqli_real_escape_string($connection, $value);
                    $keys[] = "`$key` = '$value'";
                }
                $sql .= implode(", ", $keys);
                return $sql;
            }
        }
    }
?>
