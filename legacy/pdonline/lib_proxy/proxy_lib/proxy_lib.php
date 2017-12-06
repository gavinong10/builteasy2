<?php
	set_time_limit(0);
	include_once ('simple_html_dom.php');


    class proxy
	{
		//define public variables
		    	public $base_url = "c:\wamp\www\pdonline\lib_proxy";// base directory of website
		    	public $poxy_list_file= "/proxy_list/proxy.txt";// path to list of all imported proxies
		    	public $verified_proxy_list= "/proxy_list/working.txt"; // path to list of verified proxy list
		    	public $loginurl= "http://incloak.com/login";// login url
		    	public $search_url="http://incloak.com/api/proxylist.txt?maxtime=400&ports=8888,7808,8080,8089,3127,3128&type=h&out=plain&lang=en"; // search and get list
		    	public $url_to_test = "http://infrenzy.com/YP/YP/_/proxyVerifier/index.php";// Url to test each proxy

		    	public function proxy_getter()  
		        {   
		    	
				            $url_to_file=$this->base_url.$this->poxy_list_file; // path to save imported list of proxies

							(get_page1($this->loginurl));// Login Url

							$html = file_get_html(($this->search_url))->plaintext;
							//echo $html;die();
							file_put_contents($url_to_file, '');
							$list=explode(" ",$html);

							foreach($list as $ip){
								if(!empty($ip) && $ip!=" " && $ip!=null){
									file_put_contents($url_to_file , trim($ip) . PHP_EOL, FILE_APPEND ) ;
								}
							}
							//var_dump($list);die();
		        } 

		        public function proxy_verifier()  
		        {   
		    	        
		    	        $verified_proxies= $this->base_url.$this->verified_proxy_list;
		    	        $url_to_file=$this->base_url.$this->poxy_list_file; // path to save imported list of proxies
				        $counter = 0;
						file_put_contents($verified_proxies, '');
						$list = file( $url_to_file, FILE_IGNORE_NEW_LINES | 
				            FILE_SKIP_EMPTY_LINES ) ; 
						
						foreach($list as $ip){
							$ch = curl_init();
							curl_setopt($ch, CURLOPT_URL, $this->url_to_test);
							curl_setopt($ch, CURLOPT_HEADER, 0); // return headers 0 no 1 yes
							curl_setopt($ch, CURLOPT_PROXY, $ip);
							curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1); // return page 1:yes
							curl_setopt($ch, CURLOPT_TIMEOUT, 2); // http request timeout 200 seconds
							$data = curl_exec($ch); // execute the http request
							if(strlen($data) > 50){
								file_put_contents( $verified_proxies, trim($ip) . PHP_EOL, FILE_APPEND ) ;
				                $counter++;
							}
							else{
							
							}
							curl_close($ch); // close the connection
						}
				         return $counter;
		        } 

		        public function get_proxy()
		        {
				            $verified_proxies= $this->base_url.$this->verified_proxy_list;
							

						    $file = fopen($verified_proxies, "r");
							$proxies = array();

								while (!feof($file)) {
								   $proxies[] = fgets($file);
								}

								fclose($file);
                                $rand_keys = array_rand($proxies, 2);
								return $proxies[$rand_keys[0]];
		        }
    }


	function get_page1($url)
	{
		$post="c=1452065231";
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, $url);
		curl_setopt($ch, CURLOPT_HEADER, 0); // return headers 0 no 1 yes
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1); // return page 1:yes
		curl_setopt($ch, CURLOPT_TIMEOUT, 200); // http request timeout 200 seconds
		curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); // Follow redirects, need this if the url changes
		curl_setopt($ch, CURLOPT_MAXREDIRS, 2); //if http server gives redirection responce
		curl_setopt($ch, CURLOPT_USERAGENT,
			"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7");
		curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // false for https
		
		curl_setopt($ch,CURLOPT_POST, true);
		curl_setopt($ch,CURLOPT_POSTFIELDS, $post);	
		$data = curl_exec($ch); // execute the http request
		curl_close($ch); // close the connection
		return $data;
	}
	function get_page($url)
	{
		//$post="c=1106511574";
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, $url);
		curl_setopt($ch, CURLOPT_HEADER, 0); // return headers 0 no 1 yes
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1); // return page 1:yes
		curl_setopt($ch, CURLOPT_TIMEOUT, 200); // http request timeout 200 seconds
		curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); // Follow redirects, need this if the url changes
		curl_setopt($ch, CURLOPT_MAXREDIRS, 2); //if http server gives redirection responce
		curl_setopt($ch, CURLOPT_USERAGENT,
			"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7");
		curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // false for https
		$data = curl_exec($ch); // execute the http request
		curl_close($ch); // close the connection
		return $data;
	}

	
?>
