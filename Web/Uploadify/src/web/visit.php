<?php

if(isset($_GET["id"])) {
  $int_id = (int) $_GET["id"];

  system("python3 /challenge/bot.py " . $int_id);
}
