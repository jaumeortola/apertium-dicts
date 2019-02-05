<!DOCTYPE html>
<html>
<head>
<title>Script Apertium spa-cat</title>
</head>
<body>

<h1>Puja ací el fitxer .tsv creat en el full de càlcul</h1>

<form action="index.php" method="post" enctype="multipart/form-data">
    Tria un fitxer .tsv:
    <input type="file" name="fileToUpload" id="fileToUpload">
    <input type="submit" value="Envia" name="submit">
</form>




<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$imageFileType = strtolower(pathinfo($target_file,PATHINFO_EXTENSION));

    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        $locale = 'ca_ES.UTF-8';
        setlocale(LC_ALL, $locale);
        putenv('LC_ALL='.$locale);

        $command = escapeshellcmd('python3 main.py "'.$target_file.'"');
        shell_exec($command);
        $command = escapeshellcmd('sort-files.sh');
        shell_exec($command);

echo '<h1>Resultats</h1>
<p>Heu carregat el fitxer '. basename( $_FILES["fileToUpload"]["name"]).'</p>
<p><a href="output.txt" download>output.txt</a></p>
<p><a href="spa.txt" target="_blank">spa.txt</a></p>
<p><a href="cat.txt" target="_blank">cat.txt</a></p>
<p><a href="spa-cat.txt" target="_blank">spa-cat.txt</a></p>
<p><a href="paradigmes.txt" download>paradigmes.txt</a></p>';

    } else {
        /*echo "Hi ha hagut un error: ".$target_file ;*/
    }

?>


</body>
</html>
