<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$imageFileType = strtolower(pathinfo($target_file,PATHINFO_EXTENSION));

    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        echo "S'ha carregat el fitxer ". basename( $_FILES["fileToUpload"]["name"]). ". ";

        $locale = 'ca_ES.UTF-8';
        setlocale(LC_ALL, $locale);
        putenv('LC_ALL='.$locale);

        $command = escapeshellcmd('python3 main.py "'.$target_file.'"');
        shell_exec($command);
        $command = escapeshellcmd('bash sort-files.sh');
        shell_exec($command);


    } else {
        echo "Hi ha hagut un error: ".$target_file ;
    }

?>

<!DOCTYPE html>
<html>
<body>

<h1>Resultats</h1>
<p><a href="output.txt" target="_blank">output.txt</a></p>
<p><a href="spa.txt" target="_blank">spa.txt</a></p>
<p><a href="cat.txt" target="_blank">cat.txt</a></p>
<p><a href="spa-cat.txt" target="_blank">spa-cat.txt</a></p>
<p><a href="paradigmes.txt" target="_blank">paradigmes.txt</a></p>

</body>
</html>
