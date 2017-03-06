<?php
require_once "nusoap.php";

function checkService($input) {
	if (file_exists('./serviceIP.txt')) {
        	$serviceIP = explode("\n", file_get_contents('./serviceIP.txt'));
		$serviceX = new nusoap_client("http://" . $serviceIP[X] .  "/service2.php?wsdl", true);
	}
        $result = "serviceX";
        return $result;
}

$input = "serviceX";

if (file_exists('./serviceIP.txt')) {
        $serviceIP = explode("\n", file_get_contents('./serviceIP.txt'));
	$serviceX = new nusoap_client("http://" . $serviceIP[X] .  "/service2.php?wsdl", true);
}

$errorX = $serviceX->getError();
if ($errorX) {
        echo "Constructor error: " . $errorX . "\n";
}

$resultX = $serviceX->call("checkService", array("input" => $input));

if ($serviceX->fault) {
        echo "Fault: ";
        print_r($resultX);
} else {
        $errorX = $serviceX->getError();
        if ($errorX) {
                echo "Error: " . $errorX . "\n";
        } else {
                echo $input . " poziva " . $resultX . "\n";
        }
}

$server = new soap_server();
$server->configureWSDL("status", "urn:status");

$server->register("checkService",
    array("input" => "xsd:string"),
    array("return" => "xsd:string"),
    "urn:status",
    "urn:status#checkService",
    "rpc",
    "encoded",
    "Check if service is working by passing your name");

$server->service($HTTP_RAW_POST_DATA);
?>
