<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Logan City Tool</title>
	<link rel="stylesheet" href="./assets/css/bootstrap.min.css">
	<link href="./assets/css/font-awesome.min.css" rel="stylesheet">
	<link href="./assets/font-awesome.min.css" rel="stylesheet">
	<!-- Optional theme -->
	<link rel="stylesheet" href="./assets/css/bootstrap-theme.min.css">
	
	<link rel="stylesheet" href="./assets/css/freelancer.css">
	<style>
		.top{
			margin-top: 50px;
		}
		.second{
			margin-top: 20px;
		}
		body {
	background: #EDF1EE;
}

.wrapper {
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    bottom: 10px;
    background: #FFF;
    border: 1px solid #D4E0D7;
}

.badge {
    height: 50px;
    background: #58C777;
    width: 200px;
    text-align: center;
    font-size: 20px;
    line-height: 50px;
    font-family: sans-serif;
    color: #FFF;
    transform: rotate(-45deg);
    position: relative;
    top: -2px;
    left: -70px;
    box-shadow: inset 0px 0px 0px 4px rgba(255, 255, 255, 0.34);
}

.badge:after {
	position: absolute;
	content: '';
	display: block;
	height: 100px;
	width: 100px;
	background: #EDF1EE;
	top: -55px;
	left: 130px;
 transform: rotate(-45deg);
	box-shadow: -115px -121px 0px 0px #EDF1EE;
}

.badge .left {
	position: absolute;
	content: '';
	display: block;
	top: 50px;
	left: 25px;
	height: 8px;
	width: 8px;
	background: linear-gradient(135deg, rgba(90, 146, 106, 1) 50%,rgba(90, 146, 106, 0) 50.1%);
}
.badge .right {
	position: absolute;
	content: '';
	display: block;
	top: 50px;
	left: 157px;
	height: 8px;
	width: 8px;
	background: linear-gradient(135deg, rgba(90, 146, 106, 1) 50%,rgba(90, 146, 106, 0) 50.1%);
	transform: rotate(90deg);
}
.fraction{
	margin-top: 20px;
}
	</style>
	<!-- JQuery -->
	<script src="./assets/js/jquery.js"></script>
	<script type="text/javascript">
		var datefield=document.createElement("input")
		datefield.setAttribute("type", "date")
    if (datefield.type!="date"){ //if browser doesn't support input type="date", load files for jQuery UI Date Picker
    	document.write('<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css" rel="stylesheet" type="text/css" />\n')
    document.write('<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"><\/script>\n')
    document.write('<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"><\/script>\n') 
}
</script>

<script>
if (datefield.type!="date"){ //if browser doesn't support input type="date", initialize date picker widget:
    jQuery(function($){ //on document.ready
    	$('#from').datepicker({ dateFormat: 'yy-mm-dd' }).val();
    	$('#to').datepicker({ dateFormat: 'yy-mm-dd' }).val();
    })
}
</script>

<!-- Latest compiled and minified JavaScript -->
<script src="./assets/js/bootstrap.min.js"></script>
</head>
<body id='page-top' class="index">
	<div class="wrapper">
		<div class="badge">
			<i class="left"></i>
			<i class="right"></i>
			V 2.0
		</div>
	</div>
	<!-- <nav class="navbar navbar-inverse navbar-static"></nav> --> 
	<!-- <nav class="navbar navbar-inverse navbar-fixed-bottom"></nav> -->
	<div class="container top">
		<div class="row">
			<div class="col-md-8 col-md-offset-2">
			<h5 class="note text-center alert alert-info" role = 'alert'>File will just have street and suburbs pair for both Application and Property Enquiry</h5>
				<p class="lead">Property Enquity</p>
				<form action="scrape.php" class="form-inline" role = "form" method="post">
					<div class="form-group">
						<?php
						$street = file('streets.txt', FILE_SKIP_EMPTY_LINES|FILE_IGNORE_NEW_LINES);
						?>
						<select name="street" id="propertyStreets" class="form-control">
							<option value="">Please Select</option>
							<option value="all" >ALL</option>
							<?php foreach($street as $name){ ?>
							<option value="<?php echo $name; ?>"><?php echo $name; ?></option>
							<?php } ?>
						</select>
					</div>
					<div class="form-group">
						<?php
						$subs = file('suburbs.txt', FILE_SKIP_EMPTY_LINES|FILE_IGNORE_NEW_LINES);
						?>
						<select name="suburb" id="propertySuburbs" class="form-control">
							<option value="">Please Select</option>
							<?php foreach($subs as $name){ ?>
							<option value="<?php echo $name; ?>"><?php echo $name; ?></option>
							<?php } ?>
						</select>
					</div>
					<div class="form-group fraction"><input name="useFile" type="checkbox" aria-label="Use CSV File(s) instead (from Property Enquiry Directory)">Use CSV File(s) instead (from Property Enquiry Directory)</div>
					<input type="hidden" value="property" name="type">
					<div class="form-group"><input type="submit" class="btn btn-info btn-md fraction" value="Search Property"></div>
				</form>
			</div>
		</div>
	</div>
	<div class="container second">
		<div class="row">
			<div class="col-md-8 col-md-offset-2">
				<p class="lead">Application Enquiry</p>
				<!-- /.lead -->
				<form action="scrape.php" class="form-horizontal" role = "form" method="post">
					<div class="form-group"><label for="from"class="col-md-3 control-label">From :</label><div class="col-md-5"><input id="from" name="from" type="date"/></div></div>
					<!-- /.form-group -->
					<div class="form-group"><label for="to" class="col-md-3 control-label">To :</label><div class="col-md-5"><input type="date" name="to" id="to"></div></div>
					<input type="hidden" value="application" name="type">
					<div class="form-group">
						<select name="street" id="appStreets" class="form-control">
							<option value="">Please Select</option>
							<option value="all">All</option>
							<?php foreach($street as $name){ ?>
							<option value="<?php echo $name; ?>"><?php echo $name; ?></option>
							<?php } ?>
						</select>
					</div>
					<div class="form-group">
						
						<select name="suburb" id="appSuburbs" class="form-control">
							<option value="">Please Select</option>
							<?php foreach($subs as $name){ ?>
							<option value="<?php echo $name; ?>"><?php echo $name; ?></option>
							<?php } ?>
						</select>
					</div>
					<div class="form-group fraction"><input name="useFile" type="checkbox" aria-label="Use CSV File(s) instead (from Application Enquiry Directory)">Use CSV File(s) instead (from Application Enquiry Directory)</div>
					<div class="form-group"><input type="submit" class="btn btn-info btn-md" value="Search Applications"></div>
				</form>
				<!-- /.form-horizontal -->
			</div>
			<!-- /.col-md-8 col-md-offset-2 -->
		</div>
		<!-- /.row -->
	</div>
	<!-- /.container -->
</body>