<!doctype html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chatbox Survey</title>
    <link rel="stylesheet" type="text/css" href="css/survey.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <script type="text/javascript">
        function validateForm() {
            // TODO: Validate form
            return true;
        }
    </script>
</head>

<body>
<section id="heading">
    <h1>Survey</h1>
</section>

<section id="form">
    <form name="survey" method="POST" action="survey_submit.php" onsubmit="return validateForm();" accept-charset="UTF-8">
        <input type="hidden" name="userID" value="<?php echo $_GET["id"]?>">
        <input type="hidden" name="cryptID" value="<?php echo @crypt($_GET["id"]) ?>">
        <fieldset class="section" name="turkID">
            <label for="turkid-input">Your Turk ID:</label>
            <input type="text" name="turkID" id="turkid-input" required>
        </fieldset>
        <fieldset class="section" id="part-1">
            <h1>Part 1</h1>
            <div class="instruction">
                <p>Rate how appropriate you feel the system's response with respect to your input. Try to make the decision for each round independently, try not to take context into consideration.</p>
                <p>"Not appropriate" means the system response is not coherent at all, <br>e.g. Participant: How old are you? Chatbot: Apple</p>
                <p>"Interpretable" means the system response is related and can be interpreted in a way. <br>e.g. Participant: How old are you? Chatbot: That's too big a question for me to answer.</p>
                <p>"Appropriate" means the system response, is very coherent with the user's previous utterance. <br>e.g.Participant: How is the weather today? Chatbot: Very good.</p>
            </div>

            <?php
            $log_file = dirname(__FILE__, 3) . '/logs/json_logs/' . $_GET["id"] . '.json';
            //$jsonLog = file_get_contents($log_file);
            $jsonLog = escapeshellarg($log_file);
            $jsonLog = `tail -n 1 $jsonLog`;
            $log = json_decode($jsonLog, true);

            $history = $log['history'];

            echo '<input type="hidden" name="history-count" value="' . count($history) . '">';

            for($i = 0; $i < count($history); $i++) {
                echo '<fieldset class="question" name="rating-q' . ($i + 1) . '">';
                echo '<div class="turn"><h1>Turn ' . ($i + 1) . '</h1></div>';
                echo '<div class="chat-entry">';
                echo '<h2>Computer:</h2>';
                $cResponse = $history[$i]['c'];
                if (count($cResponse) === 0) {
                    echo '<p class="did-not-respond">The chatbot did not respond</p>';
                } else {
                    for($c = 0; $c < count($cResponse); $c++) {
                        echo '<p>' . $cResponse[$c] . '</p>';
                    }
                }
                echo '</div>';

                echo '<div class="chat-entry">';
                echo '<h2>You:</h2>';
                $uResponse = $history[$i]['u'];
                if (count($uResponse) === 0) {
                    echo '<p class="did-not-respond">You did not respond.</p>';
                } else {
                    for($u = 0; $u < count($uResponse); $u++) {
                        echo '<p>' . $uResponse[$u] . '</p>';
                    }
                }
                echo '</div>';

                echo '<h2>Your rating:</h2>';
                echo '<input type="radio" name="rating-q' . ($i + 1) . '" id="rating-q' . ($i + 1) . '-input-1" value="1" required>';
                echo '<label for="rating-q' . ($i + 1) . '-input-1">Not Appropriate</label>';
                echo '<input type="radio" name="rating-q' . ($i + 1) . '" id="rating-q' . ($i + 1) . '-input-2" value="2">';
                echo '<label for="rating-q' . ($i + 1) . '-input-2">Interpretable</label>';
                echo '<input type="radio" name="rating-q' . ($i + 1) . '" id="rating-q' . ($i + 1) . '-input-3" value="3">';
                echo '<label for="rating-q' . ($i + 1) . '-input-3">Appropriate</label>';

                echo '</fieldset>';
            }
            ?>
        </fieldset>

        <fieldset class="section" id="part-2">
            <h1>Part 2</h1>
            <p>Please answer the questions below.</p>

            <fieldset class="question" name="survey-q1">
                <h2><label>Have you talked to a chatbot before?</label></h2>
                <input type="radio" name="survey-q1" id="survey-q1-input-1" value="1" required><label
                        for="survey-q1-input-1">Yes</label>
                <input type="radio" name="survey-q1" id="survey-q1-input-2" value="0"><label for="survey-q1-input-2">No</label>
            </fieldset>

            <fieldset class="question survey" name="survey-q2">
                <h2><label>Do you like the recommended movie?</label></h2>
                <input type="radio" name="survey-q2" id="survey-q2-input-1" value="1" required><label
                        for="survey-q2-input-1">1 (No)</label>
                <input type="radio" name="survey-q2" id="survey-q2-input-2" value="2"><label
                        for="survey-q2-input-2">2</label>
                <input type="radio" name="survey-q2" id="survey-q2-input-3" value="3"><label
                        for="survey-q2-input-3">3</label>
                <input type="radio" name="survey-q2" id="survey-q2-input-4" value="4"><label
                        for="survey-q2-input-4">4</label>
                <input type="radio" name="survey-q2" id="survey-q2-input-5" value="5"><label
                        for="survey-q2-input-5">5 (Very)</label>
            </fieldset>

            <fieldset class="question survey" name="survey-q3">
                <h2><label>How engaged you feel during the conversation?</label></h2>
                <input type="radio" name="survey-q3" id="survey-q3-input-1" value="1" required><label
                        for="survey-q3-input-1">1 (None)</label>
                <input type="radio" name="survey-q3" id="survey-q3-input-2" value="2"><label
                        for="survey-q3-input-2">2</label>
                <input type="radio" name="survey-q3" id="survey-q3-input-3" value="3"><label
                        for="survey-q3-input-3">3</label>
                <input type="radio" name="survey-q3" id="survey-q3-input-4" value="4"><label
                        for="survey-q3-input-4">4</label>
                <input type="radio" name="survey-q3" id="survey-q3-input-5" value="5"><label
                        for="survey-q3-input-5">5 (Very)</label>
            </fieldset>

            <fieldset class="question survey" name="survey-q4">
                <h2><label for="survey-q4-input-1">What do you like and not like about the chatbot, and any questions
                        and suggestions?</label></h2>
                <textarea name="survey-q4" id="survey-q4-input-1" required></textarea>
            </fieldset>



            <input type="submit" name="submit-survey" value="Submit">
    </form>
</section>
</body>
</html>
