<?php

/*
* @author: MMK<mbnmughal30@gmail.com>
* @version: 2.0
*/
	require_once './core/core.php';
error_reporting(1);
	class pdOnlineLogan

	{
		private $IAgree;
		private $propertyEnquiry;
		public $street;
		public $streets;

		public $sub;
		public $suburbs;

		public function __construct($type, $street = FALSE, $suburb = FALSE)
		{
			$this->streets = file('streets.txt', FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES);
			$this->suburbs = file('suburbs.txt', FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES);
			if(isset($_POST['street']))
				$this->street = $_POST['street'];
			else
				$this->street = FALSE;
			if(isset($_POST['suburb']))
				$this->sub = $_POST['suburb'];
			else
				$this->sub = FALSE;
			if($street)
				$this->street = $street;
			if($suburb)
				$this->suburb = $suburb;

			$this->IAgree = 'http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/ApplicationMaster/';
			$this->propertyEnquiry = 'http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/PropertyMaster/Default.aspx?page=search';
			$this->pressAgree($type);
			//var_dump($this);die;
		}
		private function pressAgree($type)
		{
			
			global $functions;
			$page = str_get_html($this->request($this->IAgree));
			if ($page) {
				$post['ctl00_RadScriptManager1_TSM'] = ';;System.Web.Extensions, Version=3.5.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-US:b4491a8b-c094-46c4-848c-d2a016749dfa:ea597d4b:b25378d2;Telerik.Web.UI, Version=2012.2.607.35, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-US:99e38628-ac51-4787-84f7-90d827ba8fe8:16e4e7cd:f7645509:24ee1bba:e330518b:2003d0b8:1e771326:c8618e41:8e6f0d33';
				$post = array_merge($post, $functions->getHiddenFields($page));
				$post['ctl00_cphContent_ctl01_RadTabStrip1_ClientState'] = '{"selectedIndexes":["0"],"logEntries":[],"scrollState":{}}';
				$post['ctl00$cphContent$ctl01$Button1'] = 'Agree';
				$page = $this->request('http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/ApplicationMaster/default.aspx', FALSE, http_build_query($post));
				if ($type == 'application') $this->goToApplicationEnquiry();
				else {
					$this->goToSearch();
				}
			}
			else {
				file_put_contents('error_log.txt', "Unable to click on Agree button" . PHP_EOL, FILE_APPEND);
			}
		}
		private function goToApplicationEnquiry()
		{
			
			if ($this->street) {
				$street = urlencode($this->street);
			}
			else {
				$street = '';
			}
			if ($this->sub) {
				$suburb = urlencode($this->sub);
			}
			else {
				$suburb = '';
			}
			if (!empty($_POST['from'])) {
				$startDate = explode('-', $_POST['from']);
				$startDate = urlencode($startDate[2] . '/' . $startDate[1] . '/' . $startDate[0]);
			}
			else {
				$startDate = '';
			}
			if (!empty($_POST['to'])) {
				$endDate = explode('-', $_POST['to']);
				$endDate = urlencode($endDate[2] . '/' . $endDate[1] . '/' . $endDate[0]);
			}
			else {
				$endDate = '';
			}
			if($street == 'all'){
				foreach($this->streets as $street){
					$street = urlencode($street);
					$url = "http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/ApplicationMaster/default.aspx?page=found&1=$startDate&2=$endDate&3=&4=&4a=&6=F&11=&12=&13=$street&14=$suburb&21=&22=";
					$page = str_get_html($this->request($url));
					$this->processForEnquiry($page, $url);
				}
			}
			else{
				$url = "http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/ApplicationMaster/default.aspx?page=found&1=$startDate&2=$endDate&3=&4=&4a=&6=F&11=&12=&13=$street&14=$suburb&21=&22=";
				$page = str_get_html($this->request($url));
				$this->processForEnquiry($page, $url);

			}
		}

		private function processForEnquiry($page, $url, $counter)
		{
			if ($page) {
				global $functions;
				$page = str_get_html(html_entity_decode($page));
				if(strpos($page, 'rgInfoPart') === FALSE){
					$total = 10;
				}else
					$total = $page->find('.rgInfoPart', 0)->find('strong', 0)->plaintext;
				$table = $page->find('#ctl00_cphContent_ctl01_ctl00_RadGrid1_ctl00', 0);
				foreach($table->find('.rgRow,.rgAltRow') as $tr) {
					if($counter > (int) $total){	
						//header('Location: index.php');
						return;
					}
					$counter += 1;
					$data = array();
					$data['url'] = "http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/ApplicationMaster/" . $tr->find('a', 0)->href;
					$data['number'] = $tr->find('td', 1)->plaintext;
					$data['submitted'] = $tr->find('td', 2)->plaintext;
					$data['details'] = $tr->find('td', 3)->plaintext;
					$data = array_merge($data, $this->findStreetAndSuburb($data['details']));
					$data = array_merge($data, $this->getApplicationSubPage($data['url']));
					$this->saveApplication($data);
				}
				if (strpos($page, 'rgPageNext') !== FALSE) {
					preg_match('/doPostBack\(\'(.*?)\',/is', $page->find('.rgCurrentPage', 0)->next_sibling() , $m);
					if (!isset($m[1]) || empty($m[1])) {
						return;
					}
					$evnetTarget = $m[1];
					$post = array(
						'ctl00$RadScriptManager1' => 'ctl00$cphContent$ctl01$ctl00$cphContent$ctl01$Radajaxpanel2Panel|ctl00$cphContent$ctl01$ctl00$RadGrid1$ctl00$ctl03$ctl01$ctl28',
						'ctl00_RadScriptManager1_TSM' => ';;System.Web.Extensions, Version=3.5.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-US:b4491a8b-c094-46c4-848c-d2a016749dfa:ea597d4b:b25378d2;Telerik.Web.UI, Version=2012.2.607.35, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-US:99e38628-ac51-4787-84f7-90d827ba8fe8:16e4e7cd:f7645509:24ee1bba:e330518b:2003d0b8:1e771326:c8618e41:f46195d3:4cacbc31:8e6f0d33:ed16cbdc:58366029:aa288e2d;',
						'ctl00_cphSideNave_PrevSearch_link1_radTT_ClientState' => '',
						'ctl00_cphSideNave_PrevSearch_link2_radTT_ClientState' => '',
						'ctl00_cphSideNave_PrevSearch_link3_radTT_ClientState' => '',
						'ctl00_cphSideNave_PrevSearch_link4_radTT_ClientState' => '',
						'ctl00_cphSideNave_PrevSearch_link5_radTT_ClientState' => '',
						'ctl00_cphSideNave_PrevSearch_PrevSearchMenu_ClientState' => '{"expandedItems":["0"],"logEntries":[],"selectedItems":[]}',
						'ctl00_cphSideNave_LeftSubNav_LeftSubNavMenu_ClientState' => '{"expandedItems":["0"],"logEntries":[],"selectedItems":[]}',
						'ctl00_cphContent_ctl01_RadTabStrip1_ClientState' => '{"selectedIndexes":["0"],"logEntries":[],"scrollState":{}}',
						'ctl00$cphContent$ctl01$ctl00$RadGrid1$ctl00$ctl03$ctl01$PageSizeComboBox' => 10,
						'ctl00_cphContent_ctl01_ctl00_RadGrid1_ctl00_ctl03_ctl01_PageSizeComboBox_ClientState' => '',
						'ctl00_cphContent_ctl01_ctl00_RadGrid1_ClientState' => ''
					);
					$post = array_merge($post, $functions->getHiddenFields($page));
					$post['__EVENTTARGET'] = $evnetTarget;
					$post['__ASYNCPOST'] = 'true';
					$post['RadAJAXControlID'] = 'ctl00_cphContent_ctl01_Radajaxpanel2';
					$page = (($this->request($url, array('X-MicrosoftAjax' => 'Delta=true') , http_build_query($post))));
					$this->processForEnquiry($page, $url, $counter);
				}
			}
		}
		private function findStreetAndSuburb($title, $subOnly = FALSE){
			$date = array();
			foreach($this->suburbs as $suburb){
				if(strpos($title, $suburb) !== FALSE){
					$data['suburb'] = $suburb;
					break;
				}
			}
			if($subOnly)
				return $data;
			foreach($this->streets as $street){
				if(strpos($title, $street) !== FALSE){
					$data['street'] = $street;
					break;
				}
			}
			return $data;	

		}
		private function goToSearch()
		{
			global $functions;
			if($this->street !== 'all'){
				$street = urlencode($this->street);
				$vars = array(
					'street' => urldecode($street)
					);
				$url = "http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/PropertyMaster/default.aspx?page=found&1=&2=&3=$street&4=&5=T&6=F&7=&8=&11=&12=";
				if (!empty($_POST['suburb'])) {
					$vars['suburb'] = $_POST['suburb'];
					$sub = urlencode($sub);
					$url = "http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/PropertyMaster/default.aspx?page=found&1=&2=&3=$street&4=$sub&5=T&6=F&7=&8=&11=&12=";
				}
				$page = str_get_html($this->request($url));
				$this->processPage($page, $url, $vars);
			}else{
				foreach($this->streets as $street){
					$vars = array(
						'street' => ($street)
						);
					$street = urlencode($street);
					$url = "http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/PropertyMaster/default.aspx?page=found&1=&2=&3=$street&4=&5=T&6=F&7=&8=&11=&12=";
					if (!empty($_POST['suburb'])) {
						$vars['suburb'] = $_POST['suburb'];
						$sub = urlencode($sub);
						$url = "http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/PropertyMaster/default.aspx?page=found&1=&2=&3=$street&4=$sub&5=T&6=F&7=&8=&11=&12=";
					}
					//echo $url."<hr />";//die;
					$page = str_get_html($this->request($url));
					//die();
					$this->processPage($page, $url, $vars);
				}
			}
		}
		private function findSub($sub){
			foreach($this->suburbs as $suburb){
				if(strpos($sub, $suburb) !== false)
					return $suburb;
			}
		}
		private function processPage($page, $url, $vars, $counter = 0)
		{
			if ($page) {
				global $functions;
				$page = str_get_html(html_entity_decode($page));
				$table = $page->find('#ctl00_cphContent_ctl01_ctl00_RadGrid1_ctl00', 0);
				if(strpos($page, 'rgInfoPart') === FALSE){
					$total = 10;
				}else
					$total = $page->find('.rgInfoPart', 0)->find('strong', 0)->plaintext;
				foreach($table->find('.rgRow,.rgAltRow') as $tr) {
					if($counter > (int) $total){	
						//header('Location: index.php');
						return;
					}
					$counter += 1;
					$data = array();
					$data['url'] = "http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/PropertyMaster/" . $tr->find('a', 0)->href;
					$data['title'] = $tr->find('td', 1)->plaintext;
					$data['street'] = $vars['street'];
					if (isset($vars['suburb'])) {
						$data['suburb'] = $vars['suburb'];
					}
					else {
						preg_match('/' . $data['street'] . '(.*?)\(/is', $data['title'], $suburb);
							$data['suburb'] = trim($this->findSub($suburb[1]));
						}
						$data = array_merge($data, $this->getSubPage($data['url']));
						$this->saveProperty($data);
				}
				if (strpos($page, 'rgPageNext') !== FALSE) {
					preg_match('/doPostBack\(\'(.*?)\',/is', $page->find('.rgCurrentPage', 0)->next_sibling() , $m);
						if (!isset($m[1]) || empty($m[1])) {
							return;
						}
					$evnetTarget = $m[1];
					$post = array(
						'ctl00$RadScriptManager1' => 'ctl00$cphContent$ctl01$ctl00$cphContent$ctl01$Radajaxpanel2Panel|ctl00$cphContent$ctl01$ctl00$RadGrid1$ctl00$ctl03$ctl01$ctl22',
						'ctl00_RadScriptManager1_TSM' => ';;System.Web.Extensions, Version=3.5.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-US:b4491a8b-c094-46c4-848c-d2a016749dfa:ea597d4b:b25378d2;Telerik.Web.UI, Version=2012.2.607.35, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-US:99e38628-ac51-4787-84f7-90d827ba8fe8:16e4e7cd:f7645509:24ee1bba:e330518b:2003d0b8:1e771326:c8618e41:f46195d3:4cacbc31:8e6f0d33:ed16cbdc:58366029:aa288e2d;',
						'ctl00_cphSideNave_LeftSubNav_LeftSubNavMenu_ClientState' => '{"expandedItems":["0"],"logEntries":[],"selectedItems":[]}',
						'ctl00_cphContent_ctl01_RadTabStrip1_ClientState' => '{"selectedIndexes":["0"],"logEntries":[],"scrollState":{}}',
						'ctl00$cphContent$ctl01$ctl00$RadGrid1$ctl00$ctl03$ctl01$PageSizeComboBox' => 10,
						'ctl00_cphContent_ctl01_ctl00_RadGrid1_ctl00_ctl03_ctl01_PageSizeComboBox_ClientState' => '',
						'ctl00_cphContent_ctl01_ctl00_RadGrid1_ClientState' => ''
					);
					$post = array_merge($post, $functions->getHiddenFields($page));
					$post['__EVENTTARGET'] = $evnetTarget;
					$post['__ASYNCPOST'] = 'true';
					$post['RadAJAXControlID'] = 'ctl00_cphContent_ctl01_Radajaxpanel2';
									// $url = 'http://pdonline.logan.qld.gov.au/MasterViewUI/Modules/PropertyMaster/default.aspx?page=found&1=&2=&3=Wembley+Road&4=&5=T&6=F&7=&8=&11=&12=';
					$page = (($this->request($url, array('X-MicrosoftAjax' => 'Delta=true') , http_build_query($post))));
					$this->processPage($page, $url, $vars, $counter);
				}
			}
		}
		private function getSubPage($url)
		{
			$page = str_get_html(html_entity_decode($this->request($url)));
			$data = array();
			if (!$page) {
				file_put_contents('error_log.txt', "Unable to visit URL: $url" . PHP_EOL, FILE_APPEND);
				return false;
			}
			$data['address'] = $page->find('#ctl00_cphContent_ctl00_lblPropertyHeader', 0)->plaintext;
			$data['other_details'] = strip_tags(str_replace('', '', $page->find('#lbl1', 0)->innertext));
			$data['dimensions'] = strip_tags(str_replace('<br>', ' | ', $page->find('#lblDim', 0)->innertext));
			$data['zone'] = strip_tags(str_replace('<br>', ' | ', $page->find('#lblZoning', 0)->innertext));
			$data['constraints'] = (str_replace(array('<br>', '<br />', '<br/>') , ' | ', $page->find('#lblConstraints', 0)->innertext));
			$app = $page->find('#lblApp', 0);
			$a = array();
			foreach($app->find('a') as $anchor) {
				$a[] = trim($anchor->plaintext);
			}
			$data['applications'] = implode(" | ", $a);
			return $data;
		}
		private function getApplicationSubPage($url)
		{
			$page = str_get_html(html_entity_decode($this->request($url)));
			$data = array();
			if (!$page) {
				file_put_contents('error_log.txt', "Unable to visit URL: $url" . PHP_EOL, FILE_APPEND);
				return false;
			}
			$data['address'] = $page->find('#ctl00_cphContent_ctl00_lblApplicationHeader', 0)->plaintext;
			$data['other_details'] = strip_tags(str_replace('<br>', ' | ', $page->find('#lblDetails', 0)->innertext));
			$data['decisions'] = strip_tags(str_replace('<br>', ' | ', $page->find('#lblDecision', 0)->innertext));
			$data['status'] = strip_tags(str_replace('<br>', ' | ', $page->find('#lblStatus', 0)->innertext));
			$data['people'] = (str_replace(array('<br>', '<br />', '<br/>') , ' | ', $page->find('#lblPeople', 0)->innertext)); $task = $page->find('#lblTasks', 0);
			$tasksData = array();
			$counter = 1;
			$currentTD = 0;
			foreach($task->find('td') as $td){
				if(trim($td->plaintext) == 'Started' || trim($td->plaintext) == 'Description' || trim($td->plaintext) == 'Completed') continue;
				$tasks = array();
				$tasks[] = trim($td->plaintext);
				$currentTD += 1;
				if($currentTD == 3){

					$currentTD = 0;
				}
				$tasksData[] = implode(' => ', $tasks);

			}
			$data['tasks'] = implode(' | ', array_filter($tasksData));
			$data['officer'] = (str_replace(array('<br>','<br />','<br/>') , ' | ', $page->find('#lblOfficer', 0)->innertext));
			$app = $page->find('#lblProp', 0);
			$a = array();
			foreach($app->find('a') as $anchor) {
				$a[] = trim($anchor->plaintext);
			}
			$data['properties'] = implode(" | ", $a);
			$app = $page->find('#lbldocs', 0);
			$a = array();
			$current = 0;
			foreach($app->find('a') as $anchor) {
				if(trim($anchor->plaintext) == '') continue;
				$a[$current]['name'] = trim($anchor->plaintext);
				$a[$current]['link'] = trim($anchor->href);
				$current+= 1;

			}
			$data['documents'] = $a;
			return $data;
		}
		private function request($url, $header = FALSE, $post = FALSE, $ref = FALSE)
		{
			global $functions;
			$functions->beHuman();
			$page = Spider::spider($header, $ref, $url, FALSE, $post);
			$requestCounter = 1;
			if ($page) {
				return $page;
			}
			while (!$page) {
				$functions->beHuman();
				$page = Spider::spider($header, FALSE, $url, FALSE, $post);
				$requestCounter+= 1;
				if ($requestCounter == 5) {
					$requestCounter = 0;
					return $page;
				}
				if ($page) {
					return $page;
				}
			}
		}

		private function saveApplication($data = array()){
			if(count($data)){
				if(isset($data['suburb'])){
					$file = trim($data['suburb']);
				}else{
					$file = $data['suburb'] = 'Other';
				}
				if(!is_file("./outputs/Applications/$file.csv")){
					file_put_contents("./outputs/Applications/$file.csv", 'Number,Submitted,Details,Zip,Suburb,Street,Heading,Other Details,Decisions,Status,People,Tasks,Officer,Properties,Documents,Application URL'.PHP_EOL);
				}
				$dataToPut = array();
				if(isset($data['number'])){
					$dataToPut['Number'] = trim($data['number']);
				}else{
					$dataToPut['Number'] = 'N/A';
				}
				if(isset($data['submitted'])){
					$dataToPut['Submitted'] = trim($data['submitted']);
				}else{
					$dataToPut['Submitted'] = 'N/A';
				}
				if(isset($data['details'])){
					$dataToPut['Details'] = trim($data['details']);
					preg_match('/[\d+]{4}/', $dataToPut['Details'], $m);
					$dataToPut['Zip'] = trim($m[0]);
				}else{
					$dataToPut['Details'] = 'N/A';
					$dataToPut['Zip'] = 'N/A';
				}
				$dataToPut['Suburb'] = $data['suburb'];			
				if(isset($data['street'])){
					$dataToPut['Street'] = trim($data['street']);
				}else{
					$dataToPut['Street'] = 'N/A';
				}
				if(isset($data['address'])){
					$dataToPut['Heading'] = trim($data['address']);
				}else{
					$dataToPut['Heading'] = 'N/A';
				}
				if(isset($data['other_details'])){
					$dataToPut['Other Details'] = trim($data['other_details']);
				}else{
					$dataToPut['Other Details'] = 'N/A';
				}
				if(isset($data['decisions'])){
					$dataToPut['Decisions'] = trim($data['decisions']);
				}else{
					$dataToPut['Decisions'] = 'N/A';
				}
				if(isset($data['status'])){
					$dataToPut['Status'] = trim($data['status']);
				}else{
					$dataToPut['Status'] = 'N/A';
				}
				if(isset($data['people'])){
					$dataToPut['People'] = trim($data['people']);
				}else{
					$dataToPut['People'] = 'N/A';
				}
				if(isset($data['tasks'])){
					$dataToPut['Tasks'] = trim($data['tasks']);
				}else{
					$dataToPut['Tasks'] = 'N/A';
				}
				if(isset($data['officer'])){
					$dataToPut['Officer'] = trim($data['officer']);
				}else{
					$dataToPut['Officer'] = 'N/A';
				}
				if(isset($data['properties'])){
					$dataToPut['Properties'] = trim($data['properties']);
				}else{
					$dataToPut['Properties'] = 'N/A';
				}
				if(isset($data['documents'])){
					$docs = array();
					foreach ($data['documents'] as $value) {
						$docs[] = trim($value['name'])." => http://pdonline.logan.qld.gov.au/MasterViewUI/".str_replace('../../', '', trim($value['link']));
					}
					$dataToPut['Documents'] = implode(' | ', $docs);
				}else{
					$dataToPut['Documents'] = 'N/A';
				}
				if(isset($data['url'])){
					$dataToPut['Application URL'] = $data['url'];
				}else{
					$dataToPut['Application URL'] = 'N/A';
				}
				fputcsv(fopen("./outputs/Applications/$file.csv", 'a'), $dataToPut);
			}
		}

		private function saveProperty($data = array()){
			if(count($data)){
				if(isset($data['suburb'])){
					$file = trim($data['suburb']);
				}else{
					$file = $data['suburb'] = 'Other';
				}
				if(!is_file("./outputs/Property/$file.csv")){
					file_put_contents("./outputs/Property/$file.csv", 'Title,Street,Suburb,Heading,Zip,Property Number,Lot/DP,Land Number,Ward and Other,Dimensions,Zone,Constraints,Applications,Property URL'.PHP_EOL);
				}
				$dataToPut = array();
				if(isset($data['title'])){
					$dataToPut['Title'] = preg_replace('/\s+/', ' ', trim($data['title']));
				}
				else{
					$dataToPut['Title'] = 'N/A';
				}
				if(isset($data['street'])){
					$dataToPut['Street'] = trim($data['street']);
				}
				else{
					$dataToPut['Street'] = 'N/A';
				}
				if(isset($data['suburb'])){
					$dataToPut['Suburb'] = trim($data['suburb']);
				}
				else{
					$dataToPut['Suburb'] = 'N/A';
				}
				if(isset($data['address'])){
					$dataToPut['Heading'] = trim($data['address']);
					preg_match('/[\d+]{4}/', $dataToPut['Heading'], $m);
					$dataToPut['Zip'] = trim($m[0]);
				}
				else{
					$dataToPut['Heading'] = 'N/A';
					$dataToPut['Zip'] = 'N/A';
				}
				if(isset($data['other_details'])){
					$details = explode('Lot/DP:', str_replace('Property Number:', '', $data['other_details']));
					$dataToPut['Property Number'] = trim($details[0]);
					$details = explode('Land Number(s):', $details[1]);
					$dataToPut['Lot/DP'] = trim($details[0]);
					$details = explode('Ward:', $details[1]);
					$dataToPut['Land Number'] = trim($details[0]);
					unset($details[0]);
					$details = implode(" | ", $details);
					$dataToPut['Ward and Other'] = trim($details);
					
				}
				else{
					$dataToPut['Property Number'] = 'N/A';
					$dataToPut['Lot/DP'] = 'N/A';
					$dataToPut['Land Number'] = 'N/A';
					$dataToPut['Ward and Other'] = 'N/A';
				}
				if(isset($data['dimensions'])){
					$dataToPut['Dimensions'] = trim($data['dimensions']);
				}
				else{
					$dataToPut['Dimensions'] = 'N/A';
				}
				if(isset($data['zone'])){
					$dataToPut['Zone'] = trim($data['zone']);
				}
				else{
					$dataToPut['Zone'] = 'N/A';
				}
				if(isset($data['constraints'])){
					$dataToPut['Constraints'] = trim($data['constraints']);
				}
				else{
					$dataToPut['Constraints'] = 'N/A';
				}
				if(isset($data['applications'])){
					$dataToPut['Applications'] = trim($data['applications']);
				}
				else{
					$dataToPut['Applications'] = 'N/A';
				}
				if(isset($data['url'])){
					$dataToPut['Property URL'] = trim($data['url']);
				}
				else{
					$dataToPut['Property URL'] = 'N/A';
				}
				fputcsv(fopen("./outputs/Property/$file.csv", 'a'), $dataToPut);
			}
		}


	}//End Class
	function parseFile($fileName) {
		$csv = new parseCSV();
		$csv->auto($fileName);
		if (count($csv->data)) {
			return $csv->data;
		} else
		return false;
	}
	function getFilesName($folder = 'Property Enquiry Input') {
		$CSVs = array();
		foreach (glob("./inputs/$folder/*.csv") as $file) {
			if ($file) {
				$CSVs[] = $file;
			}
		}
		return $CSVs;
	}




	if(isset($_POST['useFile'])){
		$type = $_POST['type'];
		if($type = 'application'){
			$files = getFilesName('Application Enquiry Input');
		}else{
			$files = getFilesName();
		}
		foreach($files as $file){
			$data = parseFile($file);
			foreach($data as $singleItem){
				new pdOnlineLogan($_POST['type'], $singleItem['Street'], $singleItem['Suburb']);
			}
		}
		
	}
	else
		new pdOnlineLogan($_POST['type']);

	echo "Done Scrapping..";

