<html>
<head>
	<meta charset="UTF-8">
	<title>Chatbox – Thank you!</title>
	<link rel="stylesheet" type="text/css" href="css/survey.css">
	<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
	
<?php
    // Getting the params of the form
	$cryptID = filter_input(INPUT_POST, "cryptID");
    $userID = filter_input(INPUT_POST, "userID");

    $turkID = filter_input(INPUT_POST, "turkID");

    $ratings = [];
    $ratingsCount = filter_input(INPUT_POST, "history-count");

    for($i = 0; $i < $ratingsCount; $i++) {
        $rating = filter_input(INPUT_POST, "rating-q" . ($i + 1));
        array_push($ratings, $rating);
    }

    $survey_q1 = filter_input(INPUT_POST, "survey-q1");
    $survey_q2 = filter_input(INPUT_POST, "survey-q2");
    $survey_q3 = filter_input(INPUT_POST, "survey-q3");
    $survey_q4 = filter_input(INPUT_POST, "survey-q4");

    // Save to file
    $timestamp = date("Y-m-d-H-i-s", time());

    $json_array = [
        'metadata' => array(
            'date' => $timestamp
        ),
        'cryptID'=> $cryptID,
        'userID' => $userID,
        'turkID' => $turkID,
        'survey' => [
            'q1' => $survey_q1,
            'q2' => $survey_q2,
            'q3' => $survey_q3,
	    'q4' => $survey_q4
        ],
        'rating' => $ratings
    ];

    $fn = dirname( __FILE__, 3). "/logs/survey_logs/user-" . $userID . ".txt";
    $file = fopen($fn, "a+") or die("Could not open survey_log file. Please report this to HIT administrator.");
    $json = json_encode($json_array);
    fwrite($file, $json);
    fwrite($file, "\n");
    fclose($file);
?>

<section id="heading">
    <h1>Thank you!</h1>
    <p>You can now return to the mechanical turk page. Your validation code is:</p>
	<div class="validation-code">
	    <p><?php echo $cryptID ?></p>
	</div>
</section>
	
</body>
