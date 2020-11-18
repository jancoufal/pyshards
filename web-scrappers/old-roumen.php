<html>
<head>
	<title>roumen.cz compressor</title>
	<style type="text/css">
	body {
		font: 0.7em/1.5 "Lucida Console", Courier, monospace;
		margin: 1em;
		padding: 0;
		text-align: center;
		color: #cccccc;
		background-color: #000000;
		//white-space: pre;
	}
	
	h1 {
		width: 100%;
		margin: 0 0 0.5em 0;
		padding: 0;
		text-align: left;
		border-bottom: 1px solid #cccccc;
	}
	
	a, a:visited {
		color: #ffffff;
		text-decoration: none;
	}
	
	h2 {
		width: 100%;
		margin: 0;
		padding: 0;
		border-top: 1px solid #cccccc;
		font-size: 1em;
		text-align: right;
		color: #777777;
	}
	a.hl { color: #3399ff; }
	a:hover, a:active { color: #ff3399; }
	
	.cont img {
		margin-bottom: 5em;
	}
	
	</style>
</head>

<body>
<?php

//$baseUrl = 'http://127.0.0.1';
$baseUrl = 'http://roumen.iddqd.cz';
$baseFile= '/index.php';

$section = null;
switch( @$_GET['s']) {
	
case 'maso':
		$section='maso';
		$curlSrc = 'https://www.roumenovomaso.cz?agree=on';
		$imgUrl = 'https://www.roumenovomaso.cz/upload/';
		$pregExp = '/masoShow\.php\?[^"]*/';
		break;
	
case 'kecy': // fall thru
default:
		$section='kecy';
		$curlSrc = 'https://www.rouming.cz';
		$imgUrl = 'https://www.rouming.cz/upload/';
		$pregExp = '/roumingShow\.php\?[^"]*/';
		break;
}

?>

<h1>
roumen compressor - [<?php
printf('<a class="dummy%s" href="%s?s=kecy">kecy</a>/<a class="dummy%s" href="%s?s=maso">maso</a>',
	$section=='kecy' ? ' hl' : '',
	$baseUrl.$baseFile,
	$section=='maso' ? ' hl' : '',
	$baseUrl.$baseFile
);
?>]
</h1>

<div class="cont">
<?php

$curl = curl_init();
curl_setopt($curl, CURLOPT_URL, $curlSrc);
curl_setopt($curl, CURLOPT_HEADER, 0);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($curl, CURLOPT_USERAGENT, 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0');

$curlReturn = curl_exec($curl);

/*
print_r(curl_getinfo($curl));
echo "\n\n";

echo $curlReturn;
echo "\n";
*/


/*
	src: ...<a href="http://kecy.roumen.cz/roumingShow.php?file=-Old_Men-.jpg" target="Rouming">...
*/

preg_match_all(
	$pregExp,
	$curlReturn,
	$imgSrcs,
	PREG_SET_ORDER);

/*
echo '<pre style="font-size: 2em; text-align: left;">'."\n";
print_r( $imgSrcs);
echo '</pre>'."\n";
*/

foreach($imgSrcs as $k => $v)
{
	// $v = "roumingShow.php?file=zacpane_trubky.png"
	list($dummy,$fname) = explode('=',$v[0]);
	
//	print_r($fname);
	
	printf('<span>%s</span><br />'."\n", $fname);
	printf('<img src="%s%s" /><br />'."\n", $imgUrl, $fname);
}

?>
</div>
<h2>compressed by <a href="http://iddqd.cz">griffin</a></h2>


<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-26643120-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>

</body>

