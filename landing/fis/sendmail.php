<?php

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

// sendmail.php

// Configura i parametri del destinatario e del mittente
$to = "adv.fis1967@gmail.com"; // Cambia con l'email reale
$subject = "Nuovo messaggio da landing page";

require 'vendor/autoload.php';

// Recupera e sanifica i dati dal form
$nome = isset($_POST['Nome']) ? htmlspecialchars($_POST['Nome']) : '';
$cognome = isset($_POST['Cognome']) ? htmlspecialchars($_POST['Cognome']) : '';
$citta = isset($_POST['citta']) ? htmlspecialchars($_POST['citta']) : '';
$via = isset($_POST['via']) ? htmlspecialchars($_POST['via']) : '';
$email = isset($_POST['email']) ? htmlspecialchars($_POST['email']) : '';
$telefono = isset($_POST['telefono']) ? htmlspecialchars($_POST['telefono']) : '';
$messaggio = isset($_POST['messaggio']) ? htmlspecialchars($_POST['messaggio']) : '';

// Controlla che i campi obbligatori siano compilati
if (empty($nome) || empty($cognome) || empty($email) || empty($messaggio)) {
    http_response_code(400);
    echo "Tutti i campi obbligatori devono essere compilati.";
    exit;
}

// Mappa i nomi dei campi per compatibilità con il resto del codice
$name = $nome;
$message = $messaggio;

// Invia l'email con PHPMailer
$mail = new PHPMailer(true);

try {
    // Configurazione server SMTP (modifica secondo le tue esigenze)
    $mail->isSMTP();
    $mail->Host = 'pbweb.biz'; // Cambia con il tuo server SMTP
    $mail->SMTPAuth = true;
    $mail->Username = 'sender@pbweb.biz'; // Cambia con il tuo username SMTP
    $mail->Password = '41{|342j22&5'; // Cambia con la tua password SMTP
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;
    $mail->Port = 465;

    // Mittente e destinatario
    $mail->setFrom("sender@pbweb.biz", "FIS Group Srl");
    $mail->addAddress($to);

    // Contenuto
    $mail->Subject = $subject;
    $mail->Body = "Hai ricevuto un nuovo messaggio dal sito:\n\n"
        . "Nome: $nome\n"
        . "Cognome: $cognome\n"
        . "Città: $citta\n"
        . "Via: $via\n"
        . "Email: $email\n"
        . "Telefono: $telefono\n"
        . "Messaggio:\n$messaggio\n";

    $mail->send();
    // echo "Messaggio inviato con successo!";
    header("Location: thanks.html");
    exit;
} catch (Exception $e) {
    http_response_code(500);
    echo "Errore nell'invio del messaggio: {$mail->ErrorInfo}";
    exit;
}


?>
