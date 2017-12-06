<?php
require_once 'dom.php';
/**
 * Description of class
 *                      static class and will scrap the page
 * @author Mubin Khalid
 */
	class Spider
	{
		//spider function will require a lot of arguments and that will be set as the "Header", Referer and other stuff
		// url -- the page you want to crawl
		public function __construct()
		{

		}
		public static function yql($url)
		{
			$yql_base_url = "http://query.yahooapis.com/v1/public/yql";
			$url = "select * from html where url = '$url'";

			$yql_query_url = $yql_base_url . "?q=" . urlencode($url);
			$yql_query_url .= "&format=json";
			//echo '<br />https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%20%3D%20%22http%3A%2F%2Ftrustedpros.ca%2Fmb%2Fwinnipeg%22&format=json&diagnostics=true&callback=';
			$session = curl_init($yql_query_url);
			curl_setopt($session, CURLOPT_RETURNTRANSFER, true);
			$json = curl_exec($session);
			curl_close($session);
			return json_decode($json, true);
		}
		public static function spider($header = array(), $referer = false, $url, $cookie = false,
			$post = false, $useProxy = false)
		{
			if (!$cookie)
			{
				$cookie = "cookie.txt";
			}
			$ch = curl_init();
			curl_setopt($ch, CURLOPT_ENCODING, 'gzip,deflate,sdch');
			if (isset($header) && !empty($header))
			{
				curl_setopt($ch, CURLOPT_HTTPHEADER, $header);

			}
			curl_setopt($ch, CURLOPT_URL, $url);
			$proxies = file("./lib_proxy/proxy_list/working.txt");
			if($useProxy){
				if(count($proxies)){
					$ip = explode(":", $proxies[rand(0, count($proxies)-1)]);
					curl_setopt($ch, CURLOPT_PROXY, $ip[0]);
					curl_setopt($ch, CURLOPT_PROXYPORT, $ip[1]);
				}
			}	
			curl_setopt($ch, CURLOPT_HEADER, 0);
			curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
			curl_setopt($ch, CURLOPT_TIMEOUT, 500);
			curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
			curl_setopt($ch, CURLOPT_MAXREDIRS, 5);
			curl_setopt($ch, CURLOPT_USERAGENT,
				"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0");
			curl_setopt($ch, CURLOPT_COOKIEJAR, realpath($cookie));
			curl_setopt($ch, CURLOPT_COOKIEFILE, realpath($cookie));
			curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
			if (isset($referer) && $referer != false)
			{
				curl_setopt($ch, CURLOPT_REFERER, $referer);
			} else
			{
				curl_setopt($ch, CURLOPT_REFERER, $url);
			}
			//if have to post data on the server
			if (isset($post) && !empty($post) && $post)
			{
				curl_setopt($ch, CURLOPT_POST, true);
				curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
			} //endif
			$data = curl_exec($ch);
			$info = curl_getinfo($ch);
            
			curl_close($ch);
			if($info['http_code'] == 200){
				return ($data);
			}else{
				return false;
			}
		}
	}
